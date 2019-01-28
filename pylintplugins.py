from astroid import MANAGER, scoped_nodes, extract_node

def register(_linter):
    pass

def transform(func):
    if func.name == 'logger':
        for prop in ['debug', 'info', 'warning', 'error', 'setLevel']:
            func.instance_attrs[prop] = extract_node(f'def {prop}(arg): return')

MANAGER.register_transform(scoped_nodes.FunctionDef, transform)
