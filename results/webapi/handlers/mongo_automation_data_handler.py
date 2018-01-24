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

from base_handler import BaseHandler, AutomationAPIException

'''
We want to log everything to the standard output so docker handles it
'''
LOGGER = logging.getLogger('results-api')
LOGGER.setLevel(logging.DEBUG)


class MongoAutomationDataHandler(BaseHandler):
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

    def initialize(self, automation_data_provider):
        """This implements the initialize method
        Returns:
            Nothing
        """
        self.automation_data_provider = automation_data_provider

    @gen.coroutine
    def get(self, *args, **kwargs):
        """Method implements the get http request
        Args:
            *args: pass in the automation_name as the last positional arg
                   /automation-data/mns-oam
                   if: /automation-data all data of automation_data collection are returned
        Returns:
            data responding to a specific automation_data based on automation_name
            or all the automation_data
        """
        status_code = 200
        automation_data_dict = {"automation_data": None}

        args_length = len(self.path_args)
        if args_length == 0:
            automation_name = None
        else:
            automation_name = str(self.path_args[0])

        automation_data = yield self.automation_data_provider.get_automation_data(automation_name)

        automation_data_dict = {"automation_data": automation_data}

        self.set_status(status_code)
        self.write(automation_data_dict)
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
            data = json.loads(self.json_body)
            automation_data = yield self.automation_data_provider.write_automation_data(data)
        except AttributeError as attrex:
            LOGGER.error(str(attrex))
            raise AutomationAPIException(status_code=400, reason=str(attrex))

        self.set_status(201, "Created")
        self.write(automation_data)
        self.finish()
