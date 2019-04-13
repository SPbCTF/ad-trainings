import hashlib
import json
import random

import io
import jinja2
import logging

import matplotlib
from flask import Flask, render_template, abort
from os import listdir

from os.path import isfile, join

from flask import Response
from flask import make_response
from flask import redirect
from flask import request
from flask import send_from_directory

import matplotlib.pyplot as plt

from auth import authorize, check_pow, register
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__, static_folder='./static/')


@app.route('/')
def index():
    figures = [f for f in listdir('static/img/') if
               isfile(join('static/img/', f)) and f.startswith('fig_') and f.endswith('.png')]

    return render_template('index.html', figures=figures, auth=check())


@app.route('/users')
def users():
    users = [f.split('.txt')[0] for f in listdir('static/db/') if isfile(join('static/db/', f))]
    return render_template('users.html', users=users, auth=check())


def check():
    email = request.cookies.get('email', "")
    password = request.cookies.get('password', "")
    if email and password:
        user = authorize(email, password)
        if user:
            return user
    return None


@app.route('/clustering', methods = ['GET', 'POST'])
def clustering():
    from sklearn.cluster import KMeans
    import numpy
    from sklearn.decomposition import PCA
    from sklearn.metrics import pairwise_distances_argmin
    from matplotlib.figure import Figure


    user = check()
    if not user:
        return redirect("/registration", code=302)

    if request.method == 'POST':

        try:
            samples = int(request.form.get('samples'))
            features = int(request.form.get('features'))
            clusters = int(request.form.get('clusters'))
            description = request.form.get('experiment')
            pow = int(request.form.get('pow'))

            if samples < 3 or samples > 50 or features < 2 or features > 50:
                return abort(403)

            if not check_pow(request.cookies.get('token',''), pow):
                return render_template('clustering.html',
                                         samples=int(request.args.get('samples', 4)),
                                         features=int(request.args.get('features', 4)),
                                         error='PoW is invalid for token'.format(request.cookies.get('token', '')),
                                         auth=user)


            data = [[0 for _ in range(features)] for _ in range(samples)]
            for element in request.form.keys():
                if "_" not in element:
                    continue
                i, j = element.split("_")
                data[int(i)][int(j)] = request.form[element]

            X = numpy.matrix(data)
            model = KMeans(n_clusters=clusters, init='k-means++')
            model.fit(X)
            labels = model.labels_.tolist()

            pca = PCA(n_components=2)
            datapoint = pca.fit_transform(X)

            cmap = matplotlib.cm.get_cmap('gist_rainbow')
            label1 = [cmap(1.0 * i / clusters) for i in range(clusters)]
            color = [label1[i] for i in labels]

            fig = Figure(figsize=(10, 10))
            axis = fig.add_subplot(1, 1, 1)
            name = hashlib.md5(description.encode()).hexdigest()
            axis.scatter([datapoint[:, 0]], [datapoint[:, 1]], c=color, s=50, cmap='viridis')

            output = io.BytesIO()
            FigureCanvas(fig).print_png(output)
            with open('static/img/fig_{}.png'.format(name), 'wb') as w:
                w.write(output.getvalue())

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
            return abort(400)

    token = random.randint(2**32, 2**64)
    resp = make_response(render_template('clustering.html',
                                         samples=int(request.args.get('samples', 4)),
                                         features=int(request.args.get('features', 2)),
                                         token=token,
                                         user=user,
                                         auth=user))
    resp.set_cookie('token', str(token))
    return resp


@app.route('/registration', methods = ['GET', 'POST'])
def registration():
    if request.method == 'POST':
        email = request.form.get('email', "")
        password = request.form.get('password', "")

        if not email or not password:
            return render_template('registration.html', error='Empty email or password')
        else:
            user = register(email, password)
            if user is None:
                return render_template('registration.html', error='Registration error. Maybe user already exists')
            resp = make_response(redirect("/", code=302))
            resp.set_cookie('email', email)
            resp.set_cookie('password', hashlib.md5(password.encode()).hexdigest())
            return resp

    return render_template('registration.html', auth=check())


@app.route('/login', methods = ['GET', 'POST'])
def authorization():
    if request.method == 'POST':
        email = request.form.get('email', "")
        password = request.form.get('password', "")

        if not email or not password:
            return render_template('auth.html', error='Empty email or password')
        else:
            user = authorize(email, hashlib.md5(password.encode()).hexdigest())
            if user is None:
                return render_template('auth.html', error='Authorization error. Maybe user already exists')
            resp = make_response(redirect("/", code=302))
            resp.set_cookie('email', email)
            resp.set_cookie('password', hashlib.md5(password.encode()).hexdigest())
            return resp

    return render_template('auth.html', auth=check())


@app.route('/clustering/<string:eid>')
def clustering_info(eid):
    try:
        info = json.loads(open("static/experiments/{}.txt".format(eid)).read())
        return render_template('info.html', **info)
    except Exception as e:
        logging.error(e)
        return render_template('info.html', error='experiment with id={} not found'.format(eid))


@app.route('/<path:folder>/<path:filename>')
def base_static(folder, filename):
    return send_from_directory(app.root_path + '/static/' + folder, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2800, debug=True, threaded=True)
