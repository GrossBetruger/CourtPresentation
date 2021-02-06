create or replace view bezeq_users as
(
    with users as (
        select distinct user_name
        from valid_tests
        where (isp ~* 'bezeq' or infrastructure ~* 'bezeq')
    ),

    test_count as (
     select user_name, connection, count(*) number_of_tests
     from valid_tests
     group by user_name, connection
    )

    select user_name
    from users
    where user_name not in (select user_name from test_count where number_of_tests < 500)
)
;

