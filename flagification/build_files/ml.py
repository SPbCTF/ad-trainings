import random
import string
from functools import reduce
from os import listdir
from os.path import isfile, join
from pandas.plotting import parallel_coordinates
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import numpy
import pandas
from joblib import dump, load


def generate_flag():
    return '%031X=' % random.randrange(16**31)


def generate_not_a_flag():
    return ''.join(random.choice('1234567890uBLSDUIFHPWEUI:FBHKSyrozdv.zcx=====kjvhadf') for n in range(random.randint(2, 18)))


def gen_features(f, is_flag):
    features = [len(f), len(set(f))]
    fz = f.zfill(32)[:32]
    for a,b in zip(fz[:4:2], fz[1:4:2]):
        features.append(ord(a) * 2 + ord(b))
    for a in fz[4:]:
        features.append(ord(a))
    zxor = reduce(lambda a, b: a ^ b, map(ord,list(f)), 0)
    features.append(sum([i for i, c in enumerate(f) if c == '=']))
    features.append(sum([i for i, c in enumerate(f) if c in string.ascii_lowercase]))
    features.append(zxor)
    features.append(is_flag)
    return features


def add():
    stats = {}
    flags = [f.split('.txt')[0] for f in listdir('static/flags/') if isfile(join('static/flags/', f))]
    not_flags = ['-331687A523943C7765A700C81CE84D=', '2331687A523943C7765A700C81CE84=D',
                 '9F31687A523943C7765A700C81CE84D', '=90BA59058C39774433F3E4D5AED6C2=', '7D52AFB2EDB942A19D9755A8E661B8C=2', '8865847A0C16DB8A016AAE33D15D1F36='
                 '-F31687A523943C7765A700C81CE84D=' 'test', 'lol', 'kek',
                 '978rUaUzLBz9H8ULIP=rvS=9aS2='] + [generate_not_a_flag() for _ in range(12)]
    X = []
    for f in flags:
        X.append(gen_features(f, 1))
    for f in not_flags:
        X.append(gen_features(f, 0))
    X = numpy.matrix(X)
    columns = ['len', 'uniq_symb', 'pair 1', 'pair 2'] + ["elem {}".format(i) for i in range(28)] + [
        'eq_pos', 'lower_count', 'zxor', 'is_flag']
    dataframe = pandas.DataFrame(data=X, columns=columns)

    plt.figure(figsize=(40, 20))
    parallel_coordinates(dataframe, "is_flag", colormap='flag')
    plt.title('Parallel Coordinates Plot', fontsize=20, fontweight='bold')
    plt.xlabel('Features', fontsize=15)
    plt.ylabel('Features values', fontsize=15)
    plt.yticks(numpy.arange(0, 270, 5))
    plt.legend(loc=1, prop={'size': 15}, frameon=False, shadow=False, facecolor="white", edgecolor="black")
    plt.savefig('static/images/latest.png')

    from sklearn.ensemble import ExtraTreesClassifier

    xx = X[:, :-1]
    yy = X[:, -1]

    forest = ExtraTreesClassifier(n_estimators=250, random_state=0)
    forest.fit(xx, yy)
    importances = forest.feature_importances_
    std = numpy.std([tree.feature_importances_ for tree in forest.estimators_], axis=0)
    indices = numpy.argsort(importances)[::-1]

    stats['ranking'] = []
    for f in range(xx.shape[1] - 1):
        stats['ranking'].append([columns[indices[f]], importances[indices[f]]])

    plt.figure()
    plt.title("Feature importances")
    plt.bar(range(xx.shape[1]), importances[indices], color="r", yerr=std[indices], align="center")
    plt.xticks(range(xx.shape[1]), indices)
    plt.xlim([-1, xx.shape[1]])
    plt.savefig('static/images/ranking.png')

    from sklearn.ensemble import GradientBoostingRegressor
    params = {'n_estimators': 500, 'max_depth': 4, 'min_samples_split': 2,
              'learning_rate': 0.01, 'loss': 'ls'}

    X = []
    for f in flags:
        X.append(gen_features(f, 1))
    for f in [generate_flag() for _ in range(128)]:
        X.append(gen_features(f, 1))
    for f in not_flags:
        X.append(gen_features(f, 0))
    X = numpy.matrix(X)

    gb_model = GradientBoostingRegressor(**params)
    gb_model.fit(X[:, :-1], X[:, -1])
    dump(gb_model, 'static/gb.model')

    feature_importance = gb_model.feature_importances_
    feature_importance = 100.0 * (feature_importance / feature_importance.max())
    sorted_idx = numpy.argsort(feature_importance)
    pos = numpy.arange(sorted_idx.shape[0]) + .5
    plt.subplot(1, 1, 1)

    plt.barh(pos[-10:], feature_importance[sorted_idx][-10:], align='center')
    plt.yticks(pos[-10:], [columns[i] for i in sorted_idx][-10:])
    plt.xlabel('Relative Importance')
    plt.title('Variable Importance')
    plt.savefig('static/images/ranking2.png')

    return stats