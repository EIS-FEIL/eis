# Testimiskorrata testi vastuste analyys

from simplejson import dumps
from eis.lib.baseresource import *
from eis.lib.blockview import BlockView
from eis.lib.resultstat import ResultStat
from eis.lib.resultentry import ResultEntry
from .testiosavalik import Testiosavalik
_ = i18n._
log = logging.getLogger(__name__)

class AvanalyysController(BaseResourceController, Testiosavalik):
    _permission = 'testid,ekk-testid'

    _MODEL = model.Valitudylesanne
    _INDEX_TEMPLATE = 'avalik/testid/avtulemused.analyys.mako'
    _EDIT_TEMPLATE = 'avalik/testid/avtulemused.analyysaknas.mako' 
    _DEFAULT_SORT = 'testiylesanne.seq' # vaikimisi sortimine
    _no_paginate = True
    _actions = 'index,create,show,edit' # võimalikud tegevused
    
    @property
    def _get_is_readonly(self):
        return self.c.action != 'index'
    
    def _query(self):
        q = (model.SessionR.query(model.Ylesanne, 
                                 model.Valitudylesanne,
                                 model.Testiylesanne,
                                 model.Ylesandestatistika)
             .join(model.Testiylesanne.valitudylesanded)
             .join(model.Valitudylesanne.ylesanne)
             .join(model.Testiylesanne.testiosa)
             .filter(model.Testiosa.test_id==self.c.test.id)
             .join(model.Valitudylesanne.komplekt)
             .filter(model.Komplekt.staatus.in_(
                 (const.K_STAATUS_KINNITATUD, const.K_STAATUS_KOOSTAMISEL)))
             )
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        if c.nimekiri_id:
            # oma ryhma statistika
            q1 = (model.SessionR.query(model.Testiruum.id)
                  .filter_by(nimekiri_id=c.nimekiri_id))
            truumid_id = [r_id for r_id, in q1.all()]

            q2 = (model.SessionR.query(model.sa.func.count(model.Sooritus.id))
                  .filter(model.Sooritus.testiruum_id.in_(truumid_id))
                  )
            if c.test.on_jagatudtoo:
                q2 = q2.filter(sa.exists().where(
                    sa.and_(model.Ylesandevastus.sooritus_id==model.Sooritus.id,
                            model.Ylesandevastus.kehtiv==True)))
            else:
                q2 = q2.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
            if not q2.scalar():
                # keegi pole minu nimekirjas veel testi sooritanud
                return

            f_yst = sa.and_(model.Ylesandestatistika.valitudylesanne_id==model.Valitudylesanne.id,
                            model.Ylesandestatistika.testiruum_id.in_(truumid_id))

            if c.action == 'index':
                # käivitame automaatselt oma ryhma statistika arvutamise, kui on vaja arvutada
                if self._nk_vaja_arvutada(c.nimekiri):
                    self._start_calc(True)
                    model.Session.commit()
        else:
            # kõigi avalike sooritajate statistika
            f_yst = sa.and_(model.Ylesandestatistika.valitudylesanne_id==model.Valitudylesanne.id,
                            model.Ylesandestatistika.testiruum_id==None,
                            model.Ylesandestatistika.tkorraga==False)
        q = q.outerjoin((model.Ylesandestatistika, f_yst))

        # EKK vaate mako mall eeldab, et andmed on struktuuris c.data
        # vt ekk/hindamine/analyysvastused.py
        self._get_data(q)
        return q

    def _order(self, q):
        q = q.order_by(model.Testiylesanne.testiosa_id,
                       model.Valitudylesanne.komplekt_id,
                       model.Testiylesanne.alatest_seq,
                       model.Testiylesanne.seq,
                       model.Valitudylesanne.seq)
        return q

    def _get_data(self, q):
        # leiame andmed komplektide kaupa
        c = self.c
        q = self._order(q)
        c.osad = {}
        c.komplektid = {}
        c.data = {}
        for row in q.all():
            ylesanne, vy, ty, yst = row            
            komplekt_id = vy.komplekt_id
            osa_id = ty.testiosa_id
            if osa_id not in c.osad:
                osa = model.Testiosa.get(osa_id)
                c.osad[osa_id] = osa.tahis
            if komplekt_id not in c.komplektid:
                komplekt = model.Komplekt.get(komplekt_id)
                c.komplektid[komplekt_id] = komplekt.tahis
                c.data[komplekt_id] = [[], osa_id, komplekt_id]
            c.data[komplekt_id][0].append(row)

        if c.nimekiri_id:
            c.can_calc = c.user.has_permission('nimekiri', const.BT_UPDATE, nimekiri_id=c.nimekiri_id)
        else:
            c.can_calc = c.user.has_permission('testid', const.BT_UPDATE, c.test) \
                       or c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test)
        if c.can_calc:
            self._get_protsessid()

    def _search_protsessid(self, q):
        c = self.c
        q = q.filter(model.Arvutusprotsess.test_id==c.test.id)
        q = q.filter_by(nimekiri_id=c.nimekiri_id or None)
        return q
            
    def create(self):
        """Arvutusprotsessi käivitamine
        """
        stat = self.request.params.get('stat')
        self._start_calc(stat)
        # deemon käivitatud, naaseme kasutaja juurde
        self.success(_('Arvutusprotsess on käivitatud'))
        return self._redirect('index')

    def _start_calc(self, stat):
        """Arvutusprotsessi käivitamine
        """
        if stat:
            # statistika arvutamine
            liik = model.Arvutusprotsess.LIIK_STATISTIKA
            desc = _("Statistika arvutamine")
            childfunc = self._calculate_stat
        else:
            # tulemuste arvutamine
            liik = model.Arvutusprotsess.LIIK_TULEMUSED
            desc = _("Tulemuste arvutamine")
            childfunc = self._calculate_result

        nimekiri_id = self.c.nimekiri_id or None

        params = {'liik': liik,
                  'kirjeldus': desc,
                  'nimekiri_id': nimekiri_id,
                  'test': self.c.test,
                  }
        model.Arvutusprotsess.start(self, params, childfunc)

    def _nk_vaja_arvutada(self, nimekiri):
        # kas mõni arvutamine on juba pooleli?
        q = (model.SessionR.query(model.Arvutusprotsess.id)
             .filter_by(nimekiri_id=nimekiri.id)
             .filter(model.Arvutusprotsess.liik.in_(
                 (model.Arvutusprotsess.LIIK_STATISTIKA,
                  model.Arvutusprotsess.LIIK_TULEMUSED)))
             .filter(model.Arvutusprotsess.lopp==None)
             )
        if q.first():
            # juba arvutatakse
            return False
        
        if not nimekiri.stat_arvutatud:
            # veel ei ole kordagi arvutatud
            return True
        q = (model.SessionR.query(model.Ylesandevastus.id)
             .join((model.Sooritus, model.Sooritus.id==model.Ylesandevastus.sooritus_id))
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritaja.nimekiri_id==nimekiri.id)
             .filter(model.Ylesandevastus.modified > nimekiri.stat_arvutatud)
             )
        if q.first():
            # peale viimast arvutamist on andmeid muudetud
            return True
        return False

    def _calculate_stat(self, protsess):
        """Statistika arvutamise protsessi sisu
        """
        c = self.c
        test = c.test
        nimekiri_id = c.nimekiri_id
        testimiskord = None
        resultstat = ResultStat(self, protsess, False)
        if c.nimekiri_id:
            nimekiri = model.Nimekiri.get(c.nimekiri_id)
            nimekiri.stat_arvutatud = datetime.now()
            q1 = (model.Session.query(model.Testiruum)
                  .filter_by(nimekiri_id=self.c.nimekiri_id))
            for testiruum in q1.all():
                # päriselt on avalikus testis igas nimekirjas yks ruum
                resultstat.calc_testiruum_y(testiruum, test)
            resultstat.calc_kysimused(test, testimiskord, progress_end=99., nimekiri_id=nimekiri_id)
        else:
            resultstat.calc_y(test, testimiskord)
            resultstat.calc_kysimused(test, testimiskord, progress_end=99.)

    def _calculate_result(self, protsess):
        """Tulemuste arvutamise protsessi sisu
        """
        test = self.c.test
        testiosa = self.c.testiosa
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
             .filter(model.Sooritus.testiosa_id==testiosa.id)
             .filter(model.Sooritus.toimumisaeg_id==None))
        if self.c.nimekiri_id:
            q = (q.join(model.Sooritus.sooritaja)
                 .filter(model.Sooritaja.nimekiri_id==self.c.nimekiri_id))
        cnt = q.count()
        log.debug(_('Arvutada {s} sooritust...').format(s=cnt))

        for n, tos in enumerate(q.all()):
            sooritaja = tos.sooritaja
            valimis = sooritaja.valimis

            # tagame hindamisolekute olemasolu
            tos.give_hindamisolekud()
            # e-hindamise korral lisame puuduvad vastused statistika jaoks
            resultentry.add_missing_kv(tos)

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
        self.c.hide_header_footer = True # avatakse ainult fblink kaudu
        self._index_d()
        if item.ylesanne:
            self.c.testiosa = item.testiylesanne.testiosa
            self.c.item_html = BlockView(self, item.ylesanne, self.c.lang).assessment_analysis()

    def _get_perm_bit(self):
        # kõik vaatamisõigusega kasutajad võivad käivitada statistika arvutamise
        return const.BT_SHOW

    def _perm_params(self):
        c = self.c
        if c.test.opetajale_peidus:
            return False
        return {'obj': c.nimekiri or c.test}

    def __before__(self):
        c = self.c
        Testiosavalik.set_test_testiosa(self)

