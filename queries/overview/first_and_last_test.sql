select 
       to_israel_dst_aware(min(timestamp)),
       to_israel_dst_aware(max(timestamp))
from valid_tests
;

