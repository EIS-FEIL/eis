from simplejson import dumps
import traceback
from eis.lib.baseresource import *
from eis.lib.blockview import BlockView
from eis.lib.resultstat import ResultStat
from eis.lib.resultentry import ResultEntry
from eis.handlers.ekk.hindamine.analyysvastused import AnalyysvastusedController
_ = i18n._

log = logging.getLogger(__name__)

class AnalyysController(AnalyysvastusedController):
    _permission = 'ekk-testid'
    _MODEL = model.Valitudylesanne
    _INDEX_TEMPLATE = 'ekk/testid/analyys.mako'
    _EDIT_TEMPLATE = 'ekk/testid/analyys.mako' 
    _DEFAULT_SORT = 'testiylesanne.seq' # vaikimisi sortimine
    _no_paginate = True
    _ignore_default_params = ['csv_y', 'csv_k', 'csv_v']

    def _query(self):
        # otsime tkorrata statistikat
        q = (model.Session.query(model.Ylesanne, 
                                 model.Valitudylesanne,
                                 model.Testiylesanne,
                                 model.Ylesandestatistika)
             .join(model.Testiylesanne.valitudylesanded)
             .filter(model.Testiylesanne.liik.in_((const.TY_LIIK_Y, const.TY_LIIK_K)))
             .join(model.Valitudylesanne.ylesanne)
             .join(model.Testiylesanne.testiosa)
             .filter(model.Testiosa.test_id==self.c.test.id)
             .outerjoin((model.Ylesandestatistika,
                         sa.and_(model.Ylesandestatistika.valitudylesanne_id==model.Valitudylesanne.id,
                                 model.Ylesandestatistika.testiruum_id==None,
                                 model.Ylesandestatistika.tkorraga==False)))
             )
        return q

    def _search_default(self, q):
        # vaikimisi otsitakse jooksvast testiosast
        for osa in self.c.test.testiosad:
            self.c.testiosa_id = osa.id
            break
        return self._search(q)

    def _search_protsessid(self, q):
        q = (q.filter(model.Arvutusprotsess.liik.in_((model.Arvutusprotsess.LIIK_VASTUSED,
                                                      model.Arvutusprotsess.LIIK_STATISTIKA)))
             .filter(model.Arvutusprotsess.kasutaja_id==self.c.user.id)
             .filter(model.Arvutusprotsess.toimumisaeg_id==None)
             .filter(model.Arvutusprotsess.test_id==self.c.test.id)
             )
        return q
    
    def create(self):
        """Arvutusprotsessi käivitamine
        """
        stat = self.request.params.get('stat')
        debug = self.request.params.get('debug')
        debug = debug or self.is_devel and '1'
        testiosa_id = self.request.params.get('testiosa_id')
        if testiosa_id:
            testiosa = model.Testiosa.get(testiosa_id)
        else:
            testiosa = self.c.test.testiosad[0]
        testiosa_id = testiosa.id
        
        def childfunc(rcd):
            if stat:
                self._calculate_stat(rcd)
            else:
                self._calculate_result(rcd, testiosa_id)

        if stat:
            liik = model.Arvutusprotsess.LIIK_STATISTIKA
            desc = _("Statistika arvutamine")
        else:
            liik = model.Arvutusprotsess.LIIK_TULEMUSED
            desc = _("Tulemuste arvutamine")
            if len(self.c.test.testiosad) > 1:
                desc += ' (osa %s)' % testiosa.seq
                
        params = {'test': self.c.test,
                  'liik': liik,
                  'kirjeldus': desc}
        model.Arvutusprotsess.start(self, params, childfunc)

        # deemon käivitatud, naaseme kasutaja juurde
        self.success(_("Arvutusprotsess on käivitatud"))
        return self._redirect('index')

    def _calculate_stat(self, protsess):
        """Statistika arvutamise protsessi sisu
        """
        test = self.c.test
        test_id = test.id
        testimiskord = testimiskord_id = None
        resultstat = ResultStat(self, protsess, False)
        resultstat.calc_y(test, testimiskord)

        resultstat.calc_kysimused(test, testimiskord, progress_end=90.)
        resultstat.refresh_statvastus_t(test_id, testimiskord_id, progress_end=99.)

    def _calculate_result(self, protsess, testiosa_id):
        """Tulemuste arvutamise protsessi sisu
        """
        test = self.c.test
        testiosa = model.Testiosa.get(testiosa_id)
        assert testiosa.test_id == test.id, 'vale test'
        
        resultentry = ResultEntry(self, None, test, testiosa)

        # kontrollime üle, mis on vajalikud hindamiskogumid
        # korraldaja võis olla nende parameetreid vahepeal muutnud
        hindamistasemed = {}
        for hk in testiosa.hindamiskogumid:
            for valimis in (False, True):
                hindamistase = hk.get_hindamistase(valimis)
                hindamistasemed[hk.id, valimis] = hindamistase

        # leiame sooritused, mille tulemusi arvutada
        q = (model.Sooritus.query
             .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritus.testiosa_id==testiosa.id)
             .filter(model.Sooritus.toimumisaeg_id==None))
        cnt = q.count()
        log.debug('Arvutada %d sooritust...' % cnt)

        for n, tos in enumerate(q.all()):
            #pallid = 0
            sooritaja = tos.sooritaja
            valimis = sooritaja.valimis

            # e-hindamise korral lisame puuduvad vastused statistika jaoks
            # ei lisa puuduvaid vastuseid p-hindamise korral, sest siis ei pea vastuseid andmebaasis alati olema
            resultentry.add_missing_kv(tos)
            tos.give_hindamisolekud()
            for holek in tos.hindamisolekud:
                algtase = hindamistasemed.get((holek.hindamiskogum_id, valimis))
                if algtase is not None and \
                        holek.hindamistase < const.HINDAJA3 and \
                        holek.hindamistase != algtase:
                    holek.hindamistase = algtase
                resultentry.update_hindamisolek(sooritaja, tos, holek, True, False)

            resultentry.update_sooritus(sooritaja, tos)

            if protsess:
                if not n % 10:
                    protsess.edenemisprotsent = 100 * n / cnt
                    model.Session.commit()

    def _edit(self, item):
        ty = item.testiylesanne
        self.c.komplekt_id = item.komplekt_id
        self.c.testiosa_id = ty.testiosa_id
        self._index_d()
        if item.ylesanne:
            self.c.testiosa = ty.testiosa
            self.c.item_html = BlockView(self, item.ylesanne, self.c.lang).assessment_analysis()
    
    def _trace(self, buf, pid=None):
        log.debug(buf)
        try:
            f = open('/srv/eis/log/arvutus.log', 'a')
            if pid:
                buf = '[%s] %s' % (pid, buf)
            f.write('%s %s\n' % (datetime.now(), buf))
            f.close()
        except:
            pass

    def _get_perm_bit(self):
        # kõik vaatamisõigusega kasutajad võivad käivitada statistika arvutamise
        return const.BT_SHOW

    def _perm_params(self):
        return {'obj': self.c.test}

    def __before__(self):
        self.c.test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(self.c.test_id)
        
