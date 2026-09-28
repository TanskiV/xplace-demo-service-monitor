import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from service_monitor.monitor import check_service


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        status = 200 if self.path == "/health" else 503
        self.send_response(status)
        self.end_headers()

    def log_message(self, *_args):
        return


class MonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=2)

    def test_healthy_service(self):
        result = check_service("demo", self.base_url + "/health")
        self.assertTrue(result.ok)
        self.assertEqual(result.status, 200)
        self.assertIsNotNone(result.latency_ms)

    def test_unhealthy_status(self):
        result = check_service("demo", self.base_url + "/broken")
        self.assertFalse(result.ok)
        self.assertEqual(result.status, 503)

    def test_unavailable_service_is_fail_closed(self):
        result = check_service("demo", "http://127.0.0.1:1/nope", timeout=0.1)
        self.assertFalse(result.ok)
        self.assertIsNotNone(result.error)


if __name__ == "__main__":
    unittest.main()
