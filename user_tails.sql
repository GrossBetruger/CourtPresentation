with user_centers as (
    select user_name,
           avg(ground_truth_rate) average,
           percentile_cont(0.5)
           within group ( order by ground_truth_rate ) median
    from valid_tests
    group by user_name
),
center_ratios as (
    select user_name, average / median as leaning, average, median
    from user_centers
),
leaning_binary as (
    select case
               when leaning > 1 then 'right tail'
               else 'left tail' end as leaning,
           user_name
    from center_ratios
)
-- select * from leaning_binary
-- order by leaning
select leaning, count(*)
from leaning_binary
group by leaning
;

