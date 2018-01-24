#!/usr/bin/env python
''' Automation Provision Handler '''

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

from tornado import gen, escape

from webapi.common.base_handler import BaseHandler, GatewayAPIException

'''
We want to log everything to the standard output so docker handles it
'''
LOGGER = logging.getLogger('api-gateway')
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
                '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)


class AutomationProvisionHandler(BaseHandler):
    """
    Handler to process the audit and diff workflow api calls
    """

    def initialize(self, http_provider, provision_provider):
        ''' provides implementation of base method
        args:
            provider: provides logic to implement data

        '''
        self.http_provider = http_provider
        self.provision_provider = provision_provider

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
        body = {}
        # This is setting the code to success by default
        status_code = 201

        body_data = json.loads(self.json_body)

        try:
            stack_name = body_data['stack_name']
            automation_name = body_data['automation_name']
            tenant_name = body_data['tenant_name']
        except KeyError as a_error:
            error_msg = 'Missing Required Data. Error: %s' % (str(a_error))
            raise GatewayAPIException(status_code=400, reason=error_msg)

        try:
            # Step One - Query Automation Database for Automation Provisioning Data
            if self.provision_provider:
                automation_data = yield self.provision_provider.get_automation_data(automation_name=automation_name)
                body = {"results": automation_data}
                # Step Two - Trigger Automation determined from Automation Provisioning data
                result = self.provision_provider.trigger_automation(stack_name=stack_name, automation_data=automation_data, tenant_name=tenant_name)
                if result['result']:
                    msg = 'Successfully kicked off automation for stack: %s at tenant name: %s' % (stack_name, tenant_name,)
                    body = {"results": msg}
                else:
                    msg = 'Failed to kick off automation for stack: %s at tenant name: %s' % (stack_name, tenant_name,)
                    body = {"results": msg}
            else:
                LOGGER.error('Provision Provider is None.')
                raise Exception('Internal Coding Error.')
        except Exception as an_error:
            error_msg = str(an_error)
            LOGGER.exception(error_msg)
            raise GatewayAPIException(status_code=400, reason=error_msg)

        self.set_status(status_code)
        self.write(body)
        self.finish()
