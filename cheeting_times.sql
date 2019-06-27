select * from (
  select
    avg(file_download_ratekbper_sec / 1024 * 8) average_actual_speed,
        concat(TO_CHAR(TO_TIMESTAMP(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour', 'day'),
                  ' ',
                 case when TO_CHAR(TO_TIMESTAMP(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour', 'HH24')::int between 0 and 5  then 'night'
                      when TO_CHAR(TO_TIMESTAMP(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour', 'HH24')::int between 6 and 11  then 'morning'
                      when TO_CHAR(TO_TIMESTAMP(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour', 'HH24')::int between 12 and 17  then 'noon'
                      when TO_CHAR(TO_TIMESTAMP(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour', 'HH24')::int between 18 and 23  then 'evening'
                  else 'not night' end) test_time,
    avg(file_download_ratekbper_sec / ((download_rate_in_mbps / 8.0) * 1024)) as                 ratio,
    t.speed_test_website_identifier                                                              website,
    count(t.*)                                                                                   number_of_tests
  from comparison_info
    join file_download_info on comparison_info.file_download_info_id = file_download_info.id
    join speed_test_web_site on speed_test_web_site.id = comparison_info.speed_test_web_site_download_info_id
    join test t on comparison_info.test_id = t.id
    join user_details on t.user_name = user_details.user_name
  where download_rate_in_mbps > 0 and file_download_ratekbper_sec != 'infinity'
  and analyzed_state = 0
  group by test_time, website
  order by average_actual_speed
) data
where ratio < 0.76;
