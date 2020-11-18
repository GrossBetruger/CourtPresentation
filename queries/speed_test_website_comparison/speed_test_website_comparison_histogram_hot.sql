with website_ratios as (
    select ground_truth_rate / speed_test_rate as ratio
    from valid_tests
    where true_or_null(is_classic_test)
    and speed_test_rate != 0 and ground_truth_rate != 0
    and website  = 'hot'
    and (ground_truth_rate / speed_test_rate) between 0.01 and 100
),
binned_ratios as (
    select
      ratio_20_bins(ratio)
       as binned_ratio

    from website_ratios
)
select regexp_replace(binned_ratio, '\d+:', '') error_rate, count(binned_ratio) number_of_tests
from binned_ratios
group by binned_ratio
order by substring(binned_ratio, '(\d+):')::int;

