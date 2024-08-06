from PyE2 import Session


def on_hb(session: Session, node_addr: str, data: dict):
  session.P("{} has a {}".format(node_addr, data['CPU']))
  return


if __name__ == '__main__':
  # create a session
  # the network credentials are read from the .env file automatically
  sess = Session(
      on_heartbeat=on_hb,
      encrypt_comms=True,
  )

  sess.run(wait=10, close_session=True)
  sess.log.P("Main thread exiting...")
