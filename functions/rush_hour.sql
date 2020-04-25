create or replace function rush_hour(in stamp bigint)
returns bool as $$
declare
is_rush_hour bool;
begin
    select get_time_of_day(stamp) ~ 'evening'
    into is_rush_hour;
    return is_rush_hour;
end;
$$ language PLpgSQL;
