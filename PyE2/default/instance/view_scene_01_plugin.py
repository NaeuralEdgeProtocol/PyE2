from ...base import Instance


class ViewScene01(Instance):
  signature = "VIEW_SCENE_01"

  def get_last_witness(self, response_params_key="COMMAND_PARAMS"):
    """
    Get the performance history of a node.

    Parameters
    ----------
    response_params_key : str
      The key in the response payload that contains the command parameters
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
