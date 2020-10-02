-- Oversell 100, LAN, Average speed
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
           case
               when (avg / speed < (select * from oversell)) then 'משתמשים במכירת יתר'
               when (avg / speed >= (select * from oversell)) then 'משתמשים שאינם במכירת יתר'
               else 'error'
           end as oversell
    from user_averages
)
select count(distinct user_name) number_of_users,
       round((count(oversell) / (select * from total_users)::float)::numeric, 2) * 100 percent,
       oversell
from user_oversell
group by oversell
;
