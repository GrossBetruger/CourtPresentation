from collections import defaultdict
from enum import Enum

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


def calc_intervals_user_mean_speed_by_vendor(
        user_means: pd.Series,
        speed: int,
        vendor: Vendor,
        confidence: float) -> ConfidenceIntervalResult:
    confs = [.51, .80, .95]

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


if __name__ == "__main__":
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
