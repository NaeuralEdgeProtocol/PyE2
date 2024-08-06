"""
This is another simple example of how to use the PyE2 SDK.

In this example, we connect to the network, choose a node and
    deploy a plugin with custom code that will run in real time.

For this example, we will get the bounding boxes of license plates in the frame
    and draw them on the frame, then show the frame.
"""

from time import sleep
import cv2

from PyE2 import CustomPluginTemplate, Instance, Payload, Pipeline, Session


def real_time_code(plugin: CustomPluginTemplate):
  frame = plugin.dataapi_image()
  plugin.set_image(frame)

  plates = plugin.dataapi_image_instance_inferences()
  plate_tlbrs = [plate['TLBR_POS'] for plate in plates]
  plate_nrs = [plate['LICENSE_PLATE_STN'] for plate in plates]
  plates_count = len(plates)

  if plates_count > 0:
    return {
      'PLATES_COUNT': plates_count,
      "IMAGE_RESOLUTION": frame.shape[:2],
      "PLATE_TLBR": plate_tlbrs,
      "PLATE_NRS": plate_nrs,
    }

  return


def custom_instance_on_data(pipeline: Pipeline, custom_code_data: dict, data: Payload):
  # the images can be extracted from the Payload object
  # PIL needs to be installed for this to work
  np_image = data.get_images_as_np()[0]
  tlbrs = custom_code_data['PLATE_TLBR']
  nrs = custom_code_data['PLATE_NRS']

  # images processed on the edge may be of different resolution
  # than the images we receive, so we need to scale the bounding boxes accordingly
  # (reason for this is that sending full images through the network leads to high latency and bandwidth usage)
  height_ratio = np_image.shape[0] / custom_code_data['IMAGE_RESOLUTION'][0]
  width_ratio = np_image.shape[1] / custom_code_data['IMAGE_RESOLUTION'][1]

  for tlbr, nr in zip(tlbrs, nrs):
    tlbr = [int(tlbr[0] * height_ratio), int(tlbr[1] * width_ratio),
            int(tlbr[2] * height_ratio), int(tlbr[3] * width_ratio)]

    np_image = cv2.rectangle(np_image, tlbr[:2][::-1], tlbr[2:][::-1], (0, 255, 0), 2)
    np_image = cv2.putText(np_image, nr, tlbr[:2][::-1], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

  cv2.imshow('frame', np_image)
  cv2.waitKey(1)


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
    cap_resolution=5,
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
    ai_engine="plate_reader_detector",
    object_type=["license plate"],
    # we can also specify if the payloads should be encrypted
    # if so, only the creator of this pipeline, in our case us, will be able to decrypt the payloads
    encrypt_payload=True,
  )

  pipeline.deploy(timeout=60)

  # run the program for 120 seconds, then close the session
  session.run(wait=120, close_session=True, close_pipelines=True)
  session.P("Main thread exiting...")
