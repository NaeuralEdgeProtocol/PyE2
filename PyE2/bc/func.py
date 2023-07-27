# -*- coding: utf-8 -*-
"""
Copyright (C) 2017-2021 Andrei Damian, andrei.damian@me.com,  All rights reserved.

This software and its associated documentation are the exclusive property of the creator.
Unauthorized use, copying, or distribution of this software, or any portion thereof,
is strictly prohibited.

Parts of this software are licensed and used in software developed by Lummetry.AI.
Any software proprietary to Knowledge Investment Group SRL is covered by Romanian and  Foreign Patents,
patents in process, and are protected by trade secret or copyright law.

Dissemination of this information or reproduction of this material is strictly forbidden unless prior
written permission from the author


@copyright: Lummetry.AI
@author: Lummetry.AI
@project: 
@description:
@created on: Tue Jul 18 07:26:32 2023
@created by: AID
"""
import base64
import json

from hashlib import sha256
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

class BCct:
  SIGN      = 'EE_SIGN'
  SENDER    = 'EE_SENDER'
  HASH      = 'EE_HASH'
  ADDR_PREFIX   = "aixp_"

NON_DATA_FIELDS = [BCct.HASH, BCct.SIGN, BCct.SENDER]


def create_private_key():
  sk = ec.generate_private_key(curve=ec.SECP256K1())
  return sk


def pk_to_addr(pk):
  data = pk.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.CompressedPoint,
  )
  txt = BCct.ADDR_PREFIX + base64.urlsafe_b64encode(data).decode()
  return txt

def addr_to_pk(addr):
  simple_addr = addr.replace(BCct.ADDR_PREFIX, '')
  bpublic_key = base64.urlsafe_b64decode(simple_addr)
  pk = ec.EllipticCurvePublicKey.from_encoded_point(
    curve=ec.SECP256K1(), 
    data=bpublic_key
  )
  return pk
  

def sign_object(obj, sk):
  simple_object = {k : obj[k] for k in obj if k not in NON_DATA_FIELDS}
  data = json.dumps(simple_object, sort_keys=True, separators=(',',':')).encode()
  str_digest = sha256(data).hexdigest()
  bin_digest = str_digest.encode()
  signature = sk.sign(
    data=bin_digest,
    signature_algorithm=ec.ECDSA(hashes.SHA256())
    )
  str_signature = base64.urlsafe_b64encode(signature).decode()
  obj[BCct.SENDER] = pk_to_addr(sk.public_key())
  obj[BCct.SIGN] = str_signature
  obj[BCct.HASH] = str_digest
  return str_signature


def verify_signature(obj):
  addr = obj.get(BCct.SENDER)
  str_sign = obj.get(BCct.SIGN)
  valid = False
  assert addr is not None and str_sign is not None
  simple_object = {k : obj[k] for k in obj if k not in NON_DATA_FIELDS}
  data = json.dumps(simple_object, sort_keys=True, separators=(',',':')).encode()
  str_digest = sha256(data).hexdigest()
  bin_digest = str_digest.encode()
  pk = addr_to_pk(addr)
  try:
    assert str_digest == obj[BCct.HASH], "DIGEST_ERROR"
    signature = base64.urlsafe_b64decode(str_sign)
    pk.verify(signature, bin_digest, ec.ECDSA(hashes.SHA256()))
    valid = True
  except Exception as exc:
    error_msg = str(exc)
    if len(error_msg) == 0:
      error_msg = exc.__class__.__name__
    print(error_msg)
  return valid
  

if __name__ == '__main__':
  # testing code
  d = {'9'  : 9, '2':2, '3':3, '10':{'2':2,'100':100, '1':1}}
  sk = create_private_key()
  s = sign_object(d, sk)
  message = json.dumps(d)
  print("\n{}\n---------------".format(json.dumps(d, indent=4)))
  d1 = json.loads(message)
  d2 = json.loads(message)
  d0 = json.loads(message)
  d1['9'] = None
  d2[BCct.SIGN] = 'aaaabbbbcccc' # faking the signature
  print("Bandit 1:")
  v = verify_signature(d1)
  print(v)
  print("---------------")
  print("Bandit 2:")
  v = verify_signature(d2)
  print(v)
  print("---------------")
  print("Good guy:")
  v = verify_signature(d0)
  print(v)
  print("---------------")
  
  # '{"9": 9, "2": 2, "3": 3, "10": {"2": 2, "1": 1}, "EE_SENDER": "aixp_AnYCe3QIJiVWS-borGH4S0_Hv9AKM5ybP2tCWkH3zFJE", "EE_SIGN": "MEQCICp9p9MO-urtQXEJ8rrE7Kwa930PP86GElkE16YFtSWQAiA_0HChXFIzZIS0wQ0Ut2HsNuz_ZO90LHA019h1S4IDYA==", "EE_HASH": "c49af6451a698441f212539ac9b9d196bbf5a893ef8dfc430f21db967ec7263d"}'
  external_message = "put here your json" 
  if external_message != "put here your json":
    external_data = json.loads(external_message)
    v = verify_signature(external_data)
    print("Result on external message: {}".format(v))
  
  
  