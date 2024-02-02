"""
This is a simple example of how to use the PyE2 library.

In this example, we connect to the network, listen for heartbeats from 
  AiXpand nodes and print the CPU of each node.
"""

from PyE2 import Session


def on_hb(session: Session, e2id: str, data: dict):
  session.P("{} has a {}".format(e2id, data['CPU']))
  return


if __name__ == '__main__':
  # create a session
  # the network credentials are read from the .env file automatically
  session = Session(
      on_heartbeat=on_hb
  )

  # run the program for 10 seconds, then close the session
  session.run(wait=10, close_session=True)
  session.P("Main thread exiting...")
