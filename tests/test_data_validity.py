import json
import unittest

from typing import List
from unittest import skip

import pandas as pd

from googlesheet_updater import read_sheet
from utils import get_engine
from .. import confidence_intervals


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
                                              " from randomized_valid_tests order by random_index")

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

        public_access_resources = ["file_name", "amazon-workSpaces",
                                   "windows-games", "windows-games-studio",
                                   "my-sql", "dlink", "vlc", "go", "firefox", "quicktime"]

        for _, _, _, filename in sample:
            self.assertIn(filename, public_access_resources)

    def test_evening_random_sample(self):
        evening_timestamps = self.get_rows("select timestamp from test_random_sample_evening")
        for timestamp, in evening_timestamps:
            self.assertIn("Evening", self.get_rows(f"select get_time_of_day({timestamp})")[0][0])

        random_sample_evening = self.get_rows(
            "select user_name, count(*) from test_random_sample_evening group by user_name")
        for _user_name, count in random_sample_evening:
            self.assertEqual(300, count, f"user: {_user_name} has {count} tests")

        speeds = self.get_rows("select speed from test_random_sample_evening")
        for speed, in speeds:
            self.assertIn(speed, [100, 200, 500, 1000])

    def test_ci_tables(self):
        # Test CI Tables data persistency
        bezeq_ci = self.get_rows("select * from bezeq_ci")
        bezeq_ci_first_row = ('yarden', '100', 'Cellcom Fixed Line Communication L.P.', 'BEZEQ',
                              '24.17307459253051', '22.419327471344598', '25.92682171371644', '0.9989583333333333')
        bezeq_ci_last_row = ('raz', '100', 'Hot-Net internet services Ltd.', 'BEZEQ', '66.30938669799932',
                             '61.388106035193466', '71.23066736080521', '0.9989583333333333')
        bezeq_ci_tenth_row = ('nimrod', '100', '013 NetVision Ltd', 'BEZEQ', '31.192815980664005',
                              '29.223790648991308', '33.16184131233672', '0.9989583333333333')

        self.assertEqual(bezeq_ci_first_row, bezeq_ci[0])
        self.assertEqual(bezeq_ci_last_row, bezeq_ci[-1])
        self.assertEqual(bezeq_ci_tenth_row, bezeq_ci[10])

        pure_bezeq_ci = self.get_rows("select * from pure_bezeq_ci")
        pure_bezeq_ci_first = ('michael', '100', 'Bezeq International-Ltd', 'BEZEQ',
                               '29.66160497821917', '29.077337604229974',
                               '30.245872352208366', '0.9970588235294118')
        pure_bezeq_ci_last = (
            'alon', '100', 'Bezeq International-Ltd', 'BEZEQ', '64.8046254918595', '60.96868027095032',
            '68.64057071276866',
            '0.9970588235294118')
        pure_bezeq_ci_tenth = (
            'rina', '100', 'Bezeq International-Ltd', 'BEZEQ', '52.732937250037054', '48.413901608636756',
            '57.05197289143735', '0.9970588235294118')

        self.assertEqual(pure_bezeq_ci_first, pure_bezeq_ci[0])
        self.assertEqual(pure_bezeq_ci_last, pure_bezeq_ci[-1])
        self.assertEqual(pure_bezeq_ci_tenth, pure_bezeq_ci[10])

        hot_ci = self.get_rows("select * from hot_ci")
        hot_ci_first_row = ('rom', '100', 'Hot-Net internet services Ltd.', 'HOT',
                            '12.34002004187883', '10.041289542437283', '14.638750541320395', '0.9985714285714286')
        hot_ci_last_row = ('barak', '100', '013 NetVision Ltd', 'HOT', '114.77583966117818',
                           '104.20295342751203', '125.3487258948444', '0.9985714285714286')
        hot_ci_tenth_row = ('alon_s', '100', 'ITC NG ltd', 'HOT', '49.53545118889848',
                            '43.974820709604955', '55.09608166819204', '0.9985714285714286')

        self.assertEqual(hot_ci_first_row, hot_ci[0])
        self.assertEqual(hot_ci_last_row, hot_ci[-1])
        self.assertEqual(hot_ci_tenth_row, hot_ci[10])

    @skip  # not really needed covered by next test
    def test_summary_ci_tables(self):
        isp_or_infra_summary_table = read_sheet("ממצאי רווח סמך (ספקית או תשתית)")
        isp_and_infra_summary_table = read_sheet("ממצאי רווח סמך (ספקית + תשתית)")

        isp_and_infra_raw = {
            "מספר משתמשים": {
                "0": 17,
                "1": 20,
                "2": 6
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם גבוהה מ-80% הבטחת החבילה": {
                "0": "0 (0.00%)",
                "1": "0 (0.00%)",
                "2": "0 (0.00%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה": {
                "0": "7 (41.18%)",
                "1": "8 (40.00%)",
                "2": "2 (33.33%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה בשעות הערב": {
                "0": "7 (41.18%)",
                "1": "10 (50.00%)",
                "2": "3 (50.00%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה": {
                "0": "2 (11.76%)",
                "1": "5 (25.00%)",
                "2": "2 (33.33%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה בשעות הערב": {
                "0": "2 (11.76%)",
                "1": "6 (30.00%)",
                "2": "2 (33.33%)"
            },
            "ספקית + תשתית": {
                "0": "בזק",
                "1": "הוט",
                "2": "פרטנר"
            }
        }

        isp_or_infra_raw = {
            "מספר משתמשים": {
                "0": 48,
                "1": 35,
                "2": 14
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם גבוהה מ-80% הבטחת החבילה": {
                "0": "0 (0.00%)",
                "1": "1 (2.86%)",
                "2": "0 (0.00%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה": {
                "0": "23 (47.92%)",
                "1": "13 (37.14%)",
                "2": "7 (50.00%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה בשעות הערב": {
                "0": "26 (54.17%)",
                "1": "15 (42.86%)",
                "2": "8 (57.14%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה": {
                "0": "11 (22.92%)",
                "1": "8 (22.86%)",
                "2": "2 (14.29%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה בשעות הערב": {
                "0": "11 (22.92%)",
                "1": "10 (28.57%)",
                "2": "2 (14.29%)"
            },
            "ספקית או תשתית": {
                "0": "בזק",
                "1": "הוט",
                "2": "פרטנר"
            }
        }

        self.assertEqual(isp_or_infra_raw, isp_or_infra_summary_table)
        self.assertEqual(isp_and_infra_raw, isp_and_infra_summary_table)

    def test_ci(self):
        def normalize(data: dict) -> str:
            return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False).encode(
                'utf8').decode()

        isp_and_infra_raw = {
            "מספר משתמשים": {
                "0": 17,
                "1": 20,
                "2": 6
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם גבוהה מ-80% הבטחת החבילה": {
                "0": "0 (0.00%)",
                "1": "0 (0.00%)",
                "2": "0 (0.00%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה": {
                "0": "7 (41.18%)",
                "1": "8 (40.00%)",
                "2": "2 (33.33%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה בשעות הערב": {
                "0": "7 (41.18%)",
                "1": "10 (50.00%)",
                "2": "3 (50.00%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה": {
                "0": "2 (11.76%)",
                "1": "5 (25.00%)",
                "2": "2 (33.33%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה בשעות הערב": {
                "0": "2 (11.76%)",
                "1": "6 (30.00%)",
                "2": "2 (33.33%)"
            },
            "ספקית + תשתית": {
                "0": "בזק",
                "1": "הוט",
                "2": "פרטנר"
            }
        }

        isp_or_infra_raw = {
            "מספר משתמשים": {
                "0": 48,
                "1": 35,
                "2": 14
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם גבוהה מ-80% הבטחת החבילה": {
                "0": "0 (0.00%)",
                "1": "1 (2.86%)",
                "2": "0 (0.00%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה": {
                "0": "23 (47.92%)",
                "1": "13 (37.14%)",
                "2": "7 (50.00%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה בשעות הערב": {
                "0": "26 (54.17%)",
                "1": "15 (42.86%)",
                "2": "8 (57.14%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה": {
                "0": "11 (22.92%)",
                "1": "8 (22.86%)",
                "2": "2 (14.29%)"
            },
            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה בשעות הערב": {
                "0": "11 (22.92%)",
                "1": "10 (28.57%)",
                "2": "2 (14.29%)"
            },
            "ספקית או תשתית": {
                "0": "בזק",
                "1": "הוט",
                "2": "פרטנר"
            }
        }
        ci_data = confidence_intervals.ci_tables_to_df()
        infra_and_isp_ci_table = confidence_intervals.create_ci_table(ci_data=ci_data, pure=True)
        infra_or_isp_ci_table = confidence_intervals.create_ci_table(ci_data=ci_data, pure=False)
        self.assertEqual(normalize(isp_and_infra_raw), normalize(infra_and_isp_ci_table.to_dict()))
        self.assertEqual(normalize(isp_or_infra_raw), normalize(infra_or_isp_ci_table.to_dict()))


if __name__ == '__main__':
    unittest.main()
