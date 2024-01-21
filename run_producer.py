#!/usr/bin/env python
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Producer
import time

if __name__ == '__main__':
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument('config_file', type=FileType('r'))
    parser.add_argument('topic')
    parser.add_argument('msg')
    args = parser.parse_args()

    # Parse the configuration.
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser['default'])

    # Create Producer instance
    producer = Producer(config)

    # Optional per-message delivery callback (triggered by poll() or flush())
    # when a message has been successfully delivered or permanently
    # failed delivery (after retries).
    def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print("Topic {}, Event msg = {}".format(msg.topic(), msg.value().decode('utf-8')))

    data = open('/project/hands-on/beach-water-quality-automated-sensors-1.csv','r').read().split("\n")
    for msg in data:
        producer.produce(args.topic, msg, callback=delivery_callback)
        print(msg)
        time.sleep(1)
    

    # producer.produce(args.topic, args.msg, callback=delivery_callback)

    # Block until the messages are sent.
    producer.poll(10000)
    producer.flush()