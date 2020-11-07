create view heat_map as
(
with average_speeds as (
    select user_name, avg(ground_truth_rate) average_speed
    from valid_tests
    group by user_name
)
select average_speeds.user_name, latitude, longitude, average_speed
from average_speeds
         join user_map on user_map.user_name = average_speeds.user_name
    )
;

