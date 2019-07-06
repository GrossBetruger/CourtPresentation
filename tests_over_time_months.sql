select count(comparison_info.*) num_of_tests,
  (date_part('year', TO_TIMESTAMP(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour'), date_part('month', TO_TIMESTAMP(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour')) time_of_test
from comparison_info
    join file_download_info on comparison_info.file_download_info_id = file_download_info.id
    join speed_test_web_site on speed_test_web_site.id = comparison_info.speed_test_web_site_download_info_id
    join test t on comparison_info.test_id = t.id
    join user_details on t.user_name = user_details.user_name
  where download_rate_in_mbps > 0 and file_download_ratekbper_sec != 'infinity'
  and (speed_test_web_site.analyzed_state = 0 or t.is_classic_test = false)
  group by (date_part('year', TO_TIMESTAMP(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour'), date_part('month', TO_TIMESTAMP(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour'))
  order by (date_part('year', TO_TIMESTAMP(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour'), date_part('month', TO_TIMESTAMP(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour'));
