with ci as (
    with number_bezeq as (select count(distinct bezeq_ci.שם_משתמש) from bezeq_ci),
         oversold_half_bezeq as (select count(*)
                                 from bezeq_ci
                                 where bezeq_ci.גבול_עליון::float / bezeq_ci.תכנית::float < 0.5),
         oversold_half_bezeq_evening as (select count(*)
                                         from bezeq_ci_evening
                                         where bezeq_ci_evening.גבול_עליון::float / bezeq_ci_evening.תכנית::float <
                                               0.5),
         oversold_third_bezeq as (select count(*)
                                  from bezeq_ci
                                  where bezeq_ci.גבול_עליון::float / bezeq_ci.תכנית::float < 1. / 3.),
         oversold_third_bezeq_evening as (select count(*)
                                          from bezeq_ci_evening
                                          where bezeq_ci_evening.גבול_עליון::float / bezeq_ci_evening.תכנית::float <
                                                1. / 3.),

         number_hot as (select count(distinct hot_ci.שם_משתמש) from hot_ci),
         oversold_half_hot as (select count(*) from hot_ci where hot_ci.גבול_עליון::float / hot_ci.תכנית::float < 0.5),
         oversold_half_hot_evening as (select count(*)
                                       from hot_ci_evening
                                       where hot_ci_evening.גבול_עליון::float / hot_ci_evening.תכנית::float < 0.5),
         oversold_third_hot as (select count(*)
                                from hot_ci
                                where hot_ci.גבול_עליון::float / hot_ci.תכנית::float < 1. / 3.),
         oversold_third_hot_evening as (select count(*)
                                        from hot_ci_evening
                                        where hot_ci_evening.גבול_עליון::float / hot_ci_evening.תכנית::float < 1. / 3.),


         number_partner as (select count(distinct partner_ci.שם_משתמש) from partner_ci),
         oversold_half_partner as (select count(*)
                                   from partner_ci
                                   where partner_ci.גבול_עליון::float / partner_ci.תכנית::float < 0.5),
         oversold_half_partner_evening as (select count(*)
                                           from partner_ci_evening
                                           where partner_ci_evening.גבול_עליון::float /
                                                 partner_ci_evening.תכנית::float < 0.5),
         oversold_third_partner as (select count(*)
                                    from partner_ci
                                    where partner_ci.גבול_עליון::float / partner_ci.תכנית::float < 1. / 3.),
         oversold_third_partner_evening as (select count(*)
                                            from partner_ci_evening
                                            where partner_ci_evening.גבול_עליון::float /
                                                  partner_ci_evening.תכנית::float < 1. / 3.)

    select 'בזק'                                        "ספקית או תשתית",
           (select * from number_bezeq)                 "מספר משתמשים",
           (select * from oversold_half_bezeq)          "גולשים בממוצע בפחות מחצי חבילה",
           (select * from oversold_half_bezeq_evening)  "גולשים בממוצע בפחות מחצי חבילה בשעות הערב",
           (select * from oversold_third_bezeq)         "גולשים בממוצע בפחות משליש חבילה",
           (select * from oversold_third_bezeq_evening) "גולשים בממוצע בפחות משליש חבילה בשעות הערב"

    union

    select 'הוט'                                      "ספקית או תשתית",
           (select * from number_hot)                 "מספר משתמשים",
           (select * from oversold_half_hot)          "גולשים בממוצע בפחות מחצי חבילה",
           (select * from oversold_half_hot_evening)  "גולשים בממוצע בפחות מחצי חבילה בשעות הערב",
           (select * from oversold_third_hot)         "גולשים בממוצע בפחות משליש חבילה",
           (select * from oversold_third_hot_evening) "גולשים בממוצע בפחות משליש חבילה בשעות הערב"

    union

    select 'פרטנר'                                        "ספקית או תשתית",
           (select * from number_partner)                 "מספר משתמשים",
           (select * from oversold_half_partner)          "גולשים בממוצע בפחות מחצי חבילה",
           (select * from oversold_half_partner_evening)  "גולשים בממוצע בפחות מחצי חבילה בשעות הערב",
           (select * from oversold_third_partner)         "גולשים בממוצע בפחות משליש חבילה",
           (select * from oversold_third_partner_evening) "גולשים בממוצע בפחות משליש חבילה בשעות הערב"

    order by "ספקית או תשתית"
)
select
       "ספקית או תשתית",
       "מספר משתמשים",
       concat(
               "גולשים בממוצע בפחות מחצי חבילה",
               ' (',
               percentify((("גולשים בממוצע בפחות מחצי חבילה" / "מספר משתמשים" :: float))::numeric),
               '%)'
           ) as "גולשים בממוצע בפחות מחצי חבילה",

        concat(
               "גולשים בממוצע בפחות מחצי חבילה בשעות הערב",
               ' (',
               percentify((("גולשים בממוצע בפחות מחצי חבילה בשעות הערב" / "מספר משתמשים" :: float))::numeric),
               '%)'
           ) as "גולשים בממוצע בפחות מחצי חבילה בשעות הערב",

       concat(
           "גולשים בממוצע בפחות משליש חבילה",
           ' (',
           percentify((("גולשים בממוצע בפחות משליש חבילה" / "מספר משתמשים" :: float))::numeric),
           '%)'
       ) as "גולשים בממוצע בפחות משליש חבילה",

       concat(
           "גולשים בממוצע בפחות משליש חבילה בשעות הערב",
           ' (',
           percentify((("גולשים בממוצע בפחות משליש חבילה בשעות הערב" / "מספר משתמשים" :: float))::numeric),
           '%)'
       ) as "גולשים בממוצע בפחות משליש חבילה בשעות הערב"
from ci
;
