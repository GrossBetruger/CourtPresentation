create or replace function to_israel_dst_aware(in time_of_test bigint)
returns timestamp with time zone as $$
declare israel_timestamp timestamp with time zone;
begin
    select case
        when time_of_test between 1521763200000 and 1540684800000 -- Daylight saving time Israel 2018 Friday, 23 March, 02:00 to Sunday, 28 October, 02:00
         then to_timestamp(time_of_test / 1000.0) at time zone 'IDT'

        when time_of_test between 1553817600000 and 1572134400000 -- Daylight saving time Israel 2019 Friday, 29 March, 02:00 to Sunday, 27 October, 02:00
         then to_timestamp(time_of_test / 1000.0) at time zone 'IDT'

        when time_of_test between 1585267200000 and 1603584000000 -- Daylight saving time Israel 2020 Friday, 27 March, 02:00 toSunday, 25 October, 02:00
         then to_timestamp(time_of_test / 1000.0) at time zone 'IDT'

        else to_timestamp(time_of_test / 1000.0) at time zone 'IST'
        end
    into israel_timestamp;
    return israel_timestamp;
end;
$$ language plpgsql;

