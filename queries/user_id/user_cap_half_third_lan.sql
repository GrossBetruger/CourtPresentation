select regexp_replace(capacity_half_third(ground_truth_rate, speed), '\d+:', ''),
    count(*)
from valid_tests
where user_name = {{user_name}}
and connection = 'LAN'
group by capacity_half_third(ground_truth_rate, speed)
order by capacity_half_third(ground_truth_rate, speed)
;

