create or replace function is_evening(in stamp bigint)
returns bool as $$
declare
is_evening bool;
begin
    select get_time_of_day(stamp) like '% Evening'
    into is_evening;
    return is_evening;
end;
$$ language PLpgSQL;

