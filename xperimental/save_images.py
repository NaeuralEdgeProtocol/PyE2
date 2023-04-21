from PyE2 import Session, Payload
import os
from time import sleep

from dotenv import load_dotenv

print("before_import")
print("after_import")

load_dotenv()


def on_data(pipeline, plugin, instance, payload):
  return


val = 0


def instance_on_data(pipeline, payload: Payload):
  global val
  payload.get_image_as_PIL().save("images/img_{}.jpeg".format(val))
  val += 1


if __name__ == '__main__':
  sess = Session(
      host=os.getenv('PYE2_HOSTNAME'),
      port=int(os.getenv('PYE2_PORT')),
      user=os.getenv('PYE2_USERNAME'),
      pwd=os.getenv('PYE2_PASSWORD'),
      filter_workers=['e2id']
  )

  sess.connect()

  pipeline = sess.create_pipeline(
    e2id="e2id",
    name="test",
    data_source="VideoStream",
    config={"URL": 0},
    on_data=on_data,
  )

  instance = pipeline.start_plugin_instance(
    signature="OBJECT_TRACKING_01",
    instance_id="Demo1",
    params={
      "DEMO_MODE": True,
      "OBJECT_TYPE": ["person"]
    },
    on_data=instance_on_data,
  )

  sess.run(wait=60, close_pipelines=True)
  sess.P("Main thread exiting...")
