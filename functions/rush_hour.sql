create or replace function rush_hour(in stamp bigint)
returns bool as $$
declare
is_rush_hour bool;
begin
    select get_time_of_day(stamp)
               in (
                    'Saturday  Evening',
                    'Thursday  Evening',
                    'Friday    Noon',
                    'Tuesday   Evening',
                    'Wednesday Evening',
                    'Sunday    Evening',
                    'Saturday  Noon',
                    'Monday    Evening',
                    'Friday    Evening'
                )
    into is_rush_hour;
    return is_rush_hour;
end;
$$ language PLpgSQL;
