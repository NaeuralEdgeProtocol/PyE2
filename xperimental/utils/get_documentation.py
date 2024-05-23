import ast
import inspect
import os

from PyE2 import BaseDecentrAIObject, _PluginsManagerMixin

from core.core_logging.full_logger import Logger, SBLogger
from core.main.entrypoint import main


class Utils(BaseDecentrAIObject, _PluginsManagerMixin):
    pass
  
class MethodExtractor(ast.NodeVisitor):
    def __init__(self):
        self.methods = []

    def visit_FunctionDef(self, node):
        if not node.name.startswith('_'):
            docstring = ast.get_docstring(node)
            args = [arg.arg for arg in node.args.args]
            self.methods.append((node.name, args, docstring))
        self.generic_visit(node)

def extract_methods(source_code):
    tree = ast.parse(source_code)
    extractor = MethodExtractor()
    extractor.visit(tree)
    return extractor.methods

def generate_stub_method(name, args, docstring, is_property=False):
    args_str = ', '.join(args)
    
    method = None
    decorator = '  @property\n' if is_property else ''

    if docstring:
        docstring_lines= docstring.split('\n')
        docstring = '\n'.join([f'    {line}' for line in docstring_lines])
        docstring_formatted = f'    """\n{docstring}\n    """' 
        method = f'{decorator}  def {name}({args_str}):\n{docstring_formatted}\n    raise NotImplementedError\n'
    else:
        method = f'{decorator}  def {name}({args_str}):\n    raise NotImplementedError\n'
    return method

def generate_stub_class(methods):
    stub_methods = [generate_stub_method(name, args, docstring, is_property) for name, args, docstring, is_property in methods]
    
    stub_methods = '\n'.join(stub_methods)
    
    stub_class = f'class CustomPluginTemplate:\n{stub_methods}'
    
    return stub_class

def extract_methods_from_class(cls):
    methods = []
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith('_'):
            docstring = inspect.getdoc(method)
            args = list(inspect.signature(method).parameters)
            methods.append((name, args, docstring, False))
    for name, prop in inspect.getmembers(cls, predicate=lambda x: isinstance(x, property)):
        if not name.startswith('_'):
            docstring = inspect.getdoc(prop.fget)
            methods.append((name, [], docstring, True))
    return methods

def get_all_methods(cls):
    methods = {}
    for base_cls in inspect.getmro(cls):
        if base_cls is object:
            continue
        methods.update({name: (args, docstring, is_property) for name, args, docstring, is_property in extract_methods_from_class(base_cls)})
    return [(name, args, docstring, is_property) for name, (args, docstring, is_property) in methods.items()]


def create_stub_file_from_class(cls, destination_filename):
    methods = get_all_methods(cls)
    methods.sort(key=lambda x: x[0])
    stub_class = generate_stub_class(methods)
    with open(destination_filename, 'w', encoding='utf-8') as dest_file:
        dest_file.write(stub_class)

def get_class_from_source(source_code):
    tree = ast.parse(source_code)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            return node.name
    return None

def create_stub_file(log:Logger, source_filename, destination_filename):
    with open(source_filename, 'r') as source_file:
        source_code = source_file.read()

    class_name = get_class_from_source(source_code)
    if not class_name:
        raise ValueError("No class found in the source file.")

    module_name = os.path.splitext(source_filename)[0].split(os.sep)
    module_name = '.'.join(module_name[:-1])
    module, class_name, _, _ = Utils(log)._get_module_name_and_class(
        locations=[module_name],
        name=os.path.splitext(os.path.basename(source_filename))[0],
        suffix="Plugin"
        )

    cls = getattr(module, class_name)
    create_stub_file_from_class(cls, destination_filename)
    
# Example usage
log = SBLogger()
create_stub_file(log, r'core\business\default\custom_exec_01.py', 'plugin_template.py')