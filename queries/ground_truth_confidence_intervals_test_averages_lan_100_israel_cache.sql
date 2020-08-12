-- Ground Truth Confidence Intervals Test Averages (LAN, 100, Israel Cache);
-- Mean: 62.9824779446673
-- Standard Deviation (Sample): 24.662049328875135
-- N: 15834
-- Results: 99.9% Confidence Interval: 62.9824779446673 ± 0.645 (62.3 to 63.6)
select avg(ground_truth_rate) average_speed, count(*) number_of_tests, stddev(ground_truth_rate)
from valid_tests
where connection = 'LAN'
and speed = 100
and file_name = 'israel_cache'
;
