''' Integration Results Unittest '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import json
import unittest
import tornado.testing
import os

from webapi.gateway_app import MainApplication

from webapi.providers.async_provider import AsyncProvider
from webapi.common.base_handler import GatewayAPIException


class TestIntegrationAutomation(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        ''' Overridding the get_app method '''
        provider = AsyncProvider()
        return MainApplication(logic_provider=provider)

    def test_simple(self):
        self.assertEquals(1, 1)

    def test_stack_get(self):
        ''' test_stack_get '''
        url = '/automation/stacks'
        response = self.fetch(url, method="GET", headers={'Content-Type': 'application/json'})
        print response.body
        self.assertEquals(200, response.code)

    def test_stack_get_key(self):
        ''' test_stack_get '''
        url = '/automation/stacks/mns-oam'
        response = self.fetch(url, method="GET", headers={'Content-Type': 'application/json'})
        print response.body
        self.assertEquals(200, response.code)

    def test_stack_get_bad_key(self):
        ''' test_stack_get_key '''
        url = '/automation/stacks/paul'
        response = self.fetch(url, method="GET", headers={'Content-Type': 'application/json'})
        self.assertEquals(200, response.code)

    # def test_stack_post_bad_request(self):
    #     ''' test_stack_post_bad_request '''
    #     url = '/automation/stacks'
    #     body = '{"regex":"STACK_[0-9]+_ZRDM3FRWL[a-zA-Z0-9]+", "exchange":"att.automation", "automation_queue":"mns_evn", "test_queue": "mns_oam_test", "routing_key":"mns_evn", "vhost":"%2f"}'
    #     # with self.assertRaises(GatewayAPIException) as context:
    #     response = self.fetch(url, method="POST", headers={'Content-Type': 'application/json'}, body=body)
    #     result = json.loads(response.body)
    #     print result['result']['error']
    #     self.assertIsNotNone(result['result']['error'])

    # def test_stack_post(self):
    #     ''' test_stack_post '''
    #     url = '/automation/stacks'
    #     body = '{"name": "mns-oam", "regex":"STACK_[0-9]+_ZRDM3FRWL[a-zA-Z0-9]+", "exchange":"att.automation", "automation_queue":"mns_oam", "test_queue": "mns_oam_test", "routing_key":"mns_oam", "vhost":"%2f"}'
    #     response = self.fetch(url, method="POST", headers={'Content-Type': 'application/json'}, body=body)
    #     self.assertEquals(201, response.code)

    def test_post_automation_data_mongo(self):
        ''' test_stack_post '''
        url = '/automation/data/mns-oam'
        body = '{"ztp":{"name":"mns-oam","regex":"STACK_[0-9]+_ZRDM3FRWL[a-zA-Z0-9]+","exchange":"att.automation","automation_queue":"mns.oam","vnf_image_name":"vSRX_build3-image","mgt_vn_name":"MGT","test_queue":"mns.oam.test","test_routing_key":"mns.oam.test","routing_key":"mns.oam","vhost":"%2f"},"audit_service":{"active":true,"pipeline_name":"pipeline_mns-oam","resolution":["notify","true-up"],"steps":[{"playbook":"audit.yml"},{"playbook":"true-up.yml"}]}}'
        response = self.fetch(url, method="POST", headers={'Content-Type': 'application/json'}, body=body)
        self.assertEquals(201, response.code)

    def test_get_automation_data_mongo(self):
        ''' test_get_automation_data_mongo '''
        url = '/automation/data'
        response = self.fetch(url, method="GET", headers={'Content-Type': 'application/json'})
        print response.body
        self.assertEquals(200, response.code)

    def test_get_automation_data_by_field_mongo(self):
        # test_stack_get
        url = '/automation/data/mns-oam'
        response = self.fetch(url, method="GET", headers={'Content-Type': 'application/json'})
        print response.body
        self.assertEquals(200, response.code)

if __name__ == '__main__':
    unittest.main()
