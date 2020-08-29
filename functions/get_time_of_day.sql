create or replace function get_time_of_day(in time_of_test bigint)
returns text as $$
declare time_of_day text;
begin
    select concat(
            to_char(to_israel_dst_aware(time_of_test), 'Day'),
            ' ',
            case when extract(hour from to_israel_dst_aware(time_of_test)) between 0 and 5  then 'night'
              when extract(hour from to_israel_dst_aware(time_of_test)) between 6 and 11  then 'morning'
              when extract(hour from to_israel_dst_aware(time_of_test)) between 12 and 17  then 'noon'
              when extract(hour from to_israel_dst_aware(time_of_test)) between 18 and 23  then 'evening'
            else 'ERROR' end
        )
    into time_of_day;
    return time_of_day;
end;
$$ language PLpgSQL;

