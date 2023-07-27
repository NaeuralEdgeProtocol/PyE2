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
@created on: Mon Jul 17 14:44:49 2023
@created by: AID
"""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

from .base import BaseBlockEngine, VerifyMessage, BCct



class BaseBCEllipticCurveEngine(BaseBlockEngine):
  
  
  def _get_pk(self, private_key : ec.EllipticCurvePrivateKey) -> ec.EllipticCurvePublicKey:
    """
    Simple wrapper to generate pk from sk


    Returns
    -------
    public_key : EllipticCurvePublicKey
    
    """
    return super(BaseBCEllipticCurveEngine, self)._get_pk(private_key)

  
  def _sk_to_text(
      self, 
      private_key :  ec.EllipticCurvePrivateKey, 
      password=None, 
      fn=None
    ):
    """
    Serialize a EllipticCurvePrivateKey as text

    Parameters
    ----------
    private_key : EllipticCurvePrivateKey
      the secret key object.
      
    password: str
      password to be used for sk serialization
      
    fn: str:
      text file where to save the pk

    Returns
    -------
      the sk as text string

    """
    return super(BaseBCEllipticCurveEngine, self)._sk_to_text(
      private_key=private_key, 
      password=password, 
      fn=fn
    ) 
  
  #############################################################################
  ##
  ##          MANDATORY DEFINITIONS:
  ##
  #############################################################################

  def _create_new_sk(self) -> ec.EllipticCurvePrivateKey:
    """
    Simple wrapper to generated pk


    Returns
    -------
    private_key : EllipticCurvePrivateKey
    
    """
    private_key = ec.generate_private_key(curve=ec.SECP256K1())
    return private_key

  
  def _sign(
      self, 
      data : bytes, 
      private_key : ec.EllipticCurvePrivateKey, 
      text=False
    ):
    """
    Sign a binary message with Elliptic Curve
    

    Parameters
    ----------
    data : bytes
      the binary message.
      
    private_key : ec.EllipticCurvePrivateKey
      the private key object.
      
    text : bool, optional
      return the signature as text. The default is False.

    Returns
    -------
    signature as text or binary

    """
    signature = private_key.sign(
      data=data,
      signature_algorithm=ec.ECDSA(hashes.SHA256())
      )
    txt_signature = self._binary_to_text(signature)
    return txt_signature if text else signature
    
  def _verify(
      self, 
      public_key : ec.EllipticCurvePublicKey, 
      signature : bytes, 
      data : bytes
    ):
    """
    Verifies a `EllipticCurvePublicKey` signature on a binary `data` package
    

    Parameters
    ----------
    public_key : ec.EllipticCurvePublicKey
      the pk object.
      
    signature : bytes
      the binary signature.
      
    data : bytes
      the binary message.


    Returns
    -------
    result: VerifyMessage 
      contains `result.valid` and `result.message`

    """
    result = VerifyMessage()
    try:
      public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
      result.valid = True
      result.message = '<Signature OK>'
    except Exception as exp:
      err = str(exp)
      if len(err) == 0:
        err = exp.__class__.__name__
      result.message = err
      result.valid = False      
    return result    
  
  def _pk_to_address(self, public_key):
    """
    Given a EllipticCurvePublicKey object will return the simple text address


    Parameters
    ----------
    public_key : ec.EllipticCurvePublicKey
      the pk object.
      
    Returns
    -------
      text address      
    
    """
    data = public_key.public_bytes(
      encoding=serialization.Encoding.X962,
      format=serialization.PublicFormat.CompressedPoint,
    )
    txt = BCct.ADDR_PREFIX + self._binary_to_text(data)
    return txt


  def _address_to_pk(self, address):
    """
    Given a address will return the EllipticCurvePublicKey object


    Parameters
    ----------
    address : str
      the text address (pk).


    Returns
    -------
    pk : EllipticCurvePublicKey
      the pk object.

    """
    simple_address = address.replace(BCct.ADDR_PREFIX, '')
    bpublic_key = self._text_to_binary(simple_address)
    public_key = ec.EllipticCurvePublicKey.from_encoded_point(
      curve=ec.SECP256K1(), 
      data=bpublic_key
    )
    return public_key
