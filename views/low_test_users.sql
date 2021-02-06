create or replace view low_test_users as
(
with test_count as (
    select user_name, connection, count(*) number_of_tests
    from valid_tests
    group by user_name, connection
)

select user_name from test_count where number_of_tests < 500
)
;

