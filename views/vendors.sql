create or replace view bezeq_users as (
    select distinct user_name
    from valid_tests
    where (isp ~* 'bezeq' or infrastructure ~* 'bezeq')
)
;

create or replace view hot_users as (
    select distinct user_name
    from valid_tests
    where (isp ~* 'hot' or infrastructure ~* 'hot')
)
;

create or replace view partner_users as (
    select distinct user_name
    from valid_tests
    where (isp ~* 'partner' or infrastructure ~* 'partner')
)
;
