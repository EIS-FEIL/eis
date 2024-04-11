# -*- coding: utf-8 -*-
from eis.tests.basetest import *
from eis.lib.exceptions import NotAuthorizedException

class FunctionalTestBase(BaseTestCase):

    # content-type, mis on vajalik post() parameetriks anda, kui vormi parameetrites on täpitähti
    CTYPE = 'application/x-www-form-urlencode; charset=UTF-8'

    def setUp(self):
        url = 'http://localhost:5100'
        self.testapp = TestApp(url)

    def _login(self):
        username = 'ADMIN'
        parool = 'admin'
        params = {'username': username,
                  'parool': parool,
                  'sisene': 'Sisene',
                  'request_url': '',
                  #'action': 'signin',
                  }
        res = self.testapp.post('/login/signin', params)
        return res.follow()
        
