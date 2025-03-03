select count(*) from valid_tests
where user_name in (select * from hot_users);
