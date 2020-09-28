create or replace function capacity_squash_100_plus(in rate float, in speed float)
returns text as $$
declare capacity text;
begin
    select case when (rate / speed) between 0 and 0.2 then '0: 0-20%'
            when (rate / speed) between 0.2 and 0.4 then '1: 20-40%'
            when (rate / speed) between 0.4 and 0.6 then '2: 40-60%'
            when (rate / speed) between 0.6 and 0.8 then '3: 60-80%'
            when (rate / speed) between 0.8 and 1 then '4: 80-100%'
            when (rate / speed) > 1 then '5: 100%+'
        else 'error' end
    into capacity;
    return capacity;
end;
$$ language plpgsql;
