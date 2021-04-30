select connection "סוג חיבור", avg(ground_truth_rate) as "מהירות ממוצעת",
  case when
    is_evening(timestamp)
    then 'בשעות הערב'
    else 'לא בשעות הערב'
    end as "זמן ביממה"
from valid_tests
where user_name = {{user_name}}
group by connection, is_evening(timestamp)

union

select connection, avg(ground_truth_rate), 'בכל השעות' as "מהירות ממוצעת"
from valid_tests
where user_name = {{user_name}}
group by connection
order by "סוג חיבור", "זמן ביממה"
;


