select avg(ground_truth_rate) as "מהירות"
from valid_tests
where connection = 'LAN'
and user_name = {{user_name}}
;
