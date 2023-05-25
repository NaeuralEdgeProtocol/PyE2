# -*- coding: utf-8 -*-
"""
Copyright (C) 2017-2021 Andrei Damian, andrei.damian@me.com,  All rights reserved.

This software and its associated documentation are the exclusive property of the creator. 
Unauthorized use, copying, or distribution of this software, or any portion thereof, 
is strictly prohibited.

Parts of this software are licensed and used in software developed by Knowledge Investment Group SRL.
Any software proprietary to Knowledge Investment Group SRL is covered by Romanian and  Foreign Patents, 
patents in process, and are protected by trade secret or copyright law.

Dissemination of this information or reproduction of this material is strictly forbidden unless prior 
written permission from the author.

"""

import base64
import sys
import zlib


class CodeUtils:
  """
  This class should be used either as a associated object for code checking or
  as a mixin for running code
  """

  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(CodeUtils, cls).__new__(cls)
    return cls.instance

  def __init__(self):
    super(CodeUtils, self).__init__()
    return

  def __msg(self, m, color='d'):
    if hasattr(self, 'P'):
      self.P(m, color=color)
    elif hasattr(self, 'log'):
      self.log.P(m, color=color)
    else:
      print(m)
    return

  def code_to_base64(self, code, verbose=True, compress=True):
    if verbose:
      self.__msg("Processing:\n{}".format(code), color='y')
    l_i = len(code)
    l_c = -1
    b_code = bytes(code, 'utf-8')
    if compress:
      b_code = zlib.compress(b_code, level=9)
      l_c = sys.getsizeof(b_code)
    b_encoded = base64.b64encode(b_code)
    str_encoded = b_encoded.decode('utf-8')
    l_b64 = len(str_encoded)
    self.__msg("Code checking and serialization suceeded. Initial/Compress/B64: {}/{}/{}".format(
        l_i, l_c, l_b64), color='g'
    )
    return str_encoded

  def compress_bytes(self, data):
    if not isinstance(data, bytes):
      data = bytes(str(data), 'utf-8')
    zip_data = zlib.compress(data)
    return zip_data

  def decompress_bytes(self, zip_data):
    if not isinstance(zip_data, bytes):
      raise ValueError('`decompress_bytes` input must be bytes type')
    data = zlib.decompress(zip_data)
    return data

  def compress_text(self, text):
    b_text = bytes(text, 'utf-8')
    b_code = zlib.compress(b_text, level=9)
    b_encoded = base64.b64encode(b_code)
    str_encoded = b_encoded.decode('utf-8')
    return str_encoded

  def decompress_text(self, b64text):
    decoded = None
    try:
      b_decoded = base64.b64decode(b64text)
      b_decoded = zlib.decompress(b_decoded)
      s_decoded = b_decoded.decode('utf-8')
      decoded = s_decoded
    except:
      pass
    return decoded
