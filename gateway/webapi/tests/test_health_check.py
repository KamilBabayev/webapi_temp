''' Health Check Unittest '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import unittest

import tornado.testing

from webapi.gateway_app import MainApplication


class TestHealthCheck(tornado.testing.AsyncHTTPTestCase):
    ''' Simple base unit test class '''

    def get_app(self):
        ''' Overridding the get_app method '''
        return MainApplication()

    def test_health_check_positive(self):
        ''' Test health check '''
        response = self.fetch('/healthcheck')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, '{"success": true}')

    def test_health_check_negative(self):
        ''' Test health check '''
        response = self.fetch('/healthcheck/32jv0')
        self.assertEqual(response.code, 404)

    def test_health_check_invalid_post(self):
        ''' Test invalid post '''

        url = '/healthcheck'
        body = '{"data":true}'

        response = self.fetch(url, method="POST", headers={'Content-Type': 'application/json'}, body=body)
        self.assertEqual(response.code, 405)

if __name__ == '__main__':
    unittest.main()
