"""
This is a simple example of how to use the PyE2 SDK.

In this example, we connect to the network, listen for heartbeats from 
  Naeural edge nodes and print the CPU of each node.
"""

from PyE2 import Session


def on_heartbeat(session: Session, node_id: str, heartbeat: dict):
  session.P("{} ({}) has a {}".format(node_id, heartbeat['EE_ADDR'], heartbeat["CPU"]))
  return


if __name__ == '__main__':
  # create a session
  # the network credentials are read from the .env file automatically
  session = Session(
      on_heartbeat=on_heartbeat
  )

  # run the program for 10 seconds, then close the session
  session.run(wait=10, close_session=True)
  session.P("Main thread exiting...")
