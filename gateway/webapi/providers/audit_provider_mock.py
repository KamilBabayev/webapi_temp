#!/usr/bin/env python
""" Audit Provider Base """

# Copyright 2017/2018 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.
import os
import json
import logging

from webapi.providers.audit_provider_base import AuditProviderBase
from webapi.common.base_handler import GatewayAPIException
from webapi.providers.async_provider import AsyncProvider

from tornado import gen, escape
from tornado.httpclient import HTTPError, HTTPRequest

'''
We want to log everything to the standard output so docker handles it
'''
LOGGER = logging.getLogger('api-gateway')
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
                '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

WORKFLOW_SERVICE_ENDPOINT = os.getenv('WORKFLOW_SERVICE_ENDPOINT')
WORKFLOW_API_PORT = os.getenv('WORKFLOW_API_PORT') or None

class AuditProviderMock(AuditProviderBase):
    """
    Implements base AuditProviderBase abc
    """

    @gen.coroutine
    def trigger_audit(self, **kwargs):
        """
        Implementation of the abstract method in AuditProviderBase.
        In this mock method it just simulates calling a Jenkins API call
        :param kwargs: Audit Data needed to process the step
        :return: {result: True}
        """
        result = {'result': True}
        http_client = AsyncProvider()
        vm_names = None
        stack_name = None
        regex = None

        try:
            pipeline = kwargs['pipeline']
            automation_name = kwargs['automation_name']
            tenant_name = kwargs['tenant_name']
        except KeyError as a_error:
            error_msg = 'Missing Required Data. Error: %s' % (str(a_error))
            raise GatewayAPIException(status_code=400, reason=error_msg)

        if 'vm_names' in kwargs:
            vm_names = kwargs['vm_names']

        if 'stack_name' in kwargs:
            stack_name = kwargs['stack_name']


        body_data = {'stack_name': stack_name, 'automation_name': automation_name,
                     'tenant_name': tenant_name, 'step': 0,
                     'vm_names': vm_names}

        # Call the mock jenkins pipeline workflow starting at Step 0
        try:
            if not WORKFLOW_API_PORT:
                url = 'http://%s/mock/jenkins/pipeline' % (WORKFLOW_SERVICE_ENDPOINT,)
            else:
                url = 'http://%s:%s/mock/jenkins/pipeline' % (WORKFLOW_SERVICE_ENDPOINT, WORKFLOW_API_PORT,)

            request = HTTPRequest(url=url, method="POST",
                                  headers={'Content-Type': 'application/json'}, body=json.dumps(body_data,
                                                                                                encoding='utf-8'))


            response = yield http_client.fetch_coroutine(request)
            if response.code != 201:
                raise Exception('Failed calling the jenkins pipeline')

        except Exception as error:
            error_msg = str(error)
            raise GatewayAPIException(status_code=400, reason=error_msg)

        raise gen.Return(result)

    def get_audit_data(self, **kwargs):
        """
        Implementation of the abstract method in AuditProviderBase.
        In this mock method it just sends back some mocked data to
        :param kwargs: stack_name and tenant_name
        :return: dict of mocked data for processing
        """
        try:
            automation_name = kwargs['automation_name']
            tenant_name = kwargs['tenant_name']
        except KeyError as a_error:
            error_msg = 'Missing Required Data. Error: %s' % (str(a_error))
            raise GatewayAPIException(status_code=400, reason=error_msg)

        result = {'pipeline': 'mns-oam-audit-pipeline', 'regex': 'STACK_[0-9]+_ZRDM3FRWL[a-zA-Z0-9]+',
                  'exchange':'att.automation', 'audit_routing_key': 'audit-worker',
                  'steps':[{'playbook': 'audit.yml'}, {'playbook': 'true_up.yml'}],
                  'vnf_image_name': 'vSRX_build3-image'}

        return result