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
from time import sleep

from dotenv import load_dotenv

from PyE2 import Payload, Session

load_dotenv()


def instance_on_data(pipeline, data: Payload):
  # this could refresh a UI
  pipeline.P('Receive specific message from PERIMETER_VIOLATION_02:inst01 (hardcoded)', color='m')


def another_instance_on_data(pipeline, data: Payload):
  # this could refresh a UI
  pipeline.P('Receive specific message from CUSTOM_EXEC_01:inst01 (hardcoded)')


def yet_another_pipeline_on_data(pipeline, signature, instance, data: Payload):
  # ...
  return


def pipeline_on_data(pipeline, signature, instance, data: Payload):
  # this could refresh a UI
  pipeline.P('Received from box {} by server {}, stream:{}, plugin: {}, instance:{}, the following data:{}'.format(
      pipeline.e2id,
      pipeline.session.server,
      pipeline.name,
      signature,
      instance,
      data
  ))


if __name__ == '__main__':

  e2id = 'e2id'

  dct_server = {
      'host': os.getenv('PYE2_HOSTNAME'),
      'port': int(os.getenv('PYE2_PORT')),
      'user': os.getenv('PYE2_USERNAME'),
      'pwd': os.getenv('PYE2_PASSWORD')
  }

  sess = Session(**dct_server)
  sess.connect()

  pipeline = sess.create_pipeline(
      e2id=e2id,
      name='test_normal',
      data_source='VideoStream',
      config={
          'URL': 0
      },
      plugins=None,
      on_data=pipeline_on_data
  )

  # now we start a perimeter intrusion functionality for low-res cameras with all
  # the other params default
  pipeline.start_plugin_instance(  # should return an id
      signature='PERIMETER_VIOLATION_01',
      instance_id='inst01',
      params={
          'AI_ENGINE': 'lowres_general_detector'
      },
      on_data=instance_on_data  # default None
  )

  plain_code = """
result="Data on node"
  """

  # now start a cyclic process
  instance = pipeline.start_custom_plugin(
      instance_id='inst01',
      plain_code=plain_code,
      params={},
      on_data=another_instance_on_data
  )

  try:
    sleep(30)  # wait for some info to appear adn trigger the stop
  except KeyboardInterrupt:
    pipeline.log.P("CTRL+C detected. Closing example..", color='r')

  pipeline.stop_plugin_instance('PERIMETER_VIOLATION_01', 'inst01')

  try:
    while True:
      pass
  except KeyboardInterrupt:
    pipeline.log.P("CTRL+C detected. Closing example..", color='r')

  pipeline.stop_plugin_instance(instance)

  sleep(3)  # mandatory to close the pipeline, might move it to stop call

  pipeline.close()

  # now close conn to comm server
  sess.close()
