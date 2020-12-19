import numpy as np

import matplotlib.pyplot as plt
import scipy
from matplotlib import style
from typing import List, Dict

from scipy.stats import pearsonr

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


if __name__ == "__main__":
    household_stats = get_household_data()
    x_values = np.array([x[NUM_USERS] for x in household_stats])
    y_values = np.array([y[CAPACITY] for y in household_stats])

    style.use('ggplot')

    xs = np.array(x_values, dtype=np.float64)
    ys = np.array(y_values, dtype=np.float64)

    slope, intercept, r_value, p_value, stderr = scipy.stats.linregress(xs, ys)

    fig, ax = plt.subplots()
    ax.plot(xs, ys, linewidth=0, marker='s', label=normalize_hebrew('משתמשים'))
    ax.plot(xs, intercept + slope * xs, label=normalize_hebrew('קו רגרסיה'))
    ax.set_xlabel(normalize_hebrew('מספר נפשות בבית'))
    ax.set_ylabel(normalize_hebrew('יחס מהירות לחבילה'))
    ax.legend(facecolor='white')
    plt.savefig("household_size_and_internet_capacity_correlation")
    plt.show()
    print(f"r squared: {r_value ** 2}")

