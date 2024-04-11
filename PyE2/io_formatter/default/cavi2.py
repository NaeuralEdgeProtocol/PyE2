# global dependencies
import json

# local dependencies
from ...const import FORMATTER_DATA
from ...io_formatter.base import BaseFormatter


class Cavi2Formatter(BaseFormatter):

  def __init__(self, log, **kwargs):
    super(Cavi2Formatter, self).__init__(
        log=log, prefix_log='[CAVI2-FMT]', **kwargs)
    return

  def startup(self):
    pass

  def _decode_streams(self, dct_config_streams):
    self.P("Decoding streams ...")
    for _, config_stream in dct_config_streams.items():
      stream_name = config_stream['NAME']
      stream_signatures = []
      for plugin in config_stream['PLUGINS']:
        plugin_sign = plugin.get(FORMATTER_DATA.SIGNATURE, 'Unknown')
        if plugin_sign in stream_signatures:
          str_form = self.log.dict_pretty_format(dct_config_streams)
          self.P("  Plugin '{}' previously present in stream, new declaration will be dropped, please include all instances in just one signature\n{}".format(
              plugin_sign, str_form), color='r')
          continue
        else:
          stream_signatures.append(plugin_sign)
        self.P("  Processing signature '{}' with {} instances".format(
            plugin_sign, len(plugin['INSTANCES'])
        )
        )
        instances = []
        processed_ids = set()
        for instance in plugin['INSTANCES']:
          converted = process_instance_config(instance)
          instance_id = converted['INSTANCE_ID']
          self.P("    Processed instance '{}'".format(instance_id))
          if instance_id in processed_ids:
            self.P("    Instance '{}' already processed for {}:{}. This new one will be dropped. Please check your config".format(
                instance_id, stream_name, plugin_sign), color='r'
            )
          processed_ids.add(instance_id)
          instances.append(converted)
        plugin['INSTANCES'] = instances
      # endfor
      if FORMATTER_DATA.STREAM in config_stream:
        config_stream[FORMATTER_DATA.NAME] = str(config_stream[FORMATTER_DATA.STREAM][FORMATTER_DATA.ID])
        config_stream[FORMATTER_DATA.DESCRIPTION] = config_stream[FORMATTER_DATA.STREAM]['Name']
        del config_stream[FORMATTER_DATA.STREAM]
      # endif
    # endfor
    return dct_config_streams

  def _encode_output(self, output):
    self.log.start_timer(
        '_encode_output', section='Formatter_' + str(self.signature))
    ee_event_type = output.pop('EE_EVENT_TYPE').lower()
    ee_version = output.pop('EE_VERSION')
    category = ''
    data = {
        'identifiers': {},
        'value': {},
        'specificValue': {},
        'time': None,
        'img': {
            'id': None,
            'height': None,
            'width': None,
        }
    }
    message_id = output.pop('EE_MESSAGE_ID')
    metadata = {
        'sbTotalMessages': output.pop('EE_TOTAL_MESSAGES'),
        'sbCurrentMessage': message_id
    }
    time = {
        'deviceTime': '',
        'hostTime': output.pop('EE_TIMESTAMP'),
        'internetTime': '',
    }
    sender = {
        'id': "DecentrAI-ExecutionEngine",
        'instanceId': "DecentrAI-EE-v" + ee_version,
        "hostId": output.pop('EE_ID')
    }

    if ee_event_type == 'payload':
      self.log.start_timer(
          '_encode_payload', section='Formatter_' + str(self.signature))
      ee_event_type = output.pop('SIGNATURE').lower()
      category = output.pop('PLUGIN_CATEGORY', 'general')  # showcase

      capture_metadata, plugin_metadata = {}, {}
      keys = list(output.keys())
      for k in keys:
        if k.startswith('_C_'):
          capture_metadata[k[3:]] = output.pop(k)
        if k.startswith('_P_'):
          plugin_metadata[k[3:]] = output.pop(k)
        # endif
      # endfor
      metadata['captureMetadata'] = capture_metadata
      metadata['pluginMetadata'] = plugin_metadata

      data['identifiers']['streamId'] = output.pop('STREAM')
      data['identifiers']['instanceId'] = output.pop('INSTANCE_ID')
      data['identifiers']['payloadId'] = output.pop('ID', None)
      data['identifiers']['initiatorId'] = output.pop('INITIATOR_ID', None)
      data['identifiers']['sessionId'] = output.pop('SESSION_ID', None)
      data['identifiers']['idTags'] = output.get('ID_TAGS', None)
      data['time'] = output.pop('TIMESTAMP_EXECUTION', None)
      data['img']['id'] = output.pop('IMG', None)
      data['img']['height'] = output.pop('IMG_HEIGHT', None)
      data['img']['width'] = output.pop('IMG_WIDTH', None)

      keys = list(output.keys())
      for k in keys:
        if k.startswith('_V_'):
          data['value'][k[3:].lower()] = output.pop(k)
        # endif
      # endfor

      keys = list(output.keys())
      for k in keys:
        data['specificValue'][k.lower()] = output.pop(k)
      self.log.stop_timer(
          '_encode_payload', section='Formatter_' + str(self.signature))
    elif ee_event_type in ['heartbeat', 'notification']:
      self.log.start_timer(
          '_encode_hb_notif', section='Formatter_' + str(self.signature))
      keys = list(output.keys())
      for k in keys:
        metadata[k.lower()] = output.pop(k)
      self.log.stop_timer('_encode_hb_notif',
                          section='Formatter_' + str(self.signature))

    # endif

    encoded_output = {
        'messageID': message_id,  # OK
        'type': ee_event_type,  # OK
        'category': category,  # OK
        'version': ee_version,  # OK
        'data': data,  # OK
        'metadata': metadata,
        'time': time,
        'sender': sender,
        'demoMode': False,  # OK,
    }

    self.log.stop_timer(
        '_encode_output', section='Formatter_' + str(self.signature))
    assert len(output) == 0
    return encoded_output

  def _decode_output(self, encoded_output):
    if 'SB_IMPLEMENTATION' in encoded_output:
      encoded_output.pop('SB_IMPLEMENTATION')
    if 'EE_FORMATTER' in encoded_output:
      encoded_output.pop('EE_FORMATTER')
    output = {}
    encoded_output.pop('messageID')

    event_type = encoded_output.pop('type')
    ee_event_type = event_type
    if event_type not in ['notification', 'heartbeat']:
      ee_event_type = 'payload'
    output['EE_EVENT_TYPE'] = ee_event_type.upper()

    data = encoded_output.pop('data')
    metadata = encoded_output.pop('metadata')

    # 'sender' zone
    output['EE_ID'] = encoded_output['sender'].pop('hostId')
    encoded_output['sender'].pop('id')
    encoded_output['sender'].pop('instanceId')
    assert len(encoded_output['sender']) == 0
    encoded_output.pop('sender')

    # 'time' zone
    output['EE_TIMESTAMP'] = encoded_output['time'].pop('hostTime')
    encoded_output['time'].pop('deviceTime')
    encoded_output['time'].pop('internetTime')
    assert len(encoded_output['time']) == 0
    encoded_output.pop('time')

    output['EE_TOTAL_MESSAGES'] = metadata.pop('sbTotalMessages')
    output['EE_MESSAGE_ID'] = metadata.pop('sbCurrentMessage')

    if event_type not in ['notification', 'heartbeat']:
      output['SIGNATURE'] = event_type.upper()
      capture_metadata = metadata.pop('captureMetadata')
      plugin_metadata = metadata.pop('pluginMetadata')
      for k in list(capture_metadata.keys()):
        capture_metadata['_C_{}'.format(k)] = capture_metadata.pop(k)
      for k in list(plugin_metadata.keys()):
        plugin_metadata['_P_{}'.format(k)] = plugin_metadata.pop(k)

      output['STREAM'] = data['identifiers'].pop('streamId')
      output['INITIATOR_ID'] = data['identifiers'].pop(
          'initiatorId', None)  # None is for backward compatibility
      output['INSTANCE_ID'] = data['identifiers'].pop('instanceId')
      output['SESSION_ID'] = data['identifiers'].pop(
          'sessionId', None)  # None is for backward compatibility
      output['ID'] = data['identifiers'].pop('payloadId')
      output['ID_TAGS'] = data['identifiers'].pop('idTags', None)
      assert len(data['identifiers']) == 0
      data.pop('identifiers')
      keys = list(data['value'].keys())
      for k in keys:
        output[k.upper()] = data['value'].pop(k)
      assert len(data['value']) == 0
      data.pop('value')
      keys = list(data['specificValue'].keys())
      for k in keys:
        output[k.upper()] = data['specificValue'].pop(k)
      assert len(data['specificValue']) == 0
      data.pop('specificValue')

      img = data['img'].pop('id')
      img_h = data['img'].pop('height')
      img_w = data['img'].pop('width')
      assert len(data['img']) == 0
      data.pop('img')

      if img is not None:
        output['IMG'] = img
        output['IMG_HEIGHT'] = img_h
        output['IMG_WIDTH'] = img_w
      # endif

      output['TIMESTAMP_EXECUTION'] = data.pop('time')

      # assert len(data) == 0

      output = {**output, **capture_metadata, **plugin_metadata}
    # endif

    keys = list(metadata.keys())
    for k in keys:
      output[k.upper()] = metadata.pop(k)

    # assert len(metadata) == 0
    encoded_output.pop('category')
    encoded_output.pop('version')
    encoded_output.pop('demoMode')
    # assert len(encoded_output) == 0
    for k in list(encoded_output.keys()):
      if k.startswith('EE'):
        output[k] = encoded_output[k]
    return output


def process_instance_config(instance_config, sub_dict_key=FORMATTER_DATA.PLUGIN_INSTANCE_PARAMETER_LIST):
  _EXC = "!!!EXCEPTION!!!"
  if isinstance(instance_config, list):
    dct_result = {
        x['NAME']: x['VALUE'] for x in instance_config
    }
  elif isinstance(instance_config, dict):
    dct_result = instance_config
    if FORMATTER_DATA.PLUGIN_INSTANCE_PARAMETER_LIST in dct_result:
      lst_params = dct_result[FORMATTER_DATA.PLUGIN_INSTANCE_PARAMETER_LIST]
      for dct_param in lst_params:
        dtype = dct_param.get('TYPEVALUE', 'DEFAULT').upper()
        try:
          if dtype in ['STRING', 'DEFAULT']:
            val = dct_param['VALUE']
          elif dtype == 'INTEGER':
            val = int(dct_param['VALUE'])
          elif dtype == 'FLOAT':
            val = float(dct_param['VALUE'])
          else:
            val = json.loads(dct_param['VALUE'])
        except:
          val = _EXC
        if val != _EXC:
          dct_result[dct_param['NAME']] = val
        else:
          dct_result["!!!****" + dct_param['NAME'] +
                     '***!!!'] = dct_param['VALUE']

      del dct_result[FORMATTER_DATA.PLUGIN_INSTANCE_PARAMETER_LIST]
    # endif
  else:
    raise ValueError(
        "Unknown type '{}' for instance config".format(type(instance_config)))
  return dct_result
