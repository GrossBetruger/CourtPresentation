import os
import pyautogui


from abc import ABC
from collections import OrderedDict
from time import sleep
from typing import Optional, List, Tuple
from pyautogui import Size
from selenium import webdriver
from UserIdSnapshotter.snapshotter import BASE_URL
from pathlib import Path

SLEEP_KEY = "sleep"

TEXT_KEY = "text"

HEAVY_SLEEP = 35  # for question that make the DB sweat

DEFAULT_SLEEP = 2

MEDIUM_SLEEP = 6


class PlotPositions(ABC):
    mouse_drag_positions: List[Tuple[int, int]] = NotImplemented
    on_plot_point: Optional[Tuple[int, int]] = None


class PieFullScreenPositions1920x1080(PlotPositions):
    def __init__(self):
        self.mouse_drag_positions = [
                        (133, 355),
                        (1245, 355),
                        (1245, 923),
                    ]
        self.on_plot_point = (776, 490)


class PieHalfScreenPositions1920x1080(PlotPositions):
    def __init__(self):
        up = 660
        down = 1018
        left = 230
        right = 1148
        self.mouse_drag_positions = [
                        (left, up),
                        (right, up),
                        (right, down)
                    ]
        self.on_plot_point = (776, 490)


QUESTIONS = {
    "מכירת יתר":
        {
            43: {TEXT_KEY: "משתמשים במכירת יתר תכנית 100 מגה-ביט, חיבור קווי", SLEEP_KEY: DEFAULT_SLEEP},
            44: {TEXT_KEY: "משתמשים במכירת יתר תכנית 100 מגה-ביט, חיבור קווי - שעות העומס", SLEEP_KEY: HEAVY_SLEEP},
            46: {TEXT_KEY: "משתמשים במכירת יתר תכנית 100 מגה-ביט, חיבור קווי - שרת מטמון בישראל", SLEEP_KEY: DEFAULT_SLEEP},
            45: {TEXT_KEY: "משתמשים במכירת יתר תכנית 100 מגה-ביט, חיבור קווי - שרת מטמון בישראל שעות העומס", SLEEP_KEY: HEAVY_SLEEP},
            47: {TEXT_KEY: "משתמשים במכירת יתר תכנית 40 מגה-ביט, חיבור קווי", SLEEP_KEY: DEFAULT_SLEEP},
            48: {TEXT_KEY: "משתמשים במכירת יתר תכנית 40 מגה-ביט, חיבור קווי - שעות העומס", SLEEP_KEY: HEAVY_SLEEP},
            49: {TEXT_KEY: "משתמשים במכירת יתר תכנית 200 מגה-ביט, חיבור קווי", SLEEP_KEY: DEFAULT_SLEEP},
            50: {TEXT_KEY: "משתמשים במכירת יתר תכנית 200 מגה-ביט, חיבור קווי שעות העומס", SLEEP_KEY: MEDIUM_SLEEP},
            51: {TEXT_KEY: "משתמשים במכירת יתר תכנית 200 מגה-ביט, חיבור קווי, שרת מטמון בישראל", SLEEP_KEY: MEDIUM_SLEEP},
            52: {TEXT_KEY: "משתמשים במכירת יתר תכנית 200 מגה-ביט, חיבור קווי, שרת מטמון בישראל שעות העומס", SLEEP_KEY: DEFAULT_SLEEP},
            53: {TEXT_KEY: "משתמשי פרטנר (כל התכניות) במכירת יתר, חיבור קווי", SLEEP_KEY: DEFAULT_SLEEP},
            54: {TEXT_KEY: "משתמשי פרטנר (כל התכניות) במכירת יתר, חיבור קווי, שעות העומס", SLEEP_KEY: 80},
            55: {TEXT_KEY: "משתמשי בזק, תכנית 100 מגה-ביט במכירת יתר, חיבור קווי", SLEEP_KEY: MEDIUM_SLEEP},
        },
}

QUESTIONS = OrderedDict(QUESTIONS)


class ResolutionNotSupportedException(Exception):
    pass


def resolution_to_positions(size: Size) -> Optional[PlotPositions]:
    if size.width == 1920 and size.height == 1080:
        return PieHalfScreenPositions1920x1080()


def authenticate_metabase(browser):
    user, pwd = browser.find_elements_by_tag_name("input")
    user.send_keys("israel_testers@gmail.com")
    pwd.send_keys("notasecret1")
    browser.find_element_by_tag_name("button").click()


def jump_to_question(driver: webdriver.Chrome, question_code: int):
    driver.get(BASE_URL + f"/question/{question_code}")


def take_question_snapshot(plot_positions: PlotPositions):
    hover_point = plot_positions.on_plot_point
    pyautogui.moveTo(hover_point)

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


def handle_question(topic: str, question: int):
    topic_path = Path("question_snapshots") / Path(topic)
    if not os.path.exists(topic_path):
        os.makedirs(topic_path)

    jump_to_question(driver, question)
    sleepy_time = QUESTIONS[topic][question][SLEEP_KEY]
    sleep(sleepy_time)
    positions = resolution_to_positions(pyautogui.size())
    if positions is None:
        raise ResolutionNotSupportedException(f"resolution: {pyautogui.size()} "
                                              f"is not supported,"
                                              f" please add it to the 'resolution_to_positions' function")

    open_editor(driver)

    take_question_snapshot(positions)
    sleep(0.5)  # wait for screenshot to be created
    text = QUESTIONS[topic][question][TEXT_KEY]
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
        sleep(0.5)


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--kiosk")
    driver = webdriver.Chrome(options=options, executable_path="./chromedriver")
    driver.get(BASE_URL)
    driver.find_element_by_tag_name("html")

    authenticate_metabase(driver)
    sleep(2)

    for topic in QUESTIONS:
        for question in QUESTIONS[topic]:
            handle_question(topic, question)

    sleep(1)
    driver.close()
