from PyE2.base.responses import Response
# from .responses import Response
from time import time, sleep


class Transaction():
  def __init__(self, log, session_id: str, *, lst_required_responses: list[Response] = None, timeout: int = 0, on_success_callback: callable = None, on_failure_callback: callable = None) -> None:
    self.log = log
    self.session_id = session_id
    self.lst_required_responses = lst_required_responses
    self.timeout = timeout

    self.on_success_callback = on_success_callback
    self.on_failure_callback = on_failure_callback

    self.resolved_callback = None
    self.__is_solved = False
    self.__is_finished = False

    self.start_time = time()
    for response in self.lst_required_responses:
      response.set_logger(log)

    return

  def get_unsolved_responses(self) -> list[Response]:
    """
    Returns a list of unsolved responses in the transaction.

    Returns
    -------
    list[Response]
        List of unsolved responses in the transaction.
    """
    return [response for response in self.lst_required_responses if not response.is_solved()]

  def is_solved(self) -> bool:
    """
    Returns whether the transaction is solved or not.
    If the transaction is solved in this call, the resolved_callback is set to the appropriate callback function.

    Returns
    -------
    bool
        Whether the transaction is solved or not.
    """

    # if the transaction is already solved, return True
    if self.__is_solved:
      return True

    # first check if all responses are solved
    all_responses_solved = all([response.is_solved() for response in self.lst_required_responses])
    if all_responses_solved:
      self.__is_solved = True

      all_responses_good = all([response.is_good_response() for response in self.lst_required_responses])
      if all_responses_good:
        self.resolved_callback = self.on_success_callback
      else:
        if not self.on_failure_callback:
          self.resolved_callback = lambda: self.log.P("Transaction failed")
        else:
          fail_reasons = [
            response.fail_reason for response in self.lst_required_responses if not response.is_good_response()]
          self.resolved_callback = lambda: self.on_failure_callback(fail_reasons)
        # endif computing resolved_callback for failure
      # endif computing resolved_callback
      return True
    # endif all responses solved

    # if the transaction is not solved, check if the transaction has timed out
    elapsed_time = time() - self.start_time
    if self.timeout > 0 and elapsed_time > self.timeout:
      # Timeout occurred
      self.__is_solved = True

      fail_reason = f"Transaction timeout ({self.timeout}s). Responses not received: "
      fail_reason += ", ".join([str(response) for response in self.lst_required_responses if not response.is_solved()])

      if not self.on_failure_callback:
        self.resolved_callback = lambda: self.log.P(fail_reason)
      else:
        self.resolved_callback = lambda: self.on_failure_callback([fail_reason])
      return True

    return False

  def is_finished(self) -> bool:
    """
    Returns whether the transaction is finished or not.
    A transaction finishes when the callback is called.

    Returns
    -------
    bool
        Whether the transaction is finished or not.
    """
    return self.__is_finished

  def handle_payload(self, payload: dict) -> None:
    """
    This method is called when a payload is received from the server.
    This method calls `handle_payload()` method of all the unsolved responses in the `lst_required_responses`.

    Parameters
    ----------
    payload : dict
        The payload received from the server.
    """
    unsolved_responses = self.get_unsolved_responses()

    for response in unsolved_responses:
      response.handle_payload(payload)
    return

  def handle_notification(self, notification: dict) -> None:
    """
    This method is called when a notification is received from the server.
    This method calls `handle_notification()` method of all the unsolved responses in the `lst_required_responses`.

    Parameters
    ----------
    notification : dict
        The notification received from the server.
    """
    unsolved_responses = self.get_unsolved_responses()

    for response in unsolved_responses:
      response.handle_notification(notification)
    return

  def handle_heartbeat(self, heartbeat) -> None:
    """
    This method is called when a heartbeat is received from the server.
    This method calls `handle_heartbeat()` method of all the unsolved responses in the `lst_required_responses`.

    Parameters
    ----------
    heartbeat : dict
        The heartbeat received from the server.
    """
    unsolved_responses = self.get_unsolved_responses()

    for response in unsolved_responses:
      response.handle_heartbeat(heartbeat)
    return

  def callback(self):
    """
    Calls the resolved_callback only if the transaction is solved.
    """
    if self.__is_solved:
      if self.resolved_callback:
        self.resolved_callback()
      self.__is_finished = True
    return
