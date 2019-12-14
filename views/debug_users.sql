create view debug_users as
select user_name
from user_details
where user_name in ('dev', 'dev2');
