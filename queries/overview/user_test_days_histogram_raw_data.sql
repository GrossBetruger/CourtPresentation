select datediff('day', to_israel_dst_aware(min(timestamp)), to_israel_dst_aware(max(timestamp))) diff
from valid_tests
group by user_name
;

