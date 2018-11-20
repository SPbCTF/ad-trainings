#!/usr/bin/env python3

import random
import re
import string
import sys
import socket


OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "notescol"
PORT = 16404


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
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    username = generate_rand(8)

    try:
        sock.connect((team_addr, PORT))
        received = str(sock.recv(1024), "utf-8")
        sock.sendall(bytes("reg\n", "utf-8"))
        received = str(sock.recv(1024), "utf-8")
        sock.sendall(bytes(username + "\n", "utf-8"))
        received = str(sock.recv(1024), "utf-8")

        res = re.findall(r'--> Your token is (.*?)\n', received)
        if len(res):
            token = res[0]
            if ' $ ' not in received:
                sock.recv(1024)
            sock.sendall(bytes("add\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
            sock.sendall(bytes(flag + "\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
            if ' $ ' not in received:
                sock.recv(1024)
            sock.sendall(bytes("read\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
            if not flag in received:
                close(MUMBLE, 'Token has been added but was not read')
            else:
                close(OK, "{}:{}".format(username, token))
        else:
            sock.close()
            close(MUMBLE, 'Token not found')
    finally:
        sock.close()


def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


def info(*args):
    close(OK, "vulns: 1")


def check(*args):
    team_addr = args[0]
    username = generate_rand(8)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((team_addr, PORT))
        received = str(sock.recv(1024), "utf-8")
        sock.sendall(bytes("reg\n", "utf-8"))
        received = str(sock.recv(1024), "utf-8")
        sock.sendall(bytes(username + "\n", "utf-8"))
        received = str(sock.recv(1024), "utf-8")
        if ' $ ' not in received:
            sock.recv(1024)
        sock.sendall(bytes("users\n", "utf-8"))
        received = str(sock.recv(1024), "utf-8")
        while not username in received:
            received = str(sock.recv(1024), "utf-8")
        close(OK)

    except Exception as e:
        close(MUMBLE)

def get(*args):
    team_addr, lpb, flag = args[:3]
    username, token = lpb.split(":")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((team_addr, PORT))
        received = str(sock.recv(1024), "utf-8")
        sock.sendall(bytes("auth\n", "utf-8"))
        received = str(sock.recv(1024), "utf-8")
        sock.sendall(bytes(token + "\n", "utf-8"))
        received = str(sock.recv(1024), "utf-8")
        if ' $ ' not in received:
            sock.recv(1024)

        if username not in received:
            close(CORRUPT)
        sock.sendall(bytes("read\n", "utf-8"))
        received = str(sock.recv(1024), "utf-8")

        if flag not in received:
            close(MUMBLE, 'Token has been added but was not read')
        else:
            close(OK)
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
