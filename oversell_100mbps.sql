with target_program as (
    select 100
  ),

cheaper_program as (
      select 40
  ),

rush_hour_speed_tests as (
  select *, user_details.user_name as name
  from comparison_info
  join file_download_info on comparison_info.file_download_info_id = file_download_info.id
  join test t on comparison_info.test_id = t.id
  join user_details on t.user_name = user_details.user_name and user_details.speed != 1000
  where file_download_ratekbper_sec != 'infinity'
  and speed = (select * from target_program)
  and date_part('hour', to_timestamp(start_downloading_timestamp/ 1000) at time zone 'IST' + '1 hour')::int  between 18 and 23 -- evening
  and date_part('day', to_timestamp(start_downloading_timestamp/ 1000) at time zone 'IST' + '1 hour') in (3, 5, 6, 7) -- "Thursday, Friday, Saturday, Tuesday"
  ),

user_rush_avg as (
      select
        avg(file_download_ratekbper_sec / 1024 * 8) actual_avg_speed,
        name                                        user_name
      from rush_hour_speed_tests
      group by name
      order by actual_avg_speed
  ),

oversell as (
  select count (user_name), actual_avg_speed <= (select * from cheaper_program) as oversell from user_rush_avg
  group by actual_avg_speed <= (select * from cheaper_program)
  )

select count, case when oversell then 'oversold' else 'not oversold' end
from oversell;
