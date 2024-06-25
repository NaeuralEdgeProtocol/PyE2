import json

from ...base import GenericSession
from ...comm import MQTTWrapper
from ...const import comms as comm_ct


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

  @property
  def _connected(self):
    """
    Check if the session is connected to the communication server.
    """
    return self._default_communicator.connected and self._heartbeats_communicator.connected and self._notifications_communicator.connected

  def _connect(self) -> None:
    if self._default_communicator.connection is None:
      self._default_communicator.server_connect()
      self._default_communicator.subscribe()
    if self._heartbeats_communicator.connection is None:
      self._heartbeats_communicator.server_connect()
      self._heartbeats_communicator.subscribe()
    if self._notifications_communicator.connection is None:
      self._notifications_communicator.server_connect()
      self._notifications_communicator.subscribe()
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
