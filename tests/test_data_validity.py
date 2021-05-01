import unittest

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


if __name__ == '__main__':
    unittest.main()
