from PyE2 import Payload, Pipeline, Session


val = 0


def instance_on_data(pipeline: Pipeline, payload: Payload):
  global val
  payload.get_image_as_PIL().save("images/img_{}.jpeg".format(val))
  val += 1


if __name__ == '__main__':
  sess = Session(
      filter_workers=['node_id']
  )

  sess.connect()

  pipeline = sess.create_pipeline(
    node="node_id",
    name="test",
    data_source="VideoFile",
    config={
      "URL": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
      "LIVE": False,
    },
  )

  instance = pipeline.create_plugin_instance(
    signature="OBJECT_TRACKING_01",
    instance_id="Demo1",
    config={
      "OBJECT_TYPE": ["person"]
    },
    on_data=instance_on_data,
  )

  pipeline.deploy()

  sess.run(wait=120, close_pipelines=True)
  sess.P("Main thread exiting...")
