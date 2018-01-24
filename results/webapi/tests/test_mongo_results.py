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
import tornado.testing

from webapi.webapi_app import MainApplication
from webapi.providers.test_results_provider import TestResultsProvider


class TestMongoResult(tornado.testing.AsyncHTTPTestCase):
    ''' Simple base unit test class '''

    def get_app(self):
        ''' Overridding the get_app method '''
        provider = TestResultsProvider()
        return MainApplication(results_provider=provider)

    def test_get_results(self):
        ''' Test GET without object id '''
        response = self.fetch('/automation/results')
        self.assertEqual(response.code, 200)

    def test_get_results_proper_id(self):
        ''' Test health check '''
        response = self.fetch('/automation/results/59cd5026711181000d0c9442')
        self.assertEqual(response.code, 200)

    def test_get_results_bad_id(self):
        ''' Test health check '''
        response = self.fetch('/automation/results/59c5026711181000d0c9442')
        self.assertEqual(response.code, 400)

    def test_get_results_verify_error(self):
        ''' Test health check '''
        response = self.fetch('/automation/results/59c5026711181000d0c9442')
        error = json.loads(response.body)
        self.assertIn('result', error)
        self.assertIn('error', error['result'])
        self.assertIn('message', error['result']['error'])

    def test_handler_valid_post(self):
        ''' test_handler_valid_post - positive validation '''

        url = '/automation/results'
        body = '{"data":true}'

        response = self.fetch(url, method='POST', body=body, headers={"Content-Type": "application/json"})
        self.assertEqual(response.code, 201)

    def test_handler_valid_result(self):
        ''' test_health_check_valid_result - positive validate result '''

        url = '/automation/results'
        body = '{"data":true}'

        response = self.fetch(url, method='POST', body=body, headers={"Content-Type": "application/json"})
        result = json.loads(response.body)

        self.assertIn('$oid', result)

    def test_handler_invalid_post(self):
        ''' test_handler_invalid_post should have 400 because no body data '''

        url = '/automation/results'
        body = ''

        response = self.fetch(url, method='POST', body=body, headers={"Content-Type": "application/json"})

        self.assertEqual(response.code, 400)

if __name__ == '__main__':
    unittest.main()
