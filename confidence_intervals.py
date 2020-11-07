import numpy as np
import scipy.stats
import pandas as pd
import scipy


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h, h


def calc_intervals(path):
    user_data_lan_100 = pd.read_csv(path)
    user_means_lan_100 = user_data_lan_100['user_mean']

    confs = [.95, .99, .999]
    for confidence in confs:
        mean, lower_bound, upper_bound, h = mean_confidence_interval(user_means_lan_100, confidence)
        print(f"Showing confidence interval intervals for: {data_file_path}")
        print()
        print(f"{lower_bound} to: {upper_bound}, with confidence of {confidence * 100}%")
        print()


if __name__ == "__main__":
    for data_file_path in ["user_means_lan_100.csv"]:
        calc_intervals(data_file_path)
