select connection "סוג חיבור",
       avg(ground_truth_rate) "מהירות ממוצעת",
  case when
    rush_hour(timestamp)
    then 'בשעות עומס'
    else 'לא בשעות עומס'
    end as "זמן ביממה"
    
from valid_tests
where user_name = {{user_name}}
group by connection, rush_hour(timestamp)

union all

select connection "סוג חיבור", avg(ground_truth_rate) "מהירות ממוצעת", 'בכל השעות' as "זמן ביממה"
from valid_tests
where user_name = {{user_name}}
group by connection
order by "סוג חיבור", "מהירות ממוצעת"
;

