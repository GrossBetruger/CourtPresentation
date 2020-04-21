

SPEED_TEST_HISTOGRAM_QUERY = """
-- Single Website Error Distribution - {0}
with website_ratios as (
    select (ground_truth_rate / speed_test_rate) as ratio, date_part('year', TO_TIMESTAMP(timestamp/ 1000) at time zone 'IST' + '1 hour') as year
    from valid_tests
    where true_or_null(is_classic_test)
    and speed_test_rate != 0 and ground_truth_rate != 0
    and website  = '{0}'
    and (ground_truth_rate / speed_test_rate) between 0.01 and 100
),
binned_ratios as (
    select
      year,
      case
         when ratio between 0 and 0.1 then '0: 90-100% slower'
            when ratio between 0.1 and 0.2 then '1: 90-80% slower'
            when ratio between 0.2 and 0.3 then '2: 80-70% slower'
            when ratio between 0.3 and 0.4 then '3: 70-60% slower'
            when ratio between 0.4 and 0.5 then '4: 60-50% slower'
            when ratio between 0.5 and 0.6 then '5: 50-40% slower'
            when ratio between 0.6 and 0.7 then '6: 40-30% slower'
            when ratio between 0.7 and 0.8 then '7: 30-20% slower'
            when ratio between 0.8 and 0.9 then '8: 20-10% slower'
            when ratio between 0.9 and 1 then '9: 10-0% faster'
            when ratio between 1 and 1.1 then '10: 0-10% faster'
            when ratio between 1.1 and 1.2 then '11: 10-20% faster'
            when ratio between 1.2 and 1.3 then '12: 20-30% faster'
            when ratio between 1.3 and 1.4 then '13: 30-40% faster'
            when ratio between 1.4 and 1.5 then '14: 40-50% faster'
            when ratio between 1.5 and 1.6 then '15: 50-60% faster'
            when ratio between 1.6 and 1.7 then '16: 60-70% faster'
            when ratio between 1.7 and 1.8 then '17: 70-80% faster'
            when ratio between 1.8 and 1.9 then '18: 80-90% faster'
            when ratio between 1.9 and 2 then '19: 90-100% faster'
            when ratio > 2 then '20: 200%+ faster'
              else 'WTF!!!'

       end
       as binned_ratio

    from website_ratios
)
select regexp_replace(binned_ratio, '\d+:', '') error_rate, count(binned_ratio) number_of_tests, year
from binned_ratios
group by binned_ratio, year
order by substring(binned_ratio, '(\d+):')::int;
"""

COMPARISON_AVERAGES_QUERY = \
"""
-- Website Credibility Averages 2018/19 {0}
select (ground_truth_rate / speed_test_rate) as ratio
from valid_tests
where true_or_null(is_classic_test)
and speed_test_rate != 0 and ground_truth_rate != 0
and website  = '{0}'
and (ground_truth_rate / speed_test_rate) between 0.01 and 100;
"""

def query_looper(var_lst, base_query):
    for var in var_lst:
        query = base_query.format(var)
        yield query


if __name__ == "__main__":
    # for query in query_looper(["google","ookla","fast","bezeq","hot"], SPEED_TEST_HISTOGRAM_QUERY):
    #     print(query)

    for query in query_looper(["google","ookla","fast","bezeq","hot"], COMPARISON_AVERAGES_QUERY):
        print(query)