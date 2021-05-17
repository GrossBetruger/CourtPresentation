import re

from tracerout.whois_tool import whois_lookup, update_whois_cache
from utils import get_rows


def get_traceroutes():
    traceroute_results = get_rows("""
    select file_name,
       trace_pre,
       trace_post
    from file_download_info
    where trace_pre is not null and trace_post is not null;
    """)
    return traceroute_results


def populate_whois_cache():
    for res in get_traceroutes():
        file, pre, post = res
        ips = re.findall("\[(.+?)]", pre)
        print(file)
        for ip in ips:
            for whois_data in whois_lookup(ip, file):
                if whois_data is None:
                    print(f"private: {ip}")
                    continue
    print("ALL DONE")


if __name__ == "__main__":
    populate_whois_cache()
