with user_averages_israel as (
    select ground_truth_rate rate, user_name, speed
    from valid_tests
    where connection = 'LAN'
    and user_name = {{user_name}}
    ),

capacity as (
    select case when (rate / speed) between 0 and 0.2 then '0: 0-20%'
            when (rate / speed) between 0.2 and 0.4 then '1: 20-40%'
            when (rate / speed) between 0.4 and 0.6 then '2: 40-60%'
            when (rate / speed) between 0.6 and 0.8 then '3: 60-80%'
            when (rate / speed) between 0.8 and 1 then '4: 80-100%'
            when (rate / speed) between 1 and 1.2 then '5: 100-120%'
            when (rate / speed) between 1.2 and 1.4 then '6: 120-140%'
            when (rate / speed) between 1.4 and 1.6 then '7: 140-160%'
            when (rate / speed) between 1.6 and 1.8 then '8: 160-180%'
            when (rate / speed) between 1.8 and 2 then '9: 180-200%'
        else '99: 200%+'
    end as capacity
    from user_averages_israel
    )
select regexp_replace(capacity, '\d+:', '') "נפח גלישה מחבילת מהירות", count(capacity)
from capacity
group by capacity
order by capacity
;
