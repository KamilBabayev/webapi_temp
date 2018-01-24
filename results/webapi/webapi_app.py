#!/usr/bin/env python
''' WebApp API '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.
import os
import tornado.ioloop
import tornado.web
import tornado.httpclient

from handlers.mongo_automation_data_handler import MongoAutomationDataHandler
from handlers.mongo_results_handler import MongoResultsHandler
from providers.mongo_auto_data_provider import MongoAutomationDataProvider
from providers.mongo_results_provider import MongoResultsProvider
from handlers.healthcheck_handler import HealthCheckHandler

MONGODB_PORT = os.getenv('MONGODB_PORT') or '27017'
AUTOMATION_RESULTS_PORT = os.getenv('AUTOMATION_RESULTS_PORT') or '9797'
MONGODB_RESULTS_SERVICE_ENDPOINT = os.getenv('MONGODB_RESULTS_SERVICE_ENDPOINT') or '192.168.69.10'
MONGODB_USER = os.getenv('MONGODB_USER')
MONGODB_PASSWORD = os.getenv('MONGODB_USER_PASS')


class MainApplication(tornado.web.Application):
    """Wraps a tornado web application into a class"""

    def __init__(self, **kwargs):
        """Simple init method.  Looks for kwargs

        Args:
            kwargs: pass in the results_provider parameter
        """
        provider = None
        auto_data_provider = None
        if 'results_provider' in kwargs:
            provider = kwargs['results_provider']

        if 'automation_data_provider' in kwargs:
            auto_data_provider = kwargs['automation_data_provider']

        handlers = [
            (r"/healthcheck", HealthCheckHandler),
            (r"/automation-data", MongoAutomationDataHandler, dict(automation_data_provider=auto_data_provider)),  #get
            (r"/automation-data/([^/]*)", MongoAutomationDataHandler, dict(automation_data_provider=auto_data_provider)),  #get,post
            (r"/automation/results", MongoResultsHandler, dict(results_provider=provider)),
            (r"/automation/results/([^/]*)", MongoResultsHandler, dict(results_provider=provider))

        ]
        kwargs['debug'] = False
        super(MainApplication, self).__init__(handlers, **kwargs)


if __name__ == "__main__":
    PROVIDER = MongoResultsProvider(MONGODB_USER, MONGODB_PASSWORD, MONGODB_PORT, MONGODB_RESULTS_SERVICE_ENDPOINT)
    AUTOMATION_DATA_PROVIDER = MongoAutomationDataProvider(MONGODB_USER, MONGODB_PASSWORD, MONGODB_PORT, MONGODB_RESULTS_SERVICE_ENDPOINT)
    APP = MainApplication(results_provider=PROVIDER, automation_data_provider=AUTOMATION_DATA_PROVIDER)
    SERVER = tornado.httpserver.HTTPServer(APP)
    SERVER.bind(AUTOMATION_RESULTS_PORT)
    SERVER.start(0)  # forks one process per cpu
    tornado.ioloop.IOLoop.current().start()
