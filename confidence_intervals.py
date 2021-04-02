from collections import defaultdict
from enum import Enum
from itertools import chain
from random import choice
from typing import Optional, List, Dict

import numpy as np
import pandas as pd
import scipy
import scipy.stats
from psycopg2.extensions import cursor

from utils import get_engine

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
            "confidence": self.confidence,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
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
            "user_name": self.user_name,
            "speed": self.speed,
            "isp": self.isp,
            "infra": self.infra,
            "mean": self.mean,
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

    def hot_user(self)-> bool:
        return self.vendor_pattern_check("hot")


class TestResult:
    def __init__(self, user_name: str, ground_truth_rate: float,
                 speed: int, infra: str, isp: str):
        self.user_name = user_name
        self.ground_truth_rate = ground_truth_rate
        self.speed = speed
        self.infra = infra
        self.isp = isp


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h, h


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


def get_ground_truth_rate_means(speed: int) -> pd.Series:
    engine = get_engine()
    cur: cursor = engine.cursor()
    cur.execute(
        """
        select avg(ground_truth_rate) user_mean from valid_tests
        where speed = {}
        and connection = 'LAN'
        group by user_name
        ;
        """.format(speed)
    )

    rows = []

    for r in cur.fetchall():
        mean, = r
        rows.append(mean)

    return pd.Series(rows, dtype=np.float64)


def get_ground_truth_rate_means_by_vendor(vendor: Vendor, speed: int) -> pd.Series:
    engine = get_engine()
    cur: cursor = engine.cursor()
    cur.execute(
        """
        select avg(ground_truth_rate) mean_ground_truth_rate
        from valid_tests
        where user_name in (select * from {})
        and speed = {}
        and connection = 'LAN'
        group by user_name
        ;
        """.format(vendor.value["view"], speed)
    )

    rows = []
    for r in cur.fetchall():
        mean, = r
        rows.append(mean)

    return pd.Series(rows, dtype=np.float64)


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


def calc_intervals_user_mean_speed_by_vendor(
        user_means: pd.Series,
        speed: int,
        vendor: Vendor,
        confidence: float) -> ConfidenceIntervalResult:
    # confs = [.51, .80, .95]

    print("נתוני היסק סטטיסטי משתמשי " + vendor.value["name"] + " בתכנית :" + str(speed) + " מגה-ביט לשנייה (חיבור קווי)")
    sample_mean = round(np.mean(user_means), DECIMAL_PLACES)
    print("מהירות משתמש ממוצעת: " + str(sample_mean) + " מגה-ביט לשנייה")
    # print("Mean user speed:", sample_mean)
    standard_deviation_population = round(np.std(user_means, ddof=1), DECIMAL_PLACES)
    print("סטיית תקן ממוצעי משתמשים (מדגם):", standard_deviation_population)
    print("מספר משתמשים: ", len(user_means))
    print()

    print("רווח בר סמך")
    mean, lower_bound, upper_bound, h = mean_confidence_interval(user_means, confidence)
    mean = round(mean, DECIMAL_PLACES)
    lower_bound = round(lower_bound, DECIMAL_PLACES)
    upper_bound = round(upper_bound, DECIMAL_PLACES)
    assert mean == sample_mean
    res = ConfidenceIntervalResult(confidence=confidence, lower_bound=lower_bound,
                                   upper_bound=upper_bound)

    msg = "ברמת סמך של: " + str(confidence * 100) + "%" + " המהירות הממוצעת באוכלוסיית משתמשי " + vendor.value["name"] + " בתכנית " + str(
        speed) + " מגה-ביט היא בין: " + str(lower_bound) + " ל: " + str(upper_bound) + " מגה-ביט לשנייה"
    print(msg)
    print()
    print()
    return res


def calc_intervals_user_mean_speed(user_means: pd.Series, speed: int):
    confs = [.95, .99, .999]

    print("נתוני היסק סטטיסטי משתמשי תכנית " + str(speed) + " מגה-ביט לשנייה (חיבור קווי)")
    sample_mean = round(np.mean(user_means), DECIMAL_PLACES)
    print("מהירות משתמש ממוצעת: " + str(sample_mean) + " מגה-ביט לשנייה")
    # print("Mean user speed:", sample_mean)
    standard_deviation_population = round(np.std(user_means,  ddof=1), DECIMAL_PLACES)
    print("סטיית תקן ממוצעי משתמשים (מדגם):", standard_deviation_population)
    print("מספר משתמשים: ", len(user_means))
    print()

    print("רווח בר סמך")
    for confidence in confs:
        mean, lower_bound, upper_bound, h = mean_confidence_interval(user_means, confidence)
        mean = round(mean, DECIMAL_PLACES)
        lower_bound = round(lower_bound, DECIMAL_PLACES)
        upper_bound = round(upper_bound, DECIMAL_PLACES)
        assert mean == sample_mean
        msg = "ברמת סמך של: " + str(confidence * 100) + "%" + " המהירות הממוצעת באוכלוסיית משתמשי תכנית: " + str(speed) + " מגה-ביט היא בין: " + str(lower_bound) + " ל: " + str(upper_bound) + " מגה-ביט לשנייה"
        print(msg)
        print()
    print()


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
            mean, lower_bound, upper_bound, h = mean_confidence_interval(rates, confidence)
            lower_bound = round(lower_bound, DECIMAL_PLACES)
            upper_bound = round(upper_bound, DECIMAL_PLACES)
            print("ברמת סמך של {}% יחס מהירות בפועל \ למהירות בדיקה באתר בדיקת המהירות של {} הוא בין {} ל-{}".format(confidence * 100, website, lower_bound, upper_bound))
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

        random_test_sample = [result.ground_truth_rate for result in
                              choose_k_random_results(user_group_tests, k=test_sample_size)]

        mean, lower_bound, upper_bound, h = mean_confidence_interval(random_test_sample, confidence=confidence_level)
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


def calc_confidence_mean_for_random_sample(k: int):
    all_user_tests = get_user_tests_in_time_interval()
    print(len(all_user_tests))
    all_users = []
    for user in all_user_tests:
        user_stats = UserStats(
            user_name=all_user_tests[user][0].user_name,
            speed = all_user_tests[user][0].speed,
            infra = all_user_tests[user][0].infra,
            isp = all_user_tests[user][0].isp,
        )
        all_users.append(user_stats)

    bezeq_users = [u for u in all_users
                   if u.isp == 'Bezeq International-Ltd'
                   and u.infra == 'BEZEQ']


    bezeq_tests = flatten_tests(bezeq_users, all_user_tests)
    bezeq_users = calcuate_ci_for_user_group(bezeq_users, bezeq_tests, k)
    print(f"bezeq users (n={len(bezeq_users)}):")
    print(pd.DataFrame().from_records([u.to_dict() for u in bezeq_users]).to_csv(sep="\t"))

    hot_users = [u for u in all_users
                 if u.isp == 'Hot-Net internet services Ltd.'
                 and u.infra == 'HOT']
    hot_tests = flatten_tests(hot_users, all_user_tests)
    hot_users = calcuate_ci_for_user_group(hot_users, hot_tests, k)

    print(f"hot users (n={len(hot_users)}")
    print(pd.DataFrame().from_records([u.to_dict() for u in hot_users]).to_csv(sep="\t"))

    partner_users = [u for u in all_users
                     if u.isp == 'Partner Communications Ltd.'
                     and u.infra == 'PARTNER']
    partner_tests = flatten_tests(partner_users, all_user_tests)
    partner_users = calcuate_ci_for_user_group(partner_users, partner_tests, k)
    print(f"partner users (n={len(partner_users)}")
    print(pd.DataFrame().from_records([u.to_dict() for u in partner_users]).to_csv(sep="\t"))

    # return final_result


if __name__ == "__main__":
    calc_confidence_mean_for_random_sample(k=300)

    quit()
    # # Websites Confidence Intervals
    # calc_intervals_speed_test_website_comparisons()
    # quit()

    # # User Ground Truth Means Confidence Intervals
    # for speed in [100, 40, 200]:
    #     user_means = get_ground_truth_rate_means(speed)
    #     calc_intervals_user_mean_speed(user_means, speed)

    # Vendor Ground Truth Means Confidence Intervals
    confidence = .99
    speeds = [100, 40, 200]
    result = defaultdict(lambda: defaultdict(str))

    for vendor in Vendor:
        for user_speed in speeds:
            means = get_ground_truth_rate_means_by_vendor(vendor, user_speed)
            if len(means) < 9:
                continue

            CI_result = calc_intervals_user_mean_speed_by_vendor(means, user_speed, vendor, confidence)
            result[vendor.value["name"]][user_speed] = str(CI_result.lower_bound) + " - " + str(CI_result.upper_bound)

    print(prepare_for_googlesheets(result))  # print as TSV
