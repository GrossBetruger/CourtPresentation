select avg(ratio),  website
from (
  select t.user_name, t.speed_test_website_identifier website, (file_download_ratekbper_sec / ((download_rate_in_mbps / 8.0) * 1024)) as ratio
  from comparison_info
    join file_download_info on comparison_info.file_download_info_id = file_download_info.id
    join speed_test_web_site on speed_test_web_site.id = comparison_info.speed_test_web_site_download_info_id
    join test t on comparison_info.test_id = t.id
  where download_rate_in_mbps > 0
  and (file_download_ratekbper_sec / ((download_rate_in_mbps / 8.0) * 1024)) between 0.01 and 100
  and t.speed_test_website_identifier != 'atnt'
  and analyzed_state = 0
) data
group by  website order by avg(ratio);
