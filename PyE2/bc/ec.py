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
import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

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

  def __derive_shared_key(self, peer_public_key):
    """
    Derives a shared key using own private key and peer's public key.

    Parameters
    ----------
    private_key : cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey
        The private key to use for derivation.
    peer_public_key : cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKey
        The peer's public key.
    
    Returns
    -------
    bytes
        The derived shared key.
    """
    private_key = self.private_key
    shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
    derived_key = HKDF(
      algorithm=hashes.SHA256(),
      length=32,
      salt=None,
      info=b'AiXp handshake data',
      backend=default_backend()
    ).derive(shared_key)
    return derived_key

  def encrypt(self, plaintext: str, receiver_address: str):
    """
    Encrypts plaintext using the sender's private key and receiver's public key, 
    then base64 encodes the output.

    Parameters
    ----------
    receiver_address : str
        The receiver's address
        
    plaintext : str
        The plaintext to encrypt.

    Returns
    -------
    str
        The base64 encoded nonce and ciphertext.
    """
    receiver_pk = self._address_to_pk(receiver_address)
    shared_key = self.__derive_shared_key(receiver_pk)
    aesgcm = AESGCM(shared_key)
    nonce = os.urandom(12)  # Generate a unique nonce for each encryption
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    encrypted_data = nonce + ciphertext  # Prepend the nonce to the ciphertext
    return base64.b64encode(encrypted_data).decode()  # Encode to base64

  def decrypt(self, encrypted_data_b64 : str, sender_address : str):
    """
    Decrypts base64 encoded encrypted data using the receiver's private key.

    Parameters
    ----------        
    encrypted_data_b64 : str
        The base64 encoded nonce and ciphertext.
        
    sender_address : str
        The sender's address.

    Returns
    -------
    str
        The decrypted plaintext.

    """
    try:
      sender_pk = self._address_to_pk(sender_address)
      encrypted_data = base64.b64decode(encrypted_data_b64)  # Decode from base64
      nonce = encrypted_data[:12]  # Extract the nonce
      ciphertext = encrypted_data[12:]  # The rest is the ciphertext
      shared_key = self.__derive_shared_key(sender_pk)
      aesgcm = AESGCM(shared_key)
      plaintext = aesgcm.decrypt(nonce, ciphertext, None)
      result = plaintext.decode()
    except Exception as exc:
      result = None
    return result