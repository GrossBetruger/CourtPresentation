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
    
    user_averages as (
        (select ground_truth_rate rate, user_name, speed
        from valid_tests
        where user_name = {{user_name}}
        and connection = 'LAN' limit (select * from normalized_num_of_tests))
    
        union all
    
        (select ground_truth_rate rate, user_name, speed
        from valid_tests
        where user_name = {{user_name}}
        and connection = 'Wifi' limit (select * from normalized_num_of_tests))
        ),
    
    capacity as (
        select case
                when (rate / speed) between 0 and 0.5 then '0: 0-50%'
                when (rate / speed) between 0.5 and 1.0 then '1: 50-100%'
            else '2: 100%+'
        end as capacity
        from user_averages
        )
    select regexp_replace(capacity, '\d+:', '') "נפח בפועל מחבילת גלישה",
           count(capacity)
    from capacity
    group by capacity
    order by capacity;

