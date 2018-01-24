''' Auto Results Unittest '''

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

from webapi.gateway_app import MainApplication

from webapi.providers.test_provider import TestProvider


class TestAutoResultsAPI(tornado.testing.AsyncHTTPTestCase):
    ''' Simple base unit test class '''

    def get_app(self):
        ''' Overridding the get_app method '''
        provider = TestProvider()
        return MainApplication(logic_provider=provider)

    def test_get_results_all(self):
        ''' test_get_results_all '''
        response = self.fetch('/automation/results')
        self.assertEqual(response.code, 200)

    def test_get_results_by_value(self):
        ''' test_get_results_by_value '''
        value = '48934'
        url = '/automation/results/%s' % (value,)

        response = self.fetch(url)
        self.assertEqual(response.code, 200)

    def test_post_valid_result(self):
        ''' test_handler_valid_result - positive validate result '''

        url = '/automation/results'
        body = '{"data":true}'

        response = self.fetch(url, method='POST', body=body, headers={"Content-Type": "application/json"})
        result = json.loads(response.body)

        self.assertIn('results', result)
        self.assertIn('$oid', result['results'])

    def test_get_results_400_code(self):
        ''' test_get_results_400_code '''
        value = '9999'
        url = '/automation/results/%s' % (value,)

        response = self.fetch(url)

        self.assertEqual(response.code, 400)
        error = json.loads(response.body)
        self.assertIn('result', error)
        self.assertIn('error', error['result'])
        self.assertIn('message', error['result']['error'])

    def test_get_results_400_error(self):
        ''' test_get_results_400_error '''
        value = '9999'
        url = '/automation/results/%s' % (value,)

        response = self.fetch(url)
        error = json.loads(response.body)
        self.assertEqual(response.code, 400)
        self.assertIn('result', error)
        self.assertIn('error', error['result'])
        self.assertIn('message', error['result']['error'])

    def test_fail_parameter_error(self):
        ''' test_fail_parameter_error '''
        value = '48934'
        url = '/automation/results/%s/%s' % (value, value,)

        response = self.fetch(url)
        self.assertEqual(response.code, 404)

if __name__ == '__main__':
    unittest.main()
