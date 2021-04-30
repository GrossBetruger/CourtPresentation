select avg(ground_truth_rate) as "מהירות"
from valid_tests
where connection = 'Wifi'
and user_name = {{user_name}}
;
