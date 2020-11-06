from time import sleep

from selenium import webdriver
import os

from selenium.webdriver.common.keys import Keys

BASE_URL = "http://127.0.0.1:7777"

DASHBOARD_NUM = 34

USER_VAR_NAME = "user_name"

USERS = ["omry","sivan","lior","miras","idan","dov","sery","erez","dalia","hila_s","dor_bd","inbaru","omer","evyatar","lian","noam_b","tali","ameer","stephan","daniel","Sery","artium","raz","David","michael","Haza","daniel_t","admin","zion","paz","ilil","barak_200","rachel","hod","rom","eyal","david","assif","dana","admin_200","eli_d","ella","viki","ofir","segal","roni","nimrod","gil","zvi","tali_l","s_golan","aviram","etl","itamar","hafi","or_shaked","yoel","yarden","orit","raz_s","nimrod_h","dor","fadrok","yakov","ben_b","rina","hamaoz","tankus","getzel","tamir","barak","aviad","asaf","dor_p","rotem","shay","carmit","gadi","dan_florentin","wiezel","ArielG","etl_home","meital","oren","golan","ziv","dani","ariel","tal_a","anna","zhalaby","ofer","khalifa","yosi","ron","escape_room","vitaly","sharon","dor_b","ishay","ben","gilt","zigi","alon","valenci","idang","avi","yochi","gali","shaked","elkana","yuval","carmit_hot","ariel_100","alon_s","gilad","yosef","hila","moshe","may","dudu","sheila","shay_s"]



def read_password():
    with open(os.path.expanduser("~/.metapass")) as f:
        return f.read().strip()


def read_user():
    with open(os.path.expanduser("~/.metausr")) as f:
        return f.read().strip()


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
