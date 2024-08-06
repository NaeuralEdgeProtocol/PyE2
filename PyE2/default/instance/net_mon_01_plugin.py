from ...base import Instance


class NetMon01(Instance):
  signature = "NET_MON_01"

  def get_node_history(self, node_id=None, node_addr=None, time_window_hours=1, steps=20):
    """
    Get the performance history of a node.

    Parameters
    ----------
    node_id : str, optional
        The node id, by default None
    node_addr : str, optional
        The node address, by default None
    time_window_hours: int, optional
        The time window in hours to retrieve, by default 1
    steps : int, optional
        Retrieve only each `steps` data point from the time window, by default 20

    Returns
    -------
    """
    result = None

    if node_id is None:
      node_id = self.pipeline.node_id

    if node_addr is None:
      node_addr = self.pipeline.node_addr

    command = {
      "node": node_id,
      "addr": node_addr,
      "options": {"step": steps, "time_window_hours": time_window_hours},
      "request": "history",
    }

    result_payload = self.send_instance_command_and_wait_for_response_payload(command)

    if result_payload is not None:
      result = result_payload.get("NODE_HISTORY", None)

    return result
