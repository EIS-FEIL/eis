# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
import eis.lib.regpiirang as regpiirang
_ = i18n._

log = logging.getLogger(__name__)

class OtsitestidController(BaseResourceController):
    """Testide otsimine dialoogiaknas.
    """
    _permission = 'regamine'
    _MODEL = model.Testimiskord
    _INDEX_TEMPLATE = 'ekk/regamine/avaldus.otsitestid.mako'
    _DEFAULT_SORT = 'test.nimi' # vaikimisi sortimine
    _no_paginate = True

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.testiliik:
            if self.c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
                q = q.filter(model.Test.testiliik_kood.in_((const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV)))
            else:
                q = q.filter(model.Test.testiliik_kood==self.c.testiliik)

        ained = self.c.user.get_ained(self._permission)
        if None not in ained:
            q = q.filter(model.Test.aine_kood.in_(ained))

        if self.c.testiliik == const.TESTILIIK_TASE:
            # mitmele tasemeeksamile ei või korraga regada - hoiatus ES-1078
            piirang = regpiirang.reg_te_piirang1(self, self.c.kasutaja.id, app_ekk=True)
            if piirang:
                self.notice(piirang)
            
        return q

    def _search_default(self, q):
        return self._search(q)

    def _query(self):
        d = date.today()
        return (model.Testimiskord.query
                .join(model.Testimiskord.test)
                .filter(model.Testimiskord.reg_ekk==True)
                .filter(model.Testimiskord.kuni>=d)
                .filter(~ model.Testimiskord.sooritajad.any(
                    sa.and_(model.Sooritaja.kasutaja_id==self.c.kasutaja.id,
                            model.Sooritaja.staatus!=const.S_STAATUS_TYHISTATUD)))
                )
        #filter(model.Testimiskord.reg_kool_kuni>=d)
        # filter(model.Testimiskord.reg_kool_kuni>=d)
        # ei kontrolli reg lõpu kuupäeva, sest 
        # REKK võib registreerida sooritajaid ka peale seda

    def _create(self):
        """Testide lisamine valitud testide sekka
        """
        c = self.c
        kasutaja = c.kasutaja
        c.testiliik = self.request.params.get('testiliik')
        # lisati valikusse yks test
        for kord_id in self.request.params.getall('valik_id'):
            kord = model.Testimiskord.get(kord_id)

            lang = self.request.params.get('lang_%s' % kord_id)
            piirkond_id = self.request.params.get('piirkond_id_%s' % kord_id)
            piirkond_id = piirkond_id and int(piirkond_id) or None
            kursus = self.request.params.get('kursus_%s' % kord_id)

            sooritaja = registreeri(self, kasutaja, kord, lang, piirkond_id, kursus)
            if sooritaja:
                sooritaja.reg_markus = self.request.params.get('reg_markus_%s' % kord_id)           
                sooritaja.soovib_konsultatsiooni = bool(self.request.params.get('soovib_konsultatsiooni_%s' % kord_id))
                sooritaja.kursus_kood = kursus

        if self.has_errors():
            model.Session.rollback()
            q = self._order(self._search(self._query()))
            c.items = self._paginate(q)
            html = self.form.render(self._INDEX_TEMPLATE,
                                    extra_info=self.response_dict)
            return Response(html)
        else:
            model.Session.commit()
            self.success()
            return HTTPFound(location=self.url('regamine_avaldus_testid',
                                               id=kasutaja.id,
                                               testiliik=c.testiliik))

    def __before__(self):
        self.c.kasutaja = model.Kasutaja.get(self.request.matchdict.get('kasutaja_id'))

def registreeri(handler, kasutaja, kord, lang, piirkond_id, kursus):
    "Sooritaja registreerimine testimiskorrale"
    test_id = kord.test_id
    test = kord.test
    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        err = regpiirang.reg_r_lisaeksam(handler, kasutaja.id, test, kord)
        if err:
            handler.error(err)
            return 

    opilane = kasutaja.opilane

    if test.aine_kood == const.AINE_ET2:
        warn = regpiirang.reg_et2(handler, kasutaja, test, opilane)
        if warn:
            handler.notice(warn)
            
    varemlopetanu = not opilane or opilane.on_lopetanud
    if test.testiliik_kood in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV) and varemlopetanu:
        if not piirkond_id:
            err = _("Palun valida piirkond")
            handler.error(err)
            return

    esitaja_kasutaja_id = handler.c.user.id
    esitaja_koht_id = const.KOHT_EKK
    added, sooritaja = model.Sooritaja.registreeri(kasutaja, 
                                                   test_id, 
                                                   kord, 
                                                   lang, 
                                                   piirkond_id, 
                                                   const.REGVIIS_EKK,
                                                   esitaja_kasutaja_id, 
                                                   esitaja_koht_id)
    if not added:
        handler.error(_('Kasutaja on testile "{s}" juba registreeritud').format(s=test.nimi))
    return sooritaja
