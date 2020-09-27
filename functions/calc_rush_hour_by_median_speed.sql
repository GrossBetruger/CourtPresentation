select percentile_disc(0.5) within group ( order by ground_truth_rate) as median_speed,
       get_time_of_day(timestamp) as time
from valid_tests
group by get_time_of_day(timestamp)
order by median_speed
;
