#!/usr/bin/env python3

import hashlib
import json
import random
import re
import string

import numpy as np
import sys
from faker import Faker
from requests import session

fake = Faker()

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "flagification"
PORT = 2800


def generate_rand(N=16):
    return ''.join(random.choice(string.ascii_letters) for i in range(N))


def generate_flag():
    return '%031X=' % random.randrange(16**31)


def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    print('Exit with code {}'.format(code), file=sys.stderr)
    exit(code)


def bruteforce_token(token):
    answer = 1
    while True:
        if hashlib.md5("{}{}".format(token, answer).encode()).hexdigest().startswith('000'):
            return answer

        answer += 1


def make_clustering_request(token, flag):
    samples_count = random.randint(30, 40)
    features_count = random.randint(2, 4)
    samples = np.random.randint(low=1, high=35, size=(samples_count, features_count))

    data = {
        'samples': samples_count,
        'features': features_count,
        'clusters': random.randint(3, 8),
        'pow': bruteforce_token(token),
        'experiment': flag
    }

    for i, feature_vector in enumerate(samples):
        for j, feature in enumerate(feature_vector):
            data["{}_{}".format(i, j)] = feature

    return data


def clustering(team_addr, flag):
    s = session()
    email, password = fake.email(), generate_rand()
    s.post('http://{}:{}/registration'.format(team_addr, PORT), data={'email': email,'password': password})
    res = s.get('http://{}:{}/clustering'.format(team_addr, PORT))
    token = re.findall(r'name="token" value="(\d+)"', res.text)
    if not len(token):
        close(MUMBLE, 'Token not found')

    experiments = set(re.findall(r'/clustering/(\S+?)">', res.text))
    res = s.post('http://{}:{}/clustering'.format(team_addr, PORT), data=make_clustering_request(token[0], flag))
    new_experiments = set(re.findall(r'/clustering/(\S+?)">', res.text))

    if len(new_experiments) != len(experiments) + 1:
        close(MUMBLE, 'Experiment not created', 'length mismatched {} and {}'.format(len(new_experiments), len(experiments)))

    exp = new_experiments - experiments
    last_id = exp.pop()
    res = s.get('http://{}:{}/clustering/{}'.format(team_addr, PORT, last_id))
    if flag not in res.text:
        close(MUMBLE, 'Experiment is corrupted', json.dumps(last_id))

    return "{}:{}:clustering:{}".format(email, password, last_id)


def classification(team_addr, flag):
    s = session()
    email, password = fake.email(), generate_rand()
    s.post('http://{}:{}/registration'.format(team_addr, PORT), data={'email': email, 'password': password})
    s.post('http://{}:{}/classification'.format(team_addr, PORT), data={
        'flag': 'A35B78EFAD35F4AE03DE5B58AA94997=',
        'new_flag': flag
    })
    return "{}:{}:classification:null".format(email, password)


def check(*args):
    team_addr = args[0]

    s = session()
    try:
        email, password = fake.email(), generate_rand()
        s.get('http://{}:{}/registration'.format(team_addr, PORT))
        s.post('http://{}:{}/registration'.format(team_addr, PORT), data={'email': email, 'password': password})
        users_response = s.get('http://{}:{}/users'.format(team_addr, PORT))
        if email not in users_response.text:
            close(MUMBLE, 'Registration error', 'Email {} is not found on the /users page'.format(email))

        clustering_response = s.get('http://{}:{}/clustering'.format(team_addr, PORT))
        token = re.findall(r'name="token" value="(\d+)"', clustering_response.text)
        if not len(token):
            close(MUMBLE, 'Token not found')

        flag = fake.sentence()
        clustering(team_addr, flag)

        close(OK)

    except Exception as e:
        close(CORRUPT, 'Exception in check', str(e))


def put(*args):
    team_addr, flag_id, flag, flag_type = args[:4]
    s = session()
    try:
        email, password = fake.email(), generate_rand()
        s.post('http://{}:{}/registration'.format(team_addr, PORT), data={'email': email, 'password': password})

        state = clustering(team_addr, flag)
        close(OK, state)

    except Exception as e:
        close(CORRUPT, 'Exception in check', str(e))


def info(*args):
    close(OK, "vulns:1")


def get(*args):
    team_addr, lpb, flag = args[:3]

    try:
        s = session()
        email, password, flag_type, last_id = lpb.split(":")
        s.post('http://{}:{}/login'.format(team_addr, PORT), data={'email': email, 'password': password})
        users_response = s.get('http://{}:{}/users'.format(team_addr, PORT))
        if email not in users_response.text:
            close(MUMBLE, 'Login error', 'Email {} is not found on the /users page'.format(email))
        # if flag_type == "clustering":
        res = s.get('http://{}:{}/clustering/{}'.format(team_addr, PORT, last_id))
        if flag not in res.text:
            close(MUMBLE, 'Experiment is corrupted', last_id)
        close(OK)

    except Exception as e:
        close(CORRUPT, 'Exception in check', str(e))


def init(*args):
    close(OK)


def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


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
