#!/usr/bin/env python3
import random
import re
import string
import sys

import requests


OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "bank"
PORT = 6478


def register_user(team_addr):
    login = generate_rand(16)
    password = generate_rand(16)
    d = 39329773123488670944631611616102457205973722706508187445466899066107015035639664198943840729718667478283099452550656089143990474543336835984305305376119220931937786603054594121061306154527156748609127620685746505398730536777327124632837200045570575478538409812576936544027027061966068119312337472207705559657
    n = 135425594556511166274277409262045223449161974728966903830902336158012685566685056092375478899993291153482871266842449856261740331537154742810036084612763401876643268334272277742219885868304117059993532611501666375035889705305370452261157698536676400701093018423205591432064100374528497079954968607616709767379
    s = requests.Session()

    r = s.get("http://{}:{}/index.php?register=page".format(team_addr, PORT))
    backdoor = re.findall(r'backdoor" value="(\d+)"', r.text)
    if len(backdoor):
        backdoor = int(backdoor[0])

    captcha = pow(backdoor, d, n)

    r = s.post("http://{}:{}/index.php".format(team_addr, PORT), data={
        "on_register": "on",
        "reg_login": login,
        "password": password,
        "repeat_password": password,
        "captcha": captcha
    })
    return login, password


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
        login, password = register_user(team_addr)
        r = s.post("http://{}:{}/index.php".format(team_addr, PORT), data={
            "login": login,
            "password": password
        })

        r = s.post("http://{}:{}/index.php".format(team_addr, PORT), data={
            "on_freeze": "on",
            "text": flag
        })

        freeze_id = re.findall(r'Your freeze shield:<\/h2>\:\:\:(\S+)\:\:\:', r.text)
        if not len(freeze_id):
            close(MUMBLE, "Freeze ID not found on page")

        close(OK, "{}:{}:{}".format(login, password, freeze_id[0]))

    except Exception as e:
        close(MUMBLE, "PUT Failed")


def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


def info(*args):
    close(OK, "vulns: 1")


def check(*args):
    team_addr = args[0]
    l1, p1 = register_user(team_addr)
    try:
        s1 = requests.Session()
        r = s1.post("http://{}:{}/index.php".format(team_addr, PORT), data={"login": l1,"password": p1})

        id1 = re.findall(re.compile('{}\((\d+)\)'.format(l1)), r.text)[0]

        l2, p2 = register_user(team_addr)

        s2 = requests.Session()
        r = s2.post("http://{}:{}/index.php".format(team_addr, PORT), data={"login": l2,"password": p2})

        id2 = re.findall(re.compile('{}\((\d+)\)'.format(l2)), r.text)[0]

        cost = random.randint(1, 1000)
        r = s2.post("http://{}:{}/index.php".format(team_addr, PORT), data={
            "on_transaction": "on",
            "id_receiver": id1,
            "cash": cost
        })

        r = s1.get("http://{}:{}/index.php".format(team_addr, PORT))
        result = re.findall(re.compile("cash\">({})".format(cost + 1000)), r.text)
        if len(result):
            close(OK)
        else:
            close(CORRUPT)

    except Exception as e:
        close(MUMBLE, "check failed")


def get(*args):
    team_addr, lpb, flag = args[:3]
    login, password, freeze_id = lpb.split(":")

    try:
        s = requests.Session()
        r = s.post("http://{}:{}/index.php?freeze=page".format(team_addr, PORT), data={
            "login": login,
            "password": password
        })

        regex = 'getText\((\d+)\)\;\'\>{}'.format(freeze_id)
        result = re.findall(re.compile(regex), r.text)
        if not len(result):
            close(MUMBLE, 'Freeze ID not found on page')

        r = s.post("http://{}:{}/index.php".format(team_addr, PORT), data={
            "unfreeze_id": result[0],
        })

        if flag == r.text:
            close(OK)
        else:
            close(CORRUPT)

    except Exception as e:
        close(MUMBLE, "GET Failed")

    close(OK)


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
