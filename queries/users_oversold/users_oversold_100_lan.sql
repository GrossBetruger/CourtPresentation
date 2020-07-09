with user_averages as (
    select avg(ground_truth_rate), user_name, speed, count(*) number_of_tests
    from valid_tests
    where connection = 'LAN'
    and speed = 100
    group by user_name, speed
),

oversell as (select 0.5),

total_users as (
    select count(distinct user_name) from user_averages
),

user_oversell as (
    select user_name,
           (avg / speed < (select * from oversell)) oversold
    from user_averages
)
select count(distinct user_name) number_of_users,
       round((count(oversold) / (select * from total_users)::float)::numeric, 2) percent,
       oversold,
       case when oversold then 'oversold' else 'not oversold' end oversold
from user_oversell
group by oversold
;
