from ..const.payload import NOTIFICATION_CODES, PAYLOAD_DATA


class Response():
  def __init__(self) -> None:
    self.__is_solved = False
    self.__is_good = None
    self.__log = None

    self.__fail_reason = None
    return

  def __repr__(self) -> str:
    return f"<Response: {self.__class__.__name__}>"

  def set_logger(self, log) -> None:
    self.__log = log

  def P(self, *args, **kwargs):
    if self.__log is None:
      print(*args, **kwargs)
    self.__log.P(*args, **kwargs)

  def D(self, *args, **kwargs):
    if self.__log is None:
      print(*args, **kwargs)
    self.__log.D(*args, **kwargs)

  def fail(self, fail_reason: str) -> None:
    self.__is_solved = True
    self.__is_good = False
    self.__fail_reason = fail_reason
    return

  def success(self) -> None:
    self.__is_good = True
    self.__is_solved = True
    return

  def is_solved(self) -> bool:
    return self.__is_solved

  @property
  def fail_reason(self) -> str:
    return self.__fail_reason

  def is_good_response(self) -> bool:
    return self.__is_good

  def handle_payload(self, payload: dict) -> None:
    # Implement this method and call self.success() or self.fail(fail_reason) if expected message is received
    return

  def handle_notification(self, notification: dict) -> None:
    # Implement this method and call self.success() or self.fail(fail_reason) if expected message is received
    return

  def handle_heartbeat(self, heartbeat) -> None:
    # Implement this method and call self.success() or self.fail(fail_reason) if expected message is received
    return


class PipelineGenericNotificationResponse(Response):
  def __init__(self, node, pipeline_name, success_code, fail_code) -> None:
    super(PipelineGenericNotificationResponse, self).__init__()

    self.node = node
    self.pipeline_name = pipeline_name

    self.success_code = success_code
    self.fail_code = fail_code
    return

  def handle_notification(self, notification: dict) -> None:
    if self.is_solved():
      return

    session_id = notification.get(PAYLOAD_DATA.SESSION_ID)
    payload_path = notification.get(PAYLOAD_DATA.EE_PAYLOAD_PATH)
    notification_code = notification.get("NOTIFICATION_CODE")  # TODO
    notification_message = notification.get(PAYLOAD_DATA.NOTIFICATION)
    node = payload_path[0]
    pipeline = payload_path[1]

    # ignore session_id for now, until we decide on the behavior of the EE
    same_node = node == self.node
    same_pipeline = pipeline == self.pipeline_name
    notification_code_ok = notification_code == self.success_code
    notification_code_failed = notification_code == self.fail_code

    if same_node and same_pipeline:
      self.D("Received notification CODE={} for <{}: {}>. Message: {}".format(
        notification_code, node, pipeline, notification_message))
      if notification_code_ok:
        self.success()
      elif notification_code_failed:
        self.fail(notification_message)
    return


class InstanceGenericNotificationResponse(Response):
  def __init__(self, node, pipeline_name, signature, instance_id, success_code, fail_code) -> None:
    super(InstanceGenericNotificationResponse, self).__init__()

    self.node = node
    self.pipeline_name = pipeline_name
    if signature is not None:
      self.signature = signature.upper()
    self.instance_id = instance_id

    self.success_code = success_code
    self.fail_code = fail_code

    return

  def handle_notification(self, notification: dict) -> None:
    if self.is_solved():
      return

    session_id = notification.get(PAYLOAD_DATA.SESSION_ID)
    payload_path = notification.get(PAYLOAD_DATA.EE_PAYLOAD_PATH)
    notification_code = notification.get("NOTIFICATION_CODE")  # TODO
    notification_message = notification.get(PAYLOAD_DATA.NOTIFICATION)
    notification_info = notification.get(PAYLOAD_DATA.INFO)
    node = payload_path[0]
    pipeline = payload_path[1]
    signature = payload_path[2]
    if signature is not None:
      signature = signature.upper()
    instance_id = payload_path[3]

    # ignore session_id for now, until we decide on the behavior of the EE
    same_node = node == self.node
    same_pipeline = pipeline == self.pipeline_name
    same_signature = signature == self.signature
    same_instance_id = instance_id == self.instance_id
    notification_code_ok = notification_code == self.success_code
    notification_code_failed = notification_code == self.fail_code

    if same_node and same_pipeline and same_signature and same_instance_id:
      self.D("Received notification CODE={} for <{}: {}/{}/{}>. Message: {}\nInfo: {}".format(
        notification_code, node, pipeline, signature, instance_id,
        notification_message, notification_info))
      if notification_code_ok:
        self.success()
      elif notification_code_failed:
        self.fail(notification_info)
    return


class PipelineOKResponse(PipelineGenericNotificationResponse):
  def __init__(self, node, pipeline_name) -> None:
    super(PipelineOKResponse, self).__init__(
      node=node,
      pipeline_name=pipeline_name,
      success_code=NOTIFICATION_CODES.PIPELINE_OK,
      fail_code=NOTIFICATION_CODES.PIPELINE_FAILED
    )
    return


class PipelineArchiveResponse(PipelineGenericNotificationResponse):
  def __init__(self, node, pipeline_name) -> None:
    super(PipelineArchiveResponse, self).__init__(
      node=node,
      pipeline_name=pipeline_name,
      success_code=NOTIFICATION_CODES.PIPELINE_ARCHIVE_OK,
      fail_code=NOTIFICATION_CODES.PIPELINE_ARCHIVE_FAILED
    )
    return


class PluginConfigInPauseOKResponse(InstanceGenericNotificationResponse):
  def __init__(self, node, pipeline_name, signature, instance_id) -> None:
    super(PluginConfigInPauseOKResponse, self).__init__(
      node=node,
      pipeline_name=pipeline_name,
      signature=signature,
      instance_id=instance_id,
      success_code=NOTIFICATION_CODES.PLUGIN_CONFIG_IN_PAUSE_OK,
      fail_code=NOTIFICATION_CODES.PLUGIN_CONFIG_IN_PAUSE_FAILED
    )
    return


class PluginConfigOKResponse(InstanceGenericNotificationResponse):
  def __init__(self, node, pipeline_name, signature, instance_id) -> None:
    super(PluginConfigOKResponse, self).__init__(
      node=node,
      pipeline_name=pipeline_name,
      signature=signature,
      instance_id=instance_id,
      success_code=NOTIFICATION_CODES.PLUGIN_CONFIG_OK,
      fail_code=NOTIFICATION_CODES.PLUGIN_CONFIG_FAILED
    )
    return


class PluginInstanceCommandOKResponse(InstanceGenericNotificationResponse):
  def __init__(self, node, pipeline_name, signature, instance_id) -> None:
    super(PluginInstanceCommandOKResponse, self).__init__(
      node=node,
      pipeline_name=pipeline_name,
      signature=signature,
      instance_id=instance_id,
      success_code=NOTIFICATION_CODES.PLUGIN_INSTANCE_COMMAND_OK,
      fail_code=NOTIFICATION_CODES.PLUGIN_INSTANCE_COMMAND_FAILED
    )
    return
