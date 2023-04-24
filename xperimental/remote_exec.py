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
print(os.environ['PYTHONPATH'].split(os.pathsep))

boxes = {}

custom_worker_code = """
_result=None
payload = plugin.dataapi_struct_data()
if payload is not None:
  plugin.P("Received data")

  payload_box_name = payload.get('EE_ID', payload.get('SB_ID'))
  payload_active_plugins = payload.get('ACTIVE_PLUGINS')

  if payload_box_name is not None and payload_active_plugins is not None:


    inst = []

    for active_plugin in payload_active_plugins:
      inst.append((active_plugin['STREAM_ID'], active_plugin['SIGNATURE'], active_plugin['INSTANCE_ID']))

    _result = {
      'BOX' : payload_box_name,
      'INSTANCES' : inst
    }
  else:
    plugin.P(payload)
    plugin.P(payload['EE_EVENT_TYPE'])
    plugin.P(payload_box_name)
    plugin.P(payload_active_plugins)
"""


def instance_on_data(pipeline: Pipeline, data: Payload):
  global boxes
  data['INSTANCES'].sort()
  boxes[data['BOX']] = (data['INSTANCES'], time())
  return


def instance_on_data2(pipeline: Pipeline, data: Payload):
  return


def pipeline_on_data(pipeline: Pipeline, signature: str, instance: str, data: Payload):
  pass


def pipeline_on_notification(pipeline, notification: dict):
  pipeline.P(
      "Received specific notification for pipeline {}".format(pipeline.name))
  return


def sess_on_hb(sess, e2id, hb):
  act_plug = hb['ACTIVE_PLUGINS']
  for plug in act_plug:
    sess.P((e2id, plug['STREAM_ID'], plug['SIGNATURE'], plug['INSTANCE_ID']))


dct_server = {
    'host': os.getenv('PYE2_HOSTNAME'),
    'port': int(os.getenv('PYE2_PORT')),
    'user': os.getenv('PYE2_USERNAME'),
    'pwd': os.getenv('PYE2_PASSWORD')
}

e2id = 'e2id'
sess = Session(**dct_server, on_heartbeat=sess_on_hb)
sess.connect()

listener_params = {k.upper(): v for k, v in dct_server.items()}
listener_params["PASS"] = listener_params["PWD"]
listener_params["TOPIC"] = "lummetry/ctrl"

pipeline = sess.create_pipeline(
    e2id=e2id,
    name='test_mqtt',
    data_source='IotQueueListener',
    config={
        'STREAM_CONFIG_METADATA': listener_params,
        "RECONNECTABLE": True,
    },
    plugins=None,
    on_data=pipeline_on_data,
    on_notification=pipeline_on_notification
)

# now start a ciclic process
pipeline.start_custom_plugin(
    instance_id='inst01',
    # plain_code_path="./custom_exec_scripts/custom_exec_tutorial.txt", # you can provide it as a file
    plain_code=custom_worker_code,
    params={},
    on_data=instance_on_data,
    # working_hours=
    process_delay=2
    # on_notification=instance_on_notification # TODO
)


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

    # pipeline.P(generate_net_map(), color='m')
except KeyboardInterrupt:
  pipeline.P("CTRL+C detected. Closing example..", color='r')


pipeline.close()
# pipeline2.close()
# now close conn to comm server
sess.close()
