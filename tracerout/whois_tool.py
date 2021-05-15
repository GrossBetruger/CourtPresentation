import json

from ipwhois import IPWhois

from utils import get_engine

CREATE_WHOIS_CACHE = """
    create table if not exists whois_data (
        cidr cidr,
        data json
    );
"""

engine = get_engine()
engine.cursor().execute(CREATE_WHOIS_CACHE)
engine.commit()


def whois_lookup(ip):
    """Perform Whois lookup for a given IP
        :ip: Ip to peform whois lookup
    """
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


if __name__ == "__main__":
    whois_data = whois_lookup("185.149.252.109")
    print(whois_data["cidr"])
    # update_whois_cache(whois_data["cidr"], whois_data)