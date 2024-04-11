import types
import sys
import os
import simplejson

from eis import model as model

"""
This module can be used for loading data into your models, for example when setting up default application data,
unit tests, JSON export/import and importing/exporting legacy data. Data is serialized to and from the JSON format. 
"""

VALID_FIXTURE_FILE_EXTENSIONS = ['.json']

def load_data(model, filename=None, base_dir=None):
    """Installs provided fixture files into given model. Filename may be directory, file or list of dirs or files. If filename is 
    None, assumes that source file is located in fixtures/model_module_name/model_tablename.yaml of your application directory, 
    for example MyProject/fixtures/news/newsitems.yaml. The base_dir argument is the top package of the application unless 
    specified. You can also pass the name of a table instead of a model class."""

    if type(model) is bytes:
        return load_data_to_table(model, filename, base_dir)
    else:
        if filename is None:
            filename = _default_fixture_path_for_model(model, base_dir)
        return _load_data_from_file(model, filename)

def load_data_to_table(table, filename=None, base_dir=None):
    """Installs data directly into a table. Useful if table does not have a corresponding model, for example a many-to-many join table.
    """
    
    if filename is None:
        filename = _default_fixture_path_for_table(table, base_dir)
    _load_data_to_table(table, filename)
    
def dump_data(model, filename=None, **params):
    """Dumps data to given destination. Params are optional arguments for selecting data. If filename is None, assumes that destination 
    file is located in fixtures/model_module_name/model_name_lowercase.yaml of your application directory, for example 
    MyProject/fixtures/news/newsitem.yaml.
    """
    
    if filename is None:
        filename = _default_fixture_path_for_model(model)
    _dump_data_to_file(model, filename, **params)

_base_dir = os.path.dirname(os.path.dirname(__file__))

def _default_fixture_path_for_model(model, base_dir=None):
    if base_dir is None:
        base_dir = _base_dir
    path = os.path.join(base_dir, 'fixtures')
    module_dirs = model.__module__.split('.', 2)[-1].split('.')
    for dir in module_dirs:
        path = os.path.join(path, dir)
    return os.path.join(path, model.table.name + '.json')    

def _default_fixture_path_for_table(table, base_dir=None):
    if base_dir is None:
        base_dir = _base_dir
    module_dirs = table.split('.')
    path = os.path.join(base_dir, 'fixtures')
    for name in module_dirs:
        path = os.path.join(path, name)
    return path + ".json"

def _is_fixture_file(filename):
    basename, ext = os.path.splitext(filename)
    return (ext.lower() in VALID_FIXTURE_FILE_EXTENSIONS)
    
def _load_data_from_dir(model, dirname):
    for dirpath, dirnames, filenames in os.walk(dirname):
        for filename in filenames:
            _load_data_from_file(model, filename)
    
def _load_data_from_file(model, filename):
    if not _is_fixture_file(filename): 
        return
    fp = file(filename, 'r')
    data = simplejson.load(fp)
    fp.close()
    retval = None
    if type(data) is list:
        retval = []
        for item in data:
            retval.append(_load_instance_from_dict(model, item))
    elif type(data) is dict:
        retval = {}
        for key, item in data.items():
            retval[key] = _load_instance_from_dict(model, item)    
    return retval

def _load_data_to_table(tablename, filename):
    if not _is_fixture_file(filename): 
        return
    fp = file(filename, 'r')
    data = simplejson.load(fp)
    fp.close()
    tablename = tablename.split(".")[-1]
    table = model.context.metadata.tables[tablename]
    if type(data) is list:
        for item in data:
            table.insert(item).execute()
    elif type(data) is dict:
        for key, item in data.items():
            table.insert(item).execute()
    return data
    
def _dump_data_to_file(model, filename, **params):
    if params:
        queryset = model.select_by(**params)
    else:
        queryset = model.select()
    data = []
    for instance in queryset:
        data.append(_dump_instance_to_dict(instance))
    fp = file(filename, 'w')
    simplejson.dump(data, fp)
    fp.close()
    
def _load_instance_from_dict(model, dict):
    if not dict: return 
    instance = model()
    fields = list(model._descriptor.fields.keys())
    for k, v in dict.items():
        if k in fields:
            setattr(instance, k, v)
    instance.flush()
    return instance

def _dump_instance_to_dict(instance):
    if hasattr(instance, 'to_json'):
        return instance.to_json()
    d = {}
    fields = list(instance._descriptor.fields.keys())
    for field in fields:
        d[field] = getattr(instance, field)
    return d
       
__all__ = ['load_data', 'dump_data']
