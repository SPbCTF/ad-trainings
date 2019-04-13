import hashlib
import json
import logging
import os
import random
from os import listdir
from os.path import isfile, join

import aiohttp_jinja2 as aiohttp_jinja2
import jinja2
import matplotlib
import matplotlib.pyplot as plt
import numpy
from aiohttp import web
from aiohttp_session import get_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from joblib import load
from ml import add, gen_features
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances_argmin

from auth import register, authorize, check_pow


def find_clusters(X, n_clusters, rseed=2):
    rng = numpy.random.RandomState(rseed)
    i = rng.permutation(X.shape[0])[:n_clusters]
    centers = X[i]

    while True:
        labels = pairwise_distances_argmin(X, centers)
        new_centers = numpy.array([X[labels == i].mean(0)
                                for i in range(n_clusters)])
        if numpy.all(centers == new_centers):
            break
        centers = new_centers

    return centers, labels


@aiohttp_jinja2.template('index.html')
async def index(request):
    figures = [f for f in listdir('static/images/') if isfile(join('static/images/', f)) and f.startswith('fig_') and f.endswith('.png')]
    return {
        'figures': figures,
        'auth': check(request)
    }


@aiohttp_jinja2.template('users.html')
async def users(request):
    onlyfiles = [f.split('.txt')[0] for f in listdir('static/db/') if isfile(join('static/db/', f))]
    return {
        'users': onlyfiles
    }


def check(request):
    email = request.cookies.get('email', "")
    password = request.cookies.get('password', "")
    if email and password:
        user = authorize(email, password)
        if user:
            return user
    return None


@aiohttp_jinja2.template('registration.html')
async def registration(request):
    if request.method == 'POST':
        form = await request.post()
        email = form.get('email', "")
        password = form.get('password', "")

        if not email or not password:
            return {
                'error': 'Empty email or password'
            }
        else:
            user = register(email, password)
            if user is None:
                return {
                    'error': 'Registration error. Maybe user already exists'
                }
            location = request.app.router['index'].url_for()
            response = web.HTTPFound(location=location)
            response.cookies['email'] = email
            response.cookies['password'] = hashlib.md5(password.encode()).hexdigest()
            raise response

    return {
        'auth': check(request)
    }


@aiohttp_jinja2.template('auth.html')
async def authorization(request):
    if request.method == 'POST':
        form = await request.post()
        email = form.get('email', "")
        password = form.get('password', "")

        if not email or not password:
            return {
                'error': 'Empty email or password'
            }
        else:
            user = authorize(email, hashlib.md5(password.encode()).hexdigest())
            if user is None:
                return {
                    'error': 'Authorization error. Maybe user does not exists or password is invalid'
                }
            location = request.app.router['index'].url_for()
            response = web.HTTPFound(location=location)
            response.cookies['email'] = email
            response.cookies['password'] = hashlib.md5(password.encode()).hexdigest()
            raise response

    return {
        'auth': check(request)
    }


@aiohttp_jinja2.template('classification.html')
async def classification(request):
    user = check(request)
    if not user:
        raise web.HTTPFound(location=request.app.router['registration'].url_for())

    stats = json.loads(open("static/latest.txt").read())

    if request.method == 'POST':
        form = await request.post()

        flag = form['flag']
        new_flag = form.get('new_flag', '')
        if os.path.isfile("static/flags/{}.txt".format(flag)):
            if not new_flag:
                return {
                    'flag': flag,
                    'result': True,
                    'stats': stats,
                    'auth': user
                }
            else:
                with open("static/flags/{}.txt".format(new_flag), 'w') as w:
                    w.write(flag)

                with open("static/latest.txt", 'w') as w:
                    w.write(json.dumps(add()))

                location = request.app.router['index'].url_for()
                response = web.HTTPFound(location=location)
                raise response
        else:
            test = numpy.matrix(gen_features(flag, 0)[:-1])
            clf = load('static/gb.model')
            prediction = clf.predict(test)
            return {
                'stats': stats,
                'result': prediction[0],
                'auth': user
            }

    else:
        return {
            'stats': stats,
            'auth': user
        }


@aiohttp_jinja2.template('clustering.html')
async def clustering(request):
    from sklearn.cluster import KMeans

    user = check(request)
    if not user:
        raise web.HTTPFound(location=request.app.router['registration'].url_for())

    session = await get_session(request)

    if request.method == 'POST':
        form = await request.post()

        try:
            samples = int(form.get('samples'))
            features = int(form.get('features'))
            clusters = int(form.get('clusters'))
            description = form.get('experiment')
            pow = int(form.get('pow'))

            if not check_pow(session['token'], pow):
                return {
                    'samples': int(request.rel_url.query.get('samples', 4)),
                    'features': int(request.rel_url.query.get('features', 2)),
                    'error': 'PoW is invalid for token'.format(session['token']),
                    'auth': user
                }

            data = [[0 for _ in range(features)] for _ in range(samples)]
            for element in form.keys():
                if "_" not in element:
                    continue
                i, j = element.split("_")
                data[int(i)][int(j)] = form[element]

            X = numpy.matrix(data)
            model = KMeans(n_clusters=clusters, init='k-means++')
            model.fit(X)
            labels = model.labels_.tolist()

            pca = PCA(n_components=2)
            datapoint = pca.fit_transform(X)

            plt.figure(figsize=(10, 10))
            plt.title('PCA')
            cmap = matplotlib.cm.get_cmap('gist_rainbow')
            label1 = [cmap(1.0 * i / clusters) for i in range(clusters)]
            color = [label1[i] for i in labels]

            name = hashlib.md5(description.encode()).hexdigest()
            plt.scatter([datapoint[:, 0]], [datapoint[:, 1]], c=color, s=50, cmap='viridis')
            plt.savefig('static/images/fig_{}.png'.format(name))
            with open("static/experiments/{}.txt".format(name), 'w') as w:
                w.write(json.dumps({
                    'id': name,
                    'experiment': description,
                    'features': features,
                    'samples': samples,
                    'clusters': clusters,
                    'labels': labels,
                    'centroids': model.cluster_centers_.tolist()
                }))

            user['experiments'].append(name)
            with open("static/db/{}.txt".format(user['email']), 'wb') as w:
                w.write(bytes(json.dumps(user), 'UTF-8'))

        except Exception as e:
            logging.error(e)
            raise web.HTTPBadRequest()

        token = random.randint(2 ** 32, 2 ** 64)
        session['token'] = token
        return {
            'samples': int(request.rel_url.query.get('samples', 4)),
            'features': int(request.rel_url.query.get('features', 2)),
            'token': str(token),
            'user': user,
            'auth': user
        }
    else:
        token = random.randint(2**32, 2**64)
        session['token'] = token
        return {
            'samples': int(request.rel_url.query.get('samples', 4)),
            'features': int(request.rel_url.query.get('features', 2)),
            'token': str(token),
            'user': user,
            'auth': user
        }

    return {
        'auth': user
    }


@aiohttp_jinja2.template('info.html')
async def clustering_info(request):
    eid = request.match_info['eid']
    try:
        info = json.loads(open("static/experiments/{}.txt".format(eid)).read())
        return info
    except Exception as e:
        logging.error(e)
        return {
            'error': 'experiment with id={} not found'.format(eid),
        }


app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('static/templates'))
setup(app, EncryptedCookieStorage(b'Thirty  two  length  bytes  key.'))

app.add_routes([web.get('/', index, name='index'),
                web.get('/registration', registration, name='registration'),
                web.post('/registration', registration),
                web.get('/clustering', clustering),
                web.post('/clustering', clustering),
                web.get('/login', authorization),
                web.post('/login', authorization),
                web.get('/clustering/{eid}', clustering_info),
                web.get('/users', users),
                web.get('/classification', classification),
                web.post('/classification', classification),
                ])
app.router.add_static('/img/', path=str('./static/images'))
app.router.add_static('/js/', path=str('./static/js'))
app.router.add_static('/db/', path=str('./static/db'))
app.router.add_static('/css/', path=str('./static/css'))
app.router.add_static('/fonts/', path=str('./static/fonts'))

web.run_app(app, port=2800)
