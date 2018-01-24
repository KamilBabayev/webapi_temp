#!/usr/bin/env python

''' Mongo Results Provider '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import logging
import sys
import json

from pymongo import MongoClient
from tornado import gen
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor

from bson.json_util import dumps
from bson.objectid import ObjectId

'''
We want to log everything to the standard output so docker handles it
'''
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
                '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

thread_pool = ThreadPoolExecutor()


class MongoResultsProvider(object):

    _thread_pool = thread_pool

    def __init__(self, username, password, port, end_point, collection_name='results'):
        self.mongo_conn_url = "mongodb://%s:%s@%s:%s/automation?authMechanism=SCRAM-SHA-1" % (username, password, end_point, port,)
        self.collection_name = collection_name

    @gen.coroutine
    def get_results(self, id=None):
	mongo_client = None
        try:
            mongo_client = MongoClient(self.mongo_conn_url)
            database = mongo_client['automation']
            collection = database.get_collection(self.collection_name)
            self.collection = collection

            if id:
                results = yield self.__get_result(id)
            else:
                results = yield self.__get_results()

            results_dict = json.loads(results)

        except Exception as ex:
            logging.error('Error getting automation results with id: %s' % id)
            raise
        finally:
            if mongo_client:
                mongo_client.close()

        raise gen.Return(results_dict)

    @gen.coroutine
    def write_result(self, result):
        mongo_client = None
	try:
            mongo_client = MongoClient(self.mongo_conn_url)
            database = mongo_client['automation']
            collection = database.get_collection(self.collection_name)
            self.collection = collection

            results = yield self.__write_result(result)

            if not results:
                raise Exception('Failed to write results to mongodb')

            results_dict = json.loads(results)

        except Exception as ex:
            logging.error(str(ex))
            raise
        finally:
            if mongo_client:
                mongo_client.close()

        raise gen.Return(results_dict)

    @run_on_executor(executor="_thread_pool")
    def __get_result(self, id):
        result = self.collection.find({"_id": ObjectId(id)})
        if result:
            return dumps(result)
        else:
            return ''

    @run_on_executor(executor="_thread_pool")
    def __get_results(self):
        results = self.collection.find()
        if results:
            return dumps(results)
        else:
            return ''

    @run_on_executor(executor="_thread_pool")
    def __write_result(self, result):
        return dumps(self.collection.insert(result, check_keys=False))

