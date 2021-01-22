select percentile_disc(0.5) within group ( order by ground_truth_rate) as "מהירות חציונית",
       time_of_day_to_hebrew(get_time_of_day(timestamp)) as "זמן בשבוע"
from valid_tests
group by time_of_day_to_hebrew(get_time_of_day(timestamp))
order by "מהירות חציונית"
;

