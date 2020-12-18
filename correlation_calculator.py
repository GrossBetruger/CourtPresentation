import numpy as np

from statistics import mean
import matplotlib.pyplot as plt
from matplotlib import style
from typing import List, Dict
from utils import get_engine

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


def best_fit_slope_and_intercept(xs, ys):
    m = (((mean(xs) * mean(ys)) - mean(xs * ys)) /
         ((mean(xs) * mean(xs)) - mean(xs * xs)))
    b = mean(ys) - m * mean(xs)
    return m, b


def squared_error(ys_orig, ys_line):
    return sum((ys_line - ys_orig) * (ys_line - ys_orig))


def coefficient_of_determination(ys_orig, ys_line):
    y_mean_line = [mean(ys_orig) for y in ys_orig]
    squared_error_regr = squared_error(ys_orig, ys_line)
    squared_error_y_mean = squared_error(ys_orig, y_mean_line)
    return 1 - (squared_error_regr / squared_error_y_mean)


if __name__ == "__main__":
    household_stats = get_household_data()
    x_values = np.array([x[NUM_USERS] for x in household_stats])
    y_values = np.array([y[CAPACITY] for y in household_stats])

    # x_values = np.array(list(range(20)))
    # y_values = x_values ** 10

    style.use('ggplot')

    xs = np.array(x_values, dtype=np.float64)
    ys = np.array(y_values, dtype=np.float64)

    m, b = best_fit_slope_and_intercept(xs, ys)
    regression_line = [(m * x) + b for x in xs]

    r_squared = coefficient_of_determination(ys, regression_line)
    print(r_squared)

    plt.scatter(xs,ys,color='#003F72',label='data')
    plt.plot(xs, regression_line, label='regression line')
    plt.legend(loc=4)
    plt.show()
