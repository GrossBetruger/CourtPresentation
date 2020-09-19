with times as (
    select concat(
                   (date_part('month', to_israel_dst_aware(timestamp))),
                   '/',
                   date_part('year', to_israel_dst_aware(timestamp))
               ) as timeoftest,
           user_name
    from valid_tests
    order by timestamp
)
select timeoftest as "זמן דגימה", count(*) "מספר דגימות", count(distinct user_name) as "מספר משתמשים"
from times
group by timeoftest
;

