from utils import get_engine

engine = get_engine()


def create_user_stats_view():
    global engine
    engine.cursor().execute(
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
        group by user_name
        );
        """
    )
    engine.commit()


def create_random_sample_table():
    global engine
    engine.cursor().execute("""
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
    """)
    engine.commit()


def create_random_sample_evening_table():
    engine.cursor().execute("""
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
    """)
    engine.commit()


def create_random_sample():
    global engine
    engine.cursor().execute("""
        do $$
        declare uname text;
        begin
            perform (select setseed(0.314159265359));
            for uname in (select distinct user_name from valid_tests order by user_name)
            loop
           insert into test_random_sample(user_name, result, speed, isp, infra, connection, file_name, timestamp)
           select valid_tests.user_name, ground_truth_rate, speed, isp, infrastructure, connection, file_name, timestamp
           from   valid_tests
           join user_stats on valid_tests.user_name = user_stats.user_name
           where valid_tests.user_name = uname
            and to_israel_dst_aware(timestamp) between first_test and first_test_plus_30_days
            and connection = 'LAN'
            and num_test >= 700
           order by random() limit 300;
        end loop;
            end;
        $$;
    """)
    engine.commit()


def create_random_sample_evening():
    global engine
    engine.cursor().execute("""
        do $$
        declare uname text;
        begin
            perform (select setseed(0.314159265359));
            for uname in (select distinct user_name from valid_tests order by user_name)
            loop
        insert into test_random_sample_evening(user_name, result, speed, isp, infra, connection, file_name, timestamp)
           select valid_tests.user_name, ground_truth_rate, speed, isp, infrastructure, connection, file_name, timestamp
           from   valid_tests
           join user_stats on valid_tests.user_name = user_stats.user_name
           where valid_tests.user_name = uname
            and to_israel_dst_aware(timestamp) between first_test and first_test_plus_60_days
            and connection = 'LAN'
            and num_test >= 700
            and is_evening(timestamp)
           order by random() limit 300;
        end loop;
            end;
        $$;
    """)
    engine.commit()


def drop_random_sample():
    global engine
    engine.cursor().execute("drop table if exists test_random_sample;")
    engine.commit()


def drop_random_sample_evening():
    global engine
    engine.cursor().execute("drop table if exists test_random_sample_evening")
    engine.commit()


if __name__ == "__main__":
    create_user_stats_view()
    drop_random_sample()
    drop_random_sample_evening()
    create_random_sample_table()
    create_random_sample_evening_table()
    create_random_sample_evening()
    create_random_sample()
    cur = engine.cursor()
    cur.execute("select * from test_random_sample")
    for _ in cur.fetchall():
        print(_)

    cur.execute("select * from test_random_sample_evening")
    for _ in cur.fetchall():
        print(_)

    print("ALL DONE")