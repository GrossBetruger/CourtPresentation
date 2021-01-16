import numpy as np
import scipy.stats
import pandas as pd
import scipy

from psycopg2.extensions import cursor
from utils import get_engine
from decimal import *

DECIMAL_PLACES = 3


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
        group by user_name
        ;
        """.format(speed)
    )

    rows = []

    for r in cur.fetchall():
        mean, = r
        rows.append(mean)

    return pd.Series(rows)


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h, h


def calc_intervals_user_mean_speed(user_means: pd.Series, speed: int):
    confs = [.95, .99, .999]

    print("נתוני היסק סטטיסטי משתמשי תכנית " + str(speed) + " מגה-ביט לשנייה")
    sample_mean = round(np.mean(user_means), DECIMAL_PLACES)
    print("מהירות משתמש ממוצעת: " + str(sample_mean) + " מגה-ביט לשנייה")
    # print("Mean user speed:", sample_mean)
    standard_deviation_population = round(np.std(user_means,  ddof=1), DECIMAL_PLACES)
    print("סטיית תקן ממוצעי משתמשים (מדגם):", standard_deviation_population)
    print("מספר משתמשים: ", len(user_means))
    for confidence in confs:
        mean, lower_bound, upper_bound, h = mean_confidence_interval(user_means, confidence)
        mean = round(mean, DECIMAL_PLACES)
        lower_bound = round(lower_bound, DECIMAL_PLACES)
        upper_bound = round(upper_bound, DECIMAL_PLACES)
        assert mean == sample_mean
        print(f"{lower_bound} to: {upper_bound}, with confidence of {confidence * 100}%")
    print()


def calc_intervals_speed_test_website_comparisons():
    postgres_engine = get_engine()
    cur: cursor = postgres_engine.cursor()
    for website in ["גוגל", "בזק", "אוקלה", "הוט", "נטפליקס"]:
        cur.execute(get_speed_test_websites_rates(website))
        rates = [x[0] for x in list(cur.fetchall())]
        print("רווח סמך עבור אתר בדיקת מהירות: {}".format(website))
        print("יחס ממוצע: {}".format(np.mean(rates)))
        print("סטיית תקן (מדגם): {}".format(np.std(rates, ddof=1)))
        confs = [.95, .99, .999]
        for confidence in confs:
            mean, lower_bound, upper_bound, h = mean_confidence_interval(rates, confidence)
            print("ברמת סמך של {}% יחס מהירות בפועל \ למהירות בדיקה באתר בדיקת המהירות של {} הוא בין {} ל-{}".format(confidence * 100, website, lower_bound, upper_bound))
        print()


if __name__ == "__main__":
    # Websites Confidence Intervals
    # calc_intervals_speed_test_website_comparisons()

    # User Ground Truth Means Confidence Intervals
    for speed in [100, 40, 200]:
        user_means = get_ground_truth_rate_means(speed)
        calc_intervals_user_mean_speed(user_means, speed)
