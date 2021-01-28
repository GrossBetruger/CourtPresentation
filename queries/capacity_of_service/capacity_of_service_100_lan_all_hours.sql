select regexp_replace(capacity_squash_100_plus(ground_truth_rate, speed), '\d+:', '') "Capacity of Service",
       count(*)
from valid_tests
where speed = 100
and connection = 'LAN'
group by capacity_squash_100_plus(ground_truth_rate, speed)
order by capacity_squash_100_plus(ground_truth_rate, speed)
;

