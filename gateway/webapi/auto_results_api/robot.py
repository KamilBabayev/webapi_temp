#!/usr/bin/env python
''' Auto Results Handler '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import os
import logging
import sys

from tornado import gen, escape
from tornado.httpclient import HTTPError, HTTPRequest

from webapi.common.base_handler import BaseHandler, GatewayAPIException

'''
We want to log everything to the standard output so docker handles it
'''
LOGGER = logging.getLogger('api-gateway')
LOGGER.setLevel(logging.DEBUG)

CH = logging.StreamHandler(sys.stdout)
CH.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

AUTOMATION_API_GATEWAY_PORT = os.getenv('AUTOMATION_API_GATEWAY_PORT') or '8888'
AUTOMATION_API_SERVICE_ENDPOINT = os.getenv('AUTOMATION_API_SERVICE_ENDPOINT') or '192.168.69.10'


class RobotTestsResultsHandler(BaseHandler):
    """
    Implements the tornado web.RequestHandler.
    GET and POST methods permitted
    """
    SUPPORTED_METHODS = ("GET", "POST")

    def initialize(self, logic_provider):
        ''' provides implementation of base method
        args:
            provider: provides logic to implement data
        '''
        self.http_provider = logic_provider

    def data_received(self, chunk):
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

    @gen.coroutine
    def get(self, *args, **kwargs):
        """Method implements the get http request

        args:
            id: key to get data from results db
        Returns:
            data responding to the id
        """
        status_code = 200
        results_data = {}
        LOGGER.debug('Port: %s', (AUTOMATION_API_GATEWAY_PORT,))

        args_length = len(self.path_args)
        if args_length == 0:
            url = 'http://%s:%s/automation/results/testing' % (AUTOMATION_API_SERVICE_ENDPOINT, AUTOMATION_API_GATEWAY_PORT,)
        elif args_length == 1:
            result_id = str(self.path_args[0])
            url = 'http://%s:%s/automation/results/testing/%s' % (AUTOMATION_API_SERVICE_ENDPOINT, AUTOMATION_API_GATEWAY_PORT, result_id,)
        else:
            raise GatewayAPIException(status_code=400, reason="Invalid number of arguments")

        t_request = HTTPRequest(url=url, method="GET")

        try:
            response = yield self.http_provider.fetch_coroutine(t_request)
        except HTTPError as http_error:
            raise GatewayAPIException(status_code=400, reason=str(http_error))

        results_json = response.body
        results_data = escape.json_decode(results_json)

        self.set_status(status_code)
        self.write(results_data)
        self.finish()

    @gen.coroutine
    def post(self, *args, **kwargs):
        """Method implements the post http request

        args:
            data: data
        Returns:
            result of the insert of the result record. should be an object id
        """
        url = 'http://%s:%s/automation/results/testing' % (AUTOMATION_API_SERVICE_ENDPOINT, AUTOMATION_API_GATEWAY_PORT,)
        t_request = HTTPRequest(url=url, method="POST",
                                headers={'Content-Type': 'application/json'}, body=self.json_body)

        body = {}
        # This is setting the code to success by default
        status_code = 201

        response = yield self.http_provider.fetch_coroutine(t_request)

        json_results = escape.json_decode(response.body)
        body = {"results": json_results}

        self.set_status(status_code)
        self.write(body)
        self.finish()
