from time import sleep

from selenium import webdriver
import os

BASE_URL = "http://127.0.0.1:7777"


USERS = ["rom","vitaly","dalia","Haza","inbaru","sheila","carmit_hot","yosef","ella","orly","dor_b","itamar","yoel","ArielG","raz_s","shay_s","michael","or_shaked","ariel_100","sharon","etl","moshe","lior","valenci","eyal","ofir","golan","lian","yosi","noam","avi","sery","gil","ron","artium","yarden","ilil","etl_home","tammy_a","ben","gilt","dor","gilad","roni","barak_200","paz","oren","david","adi_a","erez","tal_a","hafi","idan","ben_b","miras","aviram","evyatar","ziv","hamaoz","gadi","anna","gali","hila","rotem","nimrod","getzel","viki","ishay","aviad","yakov","nimrod_h","elkana","dudu","tali_l","sivan","daniel_t","dor_bd","wiezel","zion","zhalaby","meital","asaf","assif","s_golan","orit","dor_p","hod","alon_s","tamir","may","carmit","zigi","dani","omer","admin","robert","dan_florentin","yuval","ofer","brody","alon","shay","tali","eli_d","segal","dov","raz","Sery","David","omry","ameer","rachel","admin_200","fadrok","stephan","zvi","shaked","yochi","hila_s","ariel","dana","khalifa","tankus","escape_room","idang","daniel","noam_b","barak","rina"]


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
        browser.get(BASE_URL + f"/dashboard/7?id={user}")
        sleep(10)
        browser.get_screenshot_as_file(f"user_ids/screenshot_{user}.png")


if __name__ == "__main__":
    driver = webdriver.Chrome(executable_path="./chromedriver")
    driver.get(BASE_URL)
    driver.find_element_by_tag_name("html")
    authenticate_metabase(driver)
    sleep(1)
    iterate_user_ids(driver, USERS)
