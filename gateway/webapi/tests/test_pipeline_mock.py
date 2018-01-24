""" Pipeline Results Unittest """

# Copyright 2017/2018 Juniper Networks, Inc. All rights reserved.
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

from tornado import gen
from webapi.gateway_app import MainApplication

from webapi.providers.audit_provider_mock import AuditProviderMock
from webapi.providers.async_provider import AsyncProvider

from webapi.common.base_handler import GatewayAPIException


class TestPipelineMock(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        """
        Overriding the get_app method
        :return: None
        """
        provider = AuditProviderMock()
        http_provider = AsyncProvider()

        return MainApplication(logic_provider = http_provider, audit_provider = provider, provision_provider = None)

    def test_simple(self):
        """
        Simple Test to assert 1==1
        :return: None
        """
        self.assertEquals(1, 1)

    def test_get_pipeline(self):
        """
        Tests that mock data is returned
        :return: the mock data
        """
        url = '/automation/audit/pipeline'
        body = '{"pipeline":"pipeline_mns-oam", "vm_names":["vm12", "vm13"], "tenant_name":"jedi-fwvnfmgr", ' \
               '"automation_name":"mns-oam", "step":0, "image_name": "vSRX_build3-image"}'
        response = self.fetch(url, method="POST", headers={'Content-Type': 'application/json'}, body=body)

        self.assertEquals(201, response.code)

if __name__ == '__main__':
    unittest.main()