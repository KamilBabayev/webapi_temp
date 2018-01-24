#!/usr/bin/env python
''' testing provider '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

from tornado import gen
from tornado.httpclient import HTTPError


class MyRequest(object):

    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body


class TestProvider(object):
    ''' AsyncProvider '''

    @gen.coroutine
    def fetch_coroutine(self, request):
        """Method uses asysnc httpclient to get the data from the results api

        args:
            url: url to query
        Returns:
            response from the http request
        """
        url = request.url
        splits = url.split('/')
        key = splits[-1]

        if key == '9999':
            raise HTTPError(400, message='invalid key')
        elif request.method == 'POST':
            result = MyRequest(status_code=201, body='{"$oid": "59dd4a8f9f425f00107b9fdf"}')
            raise gen.Return(result)
        else:
            raise gen.Return('{"url":"%s"}' % url)
