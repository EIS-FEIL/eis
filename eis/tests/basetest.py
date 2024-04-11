"""
Automaattestimine

Testimiseks testbaasiga:
Vaadata, et fn väärtus oleks development.test.ini
Eelnevalt peab olema loodud andmebaasistruktuur:
   bash resettest.sh

Testide käivitamine:
   python setup.py test
"""

import unittest
from pyramid import testing
import pyramid_handlers
from paste.deploy.loadwsgi import appconfig
from pyramid.config import Configurator
from webtest import TestApp
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy.orm import sessionmaker

from eis import main, model
from eis.model import const
from eis.scripts.mockrequest import MockRequest, MockHandler
import os

fn = '/srv/eis/etc/config.ini'
app_name = 'eis'
settings = appconfig('config:%s' % fn, name=app_name)
settings['app_name'] = app_name

db_initialized = False
def _initTestingDB():
    global db_initialized, settings
    if not db_initialized:
        db_initialized = True
        engine = engine_from_config(settings, prefix='sqlalchemy.')
        model.initialize_sql(engine)

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _initTestingDB()
        
    def setUp(self):
        pass

    def tearDown(self):
        testing.tearDown()
        model.Session.rollback()
        model.Session.close()
        model.Session.remove()

class TestUser(object):
    def __init__(self, isikukood, id):
        self.id = id
        self.isikukood = isikukood
        self.app_ekk = True
        registry = None
        self.handler = MockHandler(registry, settings, model)

    @classmethod
    def get_testuser(cls):
        return TestUser('TEST', 1)
    
