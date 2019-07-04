with actual_to_program as (select file_download_ratekbper_sec / 1024 * 8 actual_speed, speed paying_for
    from comparison_info
      join file_download_info on comparison_info.file_download_info_id = file_download_info.id
      join speed_test_web_site on speed_test_web_site.id = comparison_info.speed_test_web_site_download_info_id
      join test t on comparison_info.test_id = t.id
      join user_details on t.user_name = user_details.user_name and user_details.speed not in (15, 200, 30, 1000)
      where file_download_ratekbper_sec != 'infinity'
      and t.connection = 'Wifi'
      and user_details.speed = 40
      and date_part('hour', to_timestamp(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour')::int  between 18 and 23 -- evening
      and date_part('day', to_timestamp(start_measuring_timestamp/ 1000) at time zone 'IST' + '1 hour') in (3, 5, 6, 7) -- "Thursday, Friday, Saturday, Tuesday"
    ),
      
percent_of_service as (select case when (actual_speed / paying_for) between 0 and 0.2 then '0-20%'
            when (actual_speed / paying_for) between 0.2 and 0.4 then '20-40%'
            when (actual_speed / paying_for) between 0.4 and 0.6 then '40-60%'
            when (actual_speed / paying_for) between 0.6 and 0.8 then '60-80%'
            when (actual_speed / paying_for) between 0.8 and 1 then '80-100%'
            when (actual_speed / paying_for) between 1 and 1.2 then '100-120%'
            when (actual_speed / paying_for) between 1.2 and 1.4 then '120-140%'
            when (actual_speed / paying_for) between 1.4 and 1.6 then '140-160%'
            when (actual_speed / paying_for) between 1.6 and 1.8 then '160-180%'    
            when (actual_speed / paying_for) between 1.8 and 2 then '180-200%'            
        else '200%+'
        end as percent
from actual_to_program)

select percent, count(percent) from percent_of_service group by percent order by count

