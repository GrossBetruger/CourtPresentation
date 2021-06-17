import ipaddress
import json
import psycopg2
import ttl_cache
import ipwhois

from typing import List, Union, Optional, Generator
from ipwhois import IPWhois
from utils import get_engine, get_rows


CREATE_WHOIS_CACHE = """
    create table if not exists whois_data (
        cidr cidr,
        reference_filename text,
        data json,
        last_updated timestamptz,
        unique (cidr)
    );
"""

engine = get_engine()
engine.cursor().execute(CREATE_WHOIS_CACHE)
engine.commit()


@ttl_cache(1000)
def whois_lookup(ip: str, file_name: str, use_cache=True) -> Generator[None, None, Optional[dict]]:
    """Perform Whois lookup for a given IP
        :ip: Ip to peform whois lookup
        :returns Optional[dict] with whois data
    """
    ip_obj = ipaddress.ip_address(ip)
    if ip_obj.is_private is True:
        print(ip_obj, "is private")
        return

    cached_cidr = check_ip_in_cache(ip_obj)
    if use_cache is True and cached_cidr:
        print(f"Cache HIT! {ip, cached_cidr}")
        return read_whois_cache(cached_cidr)

    print(f"cache miss: {ip}")

    response = None
    try:
        obj = IPWhois(ip)
        response = obj.lookup_whois()
    except ipwhois.exceptions.IPDefinedError:
        return

    cidr = None
    if response['nets'][0].get('cidr'):
        cidr = response['nets'][0].get('cidr')

    if cidr is None:
        return

    details = response['nets'][0]
    name = details['name']
    city = details['city']
    state = details['state']
    country = details['country']
    address = details['address']
    description = details['description']

    cidrs = cidr.split(", ")
    print(f"cidrs: {cidrs}")
    for cidr in cidrs:
        whois_data = {'cidr': cidr, 'name': name, 'city': city, 'state': state,
                'country': country, 'address': address, 'description': description}

        update_whois_cache(cidr, file_name, whois_data)
        yield whois_data


def update_whois_cache(cidr: str, filename: str, whoisdata: dict):
    try:
        engine.cursor().execute(
            "insert into whois_data values (%s, %s, %s, timezone('Israel',now()::timestamptz))",
            (cidr, filename, json.dumps(whoisdata))
        )
    except psycopg2.errors.UniqueViolation:
        engine.rollback()
        print(f"cidr already cached: {cidr}")
        return

    engine.commit()
    print(f"updated: {cidr}")


def read_whois_cache(cidr: str):
    return get_rows("select data from whois_data where cidr = %s", (cidr,))[0][0]


def get_all_cidrs() -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
    cidrs = [ipaddress.ip_network(x[0]) for x in get_rows("select cidr from whois_data")]
    return cidrs


@ttl_cache(1000)
def check_ip_in_cache(ip: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> Optional[str]:
    for cidr in get_all_cidrs():
        if ip in cidr:
            return str(cidr)


if __name__ == "__main__":
    ip_obj = ipaddress.ip_address("13.32.145.149")
    print(check_ip_in_cache(ip_obj))
    pass