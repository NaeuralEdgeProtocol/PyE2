from PyE2 import Session


def on_hb(session: Session, e2id: str, data: dict):
  session.P("{} has a {}".format(e2id, data['CPU']))
  return


if __name__ == '__main__':
  # create a session
  # the network credentials are read from the .env file automatically
  sess = Session(
      on_heartbeat=on_hb
  )

  sess.run(wait=10, close_session=True)
  sess.log.P("Main thread exiting...")
