select connection "סוג חיבור",
       avg(ground_truth_rate) "מהירות ממוצעת",
  case when
    is_evening(timestamp)
    then 'בשעות הערב'
    else 'לא בשעות הערב'
    end as "זמן ביממה"
    
from valid_tests
where user_name = {{user_name}}
group by connection, is_evening(timestamp)

union all

select connection "סוג חיבור", avg(ground_truth_rate) "מהירות ממוצעת", 'בכל השעות' as "זמן ביממה"
from valid_tests
where user_name = {{user_name}}
group by connection
order by "סוג חיבור", "מהירות ממוצעת"
;

