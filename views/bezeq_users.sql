create or replace view bezeq_users as
(
    with users as (
        select distinct user_name
        from valid_tests
        where (isp ~* 'bezeq' or infrastructure ~* 'bezeq')
    )

    select user_name
    from users
    where user_name not in (select user_name from low_test_users)
)
;

