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
