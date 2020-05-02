with user_averages_lan as (
    select user_name, avg(ground_truth_rate) total_average
    from valid_tests
    where connection = 'LAN'
    group by user_name
),
user_averages_lan_time_bins as (
    select user_name, get_time_of_day(timestamp) time_of_day, avg(ground_truth_rate) time_average
    from valid_tests
    where connection = 'LAN'
    group by user_name, time_of_day
)
select time_of_day, avg(time_average / total_average) as ratio
from user_averages_lan_time_bins
join user_averages_lan on user_averages_lan.user_name = user_averages_lan_time_bins.user_name
group by time_of_day
order by ratio, time_of_day
;

