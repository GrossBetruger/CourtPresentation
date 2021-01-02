select "יוזר",
       split_part(longitude_and_latitude, ', ', 2)::float longtitude,
       split_part(longitude_and_latitude, ', ', 1)::float latitude
from testers
where longitude_and_latitude is not null
;

