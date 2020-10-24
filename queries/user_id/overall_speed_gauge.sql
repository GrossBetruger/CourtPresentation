with normalized_num_of_tests as (
    select least(
               (
                   select count(*)
                   from valid_tests
                   where connection = 'Wifi'
                   and user_name = {{user_name}}
               ),
               (
                   select count(*)
                   from valid_tests
                   where connection = 'LAN'
                   and user_name = {{user_name}}
               )
            )
),

normalized_tests_sample as (
    (select ground_truth_rate rate, user_name, speed
    from valid_tests
    where user_name = {{user_name}}
    and connection = 'LAN' limit (select * from normalized_num_of_tests))

    union all

    (select ground_truth_rate rate, user_name, speed
    from valid_tests
    where user_name = {{user_name}}
    and connection = 'Wifi' limit (select * from normalized_num_of_tests))
    )

select avg(rate) "ממהירות ממוצעת  - חיבור קווי ואלחוטי"
from normalized_tests_sample
;

