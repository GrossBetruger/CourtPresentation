import math
import os
import numpy
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plot

from pathlib import Path
from collections import defaultdict
from typing import List, Tuple
from utils import get_engine
from psycopg2.extensions import cursor
from enum import Enum
from utils import normalize_hebrew


TEST_RESULT_HEBREW = normalize_hebrew("תוצאת דגימה")

VENDOR_HEBREW = normalize_hebrew("ספק")


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


WEBSITE_NAME_TRANSLATE = {
        "hot": "הוט",
        "bezeq": "בזק",
        "ookla": "אוקלה",
        "google": "גוגל",
        "netflix": "נטפליקס",
    }


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


def count_users(vendor: VendorUsers, speed: int) -> int:
    postgres_engine = get_engine()
    cur: cursor = postgres_engine.cursor()
    cur.execute(
        f"""
        select count(distinct user_name)
        from valid_tests
        where user_name in (select * from {vendor.value})
        and speed = {speed}
        ;
        """
    )
    return cur.fetchall()[0][0]


def plot_histogram(x_values: List[float],
                   title: str,
                   x_label: str,
                   y_label: str,
                   bins: int,
                   _range: Tuple[int, int],
                   size_of_tick: int = None):

    # title = normalize_hebrew(title)
    s = pd.Series(x_values)
    plt = s.plot(kind='hist', bins=bins, title=title, range=_range)

    # plt.axes.set_title("Title", fontsize=15)
    plt.set_xlabel("X Label", fontsize=10)
    plt.set_ylabel("Y Label", fontsize=10)

    x_label = normalize_hebrew(x_label)
    y_label = normalize_hebrew(y_label)
    plt.set_xlabel(x_label)
    plt.set_ylabel(y_label)

    first_bin, last_bin = _range
    if size_of_tick is None:
        size_of_tick = (last_bin + 1) // bins
    plt.set_xticks(list(range(first_bin, last_bin + 1, size_of_tick or 1)))
    return title


def plot_ground_truth_speeds(vendor_users: VendorUsers, ratios: List[float], speed: int):
    title = f'היסטוגרמה מהירות הורדה: ' +  vendor_to_hebrew_name(vendor_users)
    title += ' תכנית ' + str(speed) + ' מגה-ביט'
    last_xtick = speed if speed < 200 else 220
    plt = plot_histogram(x_values=ratios,
                         title=normalize_hebrew(title),
                         x_label='מהירות',
                         y_label='מספר בדיקות',
                         bins=speed // 10,
                         _range=(0, last_xtick),
                         size_of_tick=20 if speed == 200 else None)

    snapshots_path = Path("question_snapshots") / Path('ground_truth_rate_histograms')
    if not os.path.exists(snapshots_path):
        os.makedirs(snapshots_path)

    fig_path = snapshots_path / Path(title + ".png")
    print(f"saving: {fig_path}")
    plot.savefig(fig_path)
    plot.show()


def set_graphical_context():

    sns.set(font='DejaVu Sans',
            font_scale=0.8,
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

                'xtick.major.width': 0.1,
                'xtick.minor.width': 0.1,

                'ytick.direction': 'out',
                'ytick.left': True,
                'ytick.right': False})
    sns.set_style("darkgrid")


def speed_test_website_main(websites: List[str]):
    number_of_websites = len(websites) + 1 # +1 for normal distribution
    number_of_rows = 2
    row_size = (number_of_websites // 2) + number_of_websites % 2
    fig, axs = plot.subplots(number_of_rows, row_size, sharey=True, tight_layout=True)

    row_size = 3
    i = j = 0
    while websites:
        if i == row_size:
            j += 1
            i = 0

        website = websites.pop()
        print(f"getting data for: '{website}'")
        ratios = get_speed_test_ratios(website)
        axs[j, i].hist(ratios, bins=20, range=(0, 2))
        axs[j, i].set_title(normalize_hebrew(WEBSITE_NAME_TRANSLATE[website]))
        i += 1

    # add normal distribution data: μ, σ = 1.0, 0.33
    axs[1, 2].hist([numpy.random.normal(1.0, 0.33) for x in range(400000)], bins=20, range=(0, 2))
    axs[1, 2].set_title(normalize_hebrew('התפלגות נורמלית אקראית'))

    x_label = normalize_hebrew('יחס בדיקת אתר למהירות בפועל')
    x_label += ' ' * 130
    y_label = normalize_hebrew('מספר בדיקות')
    plot.xlabel(x_label)
    plot.ylabel(y_label)
    snapshots_path = Path("question_snapshots") / Path('website_comparison_histograms')
    if not os.path.exists(snapshots_path):
        os.makedirs(snapshots_path)

    plot.legend(loc='best')
    plot.savefig(snapshots_path / Path('השוואת אתרי בדיקה' + ".png"))
    plot.show()  # `.show` has to be after `.savefig` or else all hell breaks loose


def create_snapshot_path(directory: str):
    snapshots_path = Path("question_snapshots") / Path(directory)
    if not os.path.exists(snapshots_path):
        os.makedirs(snapshots_path)

    return snapshots_path


def ground_truth_main():
    violin_data = defaultdict(list)
    internet_speeds = [40, 100, 200]
    for users in [VendorUsers.Bezeq, VendorUsers.Hot, VendorUsers.Partner]:
        for speed in internet_speeds:
            num_users = count_users(users, speed)
            if num_users < 8:
                print(f'not enough users for {users}, {speed} skipping')
                continue
            ground_truth_rates = get_ground_truth_speeds_by_vendor(users, speed)
            vendor_name_hebrew = normalize_hebrew(vendor_to_hebrew_name(users))

            # create violin data
            for rate in ground_truth_rates:
                violin_data[speed].append({VENDOR_HEBREW: vendor_name_hebrew,
                                           # "תכנית": speed,
                                           TEST_RESULT_HEBREW: rate})
            if not ground_truth_rates:
                continue
            plot_ground_truth_speeds(vendor_users=users, ratios=ground_truth_rates, speed=speed)

    for speed in internet_speeds:
        raw_title = "התפלגות מהירויות דגימה תכנית: " + str(speed) + " מגה-ביט"
        speed_violin_data = pd.DataFrame.from_dict(violin_data[speed])
        sns_plot = sns.violinplot(x=speed_violin_data[VENDOR_HEBREW], y=speed_violin_data[TEST_RESULT_HEBREW])
        sns_plot.set(title=normalize_hebrew(raw_title))

        snapshots_path = Path("question_snapshots") / Path('ground_truth_violin_plots')
        if not os.path.exists(snapshots_path):
            os.makedirs(snapshots_path)

        fig_path = snapshots_path / Path(raw_title + ".png")
        plot.savefig(fig_path)
        print(f"saving {fig_path}")
        plot.show()


def speed_test_website_scatter():
    engine = get_engine()

    all_resources_query = """
          select website_to_hebrew(website) "אתר בדיקה",
          avg(ground_truth_rate / speed_test_rate) "יחס מהירות בפועל למהירות בדיקה"
          from valid_tests
          where (ground_truth_rate / speed_test_rate) between 0.01 and 100
          and  true_or_null(is_classic_test)
          and  ground_truth_rate > 0 and speed_test_rate > 0
          and not website = 'atnt'
          group by website_to_hebrew(website)
          order by  "יחס מהירות בפועל למהירות בדיקה"
          ;
      """

    public_servers_query = """
          select website_to_hebrew(website) "אתר בדיקה",
          avg(ground_truth_rate / speed_test_rate) "יחס מהירות בפועל למהירות בדיקה"
          from valid_tests
          where (ground_truth_rate / speed_test_rate) between 0.01 and 100
          and  true_or_null(is_classic_test)
          and  ground_truth_rate > 0 and speed_test_rate > 0
          and is_classic_resource(file_name)
          and not website = 'atnt'
          group by website
          order by  "יחס מהירות בפועל למהירות בדיקה"
          ;
      """

    israel_cache_query = """
    select website_to_hebrew(website) "אתר בדיקה",      
          avg(ground_truth_rate / speed_test_rate) "יחס מהירות בפועל למהירות בדיקה"
          from valid_tests
          where (ground_truth_rate / speed_test_rate) between 0.01 and 100
          and  true_or_null(is_classic_test)
          and  ground_truth_rate > 0 and speed_test_rate > 0
          and file_name = 'israel_cache'
          and not website = 'atnt'
          group by website
          order by  "יחס מהירות בפועל למהירות בדיקה"
      ;
      """

    cur = engine.cursor()
    lables = "כל המקורות", "קבצים ציבוריים", "שרת מטמון ישראל"
    for label, query in zip(lables, [all_resources_query, public_servers_query, israel_cache_query]):
        print(f"handeling: {label}")
        cur.execute(query)
        all_resources = list(cur.fetchall())
        plot.scatter(x=[normalize_hebrew(x[0]) for x in all_resources],
                     y=[x[1] for x in all_resources],
                     label=normalize_hebrew(label))

    first_on_x, last_on_x = normalize_hebrew('הוט'), normalize_hebrew('גוגל')
    plot.hlines(y=1, xmin=first_on_x, xmax=last_on_x, colors='aqua', linestyles='dotted', lw=2, label=normalize_hebrew('חיזוי מדויק'))

    plot.legend(loc="best")
    plot.ylabel(normalize_hebrew('יחס בדיקת אתר למהירות בפועל'))
    snapshots_path = Path("question_snapshots") / Path('ground_truth_violin_plots')
    if not os.path.exists(snapshots_path):
        os.makedirs(snapshots_path)

    snapshots_path = create_snapshot_path("website_comparison_scatter")

    fig_path = snapshots_path / Path("השוואת ממוצעי אתרי בדיקה" + ".png")
    plot.savefig(fig_path)
    print(f"saving {fig_path}")
    plot.show()


if __name__ == "__main__":
    set_graphical_context()  # Make Matplotlib not suck at aesthetics

    # Website comparison scatter logic
    speed_test_website_scatter()

    # Website comparison histogram logic
    speed_test_website_main(
        websites=["netflix", "ookla", "bezeq", "google", "hot"]
    )

    #  Random Normal Distribution (example):
    nums = numpy.random.normal(1, 0.3, 100000)
    plot.hist(nums, 40, density=True)
    title = "היסטוגרמה התפלגות נורמלית של משתנה אקראי"
    plot.suptitle(normalize_hebrew(title))
    plot.savefig(title + ".png")
    print(f'saving {title + ".png"}')
    plot.show()

    # Ground truth rate histogram and violin plot logic
    ground_truth_main()
