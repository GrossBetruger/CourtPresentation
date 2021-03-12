import os
import autopy
import pyautogui

from enum import Enum
from abc import ABC
from collections import OrderedDict
from time import sleep
from typing import Optional, List, Tuple
from numpy import mean
from pyautogui import Size
from selenium import webdriver
from UserIdSnapshotter.snapshotter import BASE_URL
from pathlib import Path

SLEEP_KEY = "sleep"

TEXT_KEY = "text"

HEAVY_SLEEP = 35  # for question that make the DB sweat

DEFAULT_SLEEP = 2

MEDIUM_SLEEP = 10


class PlotType(Enum):
    Oversell = "Oversell"
    CapacityOfService = "Capacity of Service"


class PlotPositions(ABC):
    up: int
    down: int
    left: int
    right: int
    mouse_drag_positions: List[Tuple[int, int]] = NotImplemented

    def on_plot_point(self) -> Tuple[int, int]:
        x = mean([self.left, self.right])
        y = mean([self.up, self.down])
        return x, y


class PieFullScreenPositions1920x1080(PlotPositions):
    def __init__(self):
        self.up = 355
        self.down = 923
        self.left = 133
        self.right = 1245
        self.mouse_drag_positions = [
            (self.left, self.up),
            (self.right, self.up),
            (self.right, self.down)
        ]
        # self.mouse_drag_positions = [
        #                 (133, 355),
        #                 (1245, 355),
        #                 (1245, 923),
        #             ]
        # self.on_plot_point = (776, 490)


class OversellPieHalfScreenPositions1920x1080(PlotPositions):
    def __init__(self):
        self.up = 660
        self.down = 1018
        self.left = 230
        self.right = 1148
        self.mouse_drag_positions = [
                        (self.left, self.up),
                        (self.right, self.up),
                        (self.right, self.down)
                    ]
        # self.on_plot_point = (776, 490)


class CapacityOfServicePieHalfScreenPositions1920x1080(PlotPositions):
    def __init__(self):
        self.up = 488
        self.down = 1018
        self.left = 261
        self.right = 1232
        self.mouse_drag_positions = [
            (self.left, self.up),
            (self.right, self.up),
            (self.right, self.down)
        ]
        # self.on_plot_point = (776, 490)


class WebsiteComparisonScreenPositions1920x1080(PlotPositions):
    def __init__(self):
        self.up = 490
        self.down = 1028
        self.left = 6
        self.right = 1913
        self.mouse_drag_positions = [
            (self.left, self.up),
            (self.right, self.up),
            (self.right, self.down)
        ]
        # self.on_plot_point = (776, 490)


OVERSELL_QUESTIONS = {
    "מכירת יתר":
        {
            # 43: {TEXT_KEY: "משתמשים במכירת יתר תכנית 100 מגה-ביט, חיבור קווי", SLEEP_KEY: DEFAULT_SLEEP},
            # 44: {TEXT_KEY: "משתמשים במכירת יתר תכנית 100 מגה-ביט, חיבור קווי - שעות העומס", SLEEP_KEY: HEAVY_SLEEP},
            # 46: {TEXT_KEY: "משתמשים במכירת יתר תכנית 100 מגה-ביט, חיבור קווי - שרת מטמון בישראל", SLEEP_KEY: DEFAULT_SLEEP},
            # 45: {TEXT_KEY: "משתמשים במכירת יתר תכנית 100 מגה-ביט, חיבור קווי - שרת מטמון בישראל שעות העומס", SLEEP_KEY: HEAVY_SLEEP},
            # 47: {TEXT_KEY: "משתמשים במכירת יתר תכנית 40 מגה-ביט, חיבור קווי", SLEEP_KEY: DEFAULT_SLEEP},
            # 48: {TEXT_KEY: "משתמשים במכירת יתר תכנית 40 מגה-ביט, חיבור קווי - שעות העומס", SLEEP_KEY: HEAVY_SLEEP},
            # 49: {TEXT_KEY: "משתמשים במכירת יתר תכנית 200 מגה-ביט, חיבור קווי", SLEEP_KEY: DEFAULT_SLEEP},
            # 50: {TEXT_KEY: "משתמשים במכירת יתר תכנית 200 מגה-ביט, חיבור קווי שעות העומס", SLEEP_KEY: MEDIUM_SLEEP},
            # 51: {TEXT_KEY: "משתמשים במכירת יתר תכנית 200 מגה-ביט, חיבור קווי, שרת מטמון בישראל", SLEEP_KEY: MEDIUM_SLEEP},
            # 52: {TEXT_KEY: "משתמשים במכירת יתר תכנית 200 מגה-ביט, חיבור קווי, שרת מטמון בישראל שעות העומס", SLEEP_KEY: DEFAULT_SLEEP},
            53: {TEXT_KEY: "משתמשי פרטנר (כל התכניות) במכירת יתר, חיבור קווי", SLEEP_KEY: MEDIUM_SLEEP},
            # 54: {TEXT_KEY: "משתמשי פרטנר (כל התכניות) במכירת יתר, חיבור קווי, שעות העומס", SLEEP_KEY: 80},
            # 55: {TEXT_KEY: "משתמשי בזק, תכנית 100 מגה-ביט במכירת יתר, חיבור קווי", SLEEP_KEY: MEDIUM_SLEEP + 4},
            67: {TEXT_KEY: "משתמשי בזק (כל התכניות) במכירת יתר, חיבור קווי", SLEEP_KEY: MEDIUM_SLEEP},
        },
}

CAPACITY_OF_SERVICE_QUESTIONS = {
    "נפח שירות":
        {
            # 56: {TEXT_KEY: "נפח שירות חבילת 100 מגה-ביט דגימות בחיבור קווי - כל השעות", SLEEP_KEY: MEDIUM_SLEEP},
            # 57: {TEXT_KEY: " נפח שירות חבילת 100 מגה-ביט דגימות בחיבור קווי - שעות העומס", SLEEP_KEY: HEAVY_SLEEP},
            # 58: {TEXT_KEY: "נפח שירות חבילת 40 מגה-ביט דגימות בחיבור קווי - כל השעות", SLEEP_KEY: DEFAULT_SLEEP},
            # 59: {TEXT_KEY: "נפח שירות חבילת 40 מגה-ביט חיבור קווי - שעות העומס", SLEEP_KEY: HEAVY_SLEEP},
            # 60: {TEXT_KEY: "נפח שירות חבילת 100 מגה-ביט דגימות בחיבור קווי שרת מטמון בישראל - כל השעות", SLEEP_KEY: DEFAULT_SLEEP},
            # 61: {TEXT_KEY: "נפח שירות חבילת 100 מגה-ביט חיבור קווי שרת מטמון בישראל - שעות העומס", SLEEP_KEY: DEFAULT_SLEEP},
            # 62: {TEXT_KEY: "נפח שירות חבילת 40 מגה-ביט חיבור קווי שרת מטמון בישראל - כל השעות", SLEEP_KEY: DEFAULT_SLEEP},
            # 63: {TEXT_KEY: "נפח שירות חבילת 40 מגה-ביט חיבור קווי שרת מטמון בישראל - שעות העומס", SLEEP_KEY: DEFAULT_SLEEP},
        },
}

WEBSITE_COMPARISON_QUESTIONS = {
    "השוואת אתרי בדיקת מהירות ברשת":
        {
            # 64: {TEXT_KEY: "השוואת אתרי בדיקת מהירות אינטרנט למדידה בפועל - הורדה מכל המקורות", SLEEP_KEY: 15},
            # 65: {TEXT_KEY: "השוואת אתרי בדיקת מהירות אינטרנט למדידה בפועל - הורדה מאתרים", SLEEP_KEY: 15},
            # 66: {TEXT_KEY: "השוואת אתרי בדיקת מהירות אינטרנט למדידה בפועל - הורדה משרת מטמון בישראל", SLEEP_KEY: 15},
        },
}

OVERSELL_QUESTIONS = OrderedDict(OVERSELL_QUESTIONS)


class ResolutionNotSupportedException(Exception):
    pass


def resolution_to_positions(size: Size, plot_type: PlotType) -> Optional[PlotPositions]:

    if size.width == 1920 and size.height == 1080:

        if plot_type is PlotType.Oversell:
            return OversellPieHalfScreenPositions1920x1080()

        elif plot_type is PlotType.CapacityOfService:
            return CapacityOfServicePieHalfScreenPositions1920x1080()


def authenticate_metabase(browser):
    user, pwd = browser.find_elements_by_tag_name("input")
    user.send_keys("israel_testers@gmail.com")
    pwd.send_keys("notasecret1")
    browser.find_element_by_tag_name("button").click()


def jump_to_question(driver: webdriver.Chrome, question_code: int):
    driver.get(BASE_URL + f"/question/{question_code}")


def take_question_snapshot(plot_positions: PlotPositions):
    hover_point = plot_positions.on_plot_point()
    # pyautogui.moveTo(hover_point)
    autopy.mouse.smooth_move(*hover_point)
    points = plot_positions.mouse_drag_positions
    first_position = points[0]
    later_positions = points[1:]
    pyautogui.moveTo(x=first_position[0], y=first_position[1])
    pyautogui.keyDown("shift")
    pyautogui.keyDown("prtscr")
    pyautogui.keyUp("prtscr")
    pyautogui.keyUp("shift")
    pyautogui.mouseDown()
    pyautogui.sleep(1)
    for x, y in later_positions:
        pyautogui.moveTo(x, y)
    pyautogui.mouseUp()


def open_editor(driver: webdriver.Chrome):
    for elem in driver.find_elements_by_class_name("mr1"):
        if elem.text == "OPEN EDITOR":
            elem.click()


def handle_question(topic: str, question: int, positions: PlotPositions, sleepy_time: int, text: str):
    topic_path = Path("question_snapshots") / Path(topic)
    if not os.path.exists(topic_path):
        os.makedirs(topic_path)

    jump_to_question(driver, question)
    # sleepy_time = OVERSELL_QUESTIONS[topic][question][SLEEP_KEY]
    sleep(sleepy_time)

    open_editor(driver)

    take_question_snapshot(positions)
    sleep(0.5)  # wait for screenshot to be created
    # text = OVERSELL_QUESTIONS[topic][question][TEXT_KEY]
    print(f"took snapshot for question: '{text}' from topic '{topic}'")
    linux_screenshot_path = os.path.expanduser("~/Pictures")
    linux_screenshots = os.listdir(os.path.expanduser("~/Pictures"))
    linux_screenshots = [Path(linux_screenshot_path) / Path(screenshot)
                         for screenshot in linux_screenshots]
    latest_screenshot = Path(max(linux_screenshots, key=os.path.getctime))
    new_path = topic_path / Path(text + f".png")
    # print("old path:", latest_screenshot)
    # print("new path:", new_path)
    os.rename(latest_screenshot, new_path)


def record_positions():
    while True:
        print(pyautogui.position())
        sleep(1)


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--kiosk")
    driver = webdriver.Chrome(options=options, executable_path="./chromedriver")
    driver.get(BASE_URL)
    driver.find_element_by_tag_name("html")

    authenticate_metabase(driver)
    sleep(2)

    oversell_positions = resolution_to_positions(pyautogui.size(), PlotType.Oversell)
    if oversell_positions is None:
        raise ResolutionNotSupportedException(f"resolution: {pyautogui.size()} "
                                              f"is not supported,"
                                              f" please add it to the 'resolution_to_positions' function")

    capacity_positions = resolution_to_positions(pyautogui.size(), PlotType.CapacityOfService)
    if capacity_positions is None:
        raise ResolutionNotSupportedException(f"resolution: {pyautogui.size()} "
                                              f"is not supported,"
                                              f" please add it to the 'resolution_to_positions' function")

    for topic in OVERSELL_QUESTIONS:
        for question in OVERSELL_QUESTIONS[topic]:
            sleep_time = OVERSELL_QUESTIONS[topic][question][SLEEP_KEY]
            title = OVERSELL_QUESTIONS[topic][question][TEXT_KEY]
            handle_question(topic, question, oversell_positions, sleep_time, title)

    for topic in CAPACITY_OF_SERVICE_QUESTIONS:
        for question in CAPACITY_OF_SERVICE_QUESTIONS[topic]:
                sleep_time = CAPACITY_OF_SERVICE_QUESTIONS[topic][question][SLEEP_KEY]
                title = CAPACITY_OF_SERVICE_QUESTIONS[topic][question][TEXT_KEY]
                handle_question(topic, question, capacity_positions, sleep_time, title)

    website_comparison_plot_positions = WebsiteComparisonScreenPositions1920x1080()
    for topic in WEBSITE_COMPARISON_QUESTIONS:
        for question in WEBSITE_COMPARISON_QUESTIONS[topic]:
            sleep_time = WEBSITE_COMPARISON_QUESTIONS[topic][question][SLEEP_KEY]
            title = WEBSITE_COMPARISON_QUESTIONS[topic][question][TEXT_KEY]
            handle_question(topic, question, website_comparison_plot_positions, sleep_time, title)

    sleep(1)
    driver.close()
