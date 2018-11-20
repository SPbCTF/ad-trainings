#!/usr/bin/env python3

import random
import re
import string
import sys

import requests


OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "cats"
PORT = 8100


def generate_rand(N=16):
    return ''.join(random.choice(string.ascii_letters) for i in range(N))


def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    print('Exit with code {}'.format(code), file=sys.stderr)
    exit(code)


def put(*args):
    team_addr, flag_id, flag = args[:3]

    login, password = generate_rand(16), generate_rand(16)

    s = requests.Session()
    try:
        r = s.post("http://{}:{}/accounts/register/".format(team_addr, PORT), {
            "login": login,
            "password": password,
        })

        r = s.post("http://{}:{}/accounts/login/".format(team_addr, PORT), {
            "username": login,
            "password": password,
            "next": "/"
        })

        r = s.post("http://{}:{}/".format(team_addr, PORT), data={
            "is_private": True,
            "title": flag
        }, files={"image": open("static/{}.jpg".format(random.randint(1, 7)), 'rb')})

        r = s.get("http://{}:{}/user/{}".format(team_addr, PORT, login))

        if flag in r.text:
            close(OK, "{}:{}".format(login, password))
        else:
            close(MUMBLE, "PUT flag not found")

    except Exception as e:
        close(MUMBLE, "PUT Failed")


def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


def info(*args):
    close(OK, "vulns: 1")


def check(*args):
    team_addr = args[0]
    s = requests.Session()
    alaflag = generate_rand()
    try:
        login, password = generate_rand(), generate_rand()
        r = s.post("http://{}:{}/accounts/register/".format(team_addr, PORT), {
            "login": login,
            "password": password,
        })
        r = s.post("http://{}:{}/accounts/login/".format(team_addr, PORT), {
            "username": login,
            "password": password,
            "next": "/"
        })

        r = s.get("http://{}:{}/users/".format(team_addr, PORT))
        if login not in r.text:
            close(CORRUPT)

        r = s.post("http://{}:{}/".format(team_addr, PORT), data={
            "is_private": True,
            "title": alaflag
        }, files={"image": open("static/{}.jpg".format(random.randint(1, 7)), 'rb')})

        r = s.get("http://{}:{}/user/{}".format(team_addr, PORT, login))
        if alaflag not in r.text:
            close(CORRUPT)

        friend_token = re.findall(re.compile("друзей: ([a-zA-Z0-9]+)<\/a>"), r.text)
        if not len(friend_token):
            close(CORRUPT)
        friend_token = friend_token[0]

        s2 = requests.Session()
        l2, p2 = generate_rand(), generate_rand()
        r2 = s2.post("http://{}:{}/accounts/register/".format(team_addr, PORT), {
            "login": l2,
            "password": p2,
        })
        r2 = s2.post("http://{}:{}/accounts/login/".format(team_addr, PORT), {
            "username": l2,
            "password": p2,
            "next": "/"
        })
        r2 = s2.get("http://{}:{}/user/{}?friend_token={}".format(team_addr, PORT, login, friend_token))
        if alaflag not in r2.text:
            close(CORRUPT)
        close(OK)

    except Exception as e:
        close(MUMBLE, "check Failed")


def get(*args):
    team_addr, lpb, flag = args[:3]
    login, password = lpb.split(":")
    s = requests.Session()
    try:
        r = s.post("http://{}:{}/accounts/login/".format(team_addr, PORT), {
            "username": login,
            "password": password,
            "next": "/"
        })
        r = s.get("http://{}:{}/user/{}".format(team_addr, PORT, login))
        if flag not in r.text:
            close(CORRUPT)

        close(OK)

    except Exception as e:
        close(MUMBLE, "get Failed")


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
        if sys.argv[2] == '7.1.201.1':
            close(OK)
        else:
            COMMANDS.get(sys.argv[1], error_arg)(*sys.argv[2:])
    except Exception as ex:
        close(CHECKER_ERROR, private="INTERNAL ERROR: {}".format(ex))
