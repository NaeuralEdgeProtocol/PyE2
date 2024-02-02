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
@author: Lummetry.AI - Stefan Saraev
@project: 
@description:
"""

from ..const import PAYLOAD_DATA


class Instance():
  """
  The Instance class is a wrapper around a plugin instance. It provides a simple API for sending commands to the instance and updating its configuration.
  """

  def __init__(self, pipeline, instance_id, signature, on_data=None, on_notification=None, params={}, **kwargs):
    """
    Create a new instance of the plugin.

    Parameters
    ----------
    pipeline : Pipeline
        The pipeline that the instance is part of
    instance_id : str
        The unique identifier of the instance
    signature : str
        The name of the plugin signature
    on_data : Callable[[Pipeline, str, str, dict], None], optional
        Callback that handles messages received from this instance. As arguments, it has a reference to this Pipeline object, along with the payload itself.
        Defaults to None.
    on_notification : Callable[[Pipeline, dict], None], optional
        Callback that handles notifications received from this instance. As arguments, it has a reference to this Pipeline object, along with the payload itself.
        Defaults to None.
    params : dict, optional
        Parameters used to customize the functionality. One can change the AI engine used for object detection, 
        or finetune alerter parameters to better fit a camera located in a low light environment.
        Defaults to {}
    """
    self.pipeline = pipeline
    self.instance_id = instance_id
    self.signature = signature.upper()
    self.config = {
      **params,
      **kwargs
    }

    self.on_data_callbacks = []
    self.on_notification_callbacks = []

    if on_data:
      self.on_data_callbacks.append(on_data)
    if on_notification:
      self.on_notification_callbacks.append(on_notification)

    return

  # Message handling
  if True:
    def _on_data(self, pipeline, data):
      """
      Handle the data received from the instance.

      Parameters
      ----------
      pipeline : Pipeline
          The pipeline that the instance is part of
      data : dict | Payload
          The data received from the instance
      """
      for callback in self.on_data_callbacks:
        callback(pipeline, data)
      return

    def _on_notification(self, pipeline, data):
      """
      Handle the notification received from the instance.

      Parameters
      ----------
      pipeline : Pipeline
          The pipeline that the instance is part of
      data : dict | Payload
          The notification received from the instance
      """
      for callback in self.on_notification_callbacks:
        callback(pipeline, data)
      return

    def _add_on_data_callback(self, callback):
      """
      Add a new callback to the list of callbacks that handle the data received from the instance.

      Parameters
      ----------
      callback : Callable[[Pipeline, dict], None]
          The callback to add
      """
      self.on_data_callbacks.append(callback)
      return

    def _reset_on_data_callback(self):
      """
      Reset the list of callbacks that handle the data received from the instance.
      """
      self.on_data_callbacks = []
      return

    def _add_on_notification_callback(self, callback):
      """
      Add a new callback to the list of callbacks that handle the notifications received from the instance.

      Parameters
      ----------
      callback : Callable[[Pipeline, dict], None]
          The callback to add
      """
      self.on_notification_callbacks.append(callback)
      return

    def _reset_on_notification_callback(self):
      """
      Reset the list of callbacks that handle the notifications received from the instance.
      """
      self.on_notification_callbacks = []
      return

  # Utils
    def _get_config_dictionary(self):
      """
      Get the configuration of the instance as a dictionary.

      Returns
      -------
      dict
          The configuration of the instance as a dictionary
      """
      config_dict = {
        'INSTANCE_ID': self.instance_id,
        **self.config
      }

      return config_dict

  # API
  if True:
    def update_instance_config(self, config={}, send_command=True, **kwargs):
      """
      Update the configuration of the instance. 
      The new configuration is merged with the existing one.
      Parameters can be passed as a dictionary in `config` or as `kwargs`.

      Parameters
      ----------
      config : dict, optional
          The new configuration of the instance, by default {}
      send_command : bool, optional
          If True, this method will send the update command to the AiXpand node,
          otherwise it will return the update config dictionary that can be sent using `pipeline.batch_update_instances`,
          by default True

      Returns
      -------
      dict | None
          The new configuration of the instance as a dictionary if `send_command` is False, otherwise None
      """
      if send_command:
        self.pipeline.session._send_command_update_instance_config(
          worker=self.pipeline.e2id,
          pipeline=self.pipeline.name,
          signature=self.signature,
          instance_id=self.instance_id,
          instance_config={**config, **kwargs},
        )
      else:
        return {
          {
            PAYLOAD_DATA.NAME: self.pipeline.name,
            PAYLOAD_DATA.SIGNATURE: self.signature,
            PAYLOAD_DATA.INSTANCE: self.instance_id,
            PAYLOAD_DATA.INSTANCE_CONFIG: {**config, **kwargs},
          },
        }
      return

    def send_instance_command(self, command, payload={}, command_params={}):
      """
      Send a command to the instance.

      Parameters
      ----------
      command : str
          The command to send
      payload : dict, optional
          The payload of the command, by default {}
      command_params : dict, optional
          The parameters of the command, by default {}
      """
      self.pipeline.session._send_command_instance_command(
        worker=self.pipeline.e2id,
        pipeline=self.pipeline.name,
        signature=self.signature,
        instance_id=self.instance_id,
        command=command,
        payload=payload,
        command_params=command_params,
      )
      return

    def close(self):
      """
      Close the instance.
      """
      self.pipeline.stop_plugin_instance(self)
      return

    def stop(self):
      """
      Close the instance. Alias for `close`.
      """
      self.close()
