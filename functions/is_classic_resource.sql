create or replace function is_classic_resource(in resource text)
returns bool as $$
declare
classic_resource bool;
begin
    select resource in (
        'vlc',
        'go',
        'dlink',
        'windows-games',
        'quicktime',
        'firefox',
        'amazon-workSpaces',
        'my-sql',
        'windows-games-studio'
        )
    into classic_resource;
    return classic_resource;
end;
$$ language plpgsql;

