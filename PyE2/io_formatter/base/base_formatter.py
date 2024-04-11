import traceback
from time import time

from ...const import PAYLOAD_DATA


class BaseFormatter(object):

  def __init__(self, log, signature, **kwargs):
    self.signature = signature
    self.log = log
    super(BaseFormatter, self).__init__()
    return

  def P(self, *args, **kwargs):
    return self.log.P(*args, **kwargs)

  def _decode_streams(self, dct_config_streams):
    """
    Maybe implement
    """
    return dct_config_streams

  def _encode_output(self, output):
    """
    Maybe implement
    """
    return output

  def _decode_output(self, encoded_output):
    """
    Maybe implement
    """
    return encoded_output

  def decode_streams(self, dct_config_streams):
    try:
      dct_config_streams = self._decode_streams(dct_config_streams)
    except Exception as e:
      dct_config_streams = {}
      msg = "ERROR! Could not decode streams!\n{}".format(e)
      self.P(msg)
      self.P(traceback.format_exc(), color='r')

    return dct_config_streams

  def encode_output(self, output):
    tm = time()
    self.log.start_timer('encode', section='Formatter_' + str(self.signature))
    try:
      encoded_output = self._encode_output(output)
    except Exception as e:
      encoded_output = {}
      msg = "ERROR! Could not encode output {}\n{}".format(output, e)
      self.P(msg)
      self.P(traceback.format_exc(), color='r')
    # end try-except

    elapsed = time() - tm
    self.log.stop_timer('encode', section='Formatter_' + str(self.signature))
    return encoded_output, elapsed

  def decode_output(self, encoded_output):
    ee_impl = encoded_output.get(PAYLOAD_DATA.EE_FORMATTER, encoded_output.get(PAYLOAD_DATA.SB_IMPLEMENTATION, None))
    if ee_impl is None or (isinstance(ee_impl, str) and ee_impl.lower() != self.signature.lower()):
      return encoded_output

    self.log.start_timer('decode', section='Formatter_' + str(self.signature))
    try:
      output = self._decode_output(encoded_output)
    except Exception as e:
      output = {}
      msg = "ERROR! Could not decode {}\n{}".format(encoded_output, e)
      self.P(msg)
      self.P(traceback.format_exc(), color='r')
    # end try-except
    self.log.stop_timer('decode', section='Formatter_' + str(self.signature))
    if isinstance(output, dict):
      output[PAYLOAD_DATA.EE_FORMATTER] = ee_impl
    return output
