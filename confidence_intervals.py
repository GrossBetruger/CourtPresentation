import random
from collections import defaultdict
from enum import Enum
from itertools import chain
from random import choice
from typing import Optional, List, Dict, Tuple, Any

import numpy as np
import pandas as pd
import scipy
import scipy.stats
from psycopg2.extensions import cursor

from utils import get_engine

USER_SPEED_PROGRAM_KEY_HEBREW = "תכנית"

ISP_KEY_HEBREW = "ספקית"

INFRASTRUCTURE_KEY_HEBREW = "תשתית"

SAMPLE_AVERAGE_SPEED_KEY_HEBREW = "מהירות ממוצעת (מדגם)"

UPPER_BOUND_KEY_HEBREW = "גבול עליון"

LOWER_BOUND_KEY_HEBREW = "גבול תחתון"

CONFIDENCE_LEVEL_KEY_HEBREW = "רמת סמך"

USER_NAME_HEBREW_KEY = "שם משתמש"

DECIMAL_PLACES = 3


class Vendor(Enum):
    Bezeq = {"view": "bezeq_users", "name": "בזק"}
    HOT = {"view": "hot_users", "name": "הוט"}
    Partner = {"view": "partner_users", "name": "פרטנר"}


class ConfidenceIntervalResult:
    def __init__(
            self,
            confidence: float,
            lower_bound: float,
            upper_bound: float,
    ):
        self.confidence = confidence
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def to_dict(self):
        return {
            CONFIDENCE_LEVEL_KEY_HEBREW: self.confidence,
            LOWER_BOUND_KEY_HEBREW: self.lower_bound,
            UPPER_BOUND_KEY_HEBREW: self.upper_bound,
        }


class UserStats:
    def __init__(
            self,
            user_name: str,
            # mean: float,
            speed: int,
            infra: str,
            isp: str,
            # ci: ConfidenceIntervalResult,
    ):
        self.user_name = user_name
        self.mean: Optional[float] = None
        self.speed = speed
        self.infra = infra
        self.isp = isp
        self.ci: Optional[ConfidenceIntervalResult] = None

    def __str__(self) -> str:
        fields = [
            self.user_name, self.speed, self.infra,
            self.isp, self.mean, self.ci.to_dict()
        ]
        fields = [str(f) for f in fields]
        return "\n".join(fields)

    def to_dict(self) -> dict:
        fields = {
            USER_NAME_HEBREW_KEY: self.user_name,
            "תכנית": self.speed,
            "ספקית": self.isp,
            "תשתית": self.infra,
            "מהירות ממוצעת (מדגם)": self.mean,
        }

        return {**self.ci.to_dict(), **fields}

    def update_descriptive_stats(self, mean: float, ci: ConfidenceIntervalResult):
        self.mean = mean
        self.ci = ci

    def vendor_pattern_check(self, vendor: str) -> bool:
        return vendor in self.infra.lower() or vendor in self.isp.lower()

    def bezeq_user(self) -> bool:
        return self.vendor_pattern_check("bezeq")

    def partner_user(self) -> bool:
        return self.vendor_pattern_check("partner")

    def hot_user(self) -> bool:
        return self.vendor_pattern_check("hot")


class TestResult:
    def __init__(self, user_name: str, ground_truth_rate: float,
                 speed: int, infra: str, isp: str):
        self.user_name = user_name
        self.ground_truth_rate = ground_truth_rate
        self.speed = speed
        self.infra = infra
        self.isp = isp


def calc_confidence_interval(data, confidence=0.95):
    m = np.mean(data)
    lower, upper = scipy.stats.t.interval(confidence, len(data) - 1, loc=m, scale=scipy.stats.sem(data))
    h = m - lower
    return m, lower, upper, h


def manual_ci_sample(x_values: List[float], confidence: float = 0.95) -> Tuple[Any, Any]:
    def calc_t(conf: float, degrees_of_freedom):
        alpha = (1 - conf) / 2.
        t_score = scipy.stats.t.ppf(1 - alpha, df=degrees_of_freedom)
        return t_score

    m = np.mean(x_values)
    t = calc_t(confidence, len(x_values) - 1)

    h = t * np.std(x_values, ddof=1) / np.sqrt(len(x_values))
    return m - h, m + h


def get_speed_test_websites_rates(website: str):
    return f"""
        select ground_truth_rate / speed_test_rate rate
            from valid_tests
            where (ground_truth_rate / speed_test_rate) between 0.01 and 100
            and true_or_null(is_classic_test)
            and ground_truth_rate > 0
            and speed_test_rate > 0
            and website_to_hebrew(website) = '{website}'
        ;
    """


def choose_k_random_results(results: list, k: int) -> list:
    return [choice(results) for _ in range(k)]


def get_user_tests_in_time_interval() -> Dict[str, List[TestResult]]:
    engine = get_engine()
    cur: cursor = engine.cursor()
    cur.execute(
        """
        with user_stats as (
            select user_name,
                   min(to_israel_dst_aware(timestamp)) first_test,
                   min(to_israel_dst_aware(timestamp)) + interval '30' day first_test_plus_30_days,
                   count(*) num_test
            from valid_tests
            where connection = 'LAN'
            group by user_name
        )
        
        select valid_tests.user_name,
               ground_truth_rate,
               speed,
               infrastructure,
               isp,
               valid_tests.connection,
               num_test,
               timestamp
        from valid_tests
        join user_stats on user_stats.user_name = valid_tests.user_name
        where to_israel_dst_aware(timestamp) between first_test and first_test_plus_30_days
        and connection = 'LAN'
        and num_test >= 700
        ;
        """
    )

    results = defaultdict(list)

    for r in cur.fetchall():
        user_name, test_result, user_speed, infra, isp, _, _, _ = r

        results[user_name].append(
            TestResult(
                user_name=user_name,
                ground_truth_rate=test_result,
                speed=user_speed,
                infra=infra,
                isp=isp
            )
        )

    return results


def calc_intervals_speed_test_website_comparisons():
    postgres_engine = get_engine()
    cur: cursor = postgres_engine.cursor()
    for website in ["גוגל", "בזק", "אוקלה", "הוט", "נטפליקס"]:
        cur.execute(get_speed_test_websites_rates(website))
        rates = [x[0] for x in list(cur.fetchall())]
        print("רווח סמך עבור אתר בדיקת מהירות: {}".format(website))
        print("יחס ממוצע: {}".format(round(np.mean(rates), DECIMAL_PLACES)))
        print("סטיית תקן (מדגם): {}".format(round(np.std(rates, ddof=1), DECIMAL_PLACES)))
        print("מספר דגימות (N): {}".format(len(rates)))
        confs = [.95, .99, .999]
        for confidence in confs:
            mean, lower_bound, upper_bound, h = calc_confidence_interval(rates, confidence)
            lower_bound = round(lower_bound, DECIMAL_PLACES)
            upper_bound = round(upper_bound, DECIMAL_PLACES)
            print("ברמת סמך של {}% יחס מהירות בפועל \ למהירות בדיקה באתר בדיקת המהירות של {} הוא בין {} ל-{}".format(
                confidence * 100, website, lower_bound, upper_bound))
        print()


def prepare_for_googlesheets(table: dict):
    return pd.DataFrame(table).to_csv(sep='\t')


def choose_confidence_by_sample_size(n: int) -> float:
    #  CI with probability 1 - 5%/N (N=num of users int this slice)
    return 1 - 0.05 / n


def calcuate_ci_for_user_group(user_group: List[UserStats],
                               user_group_tests: List[TestResult],
                               test_sample_size: int) -> List[UserStats]:
    confidence_level = choose_confidence_by_sample_size(len(user_group))

    result = list()
    for user in user_group:
        user_tests = [test for test in user_group_tests if test.user_name == user.user_name]
        random_test_sample = [result.ground_truth_rate for result in
                              choose_k_random_results(user_tests, k=test_sample_size)]

        mean, lower_bound, upper_bound, h = calc_confidence_interval(random_test_sample, confidence=confidence_level)
        # h_values[user_stats.speed].append(h)

        ci = ConfidenceIntervalResult(
            confidence=confidence_level,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )

        user.update_descriptive_stats(mean=mean, ci=ci)
        result.append(user)
    return result


def flatten_tests(user_list: List[UserStats], tests: Dict[str, List[TestResult]]) -> List[TestResult]:
    return list(chain(*[test for user, test in tests.items()
                        if user in [u.user_name for u in user_list]]))


def count_defaulted_users_by_upper_bound(users: List[UserStats], default_rate: float) -> int:
    count = int()
    for user in users:
        if user.ci.upper_bound / user.speed <= default_rate:
            count += 1
    return count


def calculate_ci_stats_for_user_group(user_group: List[UserStats], user_group_name: str,
                                      tests: Dict[str, List[TestResult]],
                                      k: int, default_rates: List[float]):
    test_random_sample = flatten_tests(user_group, tests)
    users_with_ci_results = calcuate_ci_for_user_group(user_group, test_random_sample, k)
    print(f"{user_group_name} users (n={len(user_group)}")
    for def_rate in default_rates:
        defaulted_users = count_defaulted_users_by_upper_bound(users_with_ci_results, def_rate)
        print(f"""defaulted {user_group_name} with default ratio of: {def_rate}:
            {defaulted_users}""")
        print(f"{user_group_name} default rate: {defaulted_users / len(user_group)}")
        print()
    columns = [USER_NAME_HEBREW_KEY,
               USER_SPEED_PROGRAM_KEY_HEBREW,
               ISP_KEY_HEBREW,
               INFRASTRUCTURE_KEY_HEBREW,
               SAMPLE_AVERAGE_SPEED_KEY_HEBREW,
               LOWER_BOUND_KEY_HEBREW,
               UPPER_BOUND_KEY_HEBREW]

    print(pd.DataFrame()
          .from_records([u.to_dict() for u in users_with_ci_results])
          .sort_values(UPPER_BOUND_KEY_HEBREW)
          .to_csv(sep="\t", columns=columns))


def calc_confidence_mean_for_random_sample(k: int, default_rates: List[float]):
    all_user_tests = get_user_tests_in_time_interval()
    all_users = []
    for user in all_user_tests:
        user_stats = UserStats(
            user_name=all_user_tests[user][0].user_name,
            speed=all_user_tests[user][0].speed,
            infra=all_user_tests[user][0].infra,
            isp=all_user_tests[user][0].isp,
        )
        all_users.append(user_stats)

    bezeq_users = [u for u in all_users
                   if u.isp == 'Bezeq International-Ltd'
                   and u.infra == 'BEZEQ']

    calculate_ci_stats_for_user_group(bezeq_users, "bezeq", all_user_tests, k, default_rates)

    hot_users = [u for u in all_users
                 if u.isp == 'Hot-Net internet services Ltd.'
                 and u.infra == 'HOT']

    calculate_ci_stats_for_user_group(hot_users, "hot", all_user_tests, k, default_rates)

    partner_users = [u for u in all_users
                     if u.isp == 'Partner Communications Ltd.'
                     and u.infra == 'PARTNER']

    calculate_ci_stats_for_user_group(partner_users, "partner", all_user_tests, k, default_rates)

    calculate_ci_stats_for_user_group(all_users, "all vendors", all_user_tests, k, default_rates)


if __name__ == "__main__":
    calc_confidence_mean_for_random_sample(k=300, default_rates=[.75, .5, .33, .25])
