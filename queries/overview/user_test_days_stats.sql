with diffs as (
    select datediff('day', to_israel_dst_aware(min(timestamp)), to_israel_dst_aware(max(timestamp))) diff
    from valid_tests
    group by user_name
)
select avg(diff) "average day difference",
       percentile_disc(0.5) within group ( order by diff) "median day difference",
       stddev_pop(diff) "standard deviation" -- we have the whole 'population' of testers (therefor stddev_pop)
from diffs
;

