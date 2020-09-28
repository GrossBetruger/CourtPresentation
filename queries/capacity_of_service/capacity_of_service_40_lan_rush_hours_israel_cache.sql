select regexp_replace(capacity_squash_100_plus(ground_truth_rate, speed), '\d+:', '') "Capacity of Service",
       count(*)
from valid_tests
where speed = 40
and connection = 'LAN'
and file_name = 'israel_cache'
and rush_hour(timestamp)
group by capacity_squash_100_plus(ground_truth_rate, speed)
order by capacity_squash_100_plus(ground_truth_rate, speed)
;
