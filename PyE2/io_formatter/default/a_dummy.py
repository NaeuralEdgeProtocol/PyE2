
from ...io_formatter.base import BaseFormatter
import re


def camel_to_upper_snake(name):
  name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
  return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).upper()


def snake_to_camel(name):
  name = name.lower()

  words = []
  for i, x in enumerate(name.split('_')):
    if i > 0:
      words.append(x.title())
    else:
      words.append(x)

  return ''.join(words)


class ADummyFormatter(BaseFormatter):

  def __init__(self, **kwargs):
    super(ADummyFormatter, self).__init__(**kwargs)
    return

  def _decode_streams(self, dct_config_streams):
    return dct_config_streams

  def _encode_output(self, output):
    # transforms the first level keys to camelCase
    new_output = {}

    for k, v in output.items():
      k_camel_case = snake_to_camel(k)
      new_output[k_camel_case] = v

    return new_output

  def _decode_output(self, encoded_output):
    # it is used mainly for map-reduce jobs in reduce phase!
    decoded_output = {}

    for k, v in encoded_output.items():
      k_snake_case = camel_to_upper_snake(k)
      decoded_output[k_snake_case] = v

    return decoded_output
