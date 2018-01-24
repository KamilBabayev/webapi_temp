#!/usr/bin/env python
''' Audit Provider Base '''

# Copyright 2017/2018 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import abc

class ProvisioningProviderBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_automation_data(self, **kwargs):
        """Function to get relevant Automation data from a source

        kwargs:
            pass in some data to the function for processing

        Returns:
            This should return the data required for processing the audit

        """
        return

    @abc.abstractmethod
    def trigger_automation(self, **kwargs):
        """Function to trigger the automation service

        kwargs:
            pass in some data to the function for processing

        Returns:
            Return results of method
        """
        return

    @abc.abstractmethod
    def trigger_testing_worker(self, **kwargs):
        """Function to trigger the testing worker service

        kwargs:
            pass in some data to the function for processing

        Returns:
            Return results of method
        """
        return