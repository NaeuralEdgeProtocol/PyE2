# -*- coding: utf-8 -*-
"""
Copyright 2019-2022 Lummetry.AI (Knowledge Investment Group SRL). All Rights Reserved.


* NOTICE:  All information contained herein is, and remains
* the property of Knowledge Investment Group SRL.  
* The intellectual and technical concepts contained
* herein are proprietary to Knowledge Investment Group SRL
* and may be covered by Romanian and Foreign Patents,
* patents in process, and are protected by trade secret or copyright law.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Knowledge Investment Group SRL.


@copyright: Lummetry.AI
@author: Lummetry.AI - AID
@project: 
@description:
Created on Thu Jan 26 14:57:44 2023
"""

import os
from time import sleep, time

from dotenv import load_dotenv

from PyE2 import Payload, Pipeline, Session

load_dotenv()

boxes = {}


def instance_on_data(pipeline: Pipeline, data: Payload):
  global boxes
  data['INSTANCES'].sort()
  boxes[data['BOX']] = (data['INSTANCES'], time())
  return


def instance_on_data2(pipeline: Pipeline, data: Payload):
  return


def pipeline_on_data(pipeline: Pipeline, signature: str, instance_id: str, data: Payload):
  pass


def pipeline_on_notification(pipeline: Pipeline, notification: dict):
  pipeline.P(
      "Received specific notification for pipeline {}".format(pipeline.name))
  return


dct_server = {
  'host': os.getenv('PYE2_HOSTNAME'),
  'port': int(os.getenv('PYE2_PORT')),
  'user': os.getenv('PYE2_USERNAME'),
  'pwd': os.getenv('PYE2_PASSWORD')
}

e2id = 'e2id'
sess = Session(**dct_server)
sess.connect()

listener_params = {k.upper(): v for k, v in dct_server.items()}
listener_params["PASS"] = listener_params["PWD"]
listener_params["TOPIC"] = "lummetry/ctrl"

pipeline = sess.attach_to_pipeline(
  e2id=e2id,
  pipeline_name='test_mqtt',
  on_data=pipeline_on_data,
  on_notification=pipeline_on_notification,
  max_wait_time=60)

# now start a cyclic process
inst = pipeline.attach_to_custom_instance('inst01', on_data=instance_on_data)


def generate_net_map():
  global boxes
  net_map_msgs = ["Printing network map"]
  for box, (instances, last_time) in boxes.items():
    if last_time - time() > 30:
      continue
    net_map_msgs.append(box + ":")
    for i in range(len(instances)):
      (pipeline, signature, instance) = instances[i]

      (o_pipeline, o_signature) = (None, None)
      if i != 0:
        (o_pipeline, o_signature, _) = instances[i - 1]

      same_pipeline = pipeline == o_pipeline
      same_signature = signature == o_signature

      if not same_pipeline:
        net_map_msgs.append(" --- " + pipeline + ":")
      if not same_pipeline or not same_signature:
        net_map_msgs.append("    --- " + signature + ":")
      net_map_msgs.append("        --- " + instance)

    net_map_msgs.append("")
  return "\n".join(net_map_msgs)


try:
  while True:
    sleep(10)

    pipeline.P(generate_net_map(), color='m')
except KeyboardInterrupt:
  pipeline.P("CTRL+C detected. Closing example..", color='r')


pipeline.close()
sess.close()
