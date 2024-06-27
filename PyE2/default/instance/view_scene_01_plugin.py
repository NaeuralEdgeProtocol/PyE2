from ...base import Instance


class ViewScene01(Instance):
  def get_last_witness(self, response_params_key="COMMAND_PARAMS"):
    """
    Get the performance history of a node.

    Parameters
    ----------
    node_id : str, optional
        The node id, by default None
    time_window_hours: int, optional
        The time window in hours to retrieve, by default 1
    steps : int, optional
        Retrieve only each `steps` data point from the time window, by default 20

    Returns
    -------
    """
    images = []

    result_payload = self.send_instance_command_and_wait_for_response_payload(
      command="GET_LAST_WITNESS",
      response_params_key=response_params_key,
    )

    if result_payload is not None:
      images = result_payload.get_images_as_PIL()

    return images
