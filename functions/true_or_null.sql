create or replace function true_or_null(in predicate bool)
returns bool as $$
declare
true_or_null bool;
begin
    select predicate = true or predicate is null
    into true_or_null;
    return true_or_null;
end;
$$ language PLpgSQL;
