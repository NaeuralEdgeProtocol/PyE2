from ..const import PAYLOAD_DATA
from .transaction import Transaction
from .responses import PipelineOKResponse, PluginConfigOKResponse, PluginInstanceCommandOKResponse


class Instance():
  """
  The Instance class is a wrapper around a plugin instance. It provides a simple API for sending commands to the instance and updating its configuration.
  """

  def __init__(self, log, pipeline, instance_id, signature, on_data=None, on_notification=None, config={}, is_attached=False, **kwargs):
    """
    Create a new instance of the plugin.

    Parameters
    ----------
    log : Logger
        The logger object
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
    config : dict, optional
        Parameters used to customize the functionality. One can change the AI engine used for object detection,
        or finetune alerter parameters to better fit a camera located in a low light environment.
        Defaults to {}
    """
    self.log = log
    self.pipeline = pipeline
    self.instance_id = instance_id
    self.signature = signature.upper()
    self.config = {}

    if is_attached:
      assert len(kwargs) == 0, "When attaching an instance, no additional parameters are allowed"
      self.config = config
      self.proposed_config = None
    else:
      self.proposed_config = {**config, **kwargs}
      self.proposed_config = {k.upper(): v for k, v in self.proposed_config.items()}
    self.__staged_config = None
    self.__was_last_operation_successful = None

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
  if True:
    def __repr__(self) -> str:
      node_id = self.pipeline.node_id
      pipeline_name = self.pipeline.name
      signature = self.signature
      instance_id = self.instance_id

      return f"<Instance: {node_id}/{pipeline_name}/{signature}/{instance_id}>"

    def _is_tainted(self):
      """
      Check if the instance has a proposed configuration.

      Returns
      -------
      bool
          True if the instance has a proposed configuration, False otherwise
      """
      return self.proposed_config is not None

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

    def _get_proposed_config_dictionary(self):
      """
      Get the proposed configuration of the instance as a dictionary.

      Returns
      -------
      dict
          The proposed configuration of the instance as a dictionary
      """
      if self.proposed_config is None:
        return self._get_config_dictionary()

      proposed_config_dict = {
        'INSTANCE_ID': self.instance_id,
        **self.proposed_config
      }

      return proposed_config_dict

    def _apply_staged_config(self, verbose=False):
      """
      Apply the staged configuration to the instance.
      """
      if self.__staged_config is None:
        return

      if verbose:
        self.P(f'Applying staged configuration to instance <{self.instance_id}>', color="g")
      self.__was_last_operation_successful = True

      self.config = {**self.config, **self.__staged_config}
      self.__staged_config = None
      return

    def _discard_staged_config(self, fail_reason: str):
      """
      Discard the staged configuration for the instance.
      """
      self.P(f'Discarding staged configuration for instance <{self.instance_id}>. Reason: {fail_reason}', color="r")
      self.__was_last_operation_successful = False

      self.__staged_config = None
      return

    def _stage_proposed_config(self):
      """
      Stage the proposed configuration for the instance.
      """
      if self.proposed_config is None:
        return

      if self.__staged_config is not None:
        raise ValueError("Instance configuration has already been staged, waiting for confirmation from Execution Engine")

      # self.__staged_config is None
      self.__staged_config = self.proposed_config
      self.proposed_config = None

      self.__was_last_operation_successful = None
      return

    def _handle_instance_command_success(self):
      """
      Handle the success of the instance command.
      """
      self.P(f'Instance command successful for instance <{self.instance_id}>', color="g")
      self.__was_last_operation_successful = True
      return

    def _handle_instance_command_failure(self, fail_reason: str):
      """
      Handle the failure of the instance command.
      """
      self.P(f'Instance command failed for instance <{self.instance_id}>. Reason: {fail_reason}', color="r")
      self.__was_last_operation_successful = False
      return

    def __register_transaction_for_instance_command(self, session_id: str = None, timeout: float = 0) -> list[Transaction]:
      """
      Register a new transaction for the instance command.
      This method is called before sending an instance command to the Naeural edge node.

      Parameters
      ----------
      session_id : str, optional
          The session ID of the transaction, by default None
      timeout : float, optional
          The timeout for the transaction, by default 0

      Returns
      -------
      list[Transaction]
          The list of transactions generated
      """
      required_responses = [
        PipelineOKResponse(self.pipeline.node_id, self.pipeline.name),
        PluginInstanceCommandOKResponse(self.pipeline.node_id, self.pipeline.name, self.signature, self.instance_id),
        # PluginConfigOKResponse(self.pipeline.node_id, self.pipeline.name, self.signature, self.instance_id),
      ]

      transactions = [self.pipeline.session._register_transaction(
          session_id=session_id,
          lst_required_responses=required_responses,
          timeout=timeout,
          on_success_callback=self._handle_instance_command_success,
          on_failure_callback=self._handle_instance_command_failure,
      )]

      return transactions

    def _get_instance_update_required_responses(self):
      """
      Get the responses required to update the instance.

      Returns
      -------
      list[str]
          The list of responses required to update the instance
      """
      responses = [
        PipelineOKResponse(self.pipeline.node_id, self.pipeline.name),
        PluginConfigOKResponse(self.pipeline.node_id, self.pipeline.name, self.signature, self.instance_id),
      ]

      return responses

    def _get_instance_remove_required_responses(self):
      """
      Get the responses required to delete the instance.

      Returns
      -------
      list[str]
          The list of responses required to delete the instance
      """
      responses = [
        PipelineOKResponse(self.pipeline.node_id, self.pipeline.name),
      ]

      return responses

  # API
  if True:
    @property
    def was_last_operation_successful(self) -> bool:
      """
      Get the status of the last operation.

      Example:
      --------
      ```python
      instance.send_instance_command("RESTART", wait_confirmation=False)

      if instance.was_last_operation_successful is not None:
        if instance.was_last_operation_successful:
          print("Last operation was successful")
        else:
          print("Last operation failed")
      else:
        print("No ACK received yet for this operation")
      ```

      Returns
      -------
      bool, None
          True if the last operation was successful, False if it failed, None if the ACK has not been received yet
      """
      return self.__was_last_operation_successful

    def update_instance_config(self, config={}, **kwargs):
      """
      Update the configuration of the instance.
      The new configuration is merged with the existing one.
      Parameters can be passed as a dictionary in `config` or as `kwargs`.

      Parameters
      ----------
      config : dict, optional
          The new configuration of the instance, by default {}

      Returns
      -------
      dict | None
          The new configuration of the instance as a dictionary if `send_command` is False, otherwise None
      """

      if self.__staged_config is not None:
        raise ValueError("Instance configuration has already been staged, waiting for confirmation from Execution Engine")

      if self.proposed_config is None:
        self.proposed_config = {}

      self.proposed_config = {**self.proposed_config, **config, **{k.upper(): v for k, v in kwargs.items()}}

      for k, v in self.config.items():
        if k in self.proposed_config:
          if self.proposed_config[k] == v:
            del self.proposed_config[k]

      if len(self.proposed_config) == 0:
        self.proposed_config = None

      return

    def send_instance_command(self, command, payload={}, command_params={}, wait_confirmation=True, timeout=10):
      """
      Send a command to the instance.
      This command can block until the command is confirmed by the Naeural edge node.

      Example:
      --------
      ```python
      instance.send_instance_command('START', wait_confirmation=True)

      transactions_p1 = instance1.send_instance_command('START', wait_confirmation=False)
      transactions_p2 = instance2.send_instance_command('START', wait_confirmation=False)
      # wait for both commands to be confirmed, but after both commands are sent
      session.wait_for_transactions(transactions_p1 + transactions_p2)
      ```
      Parameters
      ----------
      command : str
          The command to send
      payload : dict, optional
          The payload of the command, by default {}
      command_params : dict, optional
          The parameters of the command, by default {}
      wait_confirmation : bool, optional
          Whether to wait for the confirmation of the command, by default False
      timeout : int, optional
          The timeout for the transaction, by default 10    

      Returns
      -------
      list[Transaction] | None
          The list of transactions generated, or None if `wait_confirmation` is False.

      """
      self.P(f'Sending command <{command}> to instance <{self.__repr__()}>', color="b")

      self.__was_last_operation_successful = None

      transactions = self.__register_transaction_for_instance_command(timeout=timeout)

      self.pipeline.session._send_command_instance_command(
        worker=self.pipeline.node_id,
        pipeline_name=self.pipeline.name,
        signature=self.signature,
        instance_id=self.instance_id,
        command=command,
        payload=payload,
        command_params=command_params,
      )

      if wait_confirmation:
        self.pipeline.session.wait_for_transactions(transactions)
      else:
        return transactions
      return

    def close(self):
      """
      Close the instance.
      """
      self.pipeline.remove_plugin_instance(self)
      return

    def stop(self):
      """
      Close the instance. Alias for `close`.
      """
      self.close()

    def P(self, *args, **kwargs):
      self.log.P(*args, **kwargs)
      return

    def D(self, *args, **kwargs):
      self.log.D(*args, **kwargs)
      return
