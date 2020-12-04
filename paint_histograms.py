import arabic_reshaper
import pandas as pd
from typing import List
from confidence_intervals import get_engine
from psycopg2.extensions import cursor
from enum import Enum
from bidi.algorithm import get_display
import matplotlib.pyplot as plot


class Website(Enum):
    hot = "hot"
    google = "google"
    bezeq = "bezeq"
    ookla = "ookla"
    netflix = "netflix"


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


def normalize_hebrew(raw_text: str):
    return get_display(arabic_reshaper.reshape(raw_text))


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


if __name__ == "__main__":
    for website in [
        "netflix", "ookla", "bezeq", "google", "hot"
    ]:
        print(f"getting data for: '{website}'")
        ratios = get_speed_test_ratios(website)
        plot_website_ratios_histogram(Website(website), ratios)
        prefix = "classic_resources_"
        plot.savefig(f'{prefix}{website}_ratios_histogram.png')
        plot.show()  # `.show` has to be after `.savefig` or else all hell breaks loose
