#!/usr/bin/env python
''' async provider '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

from tornado import gen
from tornado.httpclient import AsyncHTTPClient


class AsyncProvider(object):
    ''' AsyncProvider '''

    @gen.coroutine
    def fetch_coroutine(self, request):
        """Method uses asysnc httpclient to get the data from the results api

        args:
            url: url to query
        Returns:
            response from the http request
        """
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(request)
        raise gen.Return(response)
