create or replace view partner_users as
(
    with users as (
        select distinct user_name
        from valid_tests
        where (isp ~* 'partner' or infrastructure ~* 'partner')
    )

    select user_name
    from users
    where user_name not in (select user_name from low_test_users)
)
;

