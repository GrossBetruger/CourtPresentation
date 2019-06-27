select avg(file_download_ratekbper_sec / 1024 * 8) average_actual_speed, t.connection, count(t.*) number_of_tests, user_details.speed--concat(t.user_name::text, ' (', speed::text, ')')
    from comparison_info
      join file_download_info on comparison_info.file_download_info_id = file_download_info.id
      join speed_test_web_site on speed_test_web_site.id = comparison_info.speed_test_web_site_download_info_id
      join test t on comparison_info.test_id = t.id
      join user_details on t.user_name = user_details.user_name and user_details.speed != 1000
    where file_download_ratekbper_sec != 'infinity'
    and analyzed_state = 0
    
group by t.connection, user_details.speed
order by user_details.speed;
