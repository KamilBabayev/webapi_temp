#!/usr/bin/env python

''' Base HTTP Handler '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import json
import traceback

from tornado import web


class ResultsAPIException(web.HTTPError):
    ''' Base Exception for RequestHandler '''
    pass


class AutomationAPIException(web.HTTPError):
    ''' Base Exception for RequestHandler '''
    pass

class BaseHandler(web.RequestHandler):
    ''' Base Handler for RequestHandler '''
    def data_received(self, chunk):
        pass

    def write_error(self, status_code, **kwargs):

        self.set_header('Content-Type', 'application/json')
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(json.dumps({'result': {
                'error': {
                    'code': status_code,
                    'message': self._reason,
                    'traceback': lines,
                }
            }}))
        else:
            real_reason = self._reason
            self.set_status(status_code)
            self.write(json.dumps({'result': {
                'error': {
                    'code': status_code,
                    'message': real_reason
                }
            }}))
            self.finish()
