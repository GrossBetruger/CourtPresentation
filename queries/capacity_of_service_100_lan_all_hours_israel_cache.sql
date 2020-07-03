select regexp_replace(capacity(ground_truth_rate, speed), '\d+:', '') "Capacity of Service",
       count(*)
from valid_tests
where speed = 100
and connection = 'LAN'
and file_name = 'israel_cache'
group by capacity(ground_truth_rate, speed)
order by capacity(ground_truth_rate, speed)
;
