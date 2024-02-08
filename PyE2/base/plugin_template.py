class CustomPluginTemplate:

  def set_output_image(self, img):
    """
    Add the image to the output payload.
    Note that in order to generate a payload, the method must return a non-None value.

    Parameters
    ----------
    img : np.ndarray
      The image to be added to the payload.
    """
    raise NotImplementedError

  def set_image(self, img):
    """
    Add the image to the output payload.
    Note that in order to generate a payload, the method must return a non-None value.

    Parameters
    ----------
    img : np.ndarray
      The image to be added to the payload.
    """
    raise NotImplementedError

  """TrackAPI methods"""
  if True:
    def trackapi_in_zone_total_seconds(self, object_id, object_type):
      """
      Public method for accessing the total seconds spent in the target zone by a specified object.
      Parameters
      ----------
      object_id - int
      object_type - str

      Returns
      -------
      res - int, total number of seconds spent in the target zone
      """
      raise NotImplementedError

    def trackapi_in_zone_history(self, object_id, object_type):
      """
      Public method for accessing the history in the target zone of a specified object.
      Parameters
      ----------
      object_id - int
      object_type - str

      Returns
      -------
      res - list, list of intervals that the specified object was in the target zone.
      """
      raise NotImplementedError

    def trackapi_centroid_history(self, object_id, object_type):
      """
      Public method for accessing the centroid history of a specified object.
      Parameters
      ----------
      object_id - int
      object_type - str

      Returns
      -------
      res - list, list of points that signify the provided object's centroid on each appearance.
      """
      raise NotImplementedError

    def trackapi_type_history(self, object_id, object_type):
      """
      If meta-types are not used than this will just provide the object's number of appearances.
      Public method for accessing the type history of a specified object as a frequency dictionary.
      Parameters
      ----------
      object_id - int
      object_type - str

      Returns
      -------
      res - dict, dictionary providing the number of times the current object appeared as a certain class.
      """
      raise NotImplementedError

    def trackapi_type_history_deque(self, object_id, object_type):
      """
      If meta-types are not used than this will just provide a list full of the same type.
      Public method for accessing the type history of a specified object as a deque.
      Parameters
      ----------
      object_id - int
      object_type - str

      Returns
      -------
      res - deque, list of the type that the current object was at each appearance
      """
      raise NotImplementedError

    def trackapi_class_count(self, object_id, object_type, class_name):
      """
      If meta-types are not used than this will just provide the number of appearances.
      Public method for accessing how many times the object was a certain class.
      Parameters
      ----------
      object_id - int
      object_type - str
      class_name - str or list

      Returns
      -------
      res - int, how many times the object was a certain class.
      """
      raise NotImplementedError

    def trackapi_non_class_count(self, object_id, object_type, class_name):
      """
      If meta-types are not used than this will just provide 0.
      Public method for accessing how many times the object was not a certain class.
      Parameters
      ----------
      object_id - int
      object_type - str
      class_name - str or list

      Returns
      -------
      res - int, how many times the object was not a certain class.
      """
      raise NotImplementedError

    def trackapi_class_ratio(self, object_id, object_type, class_name):
      """
      If meta-types are not used than this will just provide 1.
      Public method for accessing the ratio between how many times the object was
      a certain class and the total number of appearances.
      Parameters
      ----------
      object_id - int
      object_type - str
      class_name - str or list

      Returns
      -------
      res - float, ratio of class appearances.
      """
      raise NotImplementedError

    def trackapi_original_position(self, object_id, object_type):
      """
      Public method for accessing the original position of a specified object.
      Parameters
      ----------
      object_id - int
      object_type - str

      Returns
      -------
      res - list, centroid of the current object on its first appearance.
      """
      raise NotImplementedError

    def trackapi_max_movement(self, object_id, object_type, steps=None, method='l2'):
      """
      Public method for accessing the maximum distance between the
      original position of a specified object and all of its following centroids.
      Parameters
      ----------
      object_id - int
      object_type - str
      steps - int or None, how much further back to check for movement
      - if None this will compute the max movement for the entire history
      - if x - int, this will compute the max movement for the last k steps
      method - str, method used for computing the distance
      - if 'l1' this will return the 'l1' distance
      - if 'l2' this will return the 'l2' distance

      Returns
      -------
      res - int or float, max distance the specified object was from its original position

      """
      raise NotImplementedError

    def trackapi_last_rectangle(self, object_id, object_type):
      """
      Public method for accessing the last seen rectangle of a specified object.
      Parameters
      ----------
      object_id - int
      object_type - str

      Returns
      -------
      res - list, last seen rectangle of the specified object in format [top, left, bottom, right]
      """
      raise NotImplementedError

  """Debug Info methods"""
  if True:
    def reset_debug_info(self):
      """
      Reset the debug info list.
      """
      raise NotImplementedError

    def add_debug_info(self, value, key: str = None):
      """
      Add debug info to the output image.
      The information will be stored in a new line.

      Parameters
      ----------
      value : Any
          The info to be shown
      key : str
          The key that identifies this debug line
      """
      raise NotImplementedError

  """Base plugin methods"""
  if True:
    @property
    def ee_ver(self):
      """
      Returns the version of the node.
      """
      raise NotImplementedError

    @property
    def runs_in_docker(self):
      """
      Returns whether the plugin runs in a docker container.
      """
      raise NotImplementedError

    @property
    def docker_branch(self):
      """
      Returns the branch of the docker image.
      """
      raise NotImplementedError

    def P(self, s, color=None, **kwargs):
      """
      Print a message to the console.

      Parameters
      ----------
      s : str
          The message to be printed
      color : str
          The color of the message
      """
      raise NotImplementedError

    @property
    def plugins_shmem(self):
      """
      Returns the shared memory object.
      """
      raise NotImplementedError

    @property
    def last_payload_time(self):
      """
      Returns the time of the last payload.
      """
      raise NotImplementedError

    @property
    def last_payload_time_str(self):
      """
      Returns the time of the last payload in string format.
      """
      raise NotImplementedError

    @property
    def total_payload_count(self):
      """
      Returns the total number of payloads.
      """
      raise NotImplementedError

#  TODO: write the documentation for the following methods

    @property
    def instance_relative_path(self):
      raise NotImplementedError

    @property
    def save_path(self):
      raise NotImplementedError

    @property
    def plugin_output_path(self):
      raise NotImplementedError

    @property
    def start_time(self):
      raise NotImplementedError

    @property
    def first_process_time(self):
      raise NotImplementedError

    @property
    def unique_identification(self):
      raise NotImplementedError

    @property
    def plugin_id(self):
      raise NotImplementedError

    @property
    def str_unique_identification(self):
      raise NotImplementedError

    @property
    def eeid(self):
      raise NotImplementedError

    @property
    def ee_id(self):
      raise NotImplementedError

    @property
    def node_id(self):
      raise NotImplementedError

    @property
    def e2_id(self):
      raise NotImplementedError

    @property
    def e2_addr(self):
      raise NotImplementedError

    @property
    def ee_addr(self):
      raise NotImplementedError

    @property
    def node_addr(self):
      raise NotImplementedError

    def get_stream_id(self):
      raise NotImplementedError

    def get_signature(self):
      raise NotImplementedError

    def get_instance_id(self):
      raise NotImplementedError

    def start_timer(self, tmr_id):
      raise NotImplementedError

    def end_timer(self, tmr_id, skip_first_timing=False, periodic=False):
      raise NotImplementedError

    def stop_timer(self, tmr_id, skip_first_timing=False, periodic=False):
      raise NotImplementedError

    def add_payload(self, payload):
      """
      Adds a payload in the plugin instance output queue. If used inside plugins
      plese do NOT return the payload from _process as the payload will be duplicated

      Parameters
      ----------
      payload : GeneralPayload or dict
        the payload

      Returns
      -------
      None.

      """
      raise NotImplementedError

    def add_payload_by_fields(self, **kwargs):
      """
      Adds a payload in the plugin instance output queue based on fields rather than
      on a already created payload object.
      If used inside plugins plese do NOT return the payload from _process as the payload
      will be duplicated

      Parameters
      ----------
      **kwargs : dict

      Returns
      -------
      None.

      """
      raise NotImplementedError

    def create_and_send_payload(self, **kwargs):
      """
      Creates a payload and sends it to the output queue.
      If used inside plugins plese do NOT return the payload from _process as the payload
      will be duplicated

      Parameters
      ----------
      **kwargs : dict

      Returns
      -------
      None.

      """
      raise NotImplementedError

  """Alerter methods"""
  if True:

    def alerter_maybe_create(self, alerter, **kwargs):
      raise NotImplementedError

    def alerter_create(self, alerter='default',
                       raise_time=None, lower_time=None,
                       value_count=None,
                       raise_thr=None, lower_thr=None,
                       alert_mode=None,
                       alert_mode_lower=None,
                       reduce_value=None, reduce_threshold=None,
                       show_version=False):
      raise NotImplementedError

    def add_alerter_observation(self, value, alerter='default'):
      raise NotImplementedError

    def get_alerter(self, alerter='default'):
      raise NotImplementedError

    def alerter_status_dict(self, alerter='default'):
      raise NotImplementedError

    def alerter_get_last_value(self, alerter='default'):
      raise NotImplementedError

    def alerter_in_confirmation(self, alerter='default'):
      raise NotImplementedError

    def alerter_setup_values(self, alerter='default'):
      raise NotImplementedError

    def alerter_hard_reset(self, state=False, alerter='default'):
      raise NotImplementedError

    def alerter_hard_reset_all(self):
      raise NotImplementedError

    def alerter_add_observation(self, value, alerter='default'):
      """
      Add a new numerical value observation to the given alerter state machine instance

      Parameters
      ----------
      value : float
        The value to be added that can be a percentage or a number or elements - depeding of the configuration of the alerter
        that has been given via "ALERT_MODE".
      alerter : str, optional
        The identifier of the given alerter state machine. The default is 'default'.

      Returns
      -------
      TYPE
        None.

      """
      raise NotImplementedError

    def alerter_is_new_alert(self, alerter='default'):
      """
      Returns `True` if the current state of the given `alerter` state machine has just changed from "lowered" to "raised"

      Parameters
      ----------
      alerter : str, optional
        Identifier of the given alerter instance. The default is 'default'.

      Returns
      -------
      TYPE
        bool.

      """
      raise NotImplementedError

    def alerter_is_new_raise(self, alerter='default'):
      """
      Returns `True` if the current state of the given `alerter` state machine has just changed from "lowered" to "raised"

      Parameters
      ----------
      alerter : str, optional
        Identifier of the given alerter instance. The default is 'default'.

      Returns
      -------
      TYPE
        bool.

      """
      raise NotImplementedError

    def alerter_is_new_lower(self, alerter='default'):
      """
      Returns `True` if the current state of the given `alerter` state machine has just changed from "raised" to "lowered"

      Parameters
      ----------
      alerter : str, optional
        Identifier of the given alerter instance. The default is 'default'.

      Returns
      -------
      TYPE
        bool.

      """
      raise NotImplementedError

    def alerter_is_alert(self, alerter='default'):
      """
      Returns `True` if the current state of the given `alerter` state machine is "raised"

      Parameters
      ----------
      alerter : str, optional
        Identifier of the given alerter instance. The default is 'default'.

      Returns
      -------
      TYPE
        bool.

      """
      raise NotImplementedError

    def alerter_status_changed(self, alerter='default'):
      """
      Returns `True` if the current state of the given `alerter` state machine has just changed

      Parameters
      ----------
      alerter : str, optional
        Identifier of the given alerter instance. The default is 'default'.

      Returns
      -------
      TYPE
        bool.

      """
      raise NotImplementedError

    def alerter_time_from_last_change(self, alerter='default'):
      """
      Returns the number of seconds from the last change of the given alerter stata machine

      Parameters
      ----------
      alerter : str, optional
        Identifier of the given alerter instance. The default is 'default'.

      Returns
      -------
      TYPE
        bool.

      """
      raise NotImplementedError

    def alerter_maybe_force_lower(self, max_raised_time=0, alerter='default'):
      """
      Forces the given alerter to reset to "lowered" status if the current state is "raised"

      Parameters
      ----------
      alerter : str, optional
        Identifier of the given alerter instance. The default is 'default'.

      max_raised_time: float, optional
        The number of seconds after the raised alerter is forced to lower its status

      Returns
      -------
      TYPE
        bool.

      """
      raise NotImplementedError

  """DataAPI methods"""
  if True:
    def dataapi_specific_input(self, idx=0, raise_if_error=False):
      """
      API for accessing a specific index (by its index in the 'INPUTS' list).

      Parameters
      ----------
      idx : int, optional
        The index of the input in the 'INPUTS' list
        The default value is 0.

      raise_if_error : bool, optional
        Whether to raise IndexError or not when the requested index is out of range.
        The default value is False

      Returns
      -------
      dict
        The requested input / substream.
        For the second example in the class docstring ('multi_modal_2_images_one_sensor_stream'), if `idx==0`, the API will return
          {
            'IMG' : np.ndarray(1),
            'STRUCT_DATA' : None,
            'INIT_DATA' : None,
            'TYPE' : 'IMG',
            'METADATA' : {Dictionary with current input metadata}
          }

      Raises
      ------
      IndexError
        when the requested index is out of range
      """
      raise NotImplementedError

    def dataapi_images(self, full=False):
      """
      API for accessing all the images in the 'INPUTS' list
      Parameters
      ----------
      full : bool, optional
        Specifies whether the images are returned full (the whole input dictionary) or not (just the value of 'IMG' in the input dictionary)
        The default value is False

      Returns
      -------
      dict{int : dict} (if full==True) / dict{int : np.ndarray} (if full=False)
        The substreams that have images.
        For the second example in the class docstring ('multi_modal_2_images_one_sensor_stream'), the API will return
          {
            0 : {
              'IMG' : np.ndarray(1),
              'STRUCT_DATA' : None,
              'INIT_DATA' : None,
              'TYPE' : 'IMG',
              'METADATA' : {Dictionary with current input metadata}
            },

            1 : {
              'IMG' : np.ndarray(2),
              'STRUCT_DATA' : None,
              'INIT_DATA' : None,
              'TYPE' : 'IMG',
              'METADATA' : {Dictionary with current input metadata}
            }
          } if full==True

          or

          {
            0 : np.ndarray(1),
            1 : np.ndarray(2)
          } if full==False
      """
      raise NotImplementedError

    def dataapi_images_as_list(self):
      raise NotImplementedError

    def dataapi_specific_image(self, idx=0, full=False, raise_if_error=False):
      """
      API for accessing a specific image in the 'INPUTS' list

      Parameters
      ----------
      idx : int, optional
        The index of the image in the images list
        Attention! If there is a metastream that collects 3 inputs - ['IMG', 'STRUCT_DATA', 'IMG'], for accessing the last
        image, `idx` should be 1!
        The default value is 0

      full : bool, optional
        Passed to `dataapi_images`
        The default value is False

      raise_if_error : bool, optional
        Whether to raise IndexError or not when the requested index is out of range.
        The default value is False

      Returns
      -------
      dict (if full==True) / np.ndarray (if full==False)
        dict -> the whole input dictionary
        np.ndarray -> the value of 'IMG' in the input dictionary

      Raises
      ------
      IndexError
        when the requested index is out of range
      """
      raise NotImplementedError

    def dataapi_image(self, full=False, raise_if_error=False):
      """
      API for accessing the first image in the 'INPUTS' list
      (shortcut for `dataapi_specific_image`, most of the cases will have a single image on a stream)

      Parameters
      ----------
      full : bool, optional
        Passed to `dataapi_specific_image`
        The default value is False

      raise_if_error : bool, optional
        Passed to `dataapi_specific_image`
        The default value is False

      Returns
      -------
      dict (if full==True) / np.ndarray (if full==False)
        Returned by `dataapi_specific_image`

      Raises
      ------
      IndexError
        when there are no images on the stream if `raise_if_error == True`
      """
      raise NotImplementedError

    def dataapi_struct_datas(self, full=False):
      """
      API for accessing all the structured datas in the 'INPUTS' list

      Parameters
      ----------
      full : bool, optional
        Specifies whether the structured datas are returned full (the whole input dictionary) or not (just the value of 'STRUCT_DATA' in the input dictionary)
        The default value is False

      Returns
      -------
      dict{int : dict} (if full==True) / dict{int : object} (if full==False)
        The substreams that have structured data.
        For the second example in the class docstring ('multi_modal_2_images_one_sensor_stream'), the API will return
          {
            0: {
              'IMG' : None,
              'STRUCT_DATA' : an_object,
              'INIT_DATA' : None,
              'TYPE' : 'STRUCT_DATA',
              'METADATA' : {Dictionary with current input metadata}
            }
          } if full==True

          or

          {
            0 : an_object
          } if full==False
      """
      raise NotImplementedError

    def dataapi_specific_struct_data(self, idx=0, full=False, raise_if_error=False):
      """
      API for accessing a specific structured data in the 'INPUTS' list

      Parameters
      ----------
      idx : int, optional
        The index of the structured data in the structured datas list
        Attention! If there is a metastream that collects 3 inputs - ['IMG', 'STRUCT_DATA', 'IMG'], for accessing the structured data
        `idx` should be 0!
        The default value is 0

      full : bool, optional
        Passed to `dataapi_struct_datas`
        The default value is False

      raise_if_error : bool, optional
        Whether to raise IndexError or not when the requested index is out of range.
        The default value is True

      Returns
      -------
      dict (if full==True) / object (if full==False)
        dict -> the whole input dictionary
        object -> the value of 'STRUCT_DATA' in the input dictionary

      Raises
      ------
      IndexError
        when the requested index is out of range
      """
      raise NotImplementedError

    def dataapi_struct_data(self, full=False, raise_if_error=False):
      """
      API for accessing the first structured data in the 'INPUTS' list
      (shortcut for `dataapi_specific_struct_data`, most of the cases will have a single structured data on a stream)

      Parameters
      ----------
      full : bool, optional
        Passed to `dataapi_specific_struct_data`
        The default value is False

      raise_if_error : bool, optional
        Passed to `dataapi_specific_struct_data`
        The default value is True

      Returns
      -------
      dict (if full==True) / object (if full==False)
        Returned by `dataapi_specific_struct_data`

      Raises
      ------
      IndexError
        when there are no struct_data on the stream
      """
      raise NotImplementedError

    def dataapi_inputs_metadata(self, as_list=False):
      """
      API for accessing the concatenated metadata from all inputs (images and structured datas together)
      This is not the same as the stream metadata that points to the overall params of the execution
      pipeline.

      Returns
      -------
      dict
        the concatenated metadata from all inputs
      """
      raise NotImplementedError

    def dataapi_specific_input_metadata(self, idx=0, raise_if_error=False):
      """
      API for accessing the metadata of a specific input

      Parameters
      ----------
      idx : int, optional
        Passed to `dataapi_specific_input`
        The default value is 0

      raise_if_error : bool, optional
        Passed to `dataapi_specific_input`
        The default value is False

      Returns
      -------
      dict
        the value of "METADATA" key in the requested input

      Raises
      ------
      IndexError
        when the requested index is out of range
      """
      raise NotImplementedError

    def dataapi_input_metadata(self, raise_if_error=False):
      """
      API for accessing the metadata of the first input
      (shortcut for `dataapi_specific_input_metadata`, most of the cases will have a single input on a stream)

      Parameters
      ----------
      raise_if_error : bool, optional
        Passed to `dataapi_specific_input_metadata`
        The default value is False

      Returns
      -------
      dict
        Returned by `dataapi_specific_input_metadata`

      Raises
      ------
      IndexError
        raised by `dataapi_specific_input_metadata`
      """
      raise NotImplementedError

    def dataapi_all_metadata(self):
      """
      API for accessing the concatenated stream metadata and metadata from all inputs

      Returns
      -------
      dict
        the concatenated stream metadata and metadata from all inputs
      """
      raise NotImplementedError

    def dataapi_images_inferences(self):
      """
      API for accessing just the images inferences.
      Filters the output of `dataapi_inferences`, keeping only the AI engines that run on images

      Returns
      -------
      dict{str:list}
        the inferences that comes from the images serving plugins configured for the current plugin instance.
      """
      raise NotImplementedError

    def dataapi_images_global_inferences(self):
      """
      Alias for `dataapi_images_inferences`
      """
      raise NotImplementedError

    def dataapi_images_plugin_inferences(self):
      """
      API for accessing the images inferences, filtered by confidence threshold and object types.
      More specifically, all the plugin inferences are the global inferences that surpass a configured confidence
      threshold and have a specific type. For example, an object detector basically infers for all the objects in
      COCO dataset. But, a certain plugin may need only persons and dogs.

      Returns
      -------
      dict{str:list}
        filtered images inferences by confidence threshold and object types
      """
      raise NotImplementedError

    def dataapi_images_instance_inferences(self):
      """
      API for accessing the images inferences, filtered by confidence threshold, object types and target zone.
      More specifically, all the instance inferences are the plugin inferences that intersects (based on PRC_INTERSECT)
      with the configured target zone.

      Returns
      -------
      dict{str:list}
        filtered images inferences by confidence threshold, object types and target zone
      """
      raise NotImplementedError

    def dataapi_images_plugin_positional_inferences(self):
      """
      API for accessing the images inferences that have positions (TLBR_POS).
      Returns
      -------
      dict{str:list}
        filtered images inferences by having positions (TLBR_POS)
      """
      raise NotImplementedError

    def dataapi_specific_image_inferences(self, idx=0, how=None, mode=None, raise_if_error=False):
      """
      API for accesing inferences for a specific image (global, plugin or instance inferences)
      See `dataapi_images_global_inferences`, `dataapi_images_plugin_inferences`, `dataapi_images_instance_inferences`

      Parameters
      ----------
      idx : int, optional
        The index of the image in the images list
        Attention! If there is a metastream that collects 3 inputs - ['IMG', 'STRUCT_DATA', 'IMG'], for accessing the last
        image, `idx` should be 1!
        The default value is 0

      how : str, optional
        Could be: 'list' or 'dict'
        Specifies how the inferences are returned. If 'list', then the AI engine information will be lost and all the
        inferences from all the employed AI engines will be concatenated in a list; If 'dict', then the AI engine information
        will be preserved.
        The default value is None ('list')

      mode : str, optional
        Could be: 'global', 'plugin' or 'instance'
        Specifies which inferences are requested.
        The default value is None ('instance')

      raise_if_error : bool, optional
        Whether to raise IndexError or not when the requested index is out of range.
        The default value is False

      Returns
      -------
      dict (if how == 'dict') or list (if how == 'list')
        the requested image inferences (global, plugin or instance) in the requested format (dict or list)

      Raises
      ------
      IndexError
        when the requested index is out of range
      """
      raise NotImplementedError

    def dataapi_image_inferences(self, how=None, mode=None, raise_if_error=False):
      """
      API for accessing the first image inferences
      (shortcut for `dataapi_specific_image_inferences`, most of the cases will have a single image on a stream)

      Parameters
      ----------
      how : str, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is None

      mode : str, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is None

      raise_if_error : bool, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is False

      Returns
      -------
      dict (if how == 'dict') or list (if how == 'list')
        returned by `dataapi_specific_image_inferences`

      Raises
      ------
      IndexError
        raised by `dataapi_specific_image_inferences`
      """
      raise NotImplementedError

    def dataapi_specific_image_global_inferences(self, idx=0, how=None, raise_if_error=False):
      """
      API for accessing a specific image global inferences
      (shortcut for `dataapi_specific_image_inferences`)

      Parameters
      ----------
      idx : int, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is None

      how : str, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is None

      raise_if_error : bool, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is False

      Returns
      -------
      dict (if how == 'dict') or list (if how == 'list')
        returned by `dataapi_specific_image_inferences`

      Raises
      ------
      IndexError
        raised by `dataapi_specific_image_inferences`
      """
      raise NotImplementedError

    def dataapi_specific_image_plugin_inferences(self, idx=0, how=None, raise_if_error=False):
      """
      API for accessing a specific image plugin inferences
      (shortcut for `dataapi_specific_image_inferences`)

      Parameters
      ----------
      idx : int, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is None

      how : str, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is None

      raise_if_error : bool, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is False

      Returns
      -------
      dict (if how == 'dict') or list (if how == 'list')
        returned by `dataapi_specific_image_inferences`

      Raises
      ------
      IndexError
        raised by `dataapi_specific_image_inferences`
      """
      raise NotImplementedError

    def dataapi_specific_image_instance_inferences(self, idx=0, how=None, raise_if_error=False):
      """
      API for accessing a specific image inferences for the current plugin instance
      (shortcut for `dataapi_specific_image_inferences`)

      Parameters
      ----------
      idx : int, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is None

      how : str, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is None ('list')

      raise_if_error : bool, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is False

      Returns
      -------
      dict (if how == 'dict') or list (if how == 'list')
        returned by `dataapi_specific_image_inferences`

      Raises
      ------
      IndexError
        raised by `dataapi_specific_image_inferences`
      """
      raise NotImplementedError

    def dataapi_specific_image_plugin_positional_inferences(self, idx=0, how=None, raise_if_error=False):
      """
      API for accessing a specific image plugin positional inferences
      (shortcut for `dataapi_specific_image_inferences`)

      Parameters
      ----------
      idx : int, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is None

      how : str, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is None

      raise_if_error : bool, optional
        Passed to `dataapi_specific_image_inferences`
        The default value is False

      Returns
      -------
      dict (if how == 'dict') or list (if how == 'list')
        returned by `dataapi_specific_image_inferences`

      Raises
      ------
      IndexError
        raised by `dataapi_specific_image_inferences`
      """
      raise NotImplementedError

    def dataapi_image_global_inferences(self, how=None, raise_if_error=False):
      """
      API for accessing the first image global inferences
      (shortcut for `dataapi_specific_image_global_inferences`, most of the cases will have a single image on a stream)

      Parameters
      ----------
      how : str, optional
        Passed to `dataapi_specific_image_global_inferences`
        The default value is None

      raise_if_error : bool, optional
        Passed to `dataapi_specific_image_global_inferences`
        The default value is False

      Returns
      -------
      dict (if how == 'dict') or list (if how == 'list')
        returned by `dataapi_specific_image_global_inferences`

      Raises
      ------
      IndexError
        raised by `dataapi_specific_image_global_inferences`
      """
      raise NotImplementedError

    def dataapi_image_plugin_inferences(self, how=None, raise_if_error=False):
      """
      API for accessing the first image plugin inferences
      (shortcut for `dataapi_specific_image_plugin_inferences`, most of the cases will have a single image on a stream)

      Parameters
      ----------
      how : str, optional
        Passed to `dataapi_specific_image_plugin_inferences`
        The default value is None

      raise_if_error : bool, optional
        Passed to `dataapi_specific_image_plugin_inferences`
        The default value is False

      Returns
      -------
      dict (if how == 'dict') or list (if how == 'list')
        returned by `dataapi_specific_image_plugin_inferences`

      Raises
      ------
      IndexError
        raised by `dataapi_specific_image_plugin_inferences`
      """
      raise NotImplementedError

    def dataapi_image_instance_inferences(self, how=None, raise_if_error=False):
      """
      API for accessing the first image instance inferences
      (shortcut for `dataapi_specific_image_instance_inferences`, most of the cases will have a single image on a stream)

      Parameters
      ----------
      how : str, optional
        Passed to `dataapi_specific_image_instance_inferences`
        The default value is None ('list')

      raise_if_error : bool, optional
        Passed to `dataapi_specific_image_instance_inferences`
        The default value is False

      Returns
      -------
      dict (if how == 'dict') or list (if how == 'list')
        returned by `dataapi_specific_image_instance_inferences`

      Raises
      ------
      IndexError
        raised by `dataapi_specific_image_instance_inferences`
      """
      raise NotImplementedError

    def dataapi_image_plugin_positional_inferences(self, how=None, raise_if_error=False):
      """
      API for accessing the first image plugin positional inferences
      (shortcut for `dataapi_specific_image_plugin_positional_inferences`, most of the cases will have a single image on a stream)

      Parameters
      ----------
      how : str, optional
        Passed to `dataapi_specific_image_plugin_positional_inferences`
        The default value is None

      raise_if_error : bool, optional
        Passed to `dataapi_specific_image_plugin_positional_inferences`
        The default value is False

      Returns
      -------
      dict (if how == 'dict') or list (if how == 'list')
        returned by `dataapi_specific_image_plugin_positional_inferences`

      Raises
      ------
      IndexError
        raised by `dataapi_specific_image_plugin_positional_inferences`
      """
      raise NotImplementedError

  """DeAPI methods"""
  if True:
    def deapi_get_wokers(self, n_workers):
      raise NotImplementedError

  """Working hours methods"""
  if True:
    @property
    def working_hours(self):
      raise NotImplementedError

    @property
    def outside_working_hours(self):
      raise NotImplementedError

    @property
    def working_hours_is_new_shift(self):
      raise NotImplementedError

  """Upload methods"""
  if True:
    def upload_file(self, file_path, target_path, force_upload=False, save_db=False, verbose=0, **kwargs):
      raise NotImplementedError

    def upload_folder(self, folder_path, target_path, force_upload=False, **kwargs):
      raise NotImplementedError

    def upload_logs(self, target_path, force_upload=False):
      raise NotImplementedError

    def upload_output(self, target_path, force_upload=False):
      raise NotImplementedError

  """CommandAPI methods"""
  if True:
    def cmdapi_start_pipeline(self, config, dest=None):
      """
      Sends a start pipeline to a particular destination Execution Engine

      Parameters
      ----------
      dest : str, optional
        destination Execution Engine, `None` will default to local Execution Engine. The default is None
        .
      config : dict
        the pipeline configuration. 

      Returns
      -------
      None.

      Example:

        ```
        config = {
          "NAME" : "test123",
          "TYPE" : "Void",
        }
        ee_id = None # using current processing node
        plugin.cmdapi_start_pipeline(config=config, dest=ee_id)
        ```

      """
      raise NotImplementedError

    def cmdapi_update_instance_config(self, pipeline, signature, instance_id, instance_config, dest=None):
      """
      Sends update config for a particular plugin instance in a given box/pipeline


      Parameters
      ----------

      pipeline : str
        Name of the pipeline. 

      signature: str
        Name (signature) of the plugin 

      instance_id: str
        Name of the instance

      instance_config: dict
        The configuration for the given box/pipeline/plugin/instance

      dest : str, optional
        destination Execution Engine, `None` will default to local Execution Engine. The default is None.

      Returns
      -------
      None.

      """
      raise NotImplementedError

    def cmdapi_batch_update_instance_config(self, lst_updates, dest=None):
      """Send a batch of updates for multiple plugin instances within their individual pipelines

      Parameters
      ----------
      lst_updates : list of dicts
          The list of updates for multiple plugin instances within their individual pipelines

      dest : str, optional
          Destination node, by default None

      Returns
      -------
      None.

      Example
      -------

        ```python
        # in this example we are modifiying the config for 2 instances of the same plugin `A_PLUGIN_01`
        # within the same pipeline `test123`
        lst_updates = [
          {
            "NAME" : "test123",
            "SIGNATURE" : "A_PLUGIN_01",
            "INSTANCE_ID" : "A_PLUGIN_01_INSTANCE_01",
            "INSTANCE_CONFIG" : {
              "PARAM1" : "value1",
              "PARAM2" : "value2",
            }
          },
          {
            "NAME" : "test123",
            "SIGNATURE" : "A_PLUGIN_01",
            "INSTANCE_ID" : "A_PLUGIN_01_INSTANCE_02",
            "INSTANCE_CONFIG" : {
              "PARAM1" : "value1",
              "PARAM2" : "value2",
            }
          },
        ] 
        plugin.cmdapi_batch_update_instance_config(lst_updates=lst_updates, dest=None)
        ```

      """
      # first check if all updates are valid
      raise NotImplementedError

    def cmdapi_send_instance_command(self, pipeline, signature, instance_id, instance_command, dest=None):
      """
      Sends a INSTANCE_COMMAND for a particular plugin instance in a given box/pipeline

      Parameters
      ----------
      pipeline : str
        Name of the pipeline. 

      instance_id: str
        Name of the instance

      signature: str
        Name (signature) of the plugin     

      instance_command: any
        The configuration for the given box/pipeline/plugin/instance. Can be a string, dict, etc

      dest : str, optional
        destination Execution Engine, `None` will default to local Execution Engine. The default is None.


      Returns
      -------
      None.

      Example:
      --------


        ```
        pipeline = "test123"
        signature = "A_PLUGIN_01"
        instance_id = "A_PLUGIN_01_INSTANCE_01"
        instance_command = {
          "PARAM1" : "value1",
          "PARAM2" : "value2",
        }
        plugin.cmdapi_send_instance_command(
          pipeline=pipeline,
          signature=signature,
          instance_id=instance_id,
          instance_command=instance_command,
          dest=None,
        )
        ```

      """
      raise NotImplementedError

    def cmdapi_archive_pipeline(self, dest=None, name=None):
      """
      Stop and archive a active pipeline on destination Execution Engine

      Parameters
      ----------
      dest : str, optional
        destination Execution Engine, `None` will default to local Execution Engine. The default is None.
      name : str, optional
        Name of the pipeline. The default is `None` and will point to current pipeline where the plugin instance 
        is executed.

      Returns
      -------
      None.

      """
      raise NotImplementedError

    def cmdapi_stop_pipeline(self, dest=None, name=None):
      """
      Stop and delete a active pipeline on destination Execution Engine

      Parameters
      ----------
      dest : str, optional
        destination Execution Engine, `None` will default to local Execution Engine. The default is None.
      name : str, optional
        Name of the pipeline. The default is `None` and will point to current pipeline where the plugin instance 
        is executed.

      Returns
      -------
      None.

      """
      raise NotImplementedError

    def cmdapi_archive_all_pipelines(self, dest=None):
      """
      Stop all active pipelines on destination Execution Engine

      Parameters
      ----------
      dest : str, optional
        destination Execution Engine, `None` will default to local Execution Engine. The default is None.

      Returns
      -------
      None.

      """
      raise NotImplementedError

    def cmdapi_start_pipeline_by_params(self, name, pipeline_type, dest=None, url=None,
                                        reconnectable=None, live_feed=False, plugins=None,
                                        stream_config_metadata=None, cap_resolution=None,
                                        **kwargs):
      """
      Start a pipeline by defining specific pipeline params

      Parameters
      ----------
      name : str
        Name of the pipeline.

      pipeline_type : str
        type of the pipeline. Will point the E2 instance to a particular Data Capture Thread plugin

      dest : str, optional
        Name of the target E2 instance. The default is `None` and will run on local E2.

      url : str, optional
        The optional URL that can be used by the DCT to acquire data. The default is None.

      reconnectable : str, optional
        Attempts to reconnect after data stops if 'YES'. 'KEEP_ALIVE' will not reconnect to
        data source but will leave the DCT in a "zombie" state waiting for external pipeline 
        close command.
        The default is 'YES'.

      live_feed : bool, optional
        Will always try to generate the real-time datapoint (no queued data). The default is False.

      plugins : list of dicts, optional
        Lists all the business plugins with their respective individual instances. The default is None.

      stream_config_metadata : dict, optional
        Options (custom) for current DCT. The default is None.

      cap_resolution : float, optional
        Desired frequency (in Hz) of the DCT data reading cycles. The default is None.


      Returns
      -------
      None (actually)

      Example
      -------

        ```
        name = "test123"
        pipeline_type = "Void"
        plugins = [
          {
            "SIGNATURE" : "A_PLUGIN_01",
            "INSTANCES" : [
              {
                "INSTANCE_ID" : "A_PLUGIN_01_INSTANCE_01",
                "PARAM1" : "value1",
                "PARAM2" : "value2",
              }
            ]
          }
        ]
        plugin.cmdapi_start_pipeline_by_params(
          name=name, 
          pipeline_type=pipeline_type, 
          plugins=plugins,
        )
        ```

      """
      raise NotImplementedError

    def cmdapi_start_simple_custom_pipeline(self, *, base64code, dest=None, name=None, instance_config={}, **kwargs):
      """
      Starts a CUSTOM_EXEC_01 plugin on a Void pipeline


      Parameters
      ----------
      base64code : str
        The base64 encoded string that will be used as custom exec plugin.

      dest : str, optional
        The destination processing node. The default is None and will point to current node.

      name : str, optional
        Name of the pipeline. The default is None and will be uuid generated.

      instance_config / kwargs: dict
        Dict with params for the instance that can be given either as a dict or as kwargs


      Returns
      -------
      name : str
        returns the name of the pipeline.


      Example
      -------

        ```
        worker = plugin.cfg_destination                     # destination worker received in plugin json command
        worker_code = plugin.cfg_worker_code                # base64 code that will be executed 
        custom_code_param = plugin.cfg_custom_code_param    # a special param expected by the custom code
        pipeline_name = plugin.cmdapi_start_simple_custom_pipeline(
          base64code=worker_code, 
          dest=worker,
          custom_code_param=pcustom_code_param,
        )
        ```
      """
      raise NotImplementedError

    def cmdapi_send_pipeline_command(self, command, dest=None, pipeline_name=None):
      """Sends a command to a particular pipeline on a particular destination E2 instance

      Parameters
      ----------
      command : any
          the command content

      dest : str, optional
          name of the destination e2, by default None (self)

      pipeline_name : str, optional
          name of the pipeline, by default None (self)


      Returns
      -------
      None.

      Example
      -------

        ```
        # send a command directly to the current pipeline
        plugin.cmdapi_send_pipeline_command(
          command={"PARAM1" : "value1", "PARAM2" : "value2"},
          dest=None,
          pipeline_name=None,
        )
        ```

      """
      raise NotImplementedError

  """UtilsAPI methods"""
  if True:
    @property
    def geometry_methods(self):
      """Proxy for geometry_methods from libraries.vision.geometry_methods
      """
      raise NotImplementedError

    @property
    def gmt(self):
      """Proxy for geometry_methods from libraries.vision.geometry_methods
      """
      raise NotImplementedError

    @property
    def system_versions(self):
      raise NotImplementedError

    @property
    def system_version(self):
      raise NotImplementedError

    @property
    def utils(self):
      """
      Provides access to methods from core.bussiness.utils.py
      """
      raise NotImplementedError

    @property
    def local_data_cache(self):
      """
      Can be used as a statefull store of the instance - eg `plugin.state[key]` will return `None`
      if that key has never been initialized    


      Returns
      -------
      dict
        a default dict.


      Example
      -------
        ```
        obj = self.local_data_cache['Obj1']
        if obj is None:
          obj = ClassObj1()
          self.local_data_cache['Obj1'] = obj
        ```
      """
      raise NotImplementedError

    @property
    def state(self):
      """
      Alias for `plugin.local_data_cache`
      can be used as a statefull store of the instance - eg `plugin.state[key]` will return `None`
      if that key has never been initialized     

      Returns
      -------
      dict
        Full local data cache of the current instance.

      """
      raise NotImplementedError

    @property
    def obj_cache(self):
      """
      Can be used as a statefull store of the instance - eg `plugin.obj_cache[key]` will return `None`
      if that key has never been initialized    


      Returns
      -------
      dict
        a default dict for objects.


      Example
      -------
        ```
        obj = self.obj_cache['Obj1']
        if obj is None:
          obj = ClassObj1()
          self.obj_cache['Obj1'] = obj
        ```      

      """
      raise NotImplementedError

    @property
    def int_cache(self):
      """
      can be used as a statefull store of the instance - eg `plugin.int_cache[key]` will return 0
      if that key has never been initialized    


      Returns
      -------
      dict of ints
        Returns a default dict for int values initialized with zeros.


      Example
      -------
        ```
        self.int_cache['v1'] += 1
        if self.int_cache['v1']  == 100:
          self.P("100 run interations in this plugin")
        ```

      """
      raise NotImplementedError

    @property
    def str_cache(self):
      """
      Can be used as a statefull store of the instance - eg `plugin.str_cache[key]` will return empty string
      if that key has never been initialized    


      Returns
      -------
      defaultdict
        a defaultdict with empty strings.


      Example
      -------
      ```
      self.str_cache['s1'] += str(val)[0]
      if len(self.int_cache['s1']) > 10:
        self.P("10 numbers added in the string")
      ```

      """
      raise NotImplementedError

    @property
    def float_cache(self):
      """
      Can be used as a statefull store of the instance - eg `plugin.float_cache[key]` will return 0
      if that key has never been initialized    


      Returns
      -------
      dict of floats
        Returns a default dict for float values initialized with zeros.


      Example
      -------
        ```
        self.float_cache['f1'] += val
        if self.float_cache['f1']  >= 100:
          self.P("value 100 passed")
        ```
      """
      raise NotImplementedError

    def download(self, url, fn, target='output', **kwargs):
      """
      Dowload wrapper that will download a given file from a url to `_local_cache/_output.


      TODO: fix to use specific endpoints configs not only from base file_system_manager

      Parameters
      ----------
      url : str
        the url where to find the file.

      fn : str
        local file name to be saved in `target` folder.

      **kwargs : dict
        params for special upload procedures such as minio.


      Returns
      -------
      res : str
        path of the downloaded file, None if not found.


      Example
      -------

        ```
        res = plugin.download('http://drive.google.com/file-url', 'test.bin')
        if res is not None:
          plugin.P("Downloaded!")
        ```

      """
      raise NotImplementedError

  """DiskAPI methods"""
  if True:
    def diskapi_save_dataframe_to_data(self, df, filename: str,
                                       ignore_index: bool = True, compress: bool = False, mode: str = 'w',
                                       header=True,
                                       also_markdown: bool = False, verbose: bool = True,
                                       as_parquet: bool = False
                                       ):
      """
      Shortcut to _diskapi_save_dataframe.
      """
      raise NotImplementedError

    def diskapi_save_dataframe_to_models(self, df, filename: str,
                                         ignore_index: bool = True, compress: bool = False, mode: str = 'w',
                                         header=True,
                                         also_markdown: bool = False, verbose: bool = True,
                                         as_parquet: bool = False,
                                         ):
      """
      Shortcut to _diskapi_save_dataframe.
      """
      raise NotImplementedError

    def diskapi_save_dataframe_to_output(self, df, filename: str,
                                         ignore_index: bool = True, compress: bool = False, mode: str = 'w',
                                         header=True,
                                         also_markdown: bool = False, verbose: bool = True,
                                         as_parquet: bool = False,
                                         ):
      """
      Shortcut to _diskapi_save_dataframe.
      """
      raise NotImplementedError

    def _diskapi_load_dataframe(self, filename: str, folder: str,
                                decompress: bool = False, timestamps=None):
      """
      Parameters:
      ----------
      filename: str, mandatory
        Relative path to `folder` (in local cache), from where the dataframe should be loaded
        If filename ends in ".zip" then the loading will also uncompress in-memory

      folder: str, mandatory
        The folder in local cache
        Possible values: 'data', 'output', 'models'

      decompress: bool, optional
        Should be True if the file was saved with `compress=True`
        The default value is False.

      timestamps: str or List[str], optional
        Column names that should be parsed as dates when loading the dataframe
        The default is None

      Returns:
      --------
      pandas.DataFrame
      """
      raise NotImplementedError

    def diskapi_load_dataframe_from_data(self, filename: str, decompress: bool = False,
                                         timestamps=None):
      """
      Shortcut to _diskapi_load_dataframe.
      """
      raise NotImplementedError

    def diskapi_load_dataframe_from_models(self, filename: str, decompress: bool = False,
                                           timestamps=None):
      """
      Shortcut to _diskapi_load_dataframe.
      """
      raise NotImplementedError

    def diskapi_load_dataframe_from_output(self, filename: str, decompress: bool = False,
                                           timestamps=None):
      """
      Shortcut to _diskapi_load_dataframe.
      """
      raise NotImplementedError

    def diskapi_save_pickle_to_data(
        self, obj: object, filename: str, subfolder: str = None,
        compress: bool = False, verbose: bool = True
    ):
      """
      Shortcut to _diskapi_save_pickle.
      """
      raise NotImplementedError

    def diskapi_save_pickle_to_models(
        self, obj: object, filename: str, subfolder: str = None,
        compress: bool = False, verbose: bool = True
    ):
      """
      Shortcut to _diskapi_save_pickle.
      """
      raise NotImplementedError

    def diskapi_save_pickle_to_output(
        self, obj: object, filename: str, subfolder: str = None,
        compress: bool = False, verbose: bool = True
    ):
      """
      Shortcut to _diskapi_save_pickle.
      """
      raise NotImplementedError

    def diskapi_load_pickle_from_data(
        self, filename: str, subfolder: str = None,
        decompress: bool = False, verbose: bool = True
    ):
      """
      Shortcut to _diskapi_load_pickle.
      """
      raise NotImplementedError

    def diskapi_load_pickle_from_models(
        self, filename: str, subfolder: str = None,
        decompress: bool = False, verbose: bool = True
    ):
      """
      Shortcut to _diskapi_load_pickle.
      """
      raise NotImplementedError

    def diskapi_load_pickle_from_output(
        self, filename: str, subfolder: str = None,
        decompress: bool = False, verbose: bool = True
    ):
      """
      Shortcut to _diskapi_load_pickle.
      """
      raise NotImplementedError

    def diskapi_save_json_to_data(self, dct, filename: str, indent: bool = True):
      """
      Shortcut to _diskapi_save_json
      """
      raise NotImplementedError

    def diskapi_save_json_to_models(self, dct, filename: str, indent: bool = True):
      """
      Shortcut to _diskapi_save_json
      """
      raise NotImplementedError

    def diskapi_save_json_to_output(self, dct, filename: str, indent: bool = True):
      """
      Shortcut to _diskapi_save_json
      """
      raise NotImplementedError

    def diskapi_load_json_from_data(self, filename: str, verbose: bool = True):
      """
      Shortcut to _diskapi_load_json.
      """
      raise NotImplementedError

    def diskapi_load_json_from_models(self, filename: str, verbose: bool = True):
      """
      Shortcut to _diskapi_load_json.
      """
      raise NotImplementedError

    def diskapi_load_json_from_output(self, filename: str, verbose: bool = True):
      """
      Shortcut to _diskapi_load_json.
      """
      raise NotImplementedError

    def diskapi_create_video_file_to_data(self, filename: str, fps: int, str_codec: str,
                                          frame_size, universal_codec: str = 'XVID'):
      """
      Shortcut to `_diskapi_create_video_file`
      """
      raise NotImplementedError

    def diskapi_create_video_file_to_models(self, filename: str, fps: int, str_codec: str,
                                            frame_size, universal_codec: str = 'XVID'):
      """
      Shortcut to `_diskapi_create_video_file`
      """
      raise NotImplementedError

    def diskapi_create_video_file_to_output(self, filename: str, fps: int, str_codec: str,
                                            frame_size, universal_codec: str = 'XVID'):
      """
      Shortcut to `_diskapi_create_video_file`
      """
      raise NotImplementedError

    def diskapi_write_video_frame(self, handler, frame):
      """
      Parameters:
      -----------
      handler: _, mandatory
        the handler returned by `diskapi_create_video_file`

      frame: np.ndarray, mandatory
        the frame to be written in the video file.
        Must have the the same H,W specified in `diskapi_create_video_file`
      """
      raise NotImplementedError

    def diskapi_save_image_output(self, image, filename: str, subdir: str, extension: str = 'jpg'):
      """
      Shortcut to _diskapi_save_image.
      Parameters
      ----------
      image - np.ndarray, the image to be saved
      filename - string, the name of the file
      subdir - string, the subfolder in local cache
      extension - string, the extension of the file

      Returns
      -------
      bool, True if the image was saved successfully, False otherwise
      """
      raise NotImplementedError

    def diskapi_save_file_output(self, data: str or list, filename: str, subdir: str = '', extension: str = ''):
      """
      Shortcut to _diskapi_save_file.
      Parameters
      ----------
      data - string or list, the data to be saved
      filename - string, the name of the file
      subdir - string, the subfolder in local cache
      extension - string, the extension of the file

      Returns
      -------
      bool, True if the file was saved successfully, False otherwise
      """
      raise NotImplementedError

    def diskapi_zip_dir(self, dir_path, zip_path=None):
      """
      Zip the contents of an entire folder (with that folder included).
      Parameters
      ----------
      dir_path - string, path of directory to zip
      zip_path - string, path of the output zip file. If None, zip_path will be dir_path + ".zip"

      Returns
      -------
      string, the path to the zipped directory
      """
      raise NotImplementedError

    def diskapi_unzip_dir(self, zip_path, dir_path=None):
      """
      Unzip a file into a given directory.
      Parameters
      ----------
      zip_path - string, path to .zip file
      dir_path - string, path to directory into which to unzip the input .zip file

      Returns
      -------
      string, the path to the unzipped directory
      """
      raise NotImplementedError

    def diskapi_delete_file(self, file_path):
      """
      Delete a file from disk if safe.
      Parameters
      ----------
      file_path - string, path to the file to be deleted

      Returns
      -------

      """
      raise NotImplementedError

    def diskapi_delete_directory(self, dir_path):
      """
      Delete a directory from disk if safe.
      Parameters
      ----------
      dir_path - string, path to the directory to be deleted

      Returns
      -------

      """
      raise NotImplementedError

  """Timebins methods"""
  if True:
    def timebins_create_bin(self, key="default", weekday_names=None, report_default_empty_value=None, per_day_of_week_timeslot=None, warmup_anomaly_models=None):
      raise NotImplementedError

    def timebins_append(self, value, key='default'):
      raise NotImplementedError

    def timebins_get_bin(self, key='default'):
      raise NotImplementedError

    def timebins_get_bin_mean(self, key='default'):
      raise NotImplementedError

    def timebins_is_anomaly(self, key='default'):
      raise NotImplementedError

    def timebins_get_bin_size(self, key='default'):
      raise NotImplementedError

    def timebins_get_total_size(self, key='default'):
      raise NotImplementedError

    def timebins_get_bin_report(self, aggr_func="mean", key='default'):
      raise NotImplementedError

    def timebins_get_bin_statistic(self, aggr_func="mean", key='default'):
      raise NotImplementedError

    def timebins_get_previous_bin_statistic(self, aggr_func="mean", key='default'):
      raise NotImplementedError
