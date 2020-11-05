import logging

from flask import request

from ... import preprocessors, responses
from ...util import build_precache_map, build_score_request_from_event
from . import util

logger = logging.getLogger(__name__)


def configure(config, bp, scoring_system):
    """
    Configure a score.

    Args:
        config: (dict): write your description
        bp: (todo): write your description
        scoring_system: (todo): write your description
    """

    precache_map = build_precache_map(config)

    @bp.route("/v3/precache/", methods=["POST"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def precache_v3():
        """
        Precache the json request.

        Args:
        """
        event = request.get_json()
        if event is None:
            return responses.bad_request(
                "Must provide a POST'ed json as an event")

        try:
            score_request = build_score_request_from_event(
                precache_map, event)
        except KeyError as e:
            return responses.bad_request(
                "Must provide the '{key}' parameter".format(key=e.args[0]))
        if not score_request:
            return responses.no_content()
        else:
            return util.process_score_request(score_request, scoring_system)

    return bp
