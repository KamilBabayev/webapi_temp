#!/usr/bin/env python
''' Automation Audit Pipeline Handler '''

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
import json


from tornado import gen, escape
from tornado.httpclient import HTTPError, HTTPRequest

from webapi.common.base_handler import BaseHandler, GatewayAPIException
from webapi.common.publish_message import PublishMessage

'''
We want to log everything to the standard output so docker handles it
'''
LOGGER = logging.getLogger('api-gateway')
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
                '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

RABBITMQ_SERVICE_ENDPOINT = os.getenv('RABBITMQ_SERVICE_ENDPOINT')
RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
RABBIT_PORT = os.getenv('RABBIT_PORT')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST')

class AutomationAuditPipelineHandler(BaseHandler):
    """
    Handler to process the audit and diff workflow api calls
    """
    SUPPORTED_METHODS = ("GET", "POST")

    def initialize(self, http_provider, logic_provider):
        ''' provides implementation of base method
        args:
            provider: provides logic to implement data

        '''
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
        body = {}
        # This is setting the code to success by default
        status_code = 201

        vm_names = None
        stack_name = None

        body_data = json.loads(self.json_body)

        try:
            tenant_name = body_data['tenant_name']
            step = body_data['step']
            automation_name = body_data['automation_name']
            step = int(step)
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

        # Step One - Get Data Related to Audit Pipeline
        audit_data = self.logic_provider.get_audit_data(automation_name=automation_name, tenant_name=tenant_name)
        try:
            audit_routing_key = audit_data['audit_routing_key']
            exchange = audit_data['exchange']
            playbook = audit_data['steps'][step]
            pipeline = audit_data['pipeline']
            regex = audit_data['regex']
            image_name = audit_data['vnf_image_name']
        except KeyError as a_error:
            error_msg = 'Missing Required Data. Error: %s' % (str(a_error))
            raise GatewayAPIException(status_code=400, reason=error_msg)

        # Step Two - Publish Message to RabbitMQ
        try:
            message = {'playbook': playbook['playbook'], 'vm_names':vm_names, 'tenant_name': tenant_name,
                       'stackname': stack_name, 'pipeline': pipeline, 'step': step, 'regex': regex,
                       'image_name': image_name, 'automation_name': automation_name}
            publisher = PublishMessage(RABBITMQ_SERVICE_ENDPOINT, RABBITMQ_USERNAME, RABBITMQ_PASSWORD, RABBITMQ_VHOST, RABBIT_PORT)
            publisher.publish(exchange, audit_routing_key, message)
        except Exception as an_error:
            error_msg = 'error in publishing method: %s' % str(an_error)
            LOGGER.error(error_msg)
            raise GatewayAPIException(status_code=400, reason=error_msg)

        body = {'results': True}

        self.set_status(status_code)
        self.write(body)
        self.finish()