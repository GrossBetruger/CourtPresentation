-- Ground Truth Confidence Intervals User Averages (LAN, 100, Israel Cache);
-- Mean: 42.82024374522536
-- Standard Deviation (Sample): 14.966505882046222
-- N: 77
-- Results: 99.9% Confidence Interval: 42.82024374522536 ± 5.61 (37.2 to 48.4)
with user_means as (
    select user_name, avg(ground_truth_rate) user_mean, count(*) number_of_tests, stddev(ground_truth_rate)
from valid_tests
where connection = 'LAN'
and speed = 100
group by user_name)
select avg(user_mean) average_all_users, count(*), stddev(user_mean)
from user_means
;
