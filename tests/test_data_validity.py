import unittest
import pandas as pd
from typing import List

from utils import get_engine


class TestDataValidity(unittest.TestCase):
    engine = get_engine()
    cur = engine.cursor()

    def get_rows(self, query: str) -> List[tuple]:
        rows = []
        self.cur.execute(query)
        for row in self.cur.fetchall():
            rows.append(row)
        return rows

    def test_ci_table_vendors(self):
        bezeq_vendors = self.get_rows("""
            select 
                   bezeq_ci.ספקית,
                   bezeq_ci.תשתית
            from bezeq_ci
            ;
            """)
        bezeq_vendors += self.get_rows("""
            select 
                   bezeq_ci_evening.ספקית,
                   bezeq_ci_evening.תשתית
            from bezeq_ci_evening
            ;
            """)

        for isp, infra in bezeq_vendors:
            self.assertTrue(isp == "Bezeq International-Ltd" or infra == "BEZEQ")

        hot_vendors = self.get_rows("""
            select 
                   hot_ci.ספקית,
                   hot_ci.תשתית
            from hot_ci
            ;
            """)

        hot_vendors += self.get_rows("""
            select 
                   hot_ci_evening.ספקית,
                   hot_ci_evening.תשתית
            from hot_ci_evening
            ;
            """)

        for isp, infra in hot_vendors:
            self.assertTrue(isp == "Hot-Net internet services Ltd." or infra == "HOT")

        partner_vendors = self.get_rows("""
                  select 
                         partner_ci.ספקית,
                         partner_ci.תשתית
                  from partner_ci
                  ;
                  """)

        partner_vendors += self.get_rows("""
                       select 
                              partner_ci_evening.ספקית,
                              partner_ci_evening.תשתית
                       from partner_ci_evening
                       ;
                       """)

        for isp, infra in partner_vendors:
            self.assertTrue(isp == "Partner Communications Ltd." or infra == "PARTNER")

    def test_ci_evening_tables(self):
        partner_evening_numbers = self.get_rows("""
                       select 
                              partner_ci_evening.שם_משתמש,
                              partner_ci_evening.גבול_עליון,
                              partner_ci_evening.גבול_תחתון,
                              partner_ci_evening.מהירות_ממוצעת_מדגם
                       from partner_ci_evening
                       ;
        """)

        partner_numbers = self.get_rows("""
                       select 
                        partner_ci.שם_משתמש,      
                              partner_ci.גבול_עליון,
                              partner_ci.גבול_תחתון,
                              partner_ci.מהירות_ממוצעת_מדגם
                       from partner_ci
                       ;
        """)

        partner_evening_numbers.sort(key=lambda columns: columns[0])
        partner_numbers.sort(key=lambda columns: columns[0])

        for eve_num, num in zip(partner_evening_numbers, partner_numbers):
            eve_name, eve_upper, eve_lower, eve_average = eve_num
            name, upper, lower, average = num
            self.assertEqual(eve_name, name)
            self.assertNotEqual(eve_average, average)
            self.assertNotEqual(eve_lower, lower)
            self.assertNotEqual(eve_upper, upper)

    def test_random_sample(self):
        random_sample = self.get_rows("select user_name, count(*) from test_random_sample group by user_name")
        for _user_name, count in random_sample:
            self.assertEqual(300, count)

        speeds = self.get_rows("select speed from test_random_sample")
        for speed, in speeds:
            self.assertIn(speed, [100, 200, 500, 1000])

        # random sample data persistency
        randomized_valid_test = self.get_rows("select ground_truth_rate, user_name, file_name, timestamp, random_index"
                                              " from randomized_valid_tests")

        second = (6.437308051433778, 'ben_b', 'go', 1540301748578, 1.1055979456386922e-06)
        last_row = (63.250679088980895, 'etl', 'firefox', 1571828370256, 0.9999999137277591)
        row_minus_pi = (46.146673387096776, 'ArielG', 'go', 1543489131958, 0.8610400669148355)
        row_minus_1000 = (30.569313143358247, 'dor_p', 'dlink', 1563453594052, 0.9995655430256711)

        self.assertEqual(second, randomized_valid_test[1])
        self.assertEqual(last_row, randomized_valid_test[-1])
        self.assertEqual(row_minus_pi, randomized_valid_test[-314159])
        self.assertEqual(row_minus_1000, randomized_valid_test[-1000])

        sample = self.get_rows("select user_name, result, timestamp, file_name"
                               " from test_random_sample order by timestamp")
        first_row = ('admin', 18.813411540900443, 1529870019339, 'my-sql')
        last_row = ('dan_florentin', 36.70050094950409, 1587377434453, 'dlink')
        row_minus_1000 = ('artium', 37.905948297764226, 1584833539085, 'dlink')

        self.assertEqual(first_row, sample[0])
        self.assertEqual(last_row, sample[-1])
        self.assertEqual(row_minus_1000, sample[-1000])

        public_access_resources = ["file_name","amazon-workSpaces",
                                   "windows-games","windows-games-studio",
                                   "my-sql","dlink","vlc","go","firefox","quicktime"]

        for _, _, _, filename in sample:
            self.assertIn(filename, public_access_resources)

    def test_evening_random_sample(self):
        evening_timestamps = self.get_rows("select timestamp from test_random_sample_evening")
        for timestamp, in evening_timestamps:
            self.assertIn("Evening", self.get_rows(f"select get_time_of_day({timestamp})")[0][0])

        random_sample_evening = self.get_rows(
            "select user_name, count(*) from test_random_sample_evening group by user_name")
        for _user_name, count in random_sample_evening:
            if _user_name == "admin":
                continue
            self.assertEqual(300, count, f"user: {_user_name} has {count} tests")

        speeds = self.get_rows("select speed from test_random_sample_evening")
        for speed, in speeds:
            self.assertIn(speed, [100, 200, 500, 1000])


if __name__ == '__main__':
    unittest.main()
