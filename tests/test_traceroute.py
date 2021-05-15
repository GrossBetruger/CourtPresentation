import unittest

from tracerout.traceroute_parser import get_traceroutes
from tracerout.whois_tool import whois_lookup


class TestTraceroute(unittest.TestCase):
    def test_whois(self):
        whois = whois_lookup("31.210.191.17")
        from pprint import pprint; pprint(whois)
        self.assertEqual(True, False)

    def test_traceroute(self):
        traceroutes = get_traceroutes()

        
if __name__ == '__main__':
    unittest.main()
