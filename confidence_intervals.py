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


if __name__ == "__main__":
    for data_file_path in [
        "user_means_lan_100.csv",
        "user_means_lan_40.csv",
        "user_means_lan_200.csv",
    ]:
        calc_intervals(data_file_path)
