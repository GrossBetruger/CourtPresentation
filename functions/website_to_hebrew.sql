create or replace function website_to_hebrew(in website text)
returns text as $$
declare
hebrew_website text;
begin
    select
         case
               when website = 'hot' then 'הוט'
               when website = 'ookla' then 'אוקלה'
               when website = 'bezeq' then 'בזק'
               when website = 'netflix' then 'נטפליקס'
               when website = 'google' then 'גוגל'
               when website = 'atnt' then 'atnt'
            else 'error'
        end
    into hebrew_website;
    return hebrew_website;

end;
$$ language PLpgSQL;

