#!/usr/bin/env python
""" Provisioning Provider Base """

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
import ast

from webapi.providers.provisioning_provider_base import ProvisioningProviderBase
from webapi.common.base_handler import GatewayAPIException
from webapi.providers.async_provider import AsyncProvider

from webapi.common.publish_message import PublishMessage

from tornado import gen, escape
from tornado.httpclient import HTTPError, HTTPRequest

'''
We want to log everything to the standard output so docker handles it
'''
LOGGER = logging.getLogger('api-gateway')
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
                '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

REDIS_API_GATEWAY_PORT = os.getenv('REDIS_API_GATEWAY_PORT')
REDIS_API_SERVICE_ENDPOINT = os.getenv('REDIS_API_SERVICE_ENDPOINT')

RABBITMQ_SERVICE_ENDPOINT = os.getenv('RABBITMQ_SERVICE_ENDPOINT')
RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
RABBIT_PORT = os.getenv('RABBIT_PORT')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST')


class ProvisioningProvider(ProvisioningProviderBase):
    """
    Implements base AuditProviderBase abc
    """

    def trigger_automation(self, **kwargs):
        """
        Implementation of the abstract method in AuditProviderBase.
        In this mock method it just simulates calling a Jenkins API call
        :param kwargs: Audit Data needed to process the step
        :return: {result: True}
        """
        try:
            stack_name = kwargs['stack_name']
            tenant_name = kwargs['tenant_name']
            automation_data = kwargs['automation_data']
        except KeyError as an_error:
            error_msg = 'Missing Required Data. Error: %s' % (str(an_error))
            raise GatewayAPIException(status_code=400, reason=error_msg)

        try:
            message = {'stackname': stack_name, 'project_name': tenant_name,
                       'mgt_vn_name': automation_data['mgt_vn_name'], 'vnf_image_name': automation_data['vnf_image_name'],
                       'exchange': automation_data['exchange'], 'routing_key': automation_data['routing_key']}

            publisher = PublishMessage(RABBITMQ_SERVICE_ENDPOINT, RABBITMQ_USERNAME, RABBITMQ_PASSWORD, RABBITMQ_VHOST, RABBIT_PORT)
            publisher.publish(automation_data['exchange'], automation_data['routing_key'], message)

            result = {'result': True}
        except Exception as an_error:
            LOGGER.error(str(an_error))
            raise GatewayAPIException(status_code=400, reason=str(an_error))

        return result
    

    def trigger_testing_worker(self, **kwargs):
        """
        Implementation of the abstract method in AuditProviderBase.
        In this mock method it just simulates calling a Jenkins API call
        :param kwargs: Audit Data needed to process the step
        :return: {result: True}
        """
        try:
            stack_name = kwargs['stack_name']
            tenant_name = kwargs['tenant_name']
            automation_data = kwargs['automation_data']
        except KeyError as an_error:
            error_msg = 'Missing Required Data. Error: %s' % (str(an_error))
            raise GatewayAPIException(status_code=400, reason=error_msg)

        try:
            message = {'stackname': stack_name, 'project_name': tenant_name,
                       'vnf_image_name': automation_data['vnf_image_name'],
                       'exchange': automation_data['exchange'], 'routing_key': automation_data['routing_key']}

            publisher = PublishMessage(RABBITMQ_SERVICE_ENDPOINT, RABBITMQ_USERNAME, RABBITMQ_PASSWORD, RABBITMQ_VHOST, RABBIT_PORT)
            publisher.publish(automation_data['exchange'], automation_data['routing_key'], message)

            result = {'result': True}
        except Exception as an_error:
            LOGGER.error(str(an_error))
            raise GatewayAPIException(status_code=400, reason=str(an_error))

        return result


    @gen.coroutine
    def get_automation_data(self, **kwargs):
        """
        Implementation of the abstract method in AuditProviderBase.
        In this mock method it just sends back some mocked data to
        :param kwargs: stack_name and tenant_name
        :return: dict of mocked data for processing
        """
        try:
            stack_name = kwargs['automation_name']
        except KeyError as a_error:
            error_msg = 'Missing Required Data. Error: %s' % (str(a_error))
            raise GatewayAPIException(status_code=400, reason=error_msg)

        http_provider = AsyncProvider()
        stack_key = 'stack:%s' % stack_name
        # TODO: Refactor this to call a redis provider to return stack data, not to call api method here
        # TODO: Also keep in mind below I'm added the stack prefix to the url, when creating the stack
        #       I add the stack prefix to the redis key
        url = 'http://%s:%s/redis-data/keys/%s' % (REDIS_API_SERVICE_ENDPOINT, REDIS_API_GATEWAY_PORT, stack_key,)

        t_request = HTTPRequest(url=url, method="GET")

        try:
            response = yield http_provider.fetch_coroutine(t_request)
        except HTTPError as http_error:
            error_msg = 'Failed to get stack data: %s' % str(http_error)
            raise GatewayAPIException(status_code=400, reason=str(http_error))
        except Exception as error:
            error_msg = 'Failed to get stack data: %s' % str(error)
            raise GatewayAPIException(status_code=500, reason=error_msg)

        try:
            results_json = response.body
            results_data = escape.json_decode(results_json)
            stack_data_json = results_data['results'][stack_key]
            if stack_data_json:
                stack_data = ast.literal_eval(stack_data_json)
            else:
                stack_data = None
        except Exception as an_error:
            error_msg = str(an_error)
            raise GatewayAPIException(status_code=400, reason=error_msg)

        raise gen.Return(stack_data)