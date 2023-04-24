import os
from time import sleep

from dotenv import load_dotenv

from PyE2 import Session

load_dotenv()


def on_hb(session: Session, e2id: str, data: dict):
  session.P("{} has a {}".format(e2id, data['CPU']))
  return


if __name__ == '__main__':
  sess = Session(
      host=os.getenv('PYE2_HOSTNAME'),
      port=int(os.getenv('PYE2_PORT')),
      user=os.getenv('PYE2_USERNAME'),
      pwd=os.getenv('PYE2_PASSWORD'),
      on_heartbeat=on_hb
  )

  sess.run(wait=10)
  sess.log.P("Main thread exiting...")
