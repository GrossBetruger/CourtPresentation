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
  user_name "שם משתמש",
  isp "ספקית",
  infrastructure "תשתית",
  speed as "מהירות תכנית גלישה",
  min(to_israel_dst_aware(timestamp)) as "התחלת בדיקות",
  max(to_israel_dst_aware(timestamp)) as "סיום בדיקות",
  (select * from number_of_lan_tests) as "מספר בדיקת חיבור קווי (LAN)",
  (select * from number_of_wifi_tests) as "מספר בדיקות אלחוטיות (WiFi)"

from valid_tests
where user_name = {{user_name}}
group by user_name, isp, infrastructure, speed
;

