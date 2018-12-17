#!/usr/bin/env python3
import requests,sys
import string,random,re

def id_gen(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

ua='Mozilla/5.0 (Linux; Android 6.0.1; SM-G935S Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36'
cmd = sys.argv[1]
ip=sys.argv[2]
url = "http://"+ip+":4125"
if cmd == "check":
    s = requests.Session()
    r=s.get(url)
    if not "<img id='cat'src=\"/img/cat1.gif\"" in r.text:
        exit(102)
    exit(101)
elif cmd == "put":
    flag_id = sys.argv[3]
    flag = sys.argv[4]
    s = requests.Session()
    r=s.post(url+'/add',data={'username':flag_id,'message':flag})
    print(flag_id+"/"+r.cookies['key'])

    r = s.get(url)
    if not flag_id in r.text:
        exit(102)
    exit(101)
elif cmd == "get":
    flag_id,key = sys.argv[3].split("/")
    flag = sys.argv[4]
    s = requests.Session()
    s.cookies['key'] = key.replace('\\054',",")
    r=s.get(url+'/read/'+flag_id)
    print(r.text)
    if len(r.text)==0:
        exit(103)
    if flag in r.text:
        exit(101)
    exit(102)
