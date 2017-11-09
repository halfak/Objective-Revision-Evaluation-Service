import time

from revscoring import Model
from revscoring.datasources.revision_oriented import revision
from revscoring.features import Feature
from revscoring.scoring import ModelInfo
from revscoring.scoring.statistics import Classification


def process_reversed_last_two_in_rev_id(rev_id):
    last_two = str(rev_id)[-2:]
    if len(last_two) == 1:
        return int(last_two + "0")
    else:
        return int("".join(reversed(last_two)))


reversed_last_two_in_rev_id = Feature(
    "revision.reversed_last_two_in_rev_id",
    process_reversed_last_two_in_rev_id,
    returns=int,
    depends_on=[revision.id]
)


def process_delay():
    return 0.0


delay = Feature("delay", process_delay, returns=float)


class RevIdScorer(Model):
    """
    Implements a basic, testing scorer that predicts whether a revision ID's
    reversed last two digits are greater than 50.

    E.g. 974623 = 32 and 23754929 = 92
    """
    def __init__(self, version=None):
        super().__init__([reversed_last_two_in_rev_id, delay], version=version)
        self.info = ModelInfo()
        self.info['version'] = version
        self.info['type'] = "RevIDScorer"
        self.info['behavior'] = "Returns the last two digits in a rev_id " + \
                                "as a score."
        self.info['statistics'] = self.quick_statistics()

    def score(self, feature_values):
        last_two_in_rev_id, delay = feature_values
        time.sleep(delay)
        probability = last_two_in_rev_id / 100

        if probability > 0.5:
            prediction = True
        else:
            prediction = False

        return {
            'prediction': prediction,
            'probability': {
                True: probability,
                False: 1 - probability
            }
        }

    def quick_statistics(self):
        '''Jam some data through to generate statistics'''
        rev_ids = range(0, 100, 10)
        feature_values = zip(rev_ids, [ 0 ] * 10)
        scores = [ self.score(f) for f in feature_values ]
        labels = [ s['prediction'] for s in scores ]
        statistics = Classification(labels, threshold_ndigits=1, decision_key='probability')
        score_labels = zip(scores, labels)
        statistics.fit(score_labels)
        return statistics

    @classmethod
    def from_config(cls, config, name, section_key='scorer_models'):
        section = config[section_key][name]
        return cls(**{k: v for k, v in section.items() if k != "class"})
