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
@author: Lummetry.AI - Laurentiu
@project: 
@description:
"""

# PIKA

import uuid
from time import sleep

import pika


from ..const import COLORS, COMMS, BASE_CT, PAYLOAD_CT


class AMQPWrapper(object):
  def __init__(
    self, 
    log, 
    config, 
    recv_buff=None, 
    send_channel_name=None, 
    recv_channel_name=None, 
    comm_type=None,
    verbosity=1, 
    **kwargs
  ):
    self._config = config
    self._recv_buff = recv_buff
    self._send_to = None
    self._comm_type = comm_type
    self.__verbosity = verbosity
    self.send_channel_name = send_channel_name
    self.recv_channel_name = recv_channel_name
    self._disconnected_log = []

    if self.recv_channel_name is not None:
      assert self._recv_buff is not None

    self._recv_objects = {'queue': None, 'exchange': None}
    self._send_objects = {'queue': None, 'exchange': None}

    self._connection = None
    self._channel = None

    super(AMQPWrapper, self).__init__(log=log, **kwargs)
    return

  def P(self, s, color=None, verbosity=1, **kwargs):
    if verbosity > self.__verbosity:
      return
    if color is None or (isinstance(color, str) and color[0] not in ['e', 'r']):
      color = COLORS.COMM
    super().P(s, prefix=False, color=color, **kwargs)
    return

  @property
  def send_channel_name(self):
    return self._send_channel_name

  @property
  def recv_channel_name(self):
    return self._recv_channel_name

  @send_channel_name.setter
  def send_channel_name(self, x):
    if isinstance(x, tuple):
      self._send_channel_name, self._send_to = x
    else:
      self._send_channel_name = x
    return

  @recv_channel_name.setter
  def recv_channel_name(self, x):
    self._recv_channel_name = x
    return

  @property
  def cfg_broker(self):
    return self._config[COMMS.BROKER]

  @property
  def cfg_user(self):
    return self._config[COMMS.USER]

  @property
  def cfg_pass(self):
    return self._config[COMMS.PASS]

  @property
  def cfg_vhost(self):
    return self._config[COMMS.VHOST]

  @property
  def cfg_port(self):
    return self._config[COMMS.PORT]

  @property
  def cfg_routing_key(self):
    return self._config.get(COMMS.ROUTING_KEY, "")

  @property
  def cfg_eeid(self):
    return self._config.get(COMMS.EE_ID, self._config.get(COMMS.SB_ID, None))

  @property
  def send_channel_def(self):
    if self.send_channel_name is None:
      return

    cfg = self._config[self.send_channel_name].copy()
    queue = cfg.get(COMMS.QUEUE, cfg[COMMS.EXCHANGE])
    if self._send_to is not None and "{}" in queue:
      queue = queue.format(self._send_to)

    assert "{}" not in queue

    cfg[COMMS.QUEUE] = queue
    return cfg

  @property
  def recv_channel_def(self):
    if self.recv_channel_name is None:
      return

    cfg = self._config[self.recv_channel_name].copy()
    queue = cfg.get(COMMS.QUEUE, cfg[COMMS.EXCHANGE])
    cfg[COMMS.QUEUE] = queue
    _queue_device_specific = cfg.pop(COMMS.QUEUE_DEVICE_SPECIFIC, True)
    if _queue_device_specific:
      cfg[COMMS.QUEUE] += '/{}'.format(self.cfg_eeid)
    cfg[COMMS.QUEUE] += '/{}'.format(str(uuid.uuid4())[:8])
    return cfg

  @property
  def connection(self):
    return self._connection

  @property
  def channel(self):
    return self._channel

  @property
  def recv_queue(self):
    return self._recv_objects['queue']

  @property
  def recv_exchange(self):
    return self._recv_objects['exchange']

  @property
  def send_queue(self):
    return self._send_objects['queue']

  @property
  def send_exchange(self):
    return self._send_objects['exchange']

  def server_connect(self, max_retries=5):
    url = 'amqp://{}:{}@{}:{}/{}'.format(self.cfg_user, self.cfg_pass, self.cfg_broker, self.cfg_port, self.cfg_vhost)

    nr_retry = 1
    has_connection = False
    exception = None

    while nr_retry <= max_retries:
      try:
        self._connection = pika.BlockingConnection(parameters=pika.URLParameters(url))
        sleep(1)
        self._channel = self._connection.channel()
        has_connection = True
      except Exception as e:
        exception = e
      # end try-except

      if has_connection:
        break

      nr_retry += 1
    # endwhile

    if has_connection:
      msg = 'AMQP (Pika) SERVER conn ok: {}{}'.format(self.cfg_broker, self.cfg_port)
      msg_type = PAYLOAD_CT.STATUS_TYPE.STATUS_NORMAL
    else:
      msg = 'AMQP (Pika) SERVER connection could not be initialized after {} retries (reason:{})'.format(
        max_retries, exception
      )
      msg_type = PAYLOAD_CT.STATUS_TYPE.STATUS_EXCEPTION
    # endif

    dct_ret = {
      'has_connection': has_connection,
      'msg': msg,
      'msg_type': msg_type
    }

    return dct_ret

  def establish_one_way_connection(self, channel_name, max_retries=5):
    cfg = None
    if channel_name.lower() == 'send':
      cfg = self.send_channel_def
    elif channel_name.lower() == 'recv':
      cfg = self.recv_channel_def
    # endif

    if cfg is None:
      return

    exchange = cfg[COMMS.EXCHANGE]
    queue = cfg[COMMS.QUEUE]
    exchange_type = cfg.get(COMMS.EXCHANGE_TYPE, 'fanout')
    queue_durable = cfg.get(COMMS.QUEUE_DURABLE, True)
    queue_exclusive = cfg.get(COMMS.QUEUE_EXCLUSIVE, False)

    nr_retry = 1
    has_connection = False
    exception = None

    while nr_retry <= max_retries:
      try:
        self._channel.exchange_declare(
          exchange=exchange,
          exchange_type=exchange_type
        )
        self._channel.queue_declare(
          queue=queue,
          durable=queue_durable,
          exclusive=queue_exclusive
        )
        self._channel.queue_bind(
          queue=queue,
          exchange=exchange,
          routing_key=self.cfg_routing_key
        )

        has_connection = True
      except Exception as e:
        exception = e
      # end try-except

      if has_connection:
        break

      sleep(1)
      nr_retry += 1
    # endwhile

    if has_connection:
      msg = "AMQP (Pika) '{}' connection successfully established on exchange '{}', queue '{}'".format(
        channel_name.lower(), exchange, queue,
      )
      msg_type = PAYLOAD_CT.STATUS_TYPE.STATUS_NORMAL
    else:
      msg = "AMQP (Pika) '{}' connection on exchange '{}', queue '{}' could not be initialized after {} retries (reason:{})".format(
        channel_name.lower(), exchange, queue, max_retries, exception
      )
      msg_type = PAYLOAD_CT.STATUS_TYPE.STATUS_EXCEPTION
    # endif

    dct_objects = {'queue': queue, 'exchange': exchange}
    if channel_name.lower() == 'send':
      self._send_objects = dct_objects
    elif channel_name.lower() == 'recv':
      self._recv_objects = dct_objects
    # endif

    dct_ret = {
      'has_connection': has_connection,
      'msg': msg,
      'msg_type': msg_type
    }

    return dct_ret

  def receive(self):
    method_frame, header_frame, body = self._channel.basic_get(queue=self.recv_queue)
    if method_frame:
      msg = body.decode('utf-8')
      self._channel.basic_ack(method_frame.delivery_tag)
      self._recv_buff.append(msg)
    # endif
    return

  def send(self, message):
    properties = pika.BasicProperties(content_type='application/json')
    self._channel.basic_publish(
      exchange=self.send_exchange,
      routing_key=self.cfg_routing_key,
      body=message,
      properties=properties
    )

    ####
    self.D("Sent message '{}'".format(message))
    ####

    return

  def release(self):
    msgs = []

    if self.recv_queue is not None:
      try:
        self._channel.queue_unbind(
          queue=self.recv_queue,
          exchange=self.recv_exchange,
          routing_key=self.cfg_routing_key,
        )

        self._channel.queue_delete(queue=self.recv_queue)
        msgs.append("AMQP (Pika) deleted queue '{}'".format(self.recv_queue))
      except Exception as e:
        msgs.append("AMQP (Pika) exception when deleting queue '{}'".format(self.recv_queue))
      # end try-except
    # endif

    try:
      self._channel.cancel()
      self._channel.close()
      del self._channel
      self._channel = None
      msgs.append('AMQP (Pika) closed channel')
    except Exception as e:
      msgs.append('AMQP (Pika) exception when closing channel: `{}`'.format(str(e)))
    # end try-except

    try:
      self._connection.close()
      del self._connection
      self._connection = None
      msgs.append('AMQP (Pika) disconnected')
    except Exception as e:
      msgs.append('AMQP (Pika) exception when disconnecting: `{}`'.format(str(e)))
    # end try-except

    dct_ret = {
      'msgs': msgs
    }

    return dct_ret
