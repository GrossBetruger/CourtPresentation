create or replace function time_of_day_to_hebrew(in time_of_day text)
returns text as $$
declare
hebrew_day text;
hebrew_time text;
begin
    select
           case
               when time_of_day ~ 'Sunday'
               then 'ראשון'

               when time_of_day ~ 'Monday'
               then 'שני'

               when time_of_day ~ 'Tuesday'
               then 'שלישי'

               when time_of_day ~ 'Wednesday'
               then 'רביעי'

               when time_of_day ~ 'Thursday'
               then 'חמישי'

               when time_of_day ~ 'Friday'
               then 'שישי'

               when time_of_day ~ 'Saturday'
               then 'שבת'
            end
    into hebrew_day;

     select
           case
               when time_of_day ~ 'Morning'
               then 'בבוקר'

               when time_of_day ~ 'Noon'
               then 'בצהריים'

               when time_of_day ~ 'Evening'
               then 'בערב'

               when time_of_day ~ 'Night'
               then 'בלילה'

            end
    into hebrew_time;

    return concat_ws(' ', hebrew_day, hebrew_time);
end
$$ language PLpgSQL;

