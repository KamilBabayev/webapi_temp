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


class MongoAutomationDataProvider(object):

    _thread_pool = thread_pool

    def __init__(self, username, password, port, end_point):
        self.mongo_conn_url = "mongodb://%s:%s@%s:%s/automation?authMechanism=SCRAM-SHA-1" % (username, password, end_point, port,)

    @gen.coroutine
    def get_automation_data(self, automation_name=None):
        mongo_client = None
        try:
            mongo_client = MongoClient(self.mongo_conn_url)
            self.db = mongo_client['automation']

            if automation_name:
                automation_data = yield self.__get_automation_data_by_field(automation_name)
            else:
                automation_data = yield self.__get_automation_data()

            automation_data_dict = json.loads(automation_data)

        except Exception as ex:
            logging.error('Error getting data from automation_data collection with automation_name: %s' %automation_name)
            raise
        finally:
            if mongo_client:
                mongo_client.close()

        raise gen.Return(automation_data_dict)

    @gen.coroutine
    def write_automation_data(self, data):
        mongo_client = None
        try:
            mongo_client = MongoClient(self.mongo_conn_url)
            self.db = mongo_client['automation']

            automation_data = yield self.__write_automation_data(data)

            if not automation_data:
                raise Exception('Failed to write results to mongodb: %s', self.mongo_conn_url)

            automation_data_dict = json.loads(automation_data)

        except Exception as ex:
            logging.error(str(ex))
            raise
        finally:
            if mongo_client:
                mongo_client.close()

        raise gen.Return(automation_data_dict)

    @run_on_executor(executor="_thread_pool")
    def __get_automation_data(self):
        automation_data = self.db.automation_data.find()
        if automation_data:
            return dumps(automation_data)
        else:
            return ''

    @run_on_executor(executor="_thread_pool")
    def __get_automation_data_by_field(self, automation_name):
        automation_data = self.db.automation_data.find({"ztp.name": automation_name})
        if automation_data:
            return dumps(automation_data)
        else:
            return ''

    @run_on_executor(executor="_thread_pool")
    def __write_automation_data(self, data):
        return dumps(self.db.automation_data.insert(data, check_keys=False))
