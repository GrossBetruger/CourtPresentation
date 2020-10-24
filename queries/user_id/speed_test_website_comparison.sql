with ordered_by_percision as (
    select avg(ground_truth_rate / speed_test_rate)                "יחס מדידה \ תוצאה",
           website_to_hebrew(website)                              "אתר",
           count(*),
           abs(1 / (1 - avg(ground_truth_rate / speed_test_rate))) "דיוק"

    from valid_tests
    where speed_test_rate != 0
      and (ground_truth_rate / speed_test_rate) between 0.01 and 100
      and website not in ('atnt')
      and user_name = {{user_name}}
    group by website

    union

    select avg(ground_truth_rate / speed_test_rate)                "יחס מדידה \ תוצאה",
           'כל האתרים',
           count(*),
           abs(1 / (1 - avg(ground_truth_rate / speed_test_rate))) "דיוק"
    from valid_tests
    where speed_test_rate != 0
      and (ground_truth_rate / speed_test_rate) between 0.01 and 100
      and website not in ('atnt')
      and user_name = {{user_name}}
    order by "דיוק"
)
select "יחס מדידה \ תוצאה", "אתר" , count as "מספר בדיקות"
from ordered_by_percision
;

