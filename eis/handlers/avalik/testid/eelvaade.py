from eis.lib.baseresource import *
from eis.handlers.ekk.testid import eelvaade

log = logging.getLogger(__name__)

class EelvaadeController(eelvaade.EelvaadeController):
    """Testi sooritamise eelvaade testi koostajale
    """
    _permission = 'testid'
    _EDIT_TEMPLATE = 'avalik/testid/eelvaade.mako'
    _actions = 'index,new,create,show,update,edit,download,delete' # võimalikud tegevused

    def _get_test(self, komplekt_id=None, ty_id=None):
        c = self.c
        if not c.testiosa_id:
            # kui testiosa ei olnud (sest tuldi kohast, kus testiosa_id puudus),
            # siis määratakse
            c.testiosa_id = 0
        r = super()._get_test(komplekt_id, ty_id)
        if not c.testiosa_id:
            c.testiosa_id = c.testiosa.id
        return r
    
    def _url_edit(self, id):
        "URL, mis peale eelvaate loomist avab selle"
        c = self.c
        return self.url_current('edit', testiosa_id=c.testiosa_id, alatest_id='', id=id, e_komplekt_id=c.e_komplekt_id)
    
    def _url_out(self):
        "URL, mida kasutatakse eelvaatest väljumisel"
        c = self.c
        if c.testiruum_id and c.testiruum_id != '0':
            return self.url('testid_yldandmed', id=c.test_id, testiruum_id=c.testiruum_id)
        else:
            return self.url('test', id=c.test_id)

    def __before__(self):       
        c = self.c
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        if c.testiruum_id:
            testiruum = model.Testiruum.get(c.testiruum_id)
            c.nimekiri = testiruum and testiruum.nimekiri
        c.avalik = True
        eelvaade.EelvaadeController.__before__(self)
        # eistest päringud teha ilma puhvrita, et koostaja saaks värske
        c.test_cachepurge = True
        
