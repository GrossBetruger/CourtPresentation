import numpy as np
import scipy
import matplotlib.pyplot as plt

from collections import defaultdict
from matplotlib import style
from typing import List, Dict, Optional
from scipy.stats import pearsonr, ttest_ind
from utils import get_engine, normalize_hebrew


CAPACITY = "capacity"

NUM_USERS = "num_users"


def get_household_data() -> List[Dict[str, float]]:
    engine = get_engine()
    cur = engine.cursor()
    cur.execute(
        """
        with user_household_sizes as (
            select "יוזר" as user_name, "מס_נפשות_בבית"::int as "household_size"
            from testers
            where "מס_נפשות_בבית" is not null
            order by "מס_נפשות_בבית"::int desc
        ),

        user_capacities as (
            select user_name, avg(ground_truth_rate) / speed capacity
            from valid_tests
            where connection = 'LAN'
            group by user_name, speed
        )

        select user_capacities.user_name, capacity, household_size 
        from user_capacities
        join user_household_sizes on user_capacities.user_name = user_household_sizes.user_name
        ;
        """
    )

    result = []

    for _, capacity, number_of_internet_users in cur.fetchall():
        result.append({NUM_USERS: float(number_of_internet_users), CAPACITY: float(capacity)})

    return result


def get_capacity_data():
    result = defaultdict(list)
    engine = get_engine()
    cur = engine.cursor()

    # Get Partner Data
    cur.execute(
        """
        select user_name, avg(ground_truth_rate / speed) capacity
        from valid_tests
        where user_name in (select * from partner_users)
        and speed = 100
        group by user_name
        """
    )
    for user_name, capacity in cur.fetchall():
        result["partner"].append((user_name, capacity))

    # Get HOT Data
    cur.execute(
        """
        select user_name, avg(ground_truth_rate / speed) capacity
        from valid_tests
        where user_name in (select * from hot_users)
        and speed = 100
        group by user_name
        """
    )
    for user_name, capacity in cur.fetchall():
        result["hot"].append((user_name, capacity))

    # Get Bezeq Data
    cur.execute(
        """
        select user_name, avg(ground_truth_rate / speed) capacity
        from valid_tests
        where user_name in (select * from bezeq_users)
        and speed = 100
        group by user_name
        """
    )
    for user_name, capacity in cur.fetchall():
        result["bezeq"].append((user_name, capacity))

    # Get All Users Data
    cur.execute(
        """
        select user_name, avg(ground_truth_rate / speed) capacity
        from valid_tests
        where speed = 100
        group by user_name
        """
    )
    for user_name, capacity in cur.fetchall():
        result["all"].append((user_name, capacity))

    # Get None Hot Users Data
    cur.execute(
        """
        select user_name, avg(ground_truth_rate / speed) capacity
        from valid_tests
        where user_name not in (select * from bezeq_users)
        and speed = 100
        group by user_name
        """
    )
    for user_name, capacity in cur.fetchall():
        result["not_hot"].append((user_name, capacity))

    return result


def linear_regression(x_values: List[float], y_values: List[float],
                      data_point_label: str, line_label: str,
                      xlabel: str, ylabel: str, dump_path: Optional[str] = "regression.png"):
    style.use('ggplot')

    xs = np.array(x_values, dtype=np.float64)
    ys = np.array(y_values, dtype=np.float64)

    slope, intercept, r_value, p_value, stderr = scipy.stats.linregress(xs, ys)

    fig, ax = plt.subplots()
    ax.plot(xs, ys, linewidth=0, marker='s', label=data_point_label)
    ax.plot(xs, intercept + slope * xs, label=line_label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(facecolor='white')
    plt.savefig(dump_path)
    plt.show()
    print(f"r squared: {r_value ** 2}")


if __name__ == "__main__":
    # Student's T-Test Logic

    vendor_capacity_data = get_capacity_data()
    t_score, p_value = ttest_ind([x[1] for x in vendor_capacity_data["hot"]],
                                 [x[1] for x in vendor_capacity_data["bezeq"]])

    print("t test score:", t_score, "p value:", p_value)

    # Linear Regression Logic
    household_stats = get_household_data()
    x_values = np.array([x[NUM_USERS] for x in household_stats])
    y_values = np.array([y[CAPACITY] for y in household_stats])

    linear_regression(
        x_values=x_values,
        y_values=y_values,
        data_point_label=normalize_hebrew('משתמשים'),
        line_label=normalize_hebrew('קו רגרסיה'),
        xlabel=normalize_hebrew('מספר נפשות בבית'),
        ylabel=normalize_hebrew('יחס מהירות לחבילה'),
        dump_path=f"household_size_and_internet_capacity_correlation",
    )
    quit()
