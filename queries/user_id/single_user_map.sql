select split_part("longitude_and_latitude", ', ', 1)::float latitude,
       split_part("longitude_and_latitude", ', ', 2)::float longitude
from testers
where "יוזר" = {{user_name}}
;
