#!/usr/bin/env python
''' Automation Router Handler '''

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
import json
import ast

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

REDIS_API_GATEWAY_PORT = os.getenv('REDIS_API_GATEWAY_PORT')
REDIS_API_SERVICE_ENDPOINT = os.getenv('REDIS_API_SERVICE_ENDPOINT')

RABBITMQ_SERVICE_ENDPOINT = os.getenv('RABBITMQ_SERVICE_ENDPOINT')
RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
RABBITMQ_API_PORT = os.getenv('RABBITMQ_API_PORT')

# This is the name of the list where we store all automation stack info
STACKS_LIST_NAME = 'os-vnf-stacks'

AUTOMATION_API_GATEWAY_PORT = os.getenv('AUTOMATION_API_GATEWAY_PORT')
#or '8888'
AUTOMATION_API_SERVICE_ENDPOINT = os.getenv('AUTOMATION_API_SERVICE_ENDPOINT')
#or '192.168.69.10'

class AutomationRouterHandler(BaseHandler):
    """
    Implements the tornado web.RequestHandler.
    GET and POST methods permitted
    """
    SUPPORTED_METHODS = ("GET", "POST", "DELETE")

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
    def delete(self, *args, **kwargs):
        """Method implements the delete http request
        args:
            id: key to delete from redis database
        """
        status_code = 200
        results_data = {}

        stack_key = None

        # Let's first get the stack data so we can delete the queues
        args_length = len(self.path_args)
        if args_length == 1:
            stack_name = self.path_args[0]
            url = 'http://%s:%s/redis-data/keys/stack:%s' % (REDIS_API_SERVICE_ENDPOINT,
                                                          REDIS_API_GATEWAY_PORT, stack_name, )
        else:
            raise GatewayAPIException(status_code=400, reason="Invalid number of arguments")

        t_request = HTTPRequest(url=url, method="GET")

        try:
            response = yield self.http_provider.fetch_coroutine(t_request)
        except HTTPError as http_error:
            error_msg = 'Failed to delete stack data: %s' % str(http_error)
            raise GatewayAPIException(status_code=400, reason=str(http_error))
        except Exception as error:
            error_msg = 'Failed to delete stack data: %s' % str(error)
            raise GatewayAPIException(status_code=500, reason=error_msg)

        stack_result_json = response.body
        stack_results = escape.json_decode(stack_result_json)
        stack_key = 'stack:%s' % stack_name
        stack_json = stack_results['results'][stack_key]

        stack_data = ast.literal_eval(stack_json)

        automation_queue = stack_data['automation_queue']
        testing_queue = stack_data['test_queue']
        rabbit_vhost = stack_data['vhost']

        # Let's delete the stack from redis now
        if args_length == 1:
            stack_name = self.path_args[0]
            url = 'http://%s:%s/redis-data/list/%s/%s' % (REDIS_API_SERVICE_ENDPOINT,
                                                          REDIS_API_GATEWAY_PORT, STACKS_LIST_NAME, stack_name, )
        else:
            raise GatewayAPIException(status_code=400, reason="Invalid number of arguments")

        delete_request = HTTPRequest(url=url, method="DELETE")

        try:
            response = yield self.http_provider.fetch_coroutine(delete_request)
        except HTTPError as http_error:
            error_msg = 'Failed to delete stack data: %s' % str(http_error)
            raise GatewayAPIException(status_code=400, reason=str(http_error))
        except Exception as error:
            error_msg = 'Failed to delete stack data: %s' % str(error)
            raise GatewayAPIException(status_code=500, reason=error_msg)

        # Let's delete the automation queues from rabbit
        try:
            rabbit_url = 'http://%s:%s/api/queues/%s/%s' % (RABBITMQ_SERVICE_ENDPOINT, RABBITMQ_API_PORT, rabbit_vhost, automation_queue)
            rabbit_request = HTTPRequest(url=rabbit_url, method="DELETE", auth_username=RABBITMQ_USERNAME, auth_password=RABBITMQ_PASSWORD,
                                         headers={'Content-Type': 'application/json'})
            rabbit_response = yield self.http_provider.fetch_coroutine(rabbit_request)
        except HTTPError as http_error:
            error_msg = 'Failed removing automation queue: %s' % str(http_error)
            raise GatewayAPIException(status_code=400, reason=str(error_msg))
        except Exception as error:
            error_msg = 'Failed removing automation queue: %s' % str(error)
            raise GatewayAPIException(status_code=500, reason=error_msg)

        # Let's delete the test queue from rabbit
        try:
            rabbit_url = 'http://%s:%s/api/queues/%s/%s' % (RABBITMQ_SERVICE_ENDPOINT, RABBITMQ_API_PORT, rabbit_vhost, testing_queue)
            rabbit_request = HTTPRequest(url=rabbit_url, method="DELETE", auth_username=RABBITMQ_USERNAME, auth_password=RABBITMQ_PASSWORD,
                                         headers={'Content-Type': 'application/json'})
            rabbit_response = yield self.http_provider.fetch_coroutine(rabbit_request)
        except HTTPError as http_error:
            error_msg = 'Failed removing testing queue: %s' % str(http_error)
            raise GatewayAPIException(status_code=400, reason=str(error_msg))
        except Exception as error:
            error_msg = 'Failed removing testing queue: %s' % str(error)
            raise GatewayAPIException(status_code=500, reason=error_msg)

        response_msg = "Successfully removed stack %s" % (stack_name,)
        body = {"results": {"success": True, "message": response_msg}}

        self.set_status(status_code)
        self.write(body)
        self.finish()

    @gen.coroutine
    def get(self, *args, **kwargs):
        """Method implements the get http request
            Gets the data from Mongo database
           Gets the data from redis datastore
        args:
            id: key to get data from redis database
            automation_name: to get data from mongo database
        Returns:
            data responding to the id
        """
        ##### GET data from Automation_data collection of mongoDB (automation_API) ###############
        status_code = 200
        automation_data = {}
        LOGGER.debug('Port: %s', (AUTOMATION_API_GATEWAY_PORT,))

        args_length = len(self.path_args)
        if args_length == 0:
            url = 'http://%s:%s/automation-data' % (AUTOMATION_API_SERVICE_ENDPOINT, AUTOMATION_API_GATEWAY_PORT,)
        elif args_length == 1:
            automation_name = str(self.path_args[0])
            url = 'http://%s:%s/automation-data/%s' % (AUTOMATION_API_SERVICE_ENDPOINT, AUTOMATION_API_GATEWAY_PORT, automation_name,)
        else:
            raise GatewayAPIException(status_code=400, reason="Invalid number of arguments")

        t_request = HTTPRequest(url=url, method="GET")

        try:
            response = yield self.http_provider.fetch_coroutine(t_request)
        except HTTPError as http_error:
            error_msg = 'Failed to get automation data: %s' % str(http_error)
            raise GatewayAPIException(status_code=400, reason=str(http_error))
        except Exception as error:
            error_msg = 'Failed to get automation data: %s' % str(error)
            raise GatewayAPIException(status_code=500, reason=error_msg)

        automation_data_json = response.body
        automation_data = escape.json_decode(automation_data_json)

        self.set_status(status_code)
        self.write(automation_data)
        self.finish()
        ##########END########

        status_code = 200
        results_data = {}

        stack_key = None

        args_length = len(self.path_args)
        if args_length == 0:
            url = 'http://%s:%s/redis-data/list/%s' % (REDIS_API_SERVICE_ENDPOINT, REDIS_API_GATEWAY_PORT, STACKS_LIST_NAME,)
        elif args_length == 1:
            key = str(self.path_args[0])
            stack_key = 'stack:%s' % (key,)
            url = 'http://%s:%s/redis-data/keys/%s' % (REDIS_API_SERVICE_ENDPOINT, REDIS_API_GATEWAY_PORT, stack_key,)
        else:
            raise GatewayAPIException(status_code=400, reason="Invalid number of arguments")

        t_request = HTTPRequest(url=url, method="GET")

        try:
            response = yield self.http_provider.fetch_coroutine(t_request)
        except HTTPError as http_error:
            error_msg = 'Failed to get stack data: %s' % str(http_error)
            raise GatewayAPIException(status_code=400, reason=str(http_error))
        except Exception as error:
            error_msg = 'Failed to get stack data: %s' % str(error)
            raise GatewayAPIException(status_code=500, reason=error_msg)

        results_json = response.body
        results_data = escape.json_decode(results_json)

        if stack_key:
            stack_data_json = results_data['results'][stack_key]
            if stack_data_json:
                stack_data = ast.literal_eval(stack_data_json)
            else:
                stack_data = {"results": None}
        else:
            stack_data = results_data

        self.set_status(status_code)
        self.write(stack_data)
        self.finish()

    @gen.coroutine
    def post(self, *args, **kwargs):
        """Method implements the post http request
           Writes data to the redis datastore
           Creates RabbitMQ Automation Queues and binds together
        args:
            None Use json POST Body
        Returns:
            result of the insert of the result record. With 201 Status Code.
        """
        ####### add stack data to Mongo Automation database, automation_data collection #############

        body = {}
        status_code = 201   # This is setting the code to success by default
        auto_body_data = json.loads(self.json_body)
        if auto_body_data.has_key('ztp'):
            # check data and massage data
            try:
                massage_data = {
                    "ztp":{
                          "name": auto_body_data['ztp']['name'],
                          "regex": auto_body_data['ztp']['regex'],
                          "exchange": auto_body_data['ztp']['exchange'],
                          "automation_queue": auto_body_data['ztp']['automation_queue'],
                          "vnf_image_name": auto_body_data['ztp']['vnf_image_name'],
                          "mgt_vn_name": auto_body_data['ztp']['mgt_vn_name'],
                          "test_queue": auto_body_data['ztp']['test_queue'],
                          "test_routing_key": auto_body_data['ztp']['test_routing_key'],
                          "routing_key": auto_body_data['ztp']['routing_key'],
                          "vhost": auto_body_data['ztp']['vhost'],
                      },
                    "audit_service":{
                        "active": auto_body_data['audit_service']['active'],
                        "pipeline_name": auto_body_data['audit_service']['pipeline_name'],
                        "resolution": auto_body_data['audit_service']['resolution'],
                        "steps": auto_body_data['audit_service']['steps']
                    }
                }
                name = massage_data['ztp']['name']
                queue_name = massage_data['ztp']['automation_queue']
                rabbit_vhost = massage_data['ztp']['vhost']
                rabbit_exchange = massage_data['ztp']['exchange']
                rabbit_routing_key = massage_data['ztp']['routing_key']
                testing_queue = massage_data['ztp']['test_queue']
                testing_routing_queue = massage_data['ztp']['test_routing_key']

            except KeyError as a_error:
                error_msg = 'Missing Required Data. Error: %s' % (str(a_error))
                raise GatewayAPIException(status_code=400, reason=error_msg)
            # create post api call to store data to MongoDB
            try:
                url = 'http://%s:%s/automation-data/%s' % (AUTOMATION_API_SERVICE_ENDPOINT, AUTOMATION_API_GATEWAY_PORT, name,)
                t_request = HTTPRequest(url=url, method="POST",
                                    headers={'Content-Type': 'application/json'}, body=json.dumps(massage_data, encoding='utf-8'))
                response = yield self.http_provider.fetch_coroutine(t_request)
            except HTTPError as http_error:
                error_msg = 'Failed to save automation_data in MongoDB: %s' % str(http_error)
                raise GatewayAPIException(status_code=400, reason=str(error_msg))
            except Exception as error:
                error_msg = 'Failed to save automation_data in MongoDB: %s' % str(error)
                raise GatewayAPIException(status_code=500, reason=error_msg)



        # #### send data (POST method) to Redis DB#######
        # body = {}
        # # This is setting the code to success by default
        # status_code = 201
        #
        # body_data = json.loads(self.json_body)
        #
        # try:
        #     name = body_data['name']
        #     queue_name = body_data['automation_queue']
        #     rabbit_vhost = body_data['vhost']
        #     rabbit_exchange = body_data['exchange']
        #     rabbit_routing_key = body_data['routing_key']
        #     testing_queue = body_data['test_queue']
        #     testing_routing_queue = body_data['test_routing_key']
        # except KeyError as a_error:
        #     error_msg = 'Missing Required Data. Error: %s' % (str(a_error))
        #     raise GatewayAPIException(status_code=400, reason=error_msg)
        #
        # # Add the Stack data to the list
        # try:
        #     url = 'http://%s:%s/redis-data/list/os-vnf-stacks' % (REDIS_API_SERVICE_ENDPOINT, REDIS_API_GATEWAY_PORT,)
        #     t_request = HTTPRequest(url=url, method="POST",
        #                             headers={'Content-Type': 'application/json'}, body=json.dumps(body_data, encoding='utf-8'))
        #
        #     response = yield self.http_provider.fetch_coroutine(t_request)
        # except HTTPError as http_error:
        #     error_msg = 'Failed to save stack data: %s' % str(http_error)
        #     raise GatewayAPIException(status_code=400, reason=str(error_msg))
        # except Exception as error:
        #     error_msg = 'Failed to save stack data: %s' % str(error)
        #     raise GatewayAPIException(status_code=500, reason=error_msg)
        #
        # # Add the Stack data as a key
        # try:
        #     url = 'http://%s:%s/redis-data/keys' % (REDIS_API_SERVICE_ENDPOINT, REDIS_API_GATEWAY_PORT,)
        #     stack_key = "stack:%s" % name
        #     stack_data = {"key": stack_key, "value": body_data}
        #     t_request = HTTPRequest(url=url, method="POST",
        #                             headers={'Content-Type': 'application/json'}, body=json.dumps(stack_data, encoding='utf-8'))
        #     response = yield self.http_provider.fetch_coroutine(t_request)
        # except HTTPError as http_error:
        #     error_msg = 'Failed to save stack data: %s' % str(http_error)
        #     print error_msg
        #     raise GatewayAPIException(status_code=400, reason=str(error_msg))
        # except Exception as error:
        #     error_msg = 'Failed to save stack data: %s' % str(error)
        #     print error_msg
        #     raise GatewayAPIException(status_code=500, reason=error_msg)
        # ##################  END  ######################

        # Variables for the queue creation and bindings
        queue_data = {"auto_delete": False, "durable": True, "arguments": {}}
        test_binding_data = {"routing_key": testing_routing_queue, "arguments": {}}
        binding_data = {"routing_key": rabbit_routing_key, "arguments": {}}

        # This adds the new Queue to RabbitMQ
        try:
            rabbit_url = 'http://%s:%s/api/queues/%s/%s' % (RABBITMQ_SERVICE_ENDPOINT, RABBITMQ_API_PORT, rabbit_vhost, queue_name)
            rabbit_request = HTTPRequest(url=rabbit_url, method="PUT", auth_username=RABBITMQ_USERNAME, auth_password=RABBITMQ_PASSWORD,
                                         headers={'Content-Type': 'application/json'}, body=json.dumps(queue_data, encoding='utf-8'))
            rabbit_response = yield self.http_provider.fetch_coroutine(rabbit_request)
        except HTTPError as http_error:
            error_msg = 'Failed to create queue: %s' % str(http_error)
            raise GatewayAPIException(status_code=400, reason=str(error_msg))
        except Exception as error:
            error_msg = 'Failed to create queue: %s' % str(error)
            raise GatewayAPIException(status_code=500, reason=error_msg)

        # This adds the new testing Queue to RabbitMQ
        try:
            rabbit_url = 'http://%s:%s/api/queues/%s/%s' % (RABBITMQ_SERVICE_ENDPOINT, RABBITMQ_API_PORT, rabbit_vhost, testing_queue)
            rabbit_request = HTTPRequest(url=rabbit_url, method="PUT", auth_username=RABBITMQ_USERNAME, auth_password=RABBITMQ_PASSWORD,
                                         headers={'Content-Type': 'application/json'}, body=json.dumps(queue_data, encoding='utf-8'))
            rabbit_response = yield self.http_provider.fetch_coroutine(rabbit_request)
        except HTTPError as http_error:
            error_msg = 'Failed to create queue: %s' % str(http_error)
            raise GatewayAPIException(status_code=400, reason=str(error_msg))
        except Exception as error:
            error_msg = 'Failed to create queue: %s' % str(error)
            raise GatewayAPIException(status_code=500, reason=error_msg)

        # This adds the binding between the exchange and the queue
        try:
            rabbit_url = 'http://%s:%s/api/bindings/%s/e/%s/q/%s' % (RABBITMQ_SERVICE_ENDPOINT, RABBITMQ_API_PORT,
                                                                     rabbit_vhost, rabbit_exchange, queue_name)
            rabbit_request = HTTPRequest(url=rabbit_url, method="POST", auth_username=RABBITMQ_USERNAME, auth_password=RABBITMQ_PASSWORD,
                                         headers={'Content-Type': 'application/json'}, body=json.dumps(binding_data, encoding='utf-8'))
            rabbit_response = yield self.http_provider.fetch_coroutine(rabbit_request)
        except HTTPError as http_error:
            error_msg = 'Failed to create exchange to queue binding: %s' % str(http_error)
            raise GatewayAPIException(status_code=400, reason=error_msg)
        except Exception as error:
            error_msg = 'Failed to create exchange to queue binding: %s' % str(error)
            raise GatewayAPIException(status_code=500, reason=error_msg)

        # This adds the binding between the exchange and the queue
        try:
            rabbit_url = 'http://%s:%s/api/bindings/%s/e/%s/q/%s' % (RABBITMQ_SERVICE_ENDPOINT, RABBITMQ_API_PORT,
                                                                     rabbit_vhost, rabbit_exchange, testing_queue)
            rabbit_request = HTTPRequest(url=rabbit_url, method="POST", auth_username=RABBITMQ_USERNAME, auth_password=RABBITMQ_PASSWORD,
                                         headers={'Content-Type': 'application/json'}, body=json.dumps(test_binding_data, encoding='utf-8'))
            rabbit_response = yield self.http_provider.fetch_coroutine(rabbit_request)
        except HTTPError as http_error:
            error_msg = 'Failed to create exchange to queue binding: %s' % str(http_error)
            raise GatewayAPIException(status_code=400, reason=error_msg)
        except Exception as error:
            error_msg = 'Failed to create exchange to queue binding: %s' % str(error)
            raise GatewayAPIException(status_code=500, reason=error_msg)

        response_msg = "Successfully added stack %s" % (name,)
        body = {"results": {"success": True, "message": response_msg}}

        self.set_status(status_code)
        self.write(body)
        self.finish()
