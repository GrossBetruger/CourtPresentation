select regexp_replace(capacity(ground_truth_rate, speed), '\d+:', ''),
       count(*)
from valid_tests
where speed = 100
and connection = 'LAN'
and rush_hour(timestamp)
group by capacity(ground_truth_rate, speed)
order by capacity(ground_truth_rate, speed)
;
