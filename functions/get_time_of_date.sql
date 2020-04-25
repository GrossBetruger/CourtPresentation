create or replace function get_time_of_day(in time_of_test bigint)
returns text as $$
declare time_of_day text;
begin
    select concat(
            TO_CHAR(TO_TIMESTAMP(time_of_test / 1000.0) at time zone 'IST' + '1 hour', 'day'),
            ' ',
            case when TO_CHAR(TO_TIMESTAMP(time_of_test / 1000.0) at time zone 'IST' + '1 hour', 'HH24')::int between 0 and 5  then 'night'
              when TO_CHAR(TO_TIMESTAMP(time_of_test / 1000.0) at time zone 'IST' + '1 hour', 'HH24')::int between 6 and 11  then 'morning'
              when TO_CHAR(TO_TIMESTAMP(time_of_test / 1000.0) at time zone 'IST' + '1 hour', 'HH24')::int between 12 and 17  then 'noon'
              when TO_CHAR(TO_TIMESTAMP(time_of_test / 1000.0) at time zone 'IST' + '1 hour', 'HH24')::int between 18 and 23  then 'evening'
            else 'ERROR' end
        )
    into time_of_day;
    return time_of_day;
end;
$$ language PLpgSQL;
