from utils import get_engine


class RandomSample:
    engine = get_engine()

    def execute_persistent(self, query):
        self.engine.cursor().execute(query)
        self.engine.commit()

    def iterate_lines(self, query):
        cur = self.engine.cursor()
        cur.execute(query)
        for row in cur.fetchall():
            yield row

    def create_user_stats_view(self):
        self.execute_persistent(
            """
            create or replace view user_stats as (
            select user_name,
                   min(to_israel_dst_aware(timestamp)) first_test,
                   min(to_israel_dst_aware(timestamp)) + interval '30' day first_test_plus_30_days,
                   min(to_israel_dst_aware(timestamp)) + interval '60' day first_test_plus_60_days,
                   count(*) num_test
            from valid_tests
            where connection = 'LAN'
            and speed not in (15, 30, 40)
            and is_classic_resource(file_name)
            group by user_name
            );
            """
        )

    def create_randomized_valid_test_table(self):
        self.execute_persistent("""
            drop table if exists randomized_valid_tests;
            select setseed(0.314159265359);
            create table if not exists randomized_valid_tests as (
                select random() as random_index, is_evening(timestamp) evening, *
                 from valid_tests
                 order by random_index
            );
            create index on randomized_valid_tests(timestamp);
            create index on randomized_valid_tests(user_name);
            create index on randomized_valid_tests(random_index);
            ;
        """)

    def create_random_sample(self):
        self.execute_persistent("""
            drop table if exists test_random_sample;
            
            create table if not exists test_random_sample(
                id serial primary key,
                user_name text,
                result float,
                speed integer,
                isp text,
                infra text,
                connection text,
                file_name text,
                timestamp bigint
            );
            
            do $$
            declare uname text;
            begin
                for uname in (select distinct user_name from valid_tests order by user_name)
                loop
                   insert into test_random_sample(user_name, result, speed, isp, infra, connection, file_name, timestamp)
                   select randomized_valid_tests.user_name, ground_truth_rate, speed, isp, infrastructure, connection, file_name, timestamp
                   from   randomized_valid_tests
                   join user_stats on randomized_valid_tests.user_name = user_stats.user_name
                   where randomized_valid_tests.user_name = uname
                    and to_israel_dst_aware(timestamp) between first_test and first_test_plus_30_days
                    and connection = 'LAN'
                    and num_test >= 700
                    and is_classic_resource(file_name)
                    order by random_index limit 300;
            end loop;
                end;
            $$;
        """)

    def create_random_sample_evening(self):
        self.execute_persistent("""
            drop table if exists test_random_sample_evening;
            
            create table if not exists test_random_sample_evening(
                id serial primary key,
                user_name text,
                result float,
                speed integer,
                isp text,
                infra text,
                connection text,
                file_name text,
                timestamp bigint)
            ;
            
            do $$
            declare uname text;
            begin
                for uname in (select distinct user_name from valid_tests order by user_name)
                loop
            insert into test_random_sample_evening(user_name, result, speed, isp, infra, connection, file_name, timestamp)
               select randomized_valid_tests.user_name, ground_truth_rate, speed, isp, infrastructure, connection, file_name, timestamp
               from   randomized_valid_tests
               join user_stats on randomized_valid_tests.user_name = user_stats.user_name
               where randomized_valid_tests.user_name = uname
                and to_israel_dst_aware(timestamp) between first_test and first_test_plus_60_days
                and connection = 'LAN'
                and num_test >= 700
                and is_classic_resource(file_name)
                and evening is True
                order by random_index limit 300;
            end loop;
                end;
            $$;
        """)


if __name__ == "__main__":
    random_sample = RandomSample()
    print("create stats view")
    random_sample.create_user_stats_view()
    print("creating randomized valid tests")
    random_sample.create_randomized_valid_test_table()
    print("sampling tests")
    random_sample.create_random_sample()
    print("sampling evening tests")
    random_sample.create_random_sample_evening()

    for _ in random_sample.iterate_lines("select * from test_random_sample"):
        print(_)

    for _ in random_sample.iterate_lines("select * from test_random_sample_evening"):
        print(_)

    print("ALL DONE")