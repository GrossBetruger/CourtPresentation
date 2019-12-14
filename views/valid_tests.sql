-- VALID TESTS VIEW
create view valid_tests as
    select (calculate_download_rate_kbps(file_downloaded_time_in_ms, file_size_in_bytes) / 1024.0) * 8 as ground_truth_rate,
           download_rate_in_mbps speed_test_rate,
           test.user_name,
           test.connection,
           user_details.speed,
           speed_test_identifier as website,
           file_name,
           is_classic_test,
           infrastructure,
           regexp_replace(user_details.isp, '^\S+ (.+$)', '\1') isp,
           start_downloading_timestamp as timestamp
    from test
    join comparison_info on comparison_info.test_id = test.id
    join file_download_info on comparison_info.file_download_info_id = file_download_info.id
    full outer join speed_test_web_site on speed_test_web_site.id = comparison_info.speed_test_web_site_download_info_id
    join user_details on test.user_name = user_details.user_name
    where (analyzed_state = 0 or test.is_classic_test = False)
    and test.user_name not in (select * from debug_users)
    and file_download_ratekbper_sec != 'infinity'
