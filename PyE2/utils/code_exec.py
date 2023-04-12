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
Created on Thu Jan 26 16:53:55 2023
"""

import zlib
import sys
import base64


def code_to_base64(plain_code, verbose=False, compress=True, code_checker_callback=None):
  if verbose:
    print("Processing:\n{}".format(plain_code), color='y')
  errors = None
  if code_checker_callback is not None:
    errors = code_checker_callback(plain_code)
  if errors is not None:
    print("Cannot serialize code due to: '{}'".format(errors), color='r')
    return None
  l_i = len(plain_code)
  l_c = -1
  b_code = bytes(plain_code, 'utf-8')
  if compress:
    b_code = zlib.compress(b_code, level=9)
    l_c = sys.getsizeof(b_code)
  b_encoded = base64.b64encode(b_code)
  str_encoded = b_encoded.decode('utf-8')
  l_b64 = len(str_encoded)
  if verbose:
    print("Code checking and serialization suceeded. Initial/Compress/B64: {}/{}/{}".format(
        l_i, l_c, l_b64), color='g'
    )
  return str_encoded
