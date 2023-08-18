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
@author: Lummetry\.AI - Stefan Saraev
@project: 
@description:
"""

import json
from time import sleep
from collections import deque
from threading import Thread

from ..const import comms as comm_ct
from ..comm import MQTTWrapper
from ..base import GenericSession


# TODO: implement send_command, send_payload,
#       to be used by the Pipeline class
class MqttSession(GenericSession):
  def __init__(self, *, host, port, user, pwd, name='pySDK', config={}, filter_workers=None, log=None, on_payload=None, on_notification=None, on_heartbeat=None, silent=True, **kwargs) -> None:
    super(MqttSession, self).__init__(host=host, port=port, user=user, pwd=pwd, name=name, config=config, filter_workers=filter_workers,
                                      log=log, on_payload=on_payload, on_notification=on_notification, on_heartbeat=on_heartbeat, silent=silent, **kwargs)

    self._payload_messages = deque()
    self._default_communicator = MQTTWrapper(
        log=self.log,
        config=self._config,
        send_channel_name=comm_ct.COMMUNICATION_CONFIG_CHANNEL,
        recv_channel_name=comm_ct.COMMUNICATION_PAYLOADS_CHANNEL,
        comm_type=comm_ct.COMMUNICATION_DEFAULT,
        recv_buff=self._payload_messages
        # on_message=self._on_payload_default_mqtt_callback
    )

    self._hb_messages = deque()
    self._heartbeats_communicator = MQTTWrapper(
        log=self.log,
        config=self._config,
        recv_channel_name=comm_ct.COMMUNICATION_CTRL_CHANNEL,
        comm_type=comm_ct.COMMUNICATION_HEARTBEATS,
        recv_buff=self._hb_messages
        # on_message=self._on_heartbeat_default_mqtt_callback
    )

    self._notif_messages = deque()
    self._notifications_communicator = MQTTWrapper(
        log=self.log,
        config=self._config,
        recv_channel_name=comm_ct.COMMUNICATION_NOTIF_CHANNEL,
        comm_type=comm_ct.COMMUNICATION_NOTIFICATIONS,
        recv_buff=self._notif_messages
        # on_message=self._on_notification_default_mqtt_callback
    )

    self._running = False

    self._payload_thread = Thread(target=self._handle_payloads, args=())
    self._notif_thread = Thread(target=self._handle_notifs, args=())
    self._hb_thread = Thread(target=self._handle_hbs, args=())

    return

  def _handle_payloads(self):
    while self._running:
      if len(self._payload_messages) == 0:
        sleep(0.01)
        continue
      current_msg = self._payload_messages.popleft()
      self._on_payload_default_mqtt_callback(current_msg)
    # end while self.running

    while len(self._payload_messages) > 0:
      current_msg = self._payload_messages.popleft()
      self._on_payload_default_mqtt_callback(current_msg)
    return

  def _handle_notifs(self):
    while self._running:
      if len(self._notif_messages) == 0:
        sleep(0.01)
        continue
      current_msg = self._notif_messages.popleft()
      self._on_notification_default_mqtt_callback(current_msg)
    # end while self.running

    while len(self._notif_messages) > 0:
      current_msg = self._notif_messages.popleft()
      self._on_notification_default_mqtt_callback(current_msg)
    return

  def _handle_hbs(self):
    while self._running:
      if len(self._hb_messages) == 0:
        sleep(0.01)
        continue
      current_msg = self._hb_messages.popleft()
      self._on_heartbeat_default_mqtt_callback(current_msg)
    # end while self.running

    while len(self._hb_messages) > 0:
      current_msg = self._hb_messages.popleft()
      self._on_heartbeat_default_mqtt_callback(current_msg)
    return

  def _on_payload_default_mqtt_callback(self, message) -> None:
    dict_msg = json.loads(message)
    # parse the message
    dict_msg_parsed = self._parse_message(dict_msg)
    return self.on_payload(dict_msg_parsed)

  def _on_notification_default_mqtt_callback(self, message) -> None:
    dict_msg = json.loads(message)
    # parse the message
    dict_msg_parsed = self._parse_message(dict_msg)
    return self.on_notification(dict_msg_parsed)

  def _on_heartbeat_default_mqtt_callback(self, message) -> None:
    dict_msg = json.loads(message)
    # parse the message
    dict_msg_parsed = self._parse_message(dict_msg)
    return self.on_heartbeat(dict_msg_parsed)

  def maybe_reconnect(self):
    if self._default_communicator.connection is None or not self.connected:
      self._default_comm_con_res = self._default_communicator.server_connect()
      self._default_comm_sub_res = self._default_communicator.subscribe()
    if self._heartbeats_communicator.connection is None or not self.connected:
      self._hb_comm_con_res = self._heartbeats_communicator.server_connect()
      self._hb_comm_sub_res = self._heartbeats_communicator.subscribe()
    if self._notifications_communicator.connection is None or not self.connected:
      self._notif_comm_con_res = self._notifications_communicator.server_connect()
      self._notif_comm_sub_res = self._notifications_communicator.subscribe()
    self.connected = all([
      self._default_comm_con_res['has_connection'],
      self._default_comm_sub_res['has_connection'],
      self._hb_comm_con_res['has_connection'],
      self._hb_comm_sub_res['has_connection'],
      self._notif_comm_con_res['has_connection'],
      self._notif_comm_sub_res['has_connection'],
    ])

  def connect(self) -> None:
    self.maybe_reconnect()

    self._running = True
    self._payload_thread.setDaemon(True)
    self._payload_thread.start()
    self._notif_thread.setDaemon(True)
    self._notif_thread.start()
    self._hb_thread.setDaemon(True)
    self._hb_thread.start()

    return

  def close(self, close_pipelines=False, **kwargs):
    super(MqttSession, self).close(close_pipelines=close_pipelines, **kwargs)

    self._default_communicator.release()
    self._heartbeats_communicator.release()
    self._notifications_communicator.release()
    self._running = False
    self._payload_thread.join()
    self._notif_thread.join()
    self._hb_thread.join()
    self.connected = False

    return

  def _send_payload(self, to, msg):
    payload = json.dumps(msg)

    self._default_communicator._send_to = to
    self._default_communicator.send(payload)
    return
