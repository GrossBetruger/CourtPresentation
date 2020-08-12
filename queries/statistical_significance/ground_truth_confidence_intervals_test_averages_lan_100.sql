-- Ground Truth Confidence Intervals Test Averages (LAN, 100);
-- Mean: 42.99818499410381
-- Standard Deviation (Sample): 27.473472389651235
-- N: 694005
-- Results: 99.9% Confidence Interval: 42.99818499410381 ± 0.109 (42.9 to 43.1)
select avg(ground_truth_rate) average_speed, count(*) number_of_tests, stddev(ground_truth_rate)
from valid_tests
where connection = 'LAN'
and speed = 100
;
