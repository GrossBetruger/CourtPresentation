from time import sleep
from typing import Optional

import pyautogui
from pyautogui import Size
from selenium import webdriver

from UserIdSnapshotter.snapshotter import BASE_URL


PLOT_AT_BUTTOM_OF_SCREEN_COORDS = [
    (224, 685),
    (1126, 685),
    (1126, 1018)
]

PLOT_AT_QUESTION_OPENING = [
    (133, 345),
    (1253, 345),
    (1253, 933),
]


class ResolutionNotSupportedException(Exception):
    pass


def resolution_to_positions(size: Size) -> Optional[list]:
    if size.width == 1920 and size.height == 1080:
        return PLOT_AT_QUESTION_OPENING


def authenticate_metabase(browser):
    user, pwd = browser.find_elements_by_tag_name("input")
    user.send_keys("israel_testers@gmail.com")
    pwd.send_keys("notasecret1")
    browser.find_element_by_tag_name("button").click()


def jump_to_question(driver: webdriver.Chrome, question_code: int):
    driver.get(BASE_URL + f"/question/{question_code}")


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--kiosk")
    driver = webdriver.Chrome(options=options, executable_path="./chromedriver")
    driver.get(BASE_URL)
    driver.find_element_by_tag_name("html")

    authenticate_metabase(driver)
    sleep(1)
    jump_to_question(driver, 43)
    sleep(1)

    points = resolution_to_positions(pyautogui.size())
    if points is None:
        raise ResolutionNotSupportedException(f"resolution: {pyautogui.size()} "
                                              f"is not supported,"
                                              f" please add it to the 'resolution_to_positions' function")

    first_position = points[0]
    print(first_position)
    later_positions = points[1:]
    print(later_positions)
    pyautogui.moveTo(x=first_position[0], y=first_position[1])
    pyautogui.keyDown("shift")
    pyautogui.keyDown("prtscr")
    pyautogui.keyUp("prtscr")
    pyautogui.keyUp("shift")
    pyautogui.mouseDown()
    for x, y in later_positions:
        pyautogui.moveTo(x, y)
    pyautogui.mouseUp()

