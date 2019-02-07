import re
from django.conf import settings

from pymongo import MongoClient

from wattstrat.simulation.models import Simulation

if __debug__:
    import logging
    logger = logging.getLogger(__name__)

mongo_client = None

try:
    mongo_client = MongoClient(host=settings.MONGO_HOST, port=settings.MONGO_PORT)
    db=mongo_client[settings.DB_NAME]
except Exception:
    if __debug__:
        logger.exception("Erreur during mongo setup")


def get_simulation_results(simulation, variable_name, year, projection, geocodes=None):

    if type(simulation) is not str:
        # wrong assume, convert simulation to shortid
        shortid = simulation.shortid
    else:
        shortid=simulation

    proj_var = geocodes
    query = {"varname": variable_name, "year": year, "projection": projection}
    simulation_results_collection = db[shortid]
    results = simulation_results_collection.find_one(query, projection=proj_var)
    return results

def get_geocodes():
    col = db["geocodes"]
    projection = {'_id': 0, 'geocode_insee': 1}
    return [geo['geocode_insee'] for geo in col.find({}, projection=projection)]
