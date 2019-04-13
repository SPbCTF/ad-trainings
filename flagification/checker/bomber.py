import hashlib
import random
import re

import numpy as np
from faker import Faker
from requests import session

fake = Faker()

addr = 'http://localhost:2800'


def generate_flag():
    return '%031X=' % random.randrange(16**31)


def bruteforce_token(token):
    answer = 1
    while True:
        if hashlib.md5("{}{}".format(token, answer).encode()).hexdigest().startswith('00000'):
            return answer

        answer += 1


def make_clustering_request(token):
    samples_count = random.randint(20, 50)
    features_count = random.randint(2, 4)
    samples = np.random.randint(low=1, high=20, size=(samples_count, features_count))

    data = {
        'samples': samples_count,
        'features': features_count,
        'clusters': random.randint(3, 8),
        'pow': bruteforce_token(token),
        'experiment': generate_flag()
    }

    for i, feature_vector in enumerate(samples):
        for j, feature in enumerate(feature_vector):
            data["{}_{}".format(i, j)] = feature

    return data

def clustering():
    s = session()
    s.post('{}/registration'.format(addr), data={
        'email': fake.email(),
        'password': fake.password()
    })
    res = s.get('{}/clustering'.format(addr))
    token = re.findall(r'name="token" value="(\d+)"', res.text)
    if not len(token):
        raise Exception("Token not found")

    res = s.post('{}/clustering'.format(addr), data=make_clustering_request(token[0]))


def classification():
    s = session()
    s.post('{}/registration'.format(addr), data={
        'email': fake.email(),
        'password': fake.password()
    })
    s.post('{}/classification'.format(addr), data={
        'flag': 'A35B78EFAD35F4AE03DE5B58AA94997=',
        'new_flag': '33B556F55C22A65B5A51D8622DFD255='
    })

# for i in range(15):
#     print(i)
#     clustering()
# classification()
clustering()
