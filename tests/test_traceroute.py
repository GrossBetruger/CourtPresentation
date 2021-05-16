import ipaddress
import unittest

from tracerout.traceroute_parser import get_traceroutes
from tracerout.whois_tool import whois_lookup, check_ip_in_cache


class TestTraceroute(unittest.TestCase):
    def test_whois(self):
        whois = whois_lookup("31.210.191.17")
        self.assertEqual("IL", whois["country"])
        self.assertEqual("XFONE_Broadband", whois["name"])
        self.assertEqual("1 Bet Sheva st. Lod", whois["address"])
        self.assertEqual("185.149.252.0/23", check_ip_in_cache(ipaddress.ip_address("185.149.252.109")))

    def test_traceroute(self):
        traceroutes = get_traceroutes()


if __name__ == '__main__':
    unittest.main()
