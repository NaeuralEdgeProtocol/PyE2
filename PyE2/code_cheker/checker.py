import ast


class CheckerConstants:
  """
  ASTChecker constants.
  """
  type_key = 'type'
  error_key = 'error'
  var = 'var'
  attr = 'attribute'


class ASTChecker(ast.NodeVisitor):
  """
  An Abstract Syntax Tree based checker for custom code.
  """

  def __init__(self, unallowed_dict: dict, safe_imports: list):
    """
    Constructor for the AST checker.

    Parameters
    ----------
    unallowed_dict - a dictionary for unallowed identifiers.
      The dictionary has the indentifier names as keys. The
      Values are dictionaries with keys 'error' and 'type'.
      The error is used for error printing while the type
      specifies the context in which the identifier is not
      allowed. Valid values for the type are 'var' and
      'attribute':
        - 'var': the identifier is not allowed to be used as
          a variable
        - 'attribute': the identifier is not allowed to be used
          as the attribute name of an object.
    safe_imports: list, a list of strings containing module names
      from which we can import without producing an error.

    Example:
      TEST_UNALLOWED_DICT = {
        'getattr': {
            'error': 'Usage of `getattr()` is not allowed in plugin code ',
            'type': 'var',
        },
        'log': {
          'error': 'Logger object cannot be used directly in plugin code - please use API ',
          'type': 'attribute',
        }
      }
      safe_imports=['fiz']
      checker = ASTChecker(TEST_UNALLOWED_DICT, safe_imports)
    """
    self.unallowed_dict = unallowed_dict
    self.errors = {}
    self.safe_imports = safe_imports
    if self.safe_imports is None:
      self.safe_imports = []
    return

  def add_error(self, node, error):
    """
    Add an error to the set of found errors.

    Parameters
    ----------
    node: ast.AST, the AST node for which we've found this error.

    error: str, the error message to be recorded.

    Returns
    -------
    None
    """
    lst = self.errors.get(error)
    if lst is None:
      self.errors[error] = [node.lineno]
      return
    self.errors[error].append(node.lineno)
    return

  def _is_safe_import(self, name):
    """
    Check if the import of the class with the name `name` is considered to be
    safe and should not produce an error.

    Parameters
    ----------
    name: str, the name of the class being imported

    Returns
    -------
    bool - True if the import is safe, False otherwise.
    """
    for safe_name in self.safe_imports:
      if name == safe_name:
        return True
      if name.startswith(safe_name + '.'):
        return True
    return False

  def visit_Import(self, node):
    for imp_alias in node.names:
      if not self._is_safe_import(imp_alias.name):
        self.add_error(node, f'Import forbidden for {imp_alias.name} ')

    self.generic_visit(node)
    return

  def visit_ImportFrom(self, node):
    if not self._is_safe_import(node.module):
      self.add_error(node, f'Import forbidden for {node.module} ')
    self.generic_visit(node)
    return

  def visit_Attribute(self, node):
    handle = self.unallowed_dict.get(node.attr)
    if handle is not None and handle[CheckerConstants.type_key] == CheckerConstants.attr:
      self.add_error(node, handle[CheckerConstants.error_key])
    self.generic_visit(node)
    return

  def visit_Name(self, node):
    handle = self.unallowed_dict.get(node.id)
    if handle is not None and handle[CheckerConstants.type_key] == CheckerConstants.var:
      self.add_error(node, handle[CheckerConstants.error_key])
    self.generic_visit(node)
    return

  def validate(self, code: str) -> str:
    """
    Runs code validation on the given code.

    Parameters
    ----------
    code: str, the code to validate

    Returns
    -------
    dict - a dictionary with the error strings as the keys and a list
      of lines numbers where these occured as the values.
    """
    try:
      tree = ast.parse(code, type_comments=True)
      self.visit(tree)
      return self.errors
    except Exception as e:
      return {
        f"Unable to parse code {e}": [0]
      }


if __name__ == '__main__':
  TEST_UNALLOWED_DICT = {
    'globals': {
      'error': 'Global vars access is not allowed in plugin code ',
      'type': 'var',
    },

    'locals': {
      'error': 'Local vars dict access is not allowed in plugin code ',
      'type': 'var',
    },

    'memoryview': {
      'error': 'Pointer handling is unsafe in plugin code ',
      'type': 'var',
    },

    'log': {
      'error': 'Logger object cannot be used directly in plugin code - please use API ',
      'type': 'attribute',
    },

    'vars': {
      'error': 'Usage of `vars(obj)` is not allowed in plugin code ',
      'type': 'var',
    },

    'dir': {
      'error': 'Usage of `dir(obj)` is not allowed in plugin code ',
      'type': 'var',
    },

    'global_shmem': {
      'error': 'Usage of `global_shmem` is not allowed in plugin code ',
      'type': 'attribute',
    },

    'plugins_shmem': {
      'error': 'Usage of `plugins_shmem` is not allowed in plugin code ',
      'type': 'attribute',
    },

    'config_data': {
      'error': 'Usage of `config_data` is not allowed in plugin code ',
      'type': 'attribute',
    },

    '_default_config': {
      'error': 'Usage of `_default_config` is not allowed in plugin code ',
      'type': 'attribute',
    },

    '_upstream_config': {
      'error': 'Usage of `_upstream_config` is not allowed in plugin code ',
      'type': 'attribute',
    },

    'exec': {
      'error': 'Usage of `exec()` is not allowed in plugin code ',
      'type': 'var',
    },

    'eval': {
      'error': 'Usage of `eval()` is not allowed in plugin code ',
      'type': 'var',
    },

    'getattr': {
      'error': 'Usage of `getattr()` is not allowed in plugin code ',
      'type': 'var',
    },
  }
  safe_imports = ['fiz', 'biz']
  checker = ASTChecker(TEST_UNALLOWED_DICT, safe_imports)

  code = """import ast
import foo as bar
from foo import bar as baz

import biz

print(eval('some_string'))

foo=eval
foo('another_string')

self.log.P()
__builtins__.eval()

def bar():
  global x
  x = x + 42
  return

"""
  print(checker.validate(code))

  # Make sure we print sane errors when parsing fails.
  code = "x &&&& y"
  checker = ASTChecker(TEST_UNALLOWED_DICT, safe_imports)
  print(checker.validate(code))

  # Make sure we print sane errors when parsing fails.
  code = """
  a = x + y
"""
  checker = ASTChecker(TEST_UNALLOWED_DICT, safe_imports)
  print(checker.validate(code))

  # Even though the following import starts with 'fiz' which is safe we should
  # fail it.
  code = """
import fizzy
"""
  checker = ASTChecker(TEST_UNALLOWED_DICT, safe_imports)
  print(checker.validate(code))

  # Case when an user defines a method
  code = """
def foo():
  import fizzy
  return
  """
  checker = ASTChecker(TEST_UNALLOWED_DICT, safe_imports)
  print(checker.validate(code))

  # Case when the user defines a method with an empty line in body
  code = """

  return
  """
  checker = ASTChecker(TEST_UNALLOWED_DICT, safe_imports)
  print(checker.validate(code))

  # Case when the user defines a method with variables not defined
  code = """
def foo():

  x = a + 1
  return
  """
  checker = ASTChecker(TEST_UNALLOWED_DICT, safe_imports)
  print(checker.validate(code))
