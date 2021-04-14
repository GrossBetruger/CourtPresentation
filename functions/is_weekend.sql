create or replace function is_weekend(in stamp bigint)
returns bool as $$
declare
is_weekend bool;
begin
    select get_time_of_day(stamp) like 'Friday %'
            or get_time_of_day(stamp) like 'Saturday %'
    into is_weekend;
    return is_weekend;
end;
$$ language PLpgSQL;

