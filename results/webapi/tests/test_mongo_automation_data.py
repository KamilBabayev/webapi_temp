''' Unit Tests for Mongo Results Handler - Tests via a Mock '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import unittest
import json
import os
import tornado.testing

from webapi.webapi_app import MainApplication
from webapi.providers.test_results_provider import TestResultsProvider


class TestMongoAutomationData(tornado.testing.AsyncHTTPTestCase):
    ''' Simple base unit test class '''

    def get_app(self):
        ''' Overridding the get_app method '''
        provider = TestResultsProvider()
        return MainApplication(automation_data_provider=provider)

    def test_automation_data_post(self):
        ''' test_handler_valid_post - positive validation '''

        url = '/automation-data/mns-oam'
        body = '{"data":true}'

        response = self.fetch(url, method='POST', body=body, headers={"Content-Type": "application/json"})
        print 'Successfully post data, url at /automation-data/mns-oam => %s' %response.body
        self.assertEqual(response.code, 201)

    def test_get_automation_data(self):
        ''' Test GET without object id '''
        response = self.fetch('/automation-data')
        print 'Successfully get data, url at /automation-data => %s' % response.body
        self.assertEqual(response.code, 200)

    def test_get_automation_data_by_automation_name(self):
        ''' Test health check '''
        response = self.fetch('/automation-data/mns-oam')
        print 'Successfully get data, url at /automation-data/mns-oam => %s' % response.body
        self.assertEqual(response.code, 200)
        # error = json.loads(response.body)
        # self.assertIn('automation_data', error)
        # self.assertIn('error', error['automation_data'])
        # self.assertIn('message', error['automation_data']['error'])

if __name__ == '__main__':
    unittest.main()
