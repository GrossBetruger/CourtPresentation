select connection "סוג חיבור", avg(ground_truth_rate) as "מהירות ממוצעת",
  case when
    rush_hour(timestamp)
    then 'בשעות עומס'
    else 'לא בשעות עומס'
    end as "זמן ביממה"
    -- evening
from valid_tests
where user_name = 'oren' --{{user_name}}
group by connection, rush_hour(timestamp)

union

select connection, avg(ground_truth_rate), 'בכל השעות' as "מהירות ממוצעת"
from valid_tests
where user_name = 'oren' --{{user_name}}
group by connection
order by "סוג חיבור", "זמן ביממה"
;

