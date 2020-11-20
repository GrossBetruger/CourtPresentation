with partners as (
    select distinct user_name
    from valid_tests
    where (isp ~* 'partner' or infrastructure ~* 'partner')
),
oversell as (select 0.5),

user_averages as (
    select avg(ground_truth_rate), user_name, speed
    from valid_tests
    where connection = 'LAN'
    and user_name in (select * from partners)
    and is_classic_resource(file_name)
    group by user_name, speed
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
       round((count(oversell) / (select count(*) from partners)::float)::numeric, 2) * 100 percent,
       oversell
from user_oversell
group by oversell
;

