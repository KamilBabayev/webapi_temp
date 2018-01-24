#!/usr/bin/env python

''' Tests Results Provider '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.
import json
import os
import logging

from tornado import gen

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

'''
We want to log everything to the standard output so docker handles it
'''
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)


class TestResultsProvider(object):
    ''' Provides a testing mock for the mongo results handler '''
    @gen.coroutine
    def get_results(self, result_id=None):
        """Method implements the results mock of mongo

        args:
            result_id: key to get data from results db
        Returns:
            data responding to the result_id
        """
        try:
            path = os.path.join(ROOT_DIR, '../tests/results.json')
            results = self.__get_mock_results(path)

        except Exception as ex:
            raise ex

        raise gen.Return(results)

    @gen.coroutine
    def write_result(self, result):
        """Method implements the write results mock of mongo
        args:
            result: result to write to databse
        Returns:
            data responding to the successful write
        """
        try:
            results = '{"$oid": "59dc3e8c8f54a9000d1fb89f"}'

            if not results:
                raise Exception('Failed to write results to mongodb')

        except Exception as ex:
            raise ex

        raise gen.Return(results)

    def __get_mock_results(self, path):
        """Method loads mock data for use in tests

        args:
            path: path to the test file
        Returns:
            data loaded from the json file
        """
        with open(path) as json_data:
            results = json.load(json_data)

        return results

######################
    @gen.coroutine
    def get_automation_data(self, automation_name=None):
        """Method implements the automation_data mock of mongo

        args:
            automation_name: field to get data from automation_data collection of automation db
        Returns:
            data responding to the automation_name
        """
        try:
            path = os.path.join(ROOT_DIR, '../tests/automation_data.json')
            automation_data = self.__get_mock_automation_data(path)

        except Exception as ex:
            raise ex

        raise gen.Return(automation_data)

    @gen.coroutine
    def write_automation_data(self, data):
        """Method implements the write results mock of mongo
        args:
            result: result to write to databse
        Returns:
            data responding to the successful write
        """
        try:
            automation_data = '{"automation_name": "mns-oam-test"}'

            if not automation_data:
                raise Exception('Failed to write results to mongodb')

        except Exception as ex:
            raise ex

        raise gen.Return(automation_data)

    def __get_mock_automation_data(self, path):
        """Method loads mock data for use in tests

        args:
            path: path to the test file
        Returns:
            data loaded from the json file
        """
        with open(path) as json_data:
            automation_data = json.load(json_data)

        return automation_data
