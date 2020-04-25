create or replace function calculate_download_rate_kbps(in download_time_ms float, in size bigint)
returns float as $$
declare
download_rate_kbps float;
begin
    select (size / (download_time_ms / 1000.0)) / (2 ^ 10)
    into download_rate_kbps;
    return download_rate_kbps;
end;
$$ language PLpgSQL;
