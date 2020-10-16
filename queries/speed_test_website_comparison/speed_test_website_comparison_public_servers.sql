select website_to_hebrew(website) "אתר בדיקה",
       avg(ground_truth_rate / speed_test_rate) "יחס מהירות בפועל למהירות בדיקה"
from valid_tests
where (ground_truth_rate / speed_test_rate) between 0.01 and 100
and  true_or_null(is_classic_test)
and  ground_truth_rate > 0 and speed_test_rate > 0
and is_classic_resource(file_name)
and not website = 'atnt'
group by website
order by  "יחס מהירות בפועל למהירות בדיקה"
;

