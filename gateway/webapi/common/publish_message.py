#!/usr/bin/env python

''' Basic Publisher to RabbitMQ '''

# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License,
# which is located at http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by
# the parties, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.
import logging

from kombu import Producer, Connection, Exchange

'''
We want to log everything to the standard output so docker handles it
'''
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
                '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger('api-gateway')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

class PublishMessage(object):
    """
    Simple class that publishes a message to an
    Exchange and a routing key.
    """
    def __init__(self, host, username, password, vhost, port):
        """
        Initialize the class to comminicate with RabbitMQ
        :param host: Host or endpoint for rabbitmq
        :param username: Username to connect
        :param password: Password Credential to connect
        :param vhost: virtual host to connect to
        :param port: the port rabbitmq is listening on
        """
        self.host = host
        self.username = username
        self.password = password
        self.vhost = vhost
        self.port = port

        self.url = 'pyamqp://%s:%s@%s:%s/%s' % (username, password, host, port, vhost,)

    def publish(self, exchange_name, routing_key, message, exchange_type='topic', durable=True):
        """
        Publish Method to send a message to a specific exchange and routing key
        :param exchange_name: String: exchange name to connect to
        :param routing_key: String: routing key to send message to
        :param message: Dict: Dictionary object to convert to json and send to rabbitmq
        :param exchange_type: String: Default: topic exchange type that the exchange connection is expecting
        :param durable: Bool: Default: True if the message queue is durable
        :return: None
        """
        try:
            exchange = Exchange(exchange_name, exchange_type, durable=durable)

            with Connection(self.url) as conn:
                producer = conn.Producer(exchange=exchange, serializer='json')
                producer.publish(message, routing_key)

        except Exception as ex:
            LOGGER.error('Failed to publish message with error: %s', str(ex))
            raise