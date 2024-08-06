"""
This is a simple example of how to use the PyE2 SDK.

In this example, we connect to the network, choose a node and
    deploy a plugin with custom code that will run in real time.
    
For this example, we will count the number of persons that appear in the frames
    of a movie, so we will use a general object detection model.
"""

from time import sleep

from PyE2 import CustomPluginTemplate, Instance, Payload, Pipeline, Session


def real_time_code(plugin: CustomPluginTemplate):
  frame = plugin.dataapi_image()
  plugin.set_image(frame)

  persons = plugin.dataapi_image_instance_inferences()
  persons_count = len(persons)

  if persons_count > 0:
    return {
      'PERSONS_COUNT': persons_count,
    }

  return


def custom_instance_on_data(pipeline: Pipeline, custom_code_data: dict, data: Payload):
  # the images can be extracted from the Payload object
  # PIL needs to be installed for this to work
  data.get_images_as_PIL()[0].save('frame.jpg')
  pipeline.P("Persons in frame: {}".format(custom_code_data['PERSONS_COUNT']))


if __name__ == '__main__':
  # create a session
  # the network credentials are read from the .env file automatically
  session: Session = Session()

  # wait for any node to be available
  session.wait_for_any_node(timeout=10)

  # get the first available node
  chosen_node = session.get_active_nodes()[0]

  # we have our node, let's deploy a plugin

  # first, we create a pipeline
  # we will use the video file data source, since we want to extract frames from a video
  pipeline: Pipeline = session.create_pipeline(
    node=chosen_node,
    name='real_time_custom_code_deploy',
    data_source='VideoFile',
    config={
      'URL': "https://www.dropbox.com/scl/fi/8z2wpeelhav3k2dv8bb5p/Cars_3.mp4?rlkey=imv415rr3j1tx3zstpurlxkqb&dl=1"
    }
  )

  # next, we deploy a custom code plugin instance
  instance: Instance = pipeline.create_custom_plugin_instance(
    instance_id='inst01',
    custom_code=real_time_code,
    on_data=custom_instance_on_data,
    # we can specify the configuration for the plugin instance as kwargs
    process_delay=3,
    allow_empty_inputs=False,
    ai_engine="lowres_general_detector",
    object_type=["person"],
    # we can also specify if the payloads should be encrypted
    # if so, only the creator of this pipeline, in our case us, will be able to decrypt the payloads
    encrypt_payload=True,
  )

  # we increase the timeout because the AI engine has to start and warm up, which can take a while
  pipeline.deploy(timeout=60)

  # run the program for 120 seconds, then close the session
  session.run(wait=120, close_session=True, close_pipelines=True)
  session.P("Main thread exiting...")
