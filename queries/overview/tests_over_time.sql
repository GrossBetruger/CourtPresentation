with times as (
    select concat(
                   (date_part('month', to_israel_dst_aware(timestamp))),
                   '/',
                   date_part('year', to_israel_dst_aware(timestamp))
               ) as timeoftest,
           user_name,
           date_part('year', to_israel_dst_aware(timestamp)) raw_year,
           date_part('month', to_israel_dst_aware(timestamp)) raw_month
    from valid_tests
    order by timestamp
)
select timeoftest as "זמן דגימה", count(*) "מספר דגימות", count(distinct user_name) as "מספר משתמשים",
       raw_year, raw_month
from times
group by timeoftest, raw_year, raw_month
order by raw_year, raw_month
;

