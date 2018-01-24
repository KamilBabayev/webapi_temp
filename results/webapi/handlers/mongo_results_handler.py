#!/usr/bin/env python

''' Mongo Results Handler '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import logging
import json

from bson.objectid import ObjectId
from bson.errors import InvalidId

from tornado import gen

from base_handler import BaseHandler, ResultsAPIException

'''
We want to log everything to the standard output so docker handles it
'''
LOGGER = logging.getLogger('results-api')
LOGGER.setLevel(logging.DEBUG)


class MongoResultsHandler(BaseHandler):
    """
    This is the handler for Mongo Results
    """
    SUPPORTED_METHODS = ("GET", "POST", "PUT")

    def data_received(self, chunk):
        """ This implements data_received method """
        pass

    @gen.coroutine
    def prepare(self):
        """This Method overrides the prepare method to handle json post data
        Returns:
            Does not return data but modifies the underlying json_body param
        """
        if self.request.body:
            if self.request.headers["Content-Type"] and self.request.headers["Content-Type"].startswith("application/json") and self.request.body:
                self.json_body = self.request.body
            else:
                self.json_body = None

    def initialize(self, results_provider):
        """This implements the initialize method
        Returns:
            Nothing
        """
        self.results_provider = results_provider

    @gen.coroutine
    def get(self, *args, **kwargs):
        """Method implements the get http request
        Args:
            *args: pass in the objectid as the last positional arg
                   /automation/results/59cd5026711181000d0c944
                   if: /automation/results all results are returned
        Returns:
            data responding to a specific result based on objectId
            or all the results
        """
        status_code = 200
        results_dict = {"results": None}

        args_length = len(self.path_args)
        if args_length == 0:
            result_id = None
        else:
            result_id = str(self.path_args[0])
            try:
                ObjectId(result_id)
            except InvalidId as invalid_id_ex:
                LOGGER.error('invalid id %s', result_id)
                raise ResultsAPIException(reason=str(invalid_id_ex), status_code=400)

        results = yield self.results_provider.get_results(result_id)

        results_dict = {"results": results}

        self.set_status(status_code)
        self.write(results_dict)
        self.finish()

    @gen.coroutine
    def post(self, *args, **kwargs):
        """Method implements the get http request
        Args:
            No url arguments.
            Pass data as json body.
        Returns:
            the objectid is returned.
        """
        try:
            result_data = json.loads(self.json_body)
            results = yield self.results_provider.write_result(result_data)
        except AttributeError as attrex:
            LOGGER.error(str(attrex))
            raise ResultsAPIException(status_code=400, reason=str(attrex))

        self.set_status(201, "Created")
        self.write(results)
        self.finish()
