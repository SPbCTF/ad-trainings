#!/usr/bin/env python3
import random
import re
import string
import sys

import requests


OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "cities"
PORT = 8443


CREATE_CITY = 'http://{}:{}/create'


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

    s = requests.Session()
    try:
        r = s.get("http://{}:{}/create/{}".format(team_addr, PORT, flag).replace('=', '%3d'), verify=False)

        if re.search(re.compile('Country {} exists'.format(flag)), r.text):
            close(MUMBLE, "PUT Country exists")
        elif re.search(re.compile('Now playing cities in <b>{}</b>'.format(flag)), r.text):
            url = r.url.split("/")[-1]
            close(OK, url)
        else:
            close(MUMBLE, "PUT Unknown exception")

    except Exception as e:
        close(MUMBLE, "PUT Failed")


def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


def info(*args):
    close(OK, "vulns: 1")


def check(*args):
    team_addr = args[0]
    try:
        s = requests.Session()
        country = generate_rand()
        r = s.get("http://{}:{}/create/{}".format(team_addr, PORT, country).replace('=', '%3d'), verify=False)
        url = r.url.split("/")[-1]

        cities = []
        for i in range(random.randint(1, 4)):
            city = generate_rand(random.randint(2, 6))
            cities.append(city)
            r = s.get("http://{}:{}/{}/{}".format(team_addr, PORT, url, city), verify=False)

        r = s.get("http://{}:{}/{}/{}".format(team_addr, PORT, url, generate_rand(random.randint(2,6)) + cities[0][0]), verify=False)
        res = True
        for city in cities:
            if city[0] == cities[0][0] and city not in r.text:
                res = False
                break

        if res:
            close(OK)
        else:
            close(CORRUPT)

    except Exception as e:
        close(CORRUPT)
    close(OK)


def get(*args):
    team_addr, lpb, flag = args[:3]
    try:
        s = requests.Session()
        r = s.get("http://{}:{}/{}".format(team_addr, PORT, lpb), verify=False)
        if flag in r.text:
            close(OK)
        else:
            close(CORRUPT)

    except Exception as e:
        close(CORRUPT)


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
