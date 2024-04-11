# -*- coding: utf-8 -*-
# $Id: __init__.py 945 2016-10-19 10:45:28Z ahti $

from eis.tests.basetest import *

class IntegrationTestBase(BaseTestCase):
    app_name = 'eis'
    
    @classmethod
    def setUpClass(cls):
        settings['app_name'] = cls.app_name
        cls.app = main({}, **settings)
        super(IntegrationTestBase, cls).setUpClass()

    def setUp(self):
        self.app = TestApp(self.app)
        self.config = testing.setUp()
        super(IntegrationTestBase, self).setUp()

