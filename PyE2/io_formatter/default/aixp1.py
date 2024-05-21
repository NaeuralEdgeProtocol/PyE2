# local dependencies
from ...io_formatter.base import BaseFormatter


class Aixp1Formatter(BaseFormatter):

  def __init__(self, log, **kwargs):
    super(Aixp1Formatter, self).__init__(
        log=log, prefix_log='[INV-FORM]', **kwargs)
    return

  def startup(self):
    pass

  def _encode_output(self, output):
    event_type = output.pop('EE_EVENT_TYPE', None)

    # below fields are not required as they will be decorated post-formatting anyway
    output.pop('EE_MESSAGE_ID', None)
    output.pop('EE_MESSAGE_SEQ', None)
    output.pop('EE_TOTAL_MESSAGES', None)

    output.pop('EE_TIMESTAMP', None)
    output.pop('EE_ID', None)
    output.pop('STREAM_NAME', None)
    output.pop('SIGNATURE', None)
    output.pop('INSTANCE_ID', None)

    output.pop('EE_TIMEZONE', None)
    output.pop('EE_VERSION', None)
    output.pop('EE_TZ', None)

    output.pop('INITIATOR_ID', None)
    output.pop('SESSION_ID', None)
    # end non-managed fields

    lvl_0_dct = {
      "DATA": {
      },
    }

    lvl_1_dct = lvl_0_dct['DATA']

    if event_type == 'PAYLOAD':
      # add payload context
      output.pop('STREAM')
      output.pop('PIPELINE')

      # Plugin meta
      if True:
        lvl_1_dct['PLUGIN_META'] = {}
        plugin_meta_keys = [k for k in output.keys() if k.startswith('_P_')]
        for k in plugin_meta_keys:
          lvl_1_dct['PLUGIN_META'][k] = output.pop(k, None)
        # end for

      # Pipeline meta
      if True:
        lvl_1_dct['PIPELINE_META'] = {}
        pipeline_meta_keys = [k for k in output.keys() if k.startswith('_C_')]
        for k in pipeline_meta_keys:
          lvl_1_dct['PIPELINE_META'][k] = output.pop(k, None)
        # end for

    # endif payload

    for k, v in output.items():
      lvl_1_dct[k] = v

    return lvl_0_dct

  def _decode_output(self, encoded_output):
    # Pop the unimportant stuff
    encoded_output.get('EE_FORMATTER', None)

    node_id, pipeline, signature, instance_id = encoded_output.get('EE_PAYLOAD_PATH', [None, None, None, None])

    encoded_output['EE_ID'] = node_id

    if encoded_output['EE_EVENT_TYPE'] != 'HEARTBEAT':
      encoded_output['STREAM_NAME'] = pipeline

    if pipeline is not None:
      encoded_output['SIGNATURE'] = signature

    if instance_id is not None:
      encoded_output['INSTANCE_ID'] = instance_id

    lvl_1_dct = encoded_output.pop('DATA')
    if encoded_output['EE_EVENT_TYPE'] == 'PAYLOAD':
      encoded_output['STREAM'] = pipeline
      encoded_output['PIPELINE'] = pipeline

      # Plugin meta
      plugin_meta = lvl_1_dct.pop('PLUGIN_META', {}) or {}
      for k, v in plugin_meta.items():
        encoded_output[k] = v

      # Pipeline meta
      pipeline_meta = lvl_1_dct.pop('PIPELINE_META', {}) or {}
      for k, v in pipeline_meta.items():
        encoded_output[k] = v

      encoded_output['PLUGIN_CATEGORY'] = 'general'
      a = 1

    for k, v in lvl_1_dct.items():
      encoded_output[k] = v

    return encoded_output

  def _decode_streams(self, dct_config_streams):
    return dct_config_streams
