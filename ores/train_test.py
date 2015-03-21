"""
Trains and tests a classifier.

Usage:
    train_test -h | --help
    train_test <model> <features> [--language=<module>][--values-labels=<path>]

Options:
    -h --help                Prints this documentation
    <model>                  Classpath to a MLScorerModel to train
    <features>               Classpath to the set of features to expect as
                             input.
    --language=<module>      Classpath to a Language
    --values-labels=<path>   Path to a file containing feature values and
                             labels [default: <stdin>]
"""
import pprint
import random
import sys

import docopt

from .util import import_from_path


def read_feature_scores(f, features):
    for line in f:
        parts = line.strip().split("\t")
        values = parts[:-1]
        score = parts[-1]

        feature_values = []
        for feature, value in zip(features, values):

            if feature.returns == bool:
                feature_values.append(value == "True")
            else:
                feature_values.append(feature.returns(value))

        yield feature_values, score == "True"


def main():
    args = docopt.docopt(__doc__)

    Model = import_from_path(args['<model>'])
    features = import_from_path(args['<features>'])

    if args['--language'] is not None:
        language = import_from_path(args['--language'])
    else:
        language = None

    model = Model(features, language=language)

    if args['--values-labels'] == "<stdin>":
        values_labels_file = sys.stdin
    else:
        values_labels_file = open(args['--values-labels'], 'r')

    feature_scores = read_feature_scores(values_labels_file, features)

    run(feature_scores, model)


def run(feature_scores, model):

    feature_scores = list(feature_scores)
    random.shuffle(feature_scores)

    test_set_size = int(0.6*len(feature_scores))
    test_set = feature_scores[:test_set_size]
    train_set = feature_scores[test_set_size:]

    model.train(train_set)

    stats = model.test(test_set)
    del stats['roc']
    sys.stderr.write(pprint.pformat(stats) + "\n")

    model.dump(sys.stdout.buffer)

"""
./train_test \
    revscoring.scorers.LinearSVCModel \
    ores.features.enwiki.damaging \
    --language=revscoring.languages.english \
    --feature-scores=datasets/enwiki.features_reverted.20k.tsv > \
models/enwiki.reverted.linear_svc.model
"""
