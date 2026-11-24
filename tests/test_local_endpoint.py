import json
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

class LocalEndpointTests(unittest.TestCase):
    def status(self, origin, host='127.0.0.1:3000'):
        request = Request('http://127.0.0.1:3000/api/connect', method='POST',
                          headers={'Origin': origin, 'Host': host})
        try:
            with urlopen(request) as response:
                data = json.load(response)
                self.assertIn('token', data)
                return response.status
        except HTTPError as error:
            return error.code

    def test_browser_loopback_origin(self):
        self.assertEqual(self.status('http://127.0.0.1:3000'), 200)

    def test_browser_localhost_origin(self):
        self.assertEqual(self.status('http://localhost:3000', 'localhost:3000'), 200)

    def test_external_origin_denied(self):
        self.assertEqual(self.status('https://example.com'), 403)

    def test_external_host_denied(self):
        self.assertEqual(self.status('http://example.com:3000', 'example.com:3000'), 403)

    def test_different_local_origin_denied(self):
        self.assertEqual(self.status('http://localhost:3000'), 403)
