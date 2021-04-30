import utils

from time import sleep
from selenium import webdriver


BASE_URL = "http://127.0.0.1:7777"

DASHBOARD_NUM = 1

USER_VAR_NAME = "id"


def read_users():
    engine = utils.get_engine()
    cur = engine.cursor()
    cur.execute('''
        select distinct
                        "יוזר"
        from testers;
    ''')
    names = []
    for row in cur.fetchall():
        names.append(row[0])
    return names


USERS = read_users()


def read_password():
    return "notasecret1"

    # with open(os.path.expanduser("~/.metapass")) as f:
    #     return f.read().strip()


def read_user():
    return "israel_testers@gmail.com"

    # with open(os.path.expanduser("~/.metausr")) as f:
    #     return f.read().strip()


def authenticate_metabase(browser):
    user, pwd = browser.find_elements_by_tag_name("input")
    user.send_keys(read_user())
    pwd.send_keys(read_password())
    browser.find_element_by_tag_name("button").click()


def iterate_user_ids(browser, users):
    for user in users:
        browser.get(BASE_URL + f"/dashboard/{DASHBOARD_NUM}?{USER_VAR_NAME}={user}")
        sleep(3)
        _, _, full_screen, _ = browser.find_elements_by_class_name("Header-button")
        full_screen.click()
        sleep(1.8)
        browser.get_screenshot_as_file(f"user_ids/screenshot_{user}.png")


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--kiosk")
    driver = webdriver.Chrome(options=options, executable_path="./chromedriver")
    driver.get(BASE_URL)
    driver.find_element_by_tag_name("html")

    authenticate_metabase(driver)
    sleep(1)

    iterate_user_ids(driver, USERS)
