import inspect
import zlib
import sys
import base64


def code_to_base64(plain_code, verbose=False, compress=True, code_checker_callback=None):
  if verbose:
    print("Processing:\n{}".format(plain_code), color='y')
  errors = None
  if code_checker_callback is not None:
    errors = code_checker_callback(plain_code)
  if errors is not None:
    print("Cannot serialize code due to: '{}'".format(errors), color='r')
    return None
  l_i = len(plain_code)
  l_c = -1
  b_code = bytes(plain_code, 'utf-8')
  if compress:
    b_code = zlib.compress(b_code, level=9)
    l_c = sys.getsizeof(b_code)
  b_encoded = base64.b64encode(b_code)
  str_encoded = b_encoded.decode('utf-8')
  l_b64 = len(str_encoded)
  if verbose:
    print("Code checking and serialization suceeded. Initial/Compress/B64: {}/{}/{}".format(
        l_i, l_c, l_b64), color='g'
    )
  return str_encoded


def _get_function_source_code(func):
  plain_code = inspect.getsourcelines(func)[0]
  plain_code = plain_code[1:]
  indent = len(plain_code[0]) - len(plain_code[0].lstrip())
  plain_code = '\n'.join([line.rstrip()[indent:] for line in plain_code])
  return plain_code


def method_to_base64(func, verbose=False, compress=True, code_checker_callback=None):
  code = _get_function_source_code(func)
  return code_to_base64(code, verbose=verbose, compress=compress, code_checker_callback=code_checker_callback)
