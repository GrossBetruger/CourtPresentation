with number_of_lan_tests as (
    select count(*) from valid_tests
    where connection = 'LAN'
    and user_name = {{user_name}}
),

number_of_wifi_tests as (
    select count(*) from valid_tests
    where connection = 'Wifi'
    and user_name = {{user_name}}
)

select
--   user_name "שם משתמש",
  concat("שם_מלא", ' (', user_name, ')') "שם ומשתמש",
  isp "ספקית",
  infrastructure "תשתית",
  speed as "תכנית",
    concat(
                replace(split_part(min(to_israel_dst_aware(timestamp))::text, ' ', 1), '-', '/'),
                ' - ',
                replace(split_part(max(to_israel_dst_aware(timestamp))::text, ' ', 1), '-', '/')
            ) as "תקופה",
  (select * from number_of_lan_tests) as "מס בדיקות קווי",
  (select * from number_of_wifi_tests) as "מס בדיקות אלחוטי"

from valid_tests
join testers on testers.יוזר = valid_tests.user_name
where user_name = {{user_name}}
group by user_name, isp, infrastructure, speed, שם_מלא
;

