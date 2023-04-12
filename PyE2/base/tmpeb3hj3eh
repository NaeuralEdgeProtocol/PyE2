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

import os
import sys
import traceback
from time import localtime, mktime, strftime, strptime, sleep
from time import time as tm

from ..const import comms as comm_ct
from .pipeline import Pipeline
from .payload import Payload
from ..io_formatter import IOFormatterManager


class Logger():
  def __init__(self, **kwargs) -> None:
    return

  def P(self, msg, **kwargs):
    print(msg)

  def get_unique_id(self, size=8):
    """
    efficient and low-colision function for small unique id generation
    """
    import random
    import string
    alphabet = string.ascii_lowercase + string.digits
    uid = ''.join(random.choices(alphabet, k=size))
    return uid

  def start_timer(self, *args, **kwargs):
    return

  def end_timer(self, *args, **kwargs):
    return

  def stop_timer(self, *args, **kwargs):
    return

  def time_to_str(self, t=None, fmt='%Y-%m-%d %H:%M:%S'):
    if t is None:
      t = tm()
    return strftime(fmt, localtime(t))

  def get_error_info(self, return_err_val=False):
    """
    Returns error_type, file, method, line for last error if available

    Parameters
    ----------
    return_err_val: boolean, optional
      Whether the method returns or not the error message (err_val)

    Returns
    -------
    if not return_err_val:
      (tuple) str, str, str, str : errortype, file, method, line
    else:
      (tuple) str, str, str, str, str : errortype, file, method, line, err message
    """
    err_type, err_val, err_trace = sys.exc_info()
    if False:
      # dont try this at home :) if you want to pickle a logger instance after
      # `get_error_info` was triggered, then it won't work because `self._last_extracted_error`
      # contain an object of type `traceback` and tracebacks cannot be pickled
      self._last_extracted_error = err_type, err_val, err_trace
    # endif
    if err_type is not None:
      str_err = err_type.__name__
      stack_summary = traceback.extract_tb(err_trace)
      last_error_frame = stack_summary[-1]
      fn = os.path.splitext(os.path.split(last_error_frame.filename)[-1])[0]
      lineno = last_error_frame.lineno
      func_name = last_error_frame.name
      if not return_err_val:
        return str_err, 'File: ' + fn, 'Func: ' + func_name, 'Line: ' + str(lineno)
      else:
        return str_err, 'File: ' + fn, 'Func: ' + func_name, 'Line: ' + str(lineno), str(err_val)
    else:
      return "", "", "", "", ""

  def dict_pretty_format(self, d, indent=4, as_str=True, display_callback=None, display=False, limit_str=250):
    assert isinstance(d, dict), "`d` must be dict"
    if display and display_callback is None:
      display_callback = self.P
    lst_data = []

    def deep_parse(dct, ind=indent):
      for ki, key in enumerate(dct):
        # dct actually can be dict or list
        str_key = str(key) if not isinstance(key, str) else '"{}"'.format(key)
        if isinstance(dct, dict):
          value = dct[key]
          lst_data.append(' ' * ind + str(str_key) + ' : ')
        else:
          value = key
        if isinstance(value, dict):
          if lst_data[-1][-1] in ['[', ',']:
            lst_data.append(' ' * ind + '{')
          else:
            lst_data[-1] = lst_data[-1] + '{'
          deep_parse(value, ind=ind + indent)
          lst_data.append(' ' * ind + '}')
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
          lst_data[-1] = lst_data[-1] + '['
          deep_parse(value, ind=ind + indent)
          lst_data.append(' ' * ind + ']')
        else:
          str_value = str(value) if not isinstance(value, str) else '"{}"'.format(value)
          if isinstance(value, str) and len(str_value) > limit_str:
            str_value = str_value[:limit_str]
          lst_data[-1] = lst_data[-1] + str_value

        if ki < (len(dct) - 1):
          lst_data[-1] = lst_data[-1] + ','
      return

    deep_parse(dct=d, ind=0)

    displaybuff = "{\n"
    for itm in lst_data:
      displaybuff += '  ' + itm + '\n'
    displaybuff += "}"

    if display_callback is not None:
      displaybuff = "Dict pretty formatter:\n" + displaybuff
      display_callback(displaybuff)
    if as_str:
      return displaybuff
    else:
      return lst_data

  def camel_to_snake(self, s):
    import re
    if s.isupper():
      result = s.lower()
    else:
      s = re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
      s = s.replace('__', '_')
      result = s
    return result


class GenericSession(object):
  default_config = {
      "CONFIG_CHANNEL": {
          "TOPIC": "lummetry/{}/config"
      },
      "CTRL_CHANNEL": {
          "TOPIC": "lummetry/ctrl"
      },
      "NOTIF_CHANNEL": {
          "TOPIC": "lummetry/notif"
      },
      "PAYLOADS_CHANNEL": {
          "TOPIC": "lummetry/payloads"
      },
      "QOS": 0
  }

  def __init__(self, *, host, port, user, pwd, name='pySDK', config={}, log=None, on_notification=None, on_heartbeat=None, silent=False, **kwargs) -> None:
    """Create a session object that allows to connect to a communication server and to interact with nodes from the AiXp network.

    Args:
        host (str): Hostname of the server
        port (int): port
        user (str): username
        pwd (str): password
        name (str, optional): Will be used as `SESSION_ID` when communicating with AiXp nodes. Defaults to 'pySDK'.
        config (dict, optional): Configures the names of the channels this session will connect to. Defaults to {}.
        log (Logger, optional): instance of a Logger class that provides utility functions and prettier logs. Useful for Hyperfy devs. Defaults to None.
        on_notification (Callable[[Session, dict], None], optional): Callback that handles the notification received by this session. Defaults to None.
        on_heartbeat (Callable[[Session, dict], None], optional): Callback that handles the heartbeat received by this session. Defaults to None.
        silent (bool, optional): This flag controlls if the `.P` method dumps text to the stdout. Defaults to False.
    """
    if log is None:
      log = Logger()

    super(GenericSession, self).__init__()

    self.silent = silent

    # maybe read config from file?
    self._config = {**self.default_config, **config}
    self.log = log
    self.name = name

    self._online_boxes = {}

    self._fill_config(host, port, user, pwd, name)

    self.custom_on_heartbeat = on_heartbeat
    self.custom_on_notification = on_notification

    self.on_payload = self._on_payload_default
    self.on_heartbeat = self._on_heartbeat_default
    self.on_notification = self._on_notification_default

    self.payload_instance_callbacks = []
    self.notification_instance_callbacks = []

    self.payload_pipeline_callbacks = []
    self.notification_pipeline_callbacks = []
    self.heartbeat_pipeline_callbacks = []
    self.own_pipelines = []

    self.formatter_wrapper = IOFormatterManager(log)

    return

  @property
  def server(self):
    return self._config[comm_ct.HOST]

  def _fill_config(self, host, port, user, pwd, name):
    if self._config.get(comm_ct.SB_ID, None) is None:
      self._config[comm_ct.SB_ID] = name

    if self._config.get(comm_ct.USER, None) is None:
      self._config[comm_ct.USER] = user

    if self._config.get(comm_ct.PASS, None) is None:
      self._config[comm_ct.PASS] = pwd

    if self._config.get(comm_ct.HOST, None) is None:
      self._config[comm_ct.HOST] = host

    if self._config.get(comm_ct.PORT, None) is None:
      self._config[comm_ct.PORT] = port
    return

  def _parse_message(self, dict_msg: dict):
    formatter = self.formatter_wrapper \
        .get_required_formatter_from_payload(dict_msg)
    if formatter is not None:
      dict_msg = formatter.decode_output(dict_msg)
    return dict_msg

  def _on_heartbeat_default(self, dict_msg: dict):
    msg_eeid = dict_msg['EE_ID']
    msg_active_configs = dict_msg['CONFIG_STREAMS']

    # default action
    # TODO: print stuff
    self.P("Received hb from: {}".format(msg_eeid))
    self._online_boxes[msg_eeid] = {
        config['NAME']: config for config in msg_active_configs}

    # call the pipeline defined callbacks, if any
    for pipeline, callback in self.heartbeat_pipeline_callbacks:
      if msg_eeid == pipeline.e2id:
        callback(pipeline, dict_msg)

    # call the custom callback, if defined
    if self.custom_on_heartbeat is not None:
      self.custom_on_heartbeat(self, dict_msg)

    return

  def _on_notification_default(self, dict_msg: dict):
    msg_eeid = dict_msg['EE_ID']
    msg_stream = dict_msg.get('STREAM_NAME', None)
    notification_type = dict_msg.get("NOTIFICATION_TYPE")
    notification = dict_msg.get("NOTIFICATION")

    # call the pipeline defined callbacks, if any
    for pipeline, callback in self.notification_pipeline_callbacks:
      if msg_eeid == pipeline.e2id and msg_stream == pipeline.name:
        callback(pipeline, dict_msg)

    # call the custom callback, if defined
    if self.custom_on_notification is not None:
      self.custom_on_notification(self, dict_msg)

    # call default action on notif
    # TODO: maybe print stuff
    color = None
    if notification_type != "NORMAL":
      color = 'r'
    self.P("Received notification {} from <{}/{}>: {}".format(notification_type,
           msg_eeid, msg_stream, notification), color=color)

    return

  # TODO: maybe convert dict_msg to Payload object
  #       also maybe strip the dict from useless info for the user of the sdk
  #       Add try-except + sleep
  def _on_payload_default(self, dict_msg: dict) -> None:
    msg_stream = dict_msg.get('STREAM', None)
    msg_eeid = dict_msg['EE_ID']
    msg_signature = dict_msg.get('SIGNATURE', '').upper()
    msg_instance = dict_msg.get('INSTANCE_ID', None)
    msg_data = dict_msg

    for pipeline, callback in self.payload_pipeline_callbacks:
      if msg_eeid == pipeline.e2id and msg_stream == pipeline.name:
        callback(pipeline, msg_signature, msg_instance, msg_data)

    for pipeline, signature, instance, callback in self.payload_instance_callbacks:
      if msg_eeid == pipeline.e2id and msg_stream == pipeline.name and msg_signature == signature and msg_instance == instance:
        callback(pipeline, msg_data)
    return

  def _send_command_to_box(self, command, worker, payload):
    msg_to_send = {
        'EE_ID': worker,
        'SB_ID': worker,
        'ACTION': command,
        'PAYLOAD': payload,
        'INITIATOR_ID': self.name
    }

    self._send_payload(worker, msg_to_send)

  def remove_pipeline_callbacks(self, pipeline) -> None:
    instance_indexes = [i for i, t in enumerate(
        self.payload_instance_callbacks) if t[0] == pipeline][::-1]
    for i in instance_indexes:
      self.payload_instance_callbacks.pop(i)

    pipeline_index = [i for i, t in enumerate(
        self.payload_pipeline_callbacks) if t[0] == pipeline][0]
    self.payload_pipeline_callbacks.pop(pipeline_index)
    return

  def remove_instance_callback(self, pipeline, signature, instance_id):
    instance_index = None

    for i, (cb_pipeline, cb_signature, cb_instance_id, _) in enumerate(self.payload_instance_callbacks):
      if cb_pipeline == pipeline and cb_signature == signature and cb_instance_id == instance_id:
        instance_index = i
        break

    self.payload_instance_callbacks.pop(instance_index)
    return

  def send_command_update_pipeline(self, worker, stream_config):
    self._send_command_to_box('UPDATE_CONFIG', worker, stream_config)

  def send_command_delete_pipeline(self, worker, stream_name):
    self._send_command_to_box('ARCHIVE_CONFIG', worker, stream_name)

  def _send_payload(self, to, payload):
    raise NotImplementedError

  def P(self, *args, **kwargs):
    """Print info to stdout if the session was created with the silent argument set to `False`
    """
    if not self.silent:
      self.log.P(*args, **kwargs)

  def connect(self) -> None:
    """Connect to the communication server using the credentials provided when creating this instance
    """
    raise NotImplementedError

  def create_pipeline(self, *, e2id, name, data_source, config={}, plugins=[], on_data, on_notification=None, **kwargs) -> Pipeline:
    """Create a new pipeline on a box. A pipeline is the equivalent of the "config file" used by the Hyperfy dev team internaly.
    A pipeline allows one to define what is the data acquisition type and source, and what plugins will run on that data.

    Args:
        e2id (str): Name of the AiXp node.
        name (str): Name of the pipeline. This is good to be kept unique, as it allows multiple parties to overwrite each others configurations.
        data_source (str): Name of the DataCaptureThread plugin to be used for acquisition.
        on_data (Callable[[Pipeline, str, str, dict], None]): Callback that handles messages received from this pipeline. As arguments, it has a reference to this Pipeline object, the name of the Signature and the name of the Instance that sent the message, along with the payload itself.
        plugins (list): List of dictionaries which contain the configurations of each plugin instance that is desired to run on the box. Defaults to []. Should be left [], and instances should be created with the api.
        config (dict, optional): Data acquisition specific parameters. Defaults to {}.
        on_notification (Callable[[Pipeline, dict], None], optional): Callback that handles notifications received from this pipeline. As arguments, it has a reference to this Pipeline object, along with the payload itself. Defaults to None.

    Returns:
        Pipeline: a Pipeline object which can be used to control plugin instances.
    """
    pipeline = Pipeline(
      self,
      self.log,
      e2id=e2id,
      name=name,
      data_source=data_source,
      config=config,
      plugins=plugins,
      on_data=on_data,
      on_notification=on_notification,
      silent=self.silent,
      **kwargs
     )
    self.own_pipelines.append(pipeline)
    return pipeline
  
  
  def close_own_pipelines(self):
    # iterate through all CREATED pipelines from this session and close them
    for pipeline in self.own_pipelines:
      pipeline.close()    
    return

  def close(self, close_pipelines=False, **kwargs):
    """Close the session, releasing all resources and closing all threads
    """
    # TODO: Stefan: here we need to change from abstract to concrete - all pipelines MUST
    #       be deallocated. The child re-implementations must call self().__close__ beforehand
    if close_pipelines:
      self.close_own_pipelines()
    return
  
  def get_active_nodes(self):
    """Get the list of all AiXp nodes that sent a message since this session was created, and that are considered online

    Returns:
        list: List of names of all the AiXp nodes that are considered online
    """
    return list(self._online_boxes.keys())

  def get_active_pipelines(self, e2id):
    """Get a dictionary with all the pipelines that are active on this AiXp node

    Args:
        e2id (str): name of the AiXp node

    Returns:
        dict: The key is the name of the pipeline, and the value is the entire config dictionary of that pipeline.
    """
    return self._online_boxes.get(e2id, None)

  def attach_to_pipeline(self, e2id, pipeline_name, on_data, on_notification=None, **kwargs) -> Pipeline:
    """Create a Pipeline object and attach to an existing pipeline on a box.
    Useful when one wants to treat an existing pipeline as one of his own, 
    or when one wants to attach callbacks to various events (on_data, on_notification). 

    Args:
        e2id (str): Name of the AiXp node.
        pipeline_name (str): Name of the pipeline
        on_data (Callable[[Pipeline, str, str, dict], None]): Callback that handles messages received from this pipeline. As arguments, it has a reference to this Pipeline object, the name of the Signature and the name of the Instance that sent the message, along with the payload itself.
        on_notification (Callable[[Pipeline, dict], None], optional): Callback that handles notifications received from this pipeline. As arguments, it has a reference to this Pipeline object, along with the payload itself. Defaults to None.

    Raises:
        Exception: The session does not consider the node online or the pipeline does not exist on that box.

    Returns:
        Pipeline: a Pipeline object which can be used to control plugin instances.
    """
    if e2id not in self._online_boxes:
      raise Exception("Unable to attach to pipeline. Node does not exist")

    if pipeline_name not in self._online_boxes[e2id]:
      raise Exception("Unable to attach to pipeline. Pipeline does not exist")

    pipeline_config = {
        k.lower(): v for k, v in self._online_boxes[e2id][pipeline_name].items()}
    data_source = pipeline_config['type']
    return Pipeline(self, self.log, e2id=e2id, config={}, data_source=data_source, create_pipeline=False, silent=self.silent, on_data=on_data, on_notification=on_notification, **pipeline_config, **kwargs)
  
  
  def wait_until_sigint(self, close_session=True, close_pipelines=False):
    """
    This simple method will lock the main thread in a loop until a SIGINT signal is received

    Parameters
    ----------
    close_session : bool, optional
      If `True` will close the session when the loop is exited. The default is True.

    close_pipelines : bool, optional
      If `True` will close all pipelines initiated by this session when the loop is exited. The default is True.

    Returns
    -------
    None.

    """
    try:
      while True:
        sleep(0.1)
    except KeyboardInterrupt:
      self.P("CTRL+C detected. Stopping loop.", color='r')
      
    if close_session:
      self.close(close_pipelines=close_pipelines)
    return
