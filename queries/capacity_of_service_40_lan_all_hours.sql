select regexp_replace(capacity(ground_truth_rate, speed), '\d+:', '') "Capacity of Service",
       count(*)
from valid_tests
where speed = 40
and connection = 'LAN'
group by capacity(ground_truth_rate, speed)
order by capacity(ground_truth_rate, speed)
;

