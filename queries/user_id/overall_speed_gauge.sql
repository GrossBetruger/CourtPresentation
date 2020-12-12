with transposed as
         (
             select user_name, -1 wifi_average, avg(ground_truth_rate) lan_average
             from valid_tests
             where connection = 'LAN'
             group by user_name

             union

             select user_name, avg(ground_truth_rate) wifi_average, -1 lan_average
             from valid_tests
             where connection = 'Wifi'
             group by user_name
         ),

squashed as (
    select user_name,
           max(wifi_average) wifi_average,
           max(lan_average) lan_average
    from transposed
    group by user_name
),

normalized as (
    select user_name, (wifi_average + lan_average) / 2 normalized_average_speed
    from squashed
    where -1 not in (wifi_average, lan_average)
)
select normalized_average_speed from normalized
where user_name = {{user_name}}
;

