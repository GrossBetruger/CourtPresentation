select connection, avg(ground_truth_rate), 
  case when  
    rush_hour(timestamp)
    then 'rush hours'
    else 'not rush hours'
    end as rush_hours
    -- evening
from valid_tests
where user_name = {{user_name}}
group by connection, rush_hour(timestamp)


union all

select connection, avg(ground_truth_rate), 'all_hours' as rush_hours
from valid_tests
where user_name = {{user_name}}
group by connection

