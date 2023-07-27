# -*- coding: utf-8 -*-
"""
Copyright 2019-2021 Lummetry.AI (Knowledge Investment Group SRL). All Rights Reserved.


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
@author: Lummetry.AI
@project: 
@description:
@created on: Mon Jul 17 14:48:26 2023
@created by: damia
"""
import os
import numpy as np
from core.bc import DefaultBlockEngine, BCct
import json
from libraries import Logger

if __name__ == '__main__':
  l = Logger('BC', base_folder='.', app_folder='_local_cache')
  config_send = {
    BCct.K_PEM_LOCATION   : 'data',
    BCct.K_PEM_FILE       : 'e2.pem'  ,
    BCct.K_PASSWORD       : None,
  }

  config_bandit = {
    BCct.K_PEM_LOCATION   : 'data',
    BCct.K_PEM_FILE       : 'e2-bandit.pem'  ,
    BCct.K_PASSWORD       : None,
  }

  config_recv = {
    BCct.K_PEM_LOCATION   : 'data',
    BCct.K_PEM_FILE       : 'e2-recv.pem'  ,
    BCct.K_PASSWORD       : None,
  }
  
  c_sender = DefaultBlockEngine(name='e2-sender', log=l, config=config_send)
  
  c_s1 = DefaultBlockEngine(name='e2-sender', log=l, config=config_send)
    
  data = {str(x):x for x in np.random.randint(0,10, size=10).tolist()}
  data['5'] = {str(x):x for x in np.random.randint(10,20, size=5).tolist()}
  signature = c_sender.sign(data, use_digest=True)
  l.P("Data:\n{}".format(json.dumps(data, indent=4)))
  
  
  data_json = json.dumps(data)

  ###
  ###
  ###

  c_bandit = DefaultBlockEngine(name='e2-bandit', log=l, config=config_bandit)
  intercepted_data = json.loads(data_json)
  intercepted_data['5'] = None
  original_sender = intercepted_data.pop(BCct.SENDER)
  original_sign = intercepted_data.pop(BCct.SIGN)
  original_hash = intercepted_data.pop(BCct.HASH, None)
  use_digest = False
  # if original_hash is not None:
  #   use_digest = True
  fake_signature = c_bandit.sign(intercepted_data, add_data=True, use_digest=use_digest)
  intercepted_data[BCct.SIGN] = fake_signature
  intercepted_data[BCct.SENDER] = original_sender
  data_json_bandit = json.dumps(intercepted_data)
  
  ###
  ###
  ###
  
  c_receiver = DefaultBlockEngine(name='e2-consumer', log=l, config=config_recv)
  
  received_data_bandit = json.loads(data_json_bandit)  
  res = c_receiver.verify(dct_data=received_data_bandit)
  l.P("Received:\n{}\n\nSignature: {}".format(
    json.dumps(json.loads(data_json_bandit), indent=4),
    res
  ))
  
  received_data_original = json.loads(data_json)  
  res = c_receiver.verify(dct_data=received_data_original)
  l.P("Received:\n{}\n\nSignature: {}".format(
    json.dumps(json.loads(data_json), indent=4),
    res
  )) 
  
  
  