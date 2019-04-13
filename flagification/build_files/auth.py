import hashlib
import json
import logging
from datetime import datetime
import os.path
import crc8


def load_user(email):
    return json.loads(open("static/db/{}.txt".format(email)).read())


def authorize(email, password):
    try:
        user = load_user(email)
        h1 = crc8.crc8()
        h1.update(hashlib.md5(user['password'].encode()).hexdigest().encode())
        h2 = crc8.crc8()
        h2.update(password.encode())
        if h1.hexdigest() == h2.hexdigest():
            return user
        else:
            return None
    except Exception as e:
        logging.error(e)
    return None


def register(email, password):
    try:
        if os.path.isfile("static/db/{}.txt".format(email)):
            user = load_user(email)
            if user['password'] == password:
                return user
            else:
                return None
        else:
            with open("static/db/{}.txt".format(email), 'wb') as w:
                user = {
                    'email': email,
                    'password': password,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'coins': 0,
                    'experiments': []
                }
                w.write(bytes(json.dumps(user), 'UTF-8'))
            return user
    except Exception as e:
        logging.error(e)
        return None


def check_pow(token, answer):
    if hashlib.md5("{}{}".format(token, answer).encode()).hexdigest().startswith('000'):
        return True
    return False
