from PyE2 import Payload, Session, Pipeline, Instance


def instance_on_data(pipeline: Pipeline, data: Payload):
  # this could refresh a UI
  pipeline.P('Receive specific message from PERIMETER_VIOLATION_02:inst01 (hardcoded)', color='m')


def another_instance_on_data(pipeline: Pipeline, data: Payload):
  # this could refresh a UI
  pipeline.P('Receive specific message from CUSTOM_EXEC_01:inst01 (hardcoded)')


def pipeline_on_data(pipeline: Pipeline, signature, instance, data: Payload):
  # this could refresh a UI
  pipeline.P('Received data from box {} by server {}, stream:{}, plugin: {}, instance:{}, the following data:{}'.format(
      pipeline.node_id,  # can use pipeline.node_addr instead
      pipeline.session.server,
      pipeline.name,
      signature,
      instance,
      data
  ))


if __name__ == '__main__':

  node_id = 'stefan-box'

  sess = Session()

  pipeline: Pipeline = sess.create_pipeline(
      node=node_id,
      name='test_normal',
      data_source='VideoStream',
      config={
          'URL': 0
      },
      on_data=pipeline_on_data
  )

  # now we start a perimeter intrusion functionality for low-res cameras with all
  # the other params default
  perimeter_violation_instance: Instance = pipeline.create_plugin_instance(  # should return an id
      signature='PERIMETER_VIOLATION_01',
      instance_id='inst01',
      on_data=instance_on_data,
      ai_engine='lowres_general_detector'
  )

  plain_code = """
result="Data on node"
  """

  # now start a cyclic process
  custom_instance: Instance = pipeline.create_custom_plugin_instance(
      instance_id='inst01',
      plain_code=plain_code,
      on_data=another_instance_on_data
  )

  # now deploy the pipeline
  pipeline.deploy()

  # we wait for 30 seconds
  sess.run(30, close_session=False)

  # we can stop an instance like this
  pipeline.remove_plugin_instance(perimeter_violation_instance)

  # or like this
  custom_instance.stop()

  # we still need to deploy the changes
  pipeline.deploy()

  # we wait until the user presses `Ctrl+C`
  sess.run(0, close_session=False)

  # now close conn to comm server
  pipeline.close()
  sess.close()
