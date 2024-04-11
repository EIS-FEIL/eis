# -*- coding: utf-8 -*- 

from eis.lib.base import *
_ = i18n._
log = logging.getLogger(__name__)

class Testiosavalik:

    def set_test_testiosa(self, testiruum_key='testiruum_id', test_key='test_id'):
        c = self.c
        c.test_id = self.request.matchdict.get(test_key)
        c.test = model.Test.get(c.test_id)

        c.testiosa_id = self.request.params.get('testiosa_id')
        if c.testiosa_id:
            c.testiosa = model.Testiosa.get(c.testiosa_id)
            if c.testiosa.test_id != c.test.id:
                c.testiosa = c.testiosa_id = None
            
        c.testiruum = self._get_testiruum(c.test_id, c.testiosa_id, testiruum_key)
        if c.testiruum:
            c.testiruum_id = c.testiruum.id
            c.nimekiri = c.testiruum.nimekiri
            c.nimekiri_id = c.nimekiri and c.nimekiri.id or None
            c.testiosa = c.testiruum.testikoht.testiosa
        elif c.test:
            c.testiruum_id = 0
            if not c.testiosa:
                if len(c.test.testiosad):
                    c.testiosa = c.test.testiosad[0]
                else:
                    c.testiosa = c.test.give_testiosa()
                    model.Session.flush()

        c.testiosa_id = c.testiosa.id
        
    def _get_testiruum(self, test_id, testiosa_id, testiruum_key):
        c = self.c
        testiruum_id = int(self.request.matchdict.get(testiruum_key))
        testiruum = nimekiri_id = None
        if testiruum_id:
            # testiruum on antud
            testiruum = model.Testiruum.get(testiruum_id)
            if testiruum:
                nimekiri_id = testiruum.nimekiri_id
                if testiosa_id:
                    # testiosa on ka antud - kui see ei vasta testiruumile, siis see ei sobi
                    testikoht = testiruum.testikoht
                    if testikoht.testiosa_id != testiosa_id:
                        testiruum = None
        if not testiruum:
            # leiame viimasena loodud nimekirja
            q = (model.Testiruum.query
                 .join(model.Testiruum.nimekiri)
                 .filter(model.Nimekiri.test_id==test_id)
                 .filter(model.Nimekiri.testimiskord_id==None)
                 .filter(model.Nimekiri.esitaja_kasutaja_id==c.user.id)
                 )
            if nimekiri_id:
                q = q.filter(model.Testiruum.nimekiri_id==nimekiri_id)
            if c.user.koht_id:
                q = q.filter(model.Nimekiri.esitaja_koht_id==c.user.koht_id)
            if testiosa_id:
                q = (q.join(model.Testiruum.testikoht)
                     .filter(model.Testikoht.testiosa_id==testiosa_id))
            q = q.order_by(model.sa.desc(model.Testiruum.id))
            testiruum = q.first()
        return testiruum

    def _redirect_ruum(self, testiruum_key='testiruum_id'):
        """Peale testiosa valiku muutmist kontrollitakse, kas testiruum vastab testiosale.
        Kui ei vasta, siis tehakse redirect, et URLis oleks õige ruum.
        """
        c = self.c
        try:
            testiruum_id = int(self.request.matchdict.get(testiruum_key))
        except:
            pass
        else:
            if testiruum_id:
                new_testiruum_id = c.testiruum and c.testiruum.id or 0
                if testiruum_id != new_testiruum_id:
                    # peale testiosa muutmist suuname testiosale vastava ruumi juurde
                    log.debug('muutub testiruum %s > %s' % (testiruum_id, new_testiruum_id))
                    args = {testiruum_key: new_testiruum_id,
                            'testiosa_id': c.testiosa.id,
                            }
                    raise self._redirect(c.action, **args)
