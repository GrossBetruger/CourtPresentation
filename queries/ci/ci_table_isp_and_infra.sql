with ci as (with number_pure_bezeq as (select count(distinct pure_bezeq_ci.שם_משתמש) from pure_bezeq_ci),
                 oversold_half_pure_bezeq as (select count(*)
                                              from pure_bezeq_ci
                                              where pure_bezeq_ci.גבול_עליון::float / pure_bezeq_ci.תכנית::float < 0.5),
                 oversold_half_pure_bezeq_evening as (select count(*)
                                                      from pure_bezeq_ci_evening
                                                      where pure_bezeq_ci_evening.גבול_עליון::float /
                                                            pure_bezeq_ci_evening.תכנית::float < 0.5),
                 oversold_third_pure_bezeq as (select count(*)
                                               from pure_bezeq_ci
                                               where pure_bezeq_ci.גבול_עליון::float / pure_bezeq_ci.תכנית::float < 1. / 3.),
                 oversold_third_pure_bezeq_evening as (select count(*)
                                                       from pure_bezeq_ci_evening
                                                       where pure_bezeq_ci_evening.גבול_עליון::float /
                                                             pure_bezeq_ci_evening.תכנית::float < 1. / 3.),

                 number_pure_hot as (select count(distinct pure_hot_ci.שם_משתמש) from pure_hot_ci),
                 oversold_half_pure_hot as (select count(*)
                                            from pure_hot_ci
                                            where pure_hot_ci.גבול_עליון::float / pure_hot_ci.תכנית::float < 0.5),
                 oversold_half_pure_hot_evening as (select count(*)
                                                    from pure_hot_ci_evening
                                                    where pure_hot_ci_evening.גבול_עליון::float /
                                                          pure_hot_ci_evening.תכנית::float < 0.5),
                 oversold_third_pure_hot as (select count(*)
                                             from pure_hot_ci
                                             where pure_hot_ci.גבול_עליון::float / pure_hot_ci.תכנית::float < 1. / 3.),
                 oversold_third_pure_hot_evening as (select count(*)
                                                     from pure_hot_ci_evening
                                                     where pure_hot_ci_evening.גבול_עליון::float /
                                                           pure_hot_ci_evening.תכנית::float < 1. / 3.),


                 number_pure_partner as (select count(distinct pure_partner_ci.שם_משתמש) from pure_partner_ci),
                 oversold_half_pure_partner as (select count(*)
                                                from pure_partner_ci
                                                where pure_partner_ci.גבול_עליון::float / pure_partner_ci.תכנית::float < 0.5),
                 oversold_half_pure_partner_evening as (select count(*)
                                                        from pure_partner_ci_evening
                                                        where pure_partner_ci_evening.גבול_עליון::float /
                                                              pure_partner_ci_evening.תכנית::float < 0.5),
                 oversold_third_pure_partner as (select count(*)
                                                 from pure_partner_ci
                                                 where pure_partner_ci.גבול_עליון::float / pure_partner_ci.תכנית::float <
                                                       1. / 3.),
                 oversold_third_pure_partner_evening as (select count(*)
                                                         from pure_partner_ci_evening
                                                         where pure_partner_ci_evening.גבול_עליון::float /
                                                               pure_partner_ci_evening.תכנית::float < 1. / 3.)

            select 'בזק'                                             "ספקית + תשתית",
                   (select * from number_pure_bezeq)                 "מספר משתמשים",
                   (select * from oversold_half_pure_bezeq)          "גולשים בממוצע בפחות מחצי חבילה",
                   (select * from oversold_half_pure_bezeq_evening)  "גולשים בממוצע בפחות מחצי חבילה בשעות הערב",
                   (select * from oversold_third_pure_bezeq)         "גולשים בממוצע בפחות משליש חבילה",
                   (select * from oversold_third_pure_bezeq_evening) "גולשים בממוצע בפחות משליש חבילה בשעות הערב"

            union

            select 'הוט'                                           "ספקית + תשתית",
                   (select * from number_pure_hot)                 "מספר משתמשים",
                   (select * from oversold_half_pure_hot)          "גולשים בממוצע בפחות מחצי חבילה",
                   (select * from oversold_half_pure_hot_evening)  "גולשים בממוצע בפחות מחצי חבילה בשעות הערב",
                   (select * from oversold_third_pure_hot)         "גולשים בממוצע בפחות משליש חבילה",
                   (select * from oversold_third_pure_hot_evening) "גולשים בממוצע בפחות משליש חבילה בשעות הערב"

            union

            select 'פרטנר'                                             "ספקית + תשתית",
                   (select * from number_pure_partner)                 "מספר משתמשים",
                   (select * from oversold_half_pure_partner)          "גולשים בממוצע בפחות מחצי חבילה",
                   (select * from oversold_half_pure_partner_evening)  "גולשים בממוצע בפחות מחצי חבילה בשעות הערב",
                   (select * from oversold_third_pure_partner)         "גולשים בממוצע בפחות משליש חבילה",
                   (select * from oversold_third_pure_partner_evening) "גולשים בממוצע בפחות משליש חבילה בשעות הערב"
            order by "ספקית + תשתית"
)
select
       "ספקית + תשתית",
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
