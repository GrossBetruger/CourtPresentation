import numpy as np
import scipy.stats
import pandas as pd
import scipy
from psycopg2.extensions import cursor

from utils import get_engine


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

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h, h


def calc_intervals_user_mean_speed(path):
    user_data = pd.read_csv(path)
    user_means = user_data['user_mean']
    confs = [.95, .99, .999]

    print(f"Showing confidence interval intervals for: {data_file_path}")
    print("Mean user speed:", np.mean(user_means))
    print("Standard deviation (sample) user speed:", np.std(user_means,  ddof=1))
    print("Number of users: ", len(user_means))
    for confidence in confs:
        mean, lower_bound, upper_bound, h = mean_confidence_interval(user_means, confidence)
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
    calc_intervals_speed_test_website_comparisons()

    for data_file_path in [
        "user_means_lan_100.csv",
        "user_means_lan_40.csv",
        "user_means_lan_200.csv",
    ]:
        calc_intervals_user_mean_speed(data_file_path)
