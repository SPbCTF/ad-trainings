#!/usr/bin/env python3

import random
import re
import string
import sys

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "blogger"
PORT = 8090


def generate_rand(N=16):
    return ''.join(random.choice(string.ascii_letters) for i in range(N))


def generate_random_paragraph():
    message = generate_rand()
    tag = random.choice(['b', 'i', 'span', 'p', 'a', 'u'])
    return "<{}>{}</{}>".format(tag, message, tag)


def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    print('Exit with code {}'.format(code), file=sys.stderr)
    exit(code)


def put(*args):
    team_addr, flag_id, flag = args[:3]

    try:
        driver = webdriver.PhantomJS(executable_path='./phantomjs')
        driver.set_window_size(1024, 768)
        driver.get('http://{}:{}/site/enter'.format(team_addr, PORT))
        sbtn = driver.find_element_by_id('identifier')

        userid = generate_rand()
        sbtn.send_keys(userid)
        sbtn.send_keys(Keys.ENTER)

        wait = WebDriverWait(driver, 10)
        wait.until(lambda driver: "Hello stranger!" in driver.page_source)

        driver.get('http://{}:{}/notes'.format(team_addr, PORT))
        if userid not in driver.page_source:
            close(MUMBLE, "Login failed")

        sbtn = driver.find_element_by_id('noteform-txt')
        sbtn.send_keys(flag)

        button = driver.find_element_by_name("notes-button")
        button.click()

        wait = WebDriverWait(driver, 10)
        wait.until(lambda driver: ":{}".format(flag) in driver.page_source)

        if flag not in driver.page_source:
            close(MUMBLE, "Flag not saved")

        close(OK, userid)

    except Exception as e:
        close(MUMBLE, "put Failed", str(e))


def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


def info(*args):
    close(OK, "vulns: 1")


def check(*args):
    team_addr = args[0]
    try:
        driver = webdriver.PhantomJS(executable_path='./phantomjs')
        driver.set_window_size(1024, 768)
        driver.get('http://{}:{}/'.format(team_addr, PORT))
        sbtn = driver.find_element_by_id('comments-txt')

        message = generate_random_paragraph()
        sbtn.send_keys(message)
        driver.find_element_by_id('send-button').click()

        wait = WebDriverWait(driver, 10)
        wait.until(lambda driver: message in driver.page_source)

        if message in driver.page_source:
            close(OK)
        else:
            close(CORRUPT, "Message not found in the chat")

    except Exception as e:
        close(MUMBLE, "check Failed", str(e))


def get(*args):
    team_addr, userid, flag = args[:3]
    try:
        driver = webdriver.PhantomJS(executable_path='./phantomjs')
        driver.set_window_size(1024, 768)
        driver.get('http://{}:{}/site/enter'.format(team_addr, PORT))
        sbtn = driver.find_element_by_id('identifier')

        sbtn.send_keys(userid)
        sbtn.send_keys(Keys.ENTER)

        wait = WebDriverWait(driver, 10)
        wait.until(lambda driver: "Hello stranger!" in driver.page_source)

        driver.get('http://{}:{}/notes'.format(team_addr, PORT))
        if flag not in driver.page_source:
            close(CORRUPT, "Flag not found")

        close(OK)

    except Exception as e:
        close(MUMBLE, "get Failed", str(e))


def init(*args):
    close(OK)


COMMANDS = {
    'put': put,
    'check': check,
    'get': get,
    'info': info,
    'init': init
}


if __name__ == '__main__':
    try:
        COMMANDS.get(sys.argv[1], error_arg)(*sys.argv[2:])
    except Exception as ex:
        close(CHECKER_ERROR, private="INTERNAL ERROR: {}".format(ex))
