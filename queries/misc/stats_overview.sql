select 'Number of Speed Test Websites:', count(distinct website)
from valid_tests

union

select 'Number of Distinct Files Download Resources:', count(distinct file_name)
from valid_tests

union

select 'Number of ISPs:', count(distinct isp)
from valid_tests

union

select 'Number of Infrastructures:', count(distinct infrastructure)
from valid_tests

union

select 'Number of Tests:', count(*)
from valid_tests

union

select 'Number of Comparison Tests:', count(*)
from valid_tests
where (is_classic_test is null or is_classic_test = TRUE)

union

select 'Number of Esoteric Data Tests:', count(*)
from valid_tests
where not (is_classic_test is null or is_classic_test = TRUE)

union

select 'Number of Users:', count(distinct user_name)
from valid_tests
;
