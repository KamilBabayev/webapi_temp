#!/usr/bin/env python
""" Automation Audit Handler """

# Copyright 2018 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import logging
import json

from tornado import gen, escape
from tornado.httpclient import HTTPError, HTTPRequest

from webapi.common.base_handler import BaseHandler, GatewayAPIException

'''
We want to log everything to the standard output so docker handles it
'''
LOGGER = logging.getLogger('api-gateway')
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
                '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)


class AutomationAuditHandler(BaseHandler):
    """
    Handler to process the audit and diff workflow api calls
    """
    SUPPORTED_METHODS = ("GET", "POST")

    def initialize(self, http_provider, logic_provider):
        """
        Provides implementation wrapper for tornado
        :param http_provider: provider for http implementation
        :param logic_provider: provides implementation for logic of handler
        :return: None
        """
        self.http_provider = http_provider
        self.logic_provider = logic_provider

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
    def post(self, *args, **kwargs):
        """Method implements the post http request
        args:
            None Use json POST Body
        Returns:
            With 201 Status Code.
        """
        body = {'results': False}
        # This is setting the code to success by default
        status_code = 201

        body_data = json.loads(self.json_body)
        vm_names = None
        stack_name = None

        try:
            tenant_name = body_data['tenant_name']
            automation_name = body_data['automation_name']
        except KeyError as a_error:
            error_msg = 'Missing Required Data. Error: %s' % (str(a_error))
            raise GatewayAPIException(status_code=400, reason=error_msg)

        if 'vm_names' in body_data:
            vm_names = body_data['vm_names']

        if 'stack_name' in body_data:
            stack_name = body_data['stack_name']

        if not vm_names and not stack_name:
            LOGGER.error("Stack Name and VM Names list is None.")
            raise GatewayAPIException(status_code=400, reason="You must provide a list of VM Names or a Stack Name, both"
                                                              " are None.")

        try:
            # Step One - Query Automation Database for Audit Pipeline data
            audit_data = self.logic_provider.get_audit_data(automation_name=automation_name, tenant_name=tenant_name)
            # Step Two - Trigger Jenkins Pipeline determined from Audit Pipeline data
            audit_processed = yield self.logic_provider.trigger_audit(stack_name=stack_name,
                                                                      tenant_name=tenant_name,
                                                                      automation_name=automation_name,
                                                                      pipeline=audit_data['pipeline'],
                                                                      vm_names=vm_names)

            body = audit_processed

            # Step Three - Publish Event to Pipeline started ??????
        except Exception as an_error:
            error_msg = str(an_error)
            LOGGER.error('Occured in automation audit post: %s', error_msg)
            raise GatewayAPIException(status_code=400, reason=error_msg)

        self.set_status(status_code)
        self.write(body)
        self.finish()