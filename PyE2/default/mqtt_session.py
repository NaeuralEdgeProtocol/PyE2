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

from ..base import GenericSession
from ..comm import MQTTWrapper
from ..const import comms as comm_ct


class MqttSession(GenericSession):
  def startup(self):
    self._default_communicator = MQTTWrapper(
        log=self.log,
        config=self._config,
        send_channel_name=comm_ct.COMMUNICATION_CONFIG_CHANNEL,
        recv_channel_name=comm_ct.COMMUNICATION_PAYLOADS_CHANNEL,
        comm_type=comm_ct.COMMUNICATION_DEFAULT,
        recv_buff=self._payload_messages,
        connection_name=self.name,
        verbosity=self._verbosity,
    )

    self._heartbeats_communicator = MQTTWrapper(
        log=self.log,
        config=self._config,
        recv_channel_name=comm_ct.COMMUNICATION_CTRL_CHANNEL,
        comm_type=comm_ct.COMMUNICATION_HEARTBEATS,
        recv_buff=self._hb_messages,
        connection_name=self.name,
        verbosity=self._verbosity,
    )

    self._notifications_communicator = MQTTWrapper(
        log=self.log,
        config=self._config,
        recv_channel_name=comm_ct.COMMUNICATION_NOTIF_CHANNEL,
        comm_type=comm_ct.COMMUNICATION_NOTIFICATIONS,
        recv_buff=self._notif_messages,
        connection_name=self.name,
        verbosity=self._verbosity,
    )
    return super(MqttSession, self).startup()

  def _connect(self) -> None:
    if self._default_communicator.connection is None:
      self._default_comm_con_res = self._default_communicator.server_connect()
      self._default_comm_sub_res = self._default_communicator.subscribe()
    if self._heartbeats_communicator.connection is None:
      self._hb_comm_con_res = self._heartbeats_communicator.server_connect()
      self._hb_comm_sub_res = self._heartbeats_communicator.subscribe()
    if self._notifications_communicator.connection is None:
      self._notif_comm_con_res = self._notifications_communicator.server_connect()
      self._notif_comm_sub_res = self._notifications_communicator.subscribe()

    self.connected = self._default_communicator.connected and self._heartbeats_communicator.connected and self._notifications_communicator.connected

    return

  def _communication_close(self, **kwargs):
    self._default_communicator.release()
    self._heartbeats_communicator.release()
    self._notifications_communicator.release()
    return

  def _send_payload(self, to, msg):
    payload = json.dumps(msg)

    self._default_communicator._send_to = to
    self._default_communicator.send(payload)
    return
