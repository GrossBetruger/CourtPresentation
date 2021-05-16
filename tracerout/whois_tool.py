import ipaddress
import json
from typing import Set, List, Union, Optional

from ipwhois import IPWhois

from utils import get_engine, get_rows

CREATE_WHOIS_CACHE = """
    create table if not exists whois_data (
        cidr cidr,
        data json
    );
"""

engine = get_engine()
engine.cursor().execute(CREATE_WHOIS_CACHE)
engine.commit()


def whois_lookup(ip: str, use_cache=True) -> dict:
    """Perform Whois lookup for a given IP
        :ip: Ip to peform whois lookup
    """

    cached_cidr = check_ip_in_cache(ipaddress.ip_address(ip))
    if use_cache is True and cached_cidr:
        return read_whois_cache(cached_cidr)

    obj = IPWhois(ip)

    # cidr, ranges = "CIDR not found", "Range not found"

    # Get whois for IP. Returns a list with dictionary
    # ip_dict = IPWhois(ip).lookup_rws()
    response = obj.lookup_whois()
    cidr = None
    if response['nets'][0].get('cidr'):
        cidr = response['nets'][0].get('cidr')
    details = response['nets'][0]
    name = details['name']
    city = details['city']
    state = details['state']
    country = details['country']
    address = details['address']
    description = details['description']

    return {'cidr': cidr, 'name': name, 'city': city, 'state': state,
            'country': country, 'address': address, 'description': description}


def update_whois_cache(cidr: str, whois_data: dict):
    engine.cursor().execute(
        "insert into whois_data values (%s, %s)",
        (cidr, json.dumps(whois_data))
    )
    engine.commit()


def read_whois_cache(cidr: str):
    return get_rows("select data from whois_data where cidr = %s", (cidr,))[0][0]


def get_all_cidrs() -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
    cidrs = [ipaddress.ip_network(x[0]) for x in get_rows("select cidr from whois_data")]
    return cidrs


def check_ip_in_cache(ip: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> Optional[str]:
    # ip = ipaddress.ip_network('192.168.0.0/24')
    for cidr in get_all_cidrs():
        if ip in cidr:
            return str(cidr)


if __name__ == "__main__":
    whois_data = whois_lookup(ipaddress.ip_address("31.210.191.17"))
    # print(whois_data["cidr"])
    update_whois_cache(whois_data["cidr"], whois_data)