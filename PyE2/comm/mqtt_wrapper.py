# PAHO
# TODO: implement config validation and base config format
# TODO: add queue for to_send messages

# TODO: adding a lock for accessing self._mqttc should solve some of the bugs, but it introduces a new one
# basically, when a user thread calls send, they should acquire the lock for the self._mqttc object
# and use it to send messages. However, if the mqttc has loop started but did not connect, the lock will
# prevent the client from ever connecting.

import os
import traceback
from collections import deque
from threading import Lock
from time import sleep

import paho.mqtt.client as mqtt
from paho.mqtt import __version__ as mqtt_version

from ..const import BASE_CT, COLORS, COMMS, PAYLOAD_CT
from ..utils import resolve_domain_or_ip

from importlib import resources as impresources
from .. import certs


class MQTTWrapper(object):
  def __init__(self,
               log,
               config,
               recv_buff=None,
               send_channel_name=None,
               recv_channel_name=None,
               comm_type=None,
               on_message=None,
               post_default_on_message=None,  # callback that gets called after custom or default rcv callback
               debug_errors=False,
               connection_name='MqttWrapper',
               verbosity=1,
               **kwargs):
    self.log = log
    self._config = config
    self._recv_buff = recv_buff
    self._mqttc = None
    self.debug_errors = debug_errors
    self._thread_name = None
    self.connected = False
    self.disconnected = False
    self.__verbosity = verbosity
    self._send_to = None
    self._nr_full_retries = 0
    self.__nr_dropped_messages = 0
    self._comm_type = comm_type
    self.send_channel_name = send_channel_name
    self.recv_channel_name = recv_channel_name
    self._disconnected_log = deque(maxlen=10)
    self._disconnected_counter = 0
    self._custom_on_message = on_message
    self._post_default_on_message = post_default_on_message
    self._connection_name = connection_name
    self.last_disconnect_log = ''

    self.DEBUG = False

    if self.recv_channel_name is not None and on_message is None:
      assert self._recv_buff is not None

    self.P(f"Initializing MQTTWrapper using Paho MQTT v{mqtt_version}")
    super(MQTTWrapper, self).__init__(**kwargs)
    return

  def P(self, s, color=None, verbosity=1, **kwargs):
    if verbosity > self.__verbosity:
      return
    if color is None or (isinstance(color, str) and color[0] not in ['e', 'r']):
      color = COLORS.COMM
    comtype = self._comm_type[:7] if self._comm_type is not None else 'CUSTOM'
    self.log.P("[MQTWRP][{}] {}".format(comtype, s), color=color, **kwargs)
    return

  @property
  def nr_dropped_messages(self):
    return self.__nr_dropped_messages

  def D(self, s, t=False):
    _r = -1
    if self.DEBUG:
      if self.show_prefixes:
        msg = "[DEBUG] {}: {}".format(self.__name__, s)
      else:
        if self.prefix_log is None:
          msg = "[D] {}".format(s)
        else:
          msg = "[D]{} {}".format(self.prefix_log, s)
        # endif
      # endif
      _r = self.log.P(msg, show_time=t, color='yellow')
    # endif
    return _r

  @property
  def is_secured(self):
    val = self.cfg_secured
    if isinstance(val, str):
      val = val.upper() in ["1", "TRUE", "YES"]
    return val

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
  def cfg_node_id(self):
    return self._config.get(COMMS.EE_ID, self._config.get(COMMS.SB_ID, None))

  @property
  def cfg_node_addr(self):
    return self._config.get(COMMS.EE_ADDR)

  @property
  def cfg_user(self):
    return self._config[COMMS.USER]

  @property
  def cfg_pass(self):
    return self._config[COMMS.PASS]

  @property
  def cfg_host(self):
    return self._config[COMMS.HOST]

  @property
  def cfg_port(self):
    return self._config[COMMS.PORT]

  @property
  def cfg_qos(self):
    return self._config[COMMS.QOS]

  @property
  def cfg_cert_path(self):
    return self._config.get(COMMS.CERT_PATH)

  @property
  def cfg_secured(self):
    return self._config.get(COMMS.SECURED, 0)  # TODO: make 1 later on

  @property
  def recv_channel_def(self):
    if self.recv_channel_name is None:
      return

    cfg = self._config[self.recv_channel_name].copy()
    topic = cfg[COMMS.TOPIC]
    lst_topics = []
    if "{}" in topic:
      if self.cfg_node_id is not None:
        lst_topics.append(topic.format(self.cfg_node_id))
      if self.cfg_node_addr is not None:
        lst_topics.append(topic.format(self.cfg_node_addr))
    else:
      lst_topics.append(topic)

    if len(lst_topics) == 0:
      raise ValueError("ERROR! No topics to subscribe to")

    cfg[COMMS.TOPIC] = lst_topics
    return cfg

  @property
  def send_channel_def(self):
    if self.send_channel_name is None:
      return

    cfg = self._config[self.send_channel_name].copy()
    topic = cfg[COMMS.TOPIC]
    if self._send_to is not None and "{}" in topic:
      topic = topic.format(self._send_to)

    assert "{}" not in topic

    cfg[COMMS.TOPIC] = topic
    return cfg

  @property
  def connection(self):
    return self._mqttc

  def __get_client_id(self):
    mqttc = self._mqttc
    client_id = str(mqttc._client_id) if mqttc is not None else 'None'
    return client_id

  def __maybe_set_mqtt_tls(self, mqttc: mqtt.Client):
    if self.is_secured:  # no need to set TLS if not configured with "SECURED" : 1
      self.P("Setting up secured comms on PORT: {}".format(self.cfg_port))
      cert_path = str(self.cfg_cert_path)

      if cert_path.upper() in ["", "NONE", "NULL"]:
        cert_file_name = self.cfg_host + ".crt"
        cert_file = impresources.files(certs).joinpath(cert_file_name)

        if cert_file.exists():
          self.P("Using certificate file: {}".format(cert_file_name))
          mqttc.tls_set(cert_file)
        else:
          self.P("No certificate provided, using default TLS")
          mqttc.tls_set()
      # end if certificate not provided
      else:
        if os.path.exists(cert_path):
          self.P("Using certificate file: {}".format(cert_path))
          mqttc.tls_set(cert_path)
        else:
          self.P("Certificate file not found: {}".format(cert_path), color='r', verbosity=1)
          self.P("Using default TLS", verbosity=1)
          mqttc.tls_set()
      # end if certificate provided
    else:
      self.P("Communication is not secured. SECURED: {}, PORT: {}".format(
          self.cfg_secured, self.cfg_port), color='r'
      )
    # end if secured
    return

  def __create_mqttc_object(self, comtype, client_uid):
    client_id = self._connection_name + '_' + comtype + '_' + client_uid
    if mqtt_version.startswith('2'):
      mqttc = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=client_id,
        clean_session=True,
      )
    else:
      mqttc = mqtt.Client(
        client_id=client_id,
        clean_session=True
      )

    mqttc.username_pw_set(
      username=self.cfg_user,
      password=self.cfg_pass
    )

    self.__maybe_set_mqtt_tls(mqttc)

    mqttc.on_connect = self._callback_on_connect
    mqttc.on_disconnect = self._callback_on_disconnect
    mqttc.on_message = self._callback_on_message
    mqttc.on_publish = self._callback_on_publish

    return mqttc

  def __sleep_until_connected(self, max_sleep, sleep_time):
    for sleep_iter in range(1, int(max_sleep / sleep_time) + 1):
      sleep(sleep_time)
      if self.connected:
        break
    # endfor
    return sleep_iter

  def _callback_on_connect(self, client, userdata, flags, rc, *args, **kwargs):
    self.connected = False
    if rc == 0:
      self.connected = True
      self.P("Conn ok clntid '{}' with code: {}".format(
        self.__get_client_id(), rc), color='g', verbosity=1)
    return

  def _callback_on_disconnect(self, client, userdata, rc, *args, **kwargs):
    """
    Tricky callback

    we can piggy-back ride the client with flags:
      client.connected_flag = False
      client.disconnect_flag = True
    """

    if mqtt_version.startswith('2'):
      # In version 2, on_disconnect has a different order of parameters, and rc is passed as the 4th parameter
      # check https://eclipse.dev/paho/files/paho.mqtt.python/html/migrations.html for more info
      rc = args[0]
    if rc == 0:
      self.P('Graceful disconnect (reason_code={})'.format(rc), color='m', verbosity=1)
      str_error = "Graceful disconnect."
    else:
      str_error = mqtt.error_string(rc) + ' (reason_code={})'.format(rc)
      self.P("Unexpected disconnect for client id '{}': {}".format(
        self.__get_client_id(), str_error), color='r', verbosity=1)

    if self._disconnected_counter > 0:
      self.P("Trying to determine IP of target server...", verbosity=1)
      ok, str_ip, str_domain = resolve_domain_or_ip(self.cfg_host)
      msg = '  Multiple conn loss ({} disconnects so far), showing previous 10:\n{}'.format(
        self._disconnected_counter, self.last_disconnect_log
      )
      server_port = "*****  Please check server connection: {}:{} {} *****".format(
        self.cfg_host, self.cfg_port,
        "({}:{})".format(str_ip, self.cfg_port) if (ok and str_ip != str_domain) else ""
      )
      msg += "\n\n{}\n{}\n{}".format("*" * len(server_port), server_port, "*" * len(server_port))
      self.P(msg, color='r', verbosity=1)
    # endif multiple disconnects
    self.connected = False
    self.disconnected = True
    self._disconnected_log.append((self.log.time_to_str(), str_error))
    self._disconnected_counter += 1
    self.last_disconnect_log = '\n'.join([f"* Comm error '{x2}' occurred at {x1}" for x1, x2 in self._disconnected_log])
    # we need to stop the loop otherwise the client thread will keep working
    # so we call release->loop_stop

    self.release()
    return

  def _callback_on_publish(self, client, userdata, mid, *args, **kwargs):
    return

  def _callback_on_message(self, client, userdata, message, *args, **kwargs):
    if self._custom_on_message is not None:
      self._custom_on_message(client, userdata, message)
    else:
      try:
        msg = message.payload.decode('utf-8')
        self._recv_buff.append(msg)
      except:
        # DEBUG TODO: enable here a debug show of the message.payload if
        # the number of dropped messages rises
        # TODO: add also to ANY OTHER wrapper
        self.__nr_dropped_messages += 1
    # now call the "post-process" callback
    if self._post_default_on_message is not None:
      self._post_default_on_message()
    return

  def get_connection_issues(self):
    return {x1: x2 for x1, x2 in self._disconnected_log}

  def server_connect(self, max_retries=5):
    max_sleep = 2
    sleep_time = 0.01
    nr_retry = 1
    has_connection = False
    exception = None
    sleep_iter = None
    comtype = self._comm_type[:7] if self._comm_type is not None else 'CUSTOM'

    while nr_retry <= max_retries:
      try:
        # 1. create a unique client id
        client_uid = self.log.get_unique_id()

        # 2. create the mqtt client object (with callbacks set)
        self._mqttc = self.__create_mqttc_object(comtype, client_uid)

        # TODO: more verbose logging including when there is no actual exception
        # 3. connect to the server
        self._mqttc.connect(host=self.cfg_host, port=self.cfg_port)

        # 4. start the loop in another thread
        if self._mqttc is not None:
          self._mqttc.loop_start()  # start loop in another thread

        # 5. wait until connected
        sleep_iter = self.__sleep_until_connected(max_sleep=max_sleep, sleep_time=sleep_time)

        has_connection = self.connected
      except Exception as e:
        exception = e
        if self.debug_errors:
          self.P(exception, color='r', verbosity=1)
          self.P(traceback.format_exc(), color='r', verbosity=1)

      # end try-except

      if has_connection:
        break

      nr_retry += 1
    # endwhile

    # set thread name ; useful for debugging
    mqttc = self._mqttc
    if mqttc is not None and hasattr(mqttc, '_thread') and mqttc._thread is not None:
      mqttc._thread.name = self._connection_name + '_' + comtype + '_' + client_uid
      self._thread_name = mqttc._thread.name

    if has_connection:
      msg = "MQTT conn ok by '{}' in {:.1f}s - {}:{}".format(
        self._thread_name,
        sleep_iter * sleep_time,
        self.cfg_host,
        self.cfg_port
      )
      msg_type = PAYLOAD_CT.STATUS_TYPE.STATUS_NORMAL
      self._nr_full_retries = 0

      self.P(msg)

    else:
      reason = exception
      if reason is None:
        reason = " max retries in {:.1f}s".format(sleep_iter * sleep_time)

      self._nr_full_retries += 1
      msg = 'MQTT (Paho) conn to {}:{} failed after {} retr ({} trials) (reason:{})'.format(
        self.cfg_host,
        self.cfg_port,
        nr_retry,
        self._nr_full_retries,
        reason
      )
      msg_type = PAYLOAD_CT.STATUS_TYPE.STATUS_EXCEPTION
      self.P(msg, color='r', verbosity=1)

    # endif

    dct_ret = {
      'has_connection': has_connection,
      'msg': msg,
      'msg_type': msg_type
    }

    # if release was not called from on_disconnect, basically
    # this method of checking self._mqttc is not None is not
    # very reliable, as race conditions can occur
    if self._mqttc is not None and not has_connection:
      self.release()

    return dct_ret

  def get_thread_name(self):
    return self._thread_name

  def subscribe(self, max_retries=5):

    if self.recv_channel_name is None:
      return

    nr_retry = 1
    has_connection = True
    exception = None
    lst_topics = self.recv_channel_def[COMMS.TOPIC]
    for topic in lst_topics:
      current_topic_connection = False
      while nr_retry <= max_retries:
        try:
          if self._mqttc is not None:
            self._mqttc.subscribe(
              topic=topic,
              qos=self.cfg_qos
            )
            current_topic_connection = True
          else:
            has_connection = False
        except Exception as e:
          has_connection = False
          exception = e

        if current_topic_connection:
          break

        sleep(1)
        nr_retry += 1
      # endwhile

      if current_topic_connection:
        msg = "MQTT (Paho) subscribed to topic '{}'".format(topic)
        msg_type = PAYLOAD_CT.STATUS_TYPE.STATUS_NORMAL
      else:
        msg = "MQTT (Paho) subscribe to '{}' FAILED after {} retries (reason:{})".format(topic, max_retries, exception)
        msg_type = PAYLOAD_CT.STATUS_TYPE.STATUS_EXCEPTION
      # endif

    dct_ret = {
      'has_connection': has_connection,
      'msg': msg,
      'msg_type': msg_type
    }

    return dct_ret

  def receive(self):
    return

  def send(self, message):
    mqttc = self._mqttc
    if mqttc is None:
      return

    result = mqttc.publish(
      topic=self.send_channel_def[COMMS.TOPIC],
      payload=message,
      qos=self.cfg_qos
    )

    ####
    self.D("Sent message '{}'".format(message))
    ####

    if result.rc == mqtt.MQTT_ERR_QUEUE_SIZE:
      raise ValueError('Message is not queued due to ERR_QUEUE_SIZE')

    return

  def release(self):
    try:
      mqttc = self._mqttc

      if mqttc is not None:
        self._mqttc.disconnect()
        self._mqttc.loop_stop()  # stop the loop thread
      self._mqttc = None
      self.connected = False
      msg = 'MQTT (Paho) connection released.'
    except Exception as e:
      msg = 'MQTT (Paho) exception while releasing connection: `{}`'.format(str(e))

    self.P(msg)

    # TODO: method should return None; update code in core to reflect this
    dct_ret = {'msgs': [msg]}

    return dct_ret
