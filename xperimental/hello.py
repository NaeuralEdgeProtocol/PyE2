from PyE2 import Session
from time import sleep


def on_hb(session, data):
  session.P("{} has a {}".format(data['EE_ID'], data['CPU']))
  return


if __name__ == '__main__':
  sess = Session(
      host="hostname",
      port=88888,
      user="username",
      pwd="password",
      on_heartbeat=on_hb
  )

  sess.run(wait=10)
  sess.log.P("Main thread exiting...")
