""" Gateway App """

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

from webapi.redis_data_api.redis_api_handler import RedisAPIHandler
from webapi.redis_data_api.redis_api_list_handler import RedisAPIListHandler
from webapi.auto_results_api.auto_results_handler import AutomationResultsHandler
from webapi.health_check_api.health_check_handler import HealthCheckHandler
from webapi.automation.automation_router_handler import AutomationRouterHandler
from webapi.automation.automation_audit_handler import AutomationAuditHandler
from webapi.automation.audit_pipeline_handler import AutomationAuditPipelineHandler
from webapi.automation.automation_provision_handler import AutomationProvisionHandler
from webapi.automation.testing_worker_provision_handler import TestingWorkerProvisionHandler

from webapi.providers.async_provider import AsyncProvider
from webapi.providers.audit_provider_mock import AuditProviderMock
from webapi.providers.provisioning_provider import ProvisioningProvider

API_GATEWAY_PORT = os.getenv('API_GATEWAY_PORT')


class MainApplication(tornado.web.Application):
    """Wraps a tornado web application into a class"""
    def __init__(self, **kwargs):
        """Simple init method.  Looks for kwargs

        Args:
            kwargs: empty
        """
        logic_provider = None
        audit_provider = None
        provision_provider = None
        if 'logic_provider' in kwargs:
            logic_provider = kwargs['logic_provider']

        if 'audit_provider' in kwargs:
            audit_provider = kwargs['audit_provider']

        if 'provision_provider' in kwargs:
            provision_provider = kwargs['provision_provider']

        handlers = [
            (r"/automation/data", AutomationRouterHandler, dict(logic_provider=logic_provider)),
            (r"/automation/data/([^/]*)", AutomationRouterHandler, dict(logic_provider=logic_provider)),
            (r"/automation/stacks", AutomationRouterHandler, dict(logic_provider=logic_provider)),
            (r"/automation/stacks/provision", AutomationProvisionHandler, dict(http_provider=logic_provider, provision_provider=provision_provider)),
            (r"/automation/stacks/testprovision", TestingWorkerProvisionHandler, dict(http_provider=logic_provider, provision_provider=provision_provider)),
            (r"/automation/stacks/([^/]*)", AutomationRouterHandler, dict(logic_provider=logic_provider)),
            (r"/automation/audit", AutomationAuditHandler, dict(http_provider=logic_provider, logic_provider=audit_provider)),
            (r"/automation/audit/pipeline", AutomationAuditPipelineHandler, dict(http_provider=logic_provider, logic_provider=audit_provider)),
            (r"/redis-data/keys", RedisAPIHandler, dict(logic_provider=logic_provider)),
            (r"/redis-data/keys/([^/]*)", RedisAPIHandler, dict(logic_provider=logic_provider)),
            (r"/redis-data/list/([^/]*)", RedisAPIListHandler, dict(logic_provider=logic_provider)),
            (r"/automation/results", AutomationResultsHandler, dict(logic_provider=logic_provider)),
            (r"/automation/results/([^/]*)", AutomationResultsHandler, dict(logic_provider=logic_provider)),
            (r"/healthcheck", HealthCheckHandler)
        ]
        super(MainApplication, self).__init__(handlers, **kwargs)


if __name__ == "__main__":
    PROVIDER = AsyncProvider()
    AUDIT_MOCK = AuditProviderMock()
    PROVISIONING_PROVIDER = ProvisioningProvider()
    APP = MainApplication(logic_provider=PROVIDER, audit_provider=AUDIT_MOCK, provision_provider=PROVISIONING_PROVIDER)
    SERVER = tornado.httpserver.HTTPServer(APP)
    SERVER.bind(API_GATEWAY_PORT)
    SERVER.start(0)  # forks one process per cpu
    tornado.ioloop.IOLoop.current().start()
