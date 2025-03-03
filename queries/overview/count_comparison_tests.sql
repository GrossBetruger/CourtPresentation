select count(*) from valid_tests
where website is not null and true_or_null(is_classic_test);

