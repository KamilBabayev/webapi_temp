#!/usr/bin/env python
''' Health Check Handler '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

from tornado import gen, web


class HealthCheckHandler(web.RequestHandler):
    """Implements the tornado web.RequestHandler. Just a simple health check that returns 200 OK GET methods permitted"""
    SUPPORTED_METHODS = ("GET")

    def data_received(self, chunk):
        pass

    @gen.coroutine
    def get(self, *args, **kwargs):
        """Method implements the get http request
        Returns:
            data responding to the successful healthcheck
        """
        data = {"success": True}

        self.set_status(200, "OK")
        self.write(data)
        self.finish()
