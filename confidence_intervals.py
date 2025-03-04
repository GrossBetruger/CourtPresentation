import json
import os
from io import StringIO

import numpy as np
import pandas as pd
import psycopg2
import scipy
import scipy.stats

from collections import defaultdict
from dataclasses import dataclass
from itertools import chain
from random import choice
from typing import Optional, List, Dict, Tuple, Any
from psycopg2.extensions import cursor

from confidence_interval_utils.init_ci_tables import CITablesInit
from confidence_interval_utils.queries import CI_HIGHLEVEL_QUERY_ISP_OR_INFRA, CI_HIGHLEVEL_QUERY_ISP_AND_INFRA
from utils import get_engine, get_rows, get_sql_alchemy_engine
from googlesheet_updater import update_sheet

SPREADSHEET_TITLE_SUMMARY_ISP_AND_INFRA = "ממצאי רווח סמך (ספקית + תשתית)"

SPREADSHEET_TITLE_SUMMARY_ISP_OR_INFRA = "ממצאי רווח סמך (ספקית או תשתית)"

USER_SPEED_PROGRAM_KEY_HEBREW = "תכנית"

ISP_KEY_HEBREW = "ספקית"

INFRASTRUCTURE_KEY_HEBREW = "תשתית"

SAMPLE_AVERAGE_SPEED_KEY_HEBREW = "מהירות ממוצעת (מדגם)"

UPPER_BOUND_KEY_HEBREW = "גבול עליון"

LOWER_BOUND_KEY_HEBREW = "גבול תחתון"

CONFIDENCE_LEVEL_KEY_HEBREW = "רמת סמך"

USER_NAME_HEBREW_KEY = "שם משתמש"

DECIMAL_PLACES = 3


@dataclass
class Vendor:
    isp: str
    infra: str
    sheet_title: str
    sheet_title_evening: str
    sheet_title_pure: str
    sheet_title_pure_evening: str


BEZEQ = Vendor(
    'Bezeq International-Ltd',
    'BEZEQ',
    sheet_title='משתמשי בזק (ספקית או תשתית)',
    sheet_title_evening='משתמשי בזק (ספקית או תשתית) שעות הערב',
    sheet_title_pure='משתמשי בזק (ספקית + תשתית)',
    sheet_title_pure_evening='משתמשי בזק (ספקית + תשתית) שעות הערב'
)

HOT = Vendor(
    'Hot-Net internet services Ltd.',
    'HOT',
    sheet_title='משתמשי הוט (ספקית או תשתית)',
    sheet_title_evening='משתמשי הוט (ספקית או תשתית) שעות הערב',
    sheet_title_pure='משתמשי הוט (ספקית + תשתית)',
    sheet_title_pure_evening='משתמשי הוט (ספקית + תשתית) שעות הערב'
)

PARTNER = Vendor(
    'Partner Communications Ltd.',
    'PARTNER',
    sheet_title='משתמשי פרטנר (ספקית או תשתית)',
    sheet_title_evening='משתמשי פרטנר (ספקית או תשתית) שעות הערב',
    sheet_title_pure='משתמשי פרטנר (ספקית + תשתית)',
    sheet_title_pure_evening='משתמשי פרטנר (ספקית + תשתית) שעות הערב'
)


class ConfidenceIntervalResult:
    def __init__(
            self,
            confidence: float,
            lower_bound: float,
            upper_bound: float,
    ):
        self.confidence = confidence
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def to_dict(self):
        return {
            CONFIDENCE_LEVEL_KEY_HEBREW: self.confidence,
            LOWER_BOUND_KEY_HEBREW: self.lower_bound,
            UPPER_BOUND_KEY_HEBREW: self.upper_bound,
        }


class UserStats:
    def __init__(
            self,
            user_name: str,
            speed: int,
            infra: str,
            isp: str,
    ):
        self.user_name = user_name
        self.mean: Optional[float] = None
        self.speed = speed
        self.infra = infra
        self.isp = isp
        self.ci: Optional[ConfidenceIntervalResult] = None

    def __str__(self) -> str:
        fields = [
            self.user_name, self.speed, self.infra,
            self.isp, self.mean, self.ci.to_dict()
        ]
        fields = [str(f) for f in fields]
        return "\n".join(fields)

    def to_dict(self) -> dict:
        fields = {
            USER_NAME_HEBREW_KEY: self.user_name,
            "תכנית": self.speed,
            "ספקית": self.isp,
            "תשתית": self.infra,
            "מהירות ממוצעת (מדגם)": self.mean,
        }

        return {**self.ci.to_dict(), **fields}

    def update_descriptive_stats(self, mean: float, ci: ConfidenceIntervalResult):
        self.mean = mean
        self.ci = ci

    def vendor_pattern_check(self, vendor: str) -> bool:
        return vendor in self.infra.lower() or vendor in self.isp.lower()

    def bezeq_user(self) -> bool:
        return self.vendor_pattern_check("bezeq")

    def partner_user(self) -> bool:
        return self.vendor_pattern_check("partner")

    def hot_user(self) -> bool:
        return self.vendor_pattern_check("hot")


class TestResult:
    def __init__(self, user_name: str, ground_truth_rate: float,
                 speed: int, infra: str, isp: str):
        self.user_name = user_name
        self.ground_truth_rate = ground_truth_rate
        self.speed = speed
        self.infra = infra
        self.isp = isp


def get_sheet_title(vendor: Vendor, is_pure: bool, is_evening: bool):
    if is_pure is True and is_evening is True:
        return vendor.sheet_title_pure_evening
    elif is_pure is True:
        return vendor.sheet_title_pure
    elif is_evening is True:
        return vendor.sheet_title_evening
    return vendor.sheet_title


def calc_confidence_interval(data, confidence=0.95):
    m = np.mean(data)
    lower, upper = scipy.stats.t.interval(confidence, len(data) - 1, loc=m, scale=scipy.stats.sem(data))
    h = m - lower
    return m, lower, upper, h


def manual_ci_sample(x_values: List[float], confidence: float = 0.95) -> Tuple[Any, Any]:
    def calc_t(conf: float, degrees_of_freedom):
        alpha = (1 - conf) / 2.
        t_score = scipy.stats.t.ppf(1 - alpha, df=degrees_of_freedom)
        return t_score

    m = np.mean(x_values)
    t = calc_t(confidence, len(x_values) - 1)

    h = t * np.std(x_values, ddof=1) / np.sqrt(len(x_values))
    return m - h, m + h


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


def choose_k_random_results(results: list, k: int) -> list:
    return [choice(results) for _ in range(k)]


def fetch_sample_results(c: cursor) -> Dict[str, List[TestResult]]:
    results = defaultdict(list)

    for r in c.fetchall():
        user_name, test_result, user_speed, infra, isp = r

        results[user_name].append(
            TestResult(
                user_name=user_name,
                ground_truth_rate=test_result,
                speed=user_speed,
                infra=infra,
                isp=isp
            )
        )

    return results


def get_user_tests_in_time_interval() -> Dict[str, List[TestResult]]:
    engine = get_engine()
    cur: cursor = engine.cursor()
    cur.execute(
        """
        select user_name, result, speed, infra, isp
        from test_random_sample
        ;   
        """
    )
    return fetch_sample_results(cur)


def get_user_tests_in_time_interval_evening() -> Dict[str, List[TestResult]]:
    engine = get_engine()
    cur: cursor = engine.cursor()
    cur.execute(
        """
        select user_name, result, speed, infra, isp
        from test_random_sample_evening
        ;   
        """
    )
    return fetch_sample_results(cur)


def calc_intervals_speed_test_website_comparisons():
    postgres_engine = get_engine()
    cur: cursor = postgres_engine.cursor()
    for website in ["גוגל", "בזק", "אוקלה", "הוט", "נטפליקס"]:
        cur.execute(get_speed_test_websites_rates(website))
        rates = [x[0] for x in list(cur.fetchall())]
        print("רווח סמך עבור אתר בדיקת מהירות: {}".format(website))
        print("יחס ממוצע: {}".format(round(np.mean(rates), DECIMAL_PLACES)))
        print("סטיית תקן (מדגם): {}".format(round(np.std(rates, ddof=1), DECIMAL_PLACES)))
        print("מספר דגימות (N): {}".format(len(rates)))
        confs = [.95, .99, .999]
        for confidence in confs:
            mean, lower_bound, upper_bound, h = calc_confidence_interval(rates, confidence)
            lower_bound = round(lower_bound, DECIMAL_PLACES)
            upper_bound = round(upper_bound, DECIMAL_PLACES)
            print("ברמת סמך של {}% יחס מהירות בפועל \ למהירות בדיקה באתר בדיקת המהירות של {} הוא בין {} ל-{}".format(
                confidence * 100, website, lower_bound, upper_bound))
        print()


def prepare_for_googlesheets(table: dict):
    return pd.DataFrame(table).to_csv(sep='\t')


def choose_confidence_by_sample_size(n: int) -> float:
    #  CI with probability 1 - 5%/N (N=num of users int this slice)
    return 1 - 0.05 / n


def calcuate_ci_for_user_group(user_group: List[UserStats],
                               user_group_tests: List[TestResult],
                               test_sample_size: int) -> List[UserStats]:
    confidence_level = choose_confidence_by_sample_size(len(user_group))

    result = list()
    for user in user_group:
        user_test_sample = [test.ground_truth_rate for test in user_group_tests if test.user_name == user.user_name]
        assert len(user_test_sample) == test_sample_size
        mean, lower_bound, upper_bound, h = calc_confidence_interval(user_test_sample, confidence=confidence_level)

        ci = ConfidenceIntervalResult(
            confidence=confidence_level,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )

        user.update_descriptive_stats(mean=mean, ci=ci)
        result.append(user)
    return result


def flatten_tests(user_list: List[UserStats], tests: Dict[str, List[TestResult]]) -> List[TestResult]:
    return list(chain(*[test for user, test in tests.items()
                        if user in [u.user_name for u in user_list]]))


def count_defaulted_users_by_upper_bound(users: List[UserStats], default_rate: float) -> int:
    count = int()
    for user in users:
        if user.ci.upper_bound / user.speed <= default_rate:
            count += 1
    return count


def calculate_ci_stats_for_user_group(user_group: List[UserStats], vendor: Vendor,
                                      tests: Dict[str, List[TestResult]],
                                      k: int, default_rates: List[float],
                                      pure: bool,
                                      evening: bool):
    test_random_sample = flatten_tests(user_group, tests)
    users_with_ci_results = calcuate_ci_for_user_group(user_group, test_random_sample, k)
    suffix = " (evening)" if evening is True else ""
    print(f"{vendor.infra.capitalize()} users (n={len(user_group)})" + suffix)
    for def_rate in default_rates:
        defaulted_users = count_defaulted_users_by_upper_bound(users_with_ci_results, def_rate)
        print(f"""defaulted {vendor.infra.capitalize()} with default ratio of: {def_rate}:
            {defaulted_users}""" + suffix)
        print(f"{vendor.infra.capitalize()} default rate: {defaulted_users / len(user_group)}" + suffix)
        print()
    columns = [USER_NAME_HEBREW_KEY,
               USER_SPEED_PROGRAM_KEY_HEBREW,
               ISP_KEY_HEBREW,
               INFRASTRUCTURE_KEY_HEBREW,
               SAMPLE_AVERAGE_SPEED_KEY_HEBREW,
               LOWER_BOUND_KEY_HEBREW,
               UPPER_BOUND_KEY_HEBREW,
               CONFIDENCE_LEVEL_KEY_HEBREW]

    data = pd.DataFrame() \
        .from_records([u.to_dict() for u in users_with_ci_results], columns=columns) \
        .sort_values(UPPER_BOUND_KEY_HEBREW) \

    csv_no_header = data.to_csv(sep=",", columns=columns, index=False, header=False)

    ci_table_name = vendor.infra.lower() + "_ci"
    if evening is True:
        ci_table_name += "_evening"
    if pure is True:
        ci_table_name = "pure_" + ci_table_name
    print(f"copying to: '{ci_table_name}'")
    copy_csv_to_table(StringIO(csv_no_header), get_engine(), ci_table_name)

    spreadsheet_title = get_sheet_title(vendor, is_pure=pure, is_evening=evening)
    update_sheet(spreadsheet_title, data)


def extract_user_group(vendor: Vendor, users: List[UserStats], pure: bool = False):
    if pure is True:
        return [u for u in users
                if u.isp == vendor.isp
                and u.infra == vendor.infra]

    return [u for u in users
            if u.isp == vendor.isp
            or u.infra == vendor.infra]


def copy_csv_to_table(csv: StringIO, connection: psycopg2.extensions.connection, table_name: str):
    cur = connection.cursor()
    cur.copy_from(csv, table_name, sep=',')
    connection.commit()


def calc_confidence_mean_for_random_sample(k: int, default_rates: List[float], pure_vendor: bool, is_evening: bool):
    all_user_tests = get_user_tests_in_time_interval()
    if is_evening is True:
        all_user_tests = get_user_tests_in_time_interval_evening()
    all_users = []
    for user in all_user_tests:
        user_stats = UserStats(
            user_name=all_user_tests[user][0].user_name,
            speed=all_user_tests[user][0].speed,
            infra=all_user_tests[user][0].infra,
            isp=all_user_tests[user][0].isp,
        )
        all_users.append(user_stats)

    bezeq_users = extract_user_group(BEZEQ, all_users, pure=pure_vendor)
    calculate_ci_stats_for_user_group(bezeq_users, BEZEQ, all_user_tests, k, default_rates, pure_vendor, is_evening)

    hot_users = extract_user_group(HOT, all_users, pure=pure_vendor)
    calculate_ci_stats_for_user_group(hot_users, HOT, all_user_tests, k, default_rates, pure_vendor, is_evening)

    partner_users = extract_user_group(PARTNER, all_users, pure=pure_vendor)
    calculate_ci_stats_for_user_group(partner_users, PARTNER, all_user_tests, k, default_rates, pure_vendor, is_evening)


def summary_isp_or_infra_header() -> Tuple[str, str, str, str, str, str]:
    header = ("ספקית או תשתית",
               "מספר משתמשים",
               "מ. משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה",
               "מ. משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה בשעות הערב",
               "מ. משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה",
               "מ. משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה בשעות הערב")
    return header


def summary_isp_and_infra_header() -> Tuple[str, str, str, str, str, str]:
    header = ("ספקית + תשתית",
               "מספר משתמשים",
               "מ. משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה",
               "מ. משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה בשעות הערב",
               "מ. משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה",
               "מ. משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה בשעות הערב")
    return header


def create_summary_ci_tables():
    ci_data = ci_tables_to_df()

    infra_and_ci_table = create_ci_table(ci_data=ci_data, pure=True)
    infra_or_isp_ci_table = create_ci_table(ci_data=ci_data, pure=False)

    pretty_print_df(infra_and_ci_table)
    pretty_print_df(infra_or_isp_ci_table)
    print("updating summary tables...")
    update_sheet(SPREADSHEET_TITLE_SUMMARY_ISP_AND_INFRA, infra_and_ci_table)
    update_sheet(SPREADSHEET_TITLE_SUMMARY_ISP_OR_INFRA, infra_or_isp_ci_table)


def pretty_print_df(df: pd.DataFrame):
    with pd.option_context('expand_frame_repr', False,
                           'display.max_rows', None,
                           'display.max_columns', None):
        print(df)


# def create_user_performance_tables(ratio: float = 0.8, vendor_logic: str ='or'):
#     engine = get_engine()
#     cur = engine.cursor()
#     base_query = """select count(distinct "שם_משתמש") from {}
#                     where "גבול_עליון"::float >= "תכנית"::float * {};"""
#     raw_result = []
#     vendor_prefix = '' if vendor_logic == 'or' else 'pure_'
#     vendor_column = 'ספקית או תשתית' if vendor_logic == 'or' else 'ספקית + תשתית'
#     for vendor, vendor_heb in [('bezeq', 'בזק'), ('hot', 'הוט'), ('partner', 'פרטנר')]:
#         table_name = vendor_prefix + vendor + '_' + 'ci'
#         cur.execute(base_query.format(table_name, ratio))
#         above_ratio_user_count = cur.fetchall()[0][0]
#         cur.execute('select count(distinct "שם_משתמש") from {}'.format(table_name))
#         overall_user_count = cur.fetchall()[0][0]
#         raw_result.append({vendor_column: vendor_heb,
#                            "מספר משתמשים שמהירות הגלישה הממוצעת שלהם גבוהה מ-80% מהירות החבילה": above_ratio_user_count,
#                           'מספר משתמשים': overall_user_count})
#     result = pd.DataFrame(raw_result)
#     return result


def ci_tables_to_df() -> pd.DataFrame:
    engine = get_sql_alchemy_engine()
    vendor_tables = list()
    for vendor in ["bezeq", "hot", "partner"]:
        vendor_table_name = vendor + "_ci"
        vendor_table_name_evening = vendor_table_name + "_evening"
        pure_vendor_table_name = "pure_" + vendor_table_name
        pure_vendor_table_name_evening = pure_vendor_table_name + "_evening"

        vendor_table = pd.read_sql_table(vendor_table_name, engine)
        vendor_table_evening = pd.read_sql_table(vendor_table_name_evening, engine)
        pure_vendor_table = pd.read_sql_table(pure_vendor_table_name, engine)
        pure_vendor_table_evening = pd.read_sql_table(pure_vendor_table_name_evening, engine)

        vendor_table["evening"] = False
        vendor_table["group"] = vendor
        pure_vendor_table["evening"] = False
        pure_vendor_table["group"] = "pure_" + vendor
        vendor_table_evening["evening"] = True
        vendor_table_evening["group"] = vendor
        pure_vendor_table_evening["evening"] = True
        pure_vendor_table_evening["group"] = "pure_" + vendor

        for table in [vendor_table, pure_vendor_table, vendor_table_evening, pure_vendor_table_evening]:
            vendor_tables.append(table)
    all_ci_tables = pd.concat(vendor_tables, ignore_index=True)
    return all_ci_tables


def calculate_users_below_bound(ci_data: pd.DataFrame, group: str, evening: bool, bound: float) -> str:
    users = ci_data[(ci_data["group"] == group) & (ci_data["evening"] == evening)]
    users_blow_bound: int = len(users[(users[UPPER_BOUND_KEY_HEBREW.replace(" ", "_")].astype(float) /
                        users[USER_SPEED_PROGRAM_KEY_HEBREW.replace(" ", "_")].astype(float) < bound)])
    ratio = (users_blow_bound / len(users)) * 100
    return f'{users_blow_bound} ({ratio:.2f}%)'


def calculate_users_above_bound(ci_data: pd.DataFrame, group: str, evening: bool, bound: float) -> str:
    users = ci_data[(ci_data["group"] == group) & (ci_data["evening"] == evening)]
    users_above_bound: int = len(users[(users[UPPER_BOUND_KEY_HEBREW.replace(" ", "_")].astype(float) /
                        users[USER_SPEED_PROGRAM_KEY_HEBREW.replace(" ", "_")].astype(float) >= bound)])
    ratio = (users_above_bound / len(users)) * 100
    return f'{users_above_bound} ({ratio:.2f}%)'


def create_ci_table(ci_data: pd.DataFrame, pure=False) -> pd.DataFrame:
    raw_table = list()
    for vendor in ["bezeq", "hot", "partner"]:
        raw_item = dict()
        vendor = vendor if pure is False else "pure_" + vendor
        vendor_column = "ספקית או תשתית" if pure is False else "ספקית + תשתית"
        raw_item[vendor_column] = {"bezeq": "בזק", "hot": "הוט", "partner": "פרטנר"}[vendor.split("_")[-1]]
        raw_item["מספר משתמשים"] = len(ci_data[(ci_data["group"] == vendor) & (ci_data["evening"] == False)])
        raw_item["מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה"] = \
            calculate_users_below_bound(ci_data=ci_data, group=vendor, evening=False, bound=1/2)
        raw_item["מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה מחצי הבטחת החבילה בשעות הערב"] = \
            calculate_users_below_bound(ci_data=ci_data, group=vendor, evening=True, bound=1/2)
        raw_item["מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה"] = \
            calculate_users_below_bound(ci_data=ci_data, group=vendor, evening=False, bound=1/3)
        raw_item["מספר משתמשים שמהירות הגלישה הממוצעת שלהם נמוכה משליש הבטחת החבילה בשעות הערב"] = \
            calculate_users_below_bound(ci_data=ci_data, group=vendor, evening=True, bound=1/3)
        raw_item["מספר משתמשים שמהירות הגלישה הממוצעת שלהם גבוהה מ-80% הבטחת החבילה"] = \
            calculate_users_above_bound(ci_data=ci_data, group=vendor, evening=False, bound=4/5)
        raw_table.append(raw_item)

    table = pd.DataFrame.from_dict(
        raw_table)
    table = table[table.columns[::-1]] # reverse column order (hebrew - right to left)
    return table


if __name__ == "__main__":
    # Init CI tables
    ci_table_initiator = CITablesInit()
    ci_table_initiator.init_all_ci_tables()

    for pv in [True, False]:
        for iv in [True, False]:
            calc_confidence_mean_for_random_sample(k=300, default_rates=[0.5, 1/3], pure_vendor=pv, is_evening=iv)

    print("uploading ci summary tables")
    create_summary_ci_tables()
    print("ALL DONE")
