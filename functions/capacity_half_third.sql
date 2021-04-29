create or replace function capacity_half_third(in rate float, in speed float)
returns text as $$
declare capacity_half_third text;
begin
    select case when (rate / speed) between 0 and 1./3. then '0: 0-33.3%'
            when (rate / speed) between 1./3. and 0.5 then '1: 33-50%'
            when (rate / speed) between 0.5 and 'infinity' then '2: 50%+'
          end
    into capacity_half_third;
    return capacity_half_third;
end;
$$ language plpgsql;

