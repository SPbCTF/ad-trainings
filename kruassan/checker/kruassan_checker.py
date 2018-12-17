#!/usr/bin/env python2

from socket import *
import sys,string,random,re

cmd = sys.argv[1]
IP = sys.argv[2]
TIMEOUT = 0.5
def readall(s):
    mes=''
    try:
        while 1:
            m = s.recv(1)
            mes += m
    except timeout:
        return mes
def idgen(N=5):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
s = socket(AF_INET,SOCK_STREAM)
s.settimeout(TIMEOUT)
if cmd == 'check':
    s.connect((IP,3758))
    s.send(idgen()+"\n")
    mes = readall(s)
    s.send("exit\n")
    s.close()
    if "Commands:" in mes:
        exit(101)
    exit(102)
elif cmd == 'put':
    s.connect((IP,3758))
    s.send("bake\n")
    mes = readall(s)
    bid = re.findall(r'Baked kruassan (\w+)',mes)
    if len(bid)==0:
        exit(103)
    s.send("fillup %s\n" %(sys.argv[4]))
    mes = readall(s)
    s.send("exit\n")
    s.close()
    if not "Filling up" in mes:
        exit(102)
    print bid[0]
    exit(101)
elif cmd == 'get':
    s.connect((IP,3758))
    s.send("eat %s\n" %sys.argv[3])
    mes = readall(s)
    s.send("exit\n")
    s.close()
    print mes
    if sys.argv[4] in mes:
        exit(101)
    exit(102)
