from time import sleep, time

from PyE2 import Payload, Pipeline, Session, load_dotenv

boxes = {}


def instance_on_data(pipeline: Pipeline, data: Payload):
  global boxes
  data['INSTANCES'].sort()
  boxes[data['BOX']] = (data['INSTANCES'], time())
  return


def pipeline_on_notification(pipeline: Pipeline, notification: dict):
  pipeline.P(
      "Received specific notification for pipeline {}".format(pipeline.name))
  return


env_variables = load_dotenv(load_env=False)
listener_params = {
  'HOST': env_variables['AIXP_HOSTNAME'],
  'PORT': int(env_variables['AIXP_PORT']),
  'USER': env_variables['AIXP_USERNAME'],
  'PASS': env_variables['AIXP_PASSWORD'],
  'TOPIC': 'lummetry/ctrl',
}

node_id = 'node_id'
sess = Session()

pipeline = sess.attach_to_pipeline(
  node=node_id,
  name='test_mqtt',
  on_notification=pipeline_on_notification,
  max_wait_time=60
)

# now start a cyclic process
inst = pipeline.attach_to_custom_plugin_instance('inst01', on_data=instance_on_data)


def generate_net_map():
  global boxes
  net_map_msgs = ["Printing network map"]
  for box, (instances, last_time) in boxes.items():
    if last_time - time() > 30:
      continue
    net_map_msgs.append(box + ":")
    for i in range(len(instances)):
      (pipeline, signature, instance) = instances[i]

      (o_pipeline, o_signature) = (None, None)
      if i != 0:
        (o_pipeline, o_signature, _) = instances[i - 1]

      same_pipeline = pipeline == o_pipeline
      same_signature = signature == o_signature

      if not same_pipeline:
        net_map_msgs.append(" --- " + pipeline + ":")
      if not same_pipeline or not same_signature:
        net_map_msgs.append("    --- " + signature + ":")
      net_map_msgs.append("        --- " + instance)

    net_map_msgs.append("")
  return "\n".join(net_map_msgs)


try:
  while True:
    sleep(10)

    pipeline.P(generate_net_map(), color='m')
except KeyboardInterrupt:
  pipeline.P("CTRL+C detected. Closing example..", color='r')


pipeline.close()
sess.close()
