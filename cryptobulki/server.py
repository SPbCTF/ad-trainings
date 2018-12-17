#!/usr/bin/env python3
from flask import Flask,request,render_template,make_response,send_from_directory
import os,json,base64,random,millerrabin,time,string
import os.path
app = Flask(__name__)

@app.route('/img/<path>')
def send_js(path):
    return send_from_directory('img', path)

@app.route('/')
def index():
    messages = []
    fls = []
    for f in os.listdir("messages"):
        fls.append({'uname':f,'name':"messages/"+f,'md':os.path.getmtime("messages/"+f)})
    fls.sort(key=lambda x: x['md'])
    if len(fls) > 20:
        fls = fls[-20:]
    for f in fls:
        m = open(f['name'],'r').read().split(',')
        messages.append(dict(username=f['uname'],message=m[3][:10]+"...",date=time.strftime('%l:%M%p %Z on %b %d, %Y',time.localtime(f['md']))))
    return render_template('index.html', messages=messages)

def mod_inverse(x,y):
    def eea(a,b):
        if b==0:return (1,0)
        (q,r) = (a//b,a%b)
        (s,t) = eea(b,r)
        return (t, s-(q*t) )
    inv = eea(x,y)[0]
    if inv < 1:inv += y
    return inv

def test(p,q):
    n = p*q
    fi = (p-1)*(q-1)
    e = 17
    d = mod_inverse(e,fi)
    dmesg = encrypt(n,e,"q"*32)
    aa=decrypt(n,d,dmesg)
    bb=str(int(aa).to_bytes(int(aa.bit_length()/8)+1,byteorder='big'))[2:-1]
    if bb != "q"*32:
        return False
    return True

def genkey():
    num = random.getrandbits(130)
    (p,q) = (num-1,num+1)
    while 1:
        if millerrabin.is_prime(p):
            break;
        p+=1
    while 1:
        if millerrabin.is_prime(q):
            break;
        q-=1
    return p,q
def encrypt(n,e,mes):
    mes = int(mes.encode().hex(),16)
    res = pow(mes,e,n)
    return res

def decrypt(n,d,mes):
    mes = mes
    res = pow(mes,d,n)
    return res
@app.route('/add',methods=['GET','POST'])
def addmes():
    if request.method == "GET":
        return render_template('add.html')

    if not 'username' in request.values or not 'message' in request.values or \
        len(request.values['username']) ==0 or len(request.values['message'])==0 :
        return render_template('error.html',message='Username or message is empty')

    username = request.values['username']
    mess = request.values['message']
    resp = make_response(render_template("add.html"))

    (n,e,d) = (0,0,0)
    if 'key' in request.cookies:
        (n,e,d) = map(lambda x:int(x,16),request.cookies['key'].split(","))
    else:
        (p,q) = genkey()
        while test(p,q) == False:
            print("P,Q are invalid, retrying...")
            (p,q) = genkey()

        n = p*q
        fi = (p-1)*(q-1)
        e = 17
        d = mod_inverse(e,fi)
        print ("New key",e,d,fi,(e*d) % fi)
    key = ",".join(map(lambda x: hex(x),[n,e,d]))
    dmesg = encrypt(n,e,mess)
    username = ''.join(ch for ch in username if ch in string.ascii_lowercase + string.ascii_uppercase+'-'+string.digits )

    if os.path.isfile("messages/"+username):
        f = open("messages/"+username,'r')
        (_n,_e,_d,_dmesg) = f.read().split(',')
        f.close()
        if n == _n and d == _d:
            _dmesg = dmesg
            f = open("messages/"+username,'w+')
            f.seek(0)
            f.truncate()
            f.write(",".join(map(str,[_n,_e,_d,_dmesg])))
            f.close()
            resp = make_response(render_template('add.html',message='Successfully stored',dmes=hex(dmesg)))
            resp.set_cookie("key",key)
            return resp
        else:
            return render_template('error.html',message='You have not key for this file')
    else:
        f = open("messages/"+username,'w+')
        f.write(",".join(map(str,[n,e,d,dmesg])))
        f.close()
        resp = make_response(render_template('add.html',message='Successfully stored',dmes=hex(dmesg)))
        resp.set_cookie("key",key)
        return resp

@app.route('/read/<username>')
def readmes(username):
    (n,e,d) = (0,0,0)
    if 'key' in request.cookies:
        (n,e,d) = map(lambda x:int(x,16),request.cookies['key'].split(","))
    else:
        return render_template('error.html',message="No key you have")
    f = open("messages/"+username,'r')
    (_n,_e,_d,_dmesg) = f.read().split(',')
    f.close()
    decoded = decrypt(int(n),int(d),int(_dmesg))
    decoded = str(int(decoded).to_bytes(int(decoded.bit_length()/8)+1,byteorder='big'))[2:-1]
    return render_template('read.html',source=hex(int(_n))+":"+hex(int(_e)),message=decoded)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4125,threaded=True)
