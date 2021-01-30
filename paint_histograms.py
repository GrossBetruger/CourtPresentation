import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plot

from typing import List, Tuple
from confidence_intervals import get_engine
from psycopg2.extensions import cursor
from enum import Enum


from utils import normalize_hebrew


class Website(Enum):
    hot = "hot"
    google = "google"
    bezeq = "bezeq"
    ookla = "ookla"
    netflix = "netflix"


class VendorUsers(Enum):
    Bezeq = "bezeq_users"
    Hot = "hot_users"
    Partner = "partner_users"


def vendor_to_hebrew_name(vendor: VendorUsers) -> str:
    if vendor is VendorUsers.Bezeq:
        return 'בזק'

    if vendor is VendorUsers.Hot:
        return 'הוט'

    if vendor is VendorUsers.Partner:
        return 'פרטנר'


def get_speed_test_ratios(speed_test: str) -> List[float]:
    postgres_engine = get_engine()
    cur: cursor = postgres_engine.cursor()
    cur.execute(
        f"""
        select ground_truth_rate / speed_test_rate as ratio
        from valid_tests
        where true_or_null(is_classic_test)
        and is_classic_resource(file_name)
        and speed_test_rate != 0 and ground_truth_rate != 0
        and website  = '{speed_test}'
        and (ground_truth_rate / speed_test_rate) between 0.01 and 100
        ;
        """
    )
    return [row[0] for row in cur.fetchall()]


def get_ground_truth_speeds_by_vendor(vendor: VendorUsers, speed: int):
    postgres_engine = get_engine()
    cur: cursor = postgres_engine.cursor()
    cur.execute(
        f"""
        select ground_truth_rate
        from valid_tests
        where speed = {speed}
        and user_name in (select * from {vendor.value})
        and connection = 'LAN'
        ;
        """
    )
    return [row[0] for row in cur.fetchall()]


def plot_histogram(x_values: List[float],
                   title: str,
                   x_label: str,
                   y_label: str,
                   bins: float,
                   _range: Tuple[int, int]):

    title = normalize_hebrew(title)
    s = pd.Series(x_values)
    plt = s.plot(kind='hist', bins=bins, title=title, range=_range)
    x_label = normalize_hebrew(x_label)
    y_label = normalize_hebrew(y_label)
    plt.set_xlabel(x_label)
    plt.set_ylabel(y_label)
    return title


def plot_website_ratios_histogram(website: Website, ratios: List[float]):
    name_translate = {
        "hot": "הוט",
        "bezeq": "בזק",
        "ookla": "אוקלה",
        "google": "גוגל",
        "netflix": "נטפליקס",
    }

    title = normalize_hebrew(f'התפלגות תוצאות בדיקות מהירות {name_translate[website.value]} - היסטוגרמה')
    s = pd.Series(ratios)
    plt = s.plot(kind='hist', bins=20, color='red', title=title, range=[0, 2])
    xlabel = normalize_hebrew('יחס מהירות בפועל למהירות אתר בדיקה (1.0 = בדיקה מושלמת)')
    plt.set_xlabel(xlabel)

    ylable = normalize_hebrew("מספר בדיקות")
    plt.set_xlabel(ylable)
    for patch in plt.patches:
        left, right = patch.xy
        if left >= 1:  # color bars that are >= 1 green (actual speed was higher than website speed)
            patch.set_color('green')
    return plt


def plot_ground_truth_speeds(vendor_users: VendorUsers, ratios: List[float]):
    title = f'היסטוגרמה מהירות הורדה: ' +  vendor_to_hebrew_name(vendor_users)
    title += ' תכנית ' + str(speed) + ' מגהביט'
    plt = plot_histogram(x_values=ratios,
                         title=title,
                         x_label='מהירות',
                         y_label='מספר בדיקות',
                         bins=10,
                         _range=(0, 100))

    plot.savefig(title + ".png")
    plot.show()


def set_graphical_context():
    sns.set(font='DejaVu Sans',
            rc={
                'axes.axisbelow': False,
                'axes.edgecolor': 'lightgrey',
                'axes.facecolor': 'None',
                'axes.grid': False,
                'axes.labelcolor': 'dimgrey',
                'axes.spines.right': False,
                'axes.spines.top': False,
                'figure.facecolor': 'white',
                'lines.solid_capstyle': 'round',
                'patch.edgecolor': 'w',
                'patch.force_edgecolor': True,
                'text.color': 'dimgrey',
                'xtick.bottom': False,
                'xtick.color': 'dimgrey',
                'xtick.direction': 'out',
                'xtick.top': False,
                'ytick.color': 'dimgrey',
                'ytick.direction': 'out',
                'ytick.left': True,
                'ytick.right': False})

    sns.set_context("notebook", rc={"font.size": 16,
                                    "axes.titlesize": 20,
                                    "axes.labelsize": 12})

    sns.set_color_codes("dark")


if __name__ == "__main__":
    # Website comparison histogram logic
    for website in [
        "netflix", "ookla", "bezeq", "google", "hot"
    ]:
        print(f"getting data for: '{website}'")
        ratios = get_speed_test_ratios(website)
        plot_website_ratios_histogram(Website(website), ratios)
        prefix = "classic_resources_"
        plot.savefig(f'{prefix}{website}_ratios_histogram.png')
        plot.show()  # `.show` has to be after `.savefig` or else all hell breaks loose

    set_graphical_context()  # Make Matplotlib not suck at aesthetics

    #  Random Normal Distribution (example):
    import numpy

    nums = numpy.random.normal(1, 0.3, 100000)
    plot.hist(nums, 40, density=True)
    plot.show()

    # Ground truth rate histogram logic
    for users in [VendorUsers.Bezeq, VendorUsers.Hot, VendorUsers.Partner]:
        for speed in [40, 100, 200]:
            ground_truth_rates = get_ground_truth_speeds_by_vendor(users, speed)
            if not ground_truth_rates:
                continue
            plot_ground_truth_speeds(vendor_users=users, ratios=ground_truth_rates)
    quit()