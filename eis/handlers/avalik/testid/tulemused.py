# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
log = logging.getLogger(__name__)

class TulemusedController(BaseResourceController):

    _permission = 'omanimekirjad'
    _actions = 'index' # võimalikud tegevused

    def index(self):
        "Suunatakse õigele nimekirja tulemuste kuvamise vormile"
        c = self.c
        if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
            raise NotAuthorizedException(self.url('avaleht'))
        elif c.test.diagnoosiv:
            url = self.url('test_tagasiside', test_id=c.test_id, testiruum_id=c.testiruum_id)
        elif c.test.on_jagatudtoo:
            url = self.url('test_tootulemused', test_id=c.test_id, testiruum_id=c.testiruum_id)
        elif c.test.on_avaliktest:
            url = self.url('test_avtulemused', test_id=c.test_id, testiruum_id=c.testiruum_id)
        else:
            url = self.url('test_avtulemused', test_id=c.test_id, testiruum_id=c.testiruum_id)            
        raise HTTPFound(location=url)

    def __before__(self):
        self.c.testiruum_id = self.request.matchdict.get('testiruum_id')
        self.c.test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(self.c.test_id)
        
