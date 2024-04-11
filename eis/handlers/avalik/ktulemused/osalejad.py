from eis.lib.feedbackreport import FeedbackReport
from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class OsalejadController(BaseResourceController):
    "Testi kirjeldus"
    _permission = 'avalikadmin,testiadmin,aineopetaja'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'avalik/ktulemused/osalejad.mako'
    _no_paginate = True
    _actions = 'index'
    
    def _query(self):
        c = self.c
        q = (model.Session.query(model.Sooritaja)
             .filter(model.Sooritaja.testimiskord_id==c.testimiskord.id)
             )
        # oma kooli õpilane või on antud kooli sisseastumistest 
        if c.test.testiliik_kood == const.TESTILIIK_SISSE:
            q = q.filter(model.Sooritaja.kandideerimiskohad.any(
                model.Kandideerimiskoht.koht_id==c.user.koht_id))
        else:
            q = q.filter(model.Sooritaja.kool_koht_id==c.user.koht_id)
        if c.kursus:
            q = q.filter(model.Sooritaja.kursus_kood==c.kursus)
        return q

    def _search_default(self, q):
        return self._search(q)

    def _get_klassid(self, q):
        c = self.c
        
        # oma kooli õpilaste klassid
        q1 = (q.with_entities(model.Sooritaja.klass, model.Sooritaja.paralleel)
              .distinct()
              .filter(model.Sooritaja.kool_koht_id==c.user.koht_id)
              .order_by(model.Sooritaja.klass, model.Sooritaja.paralleel)
              )
        li = []
        for klass, paralleel in q1.all():
            li.append(model.KlassID(klass, paralleel))

        if c.test.testiliik_kood == const.TESTILIIK_SISSE:
            # kas keegi kandideerib minu kooli
            q2 = (q.with_entities(sa.func.count(model.Sooritaja.id))
                  .filter(model.Sooritaja.kandideerimiskohad.any(
                      sa.and_(model.Kandideerimiskoht.koht_id==c.user.koht_id,
                              model.Kandideerimiskoht.automaatne==False)))
                  )
            cnt = q2.scalar()
            if cnt:
                li.append(model.KlassID(model.KlassID.KANDIDAADID, None))
                                 
        return li
            
    def _search(self, q):
        c = self.c
        self._has_valim()
        c.klass, c.paralleel = model.KlassID.parse_id(c.klass_id)

        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item

        lang = c.test.lang
        c.on_tagasiside_opetaja = FeedbackReport.init_opetaja(self, c.test, lang, c.kursus, check=True) or \
                                  FeedbackReport.init_opilane(self, c.test, lang, c.kursus, check=True)

        c.klassidID = self._get_klassid(q)
        if c.test.testiliik_kood == const.TESTILIIK_SISSE:
            # sisseastumiseksamil on eraldi pseudoklass minu kooli kandideerijaile
            if c.klass == model.KlassID.KANDIDAADID:
                q = q.filter(model.Sooritaja.kandideerimiskohad.any(
                    sa.and_(model.Kandideerimiskoht.koht_id==c.user.koht_id,
                            model.Kandideerimiskoht.automaatne==False)))
            elif c.klass:
                q = q.filter(model.Sooritaja.kool_koht_id==c.user.koht_id)
                q = q.filter(model.Sooritaja.klass==c.klass)
        elif c.klass:
            # tavaline test
            q = q.filter(model.Sooritaja.klass==c.klass)

        if c.paralleel:
            q = q.filter(model.Sooritaja.paralleel==c.paralleel)

        if c.xls:
            return self._index_xls(q)
        return q

    def _has_valim(self):
        "Kas testimiskorral on valim? (Vajalik valimi tabi kuvamiseks.)"
        c = self.c
        sis_valim_tk_id, valimid_tk_id, v_avaldet = \
            eis.lib.feedbackreport.FeedbackReport.leia_valimi_testimiskord(c.test.id, c.testimiskord.id)
        c.on_valim = (sis_valim_tk_id or valimid_tk_id) and True or False

    def _prepare_header(self):
        c = self.c
        li = [('sooritaja.eesnimi', _("Eesnimi")),
              ('sooritaja.perenimi', _("Perekonnanimi")),
              ]
        if not c.klass:
            li.append(('sooritaja.klass,sooritaja.paralleel', _("Klass")))
        li.append(('sooritaja.staatus', _("Testi olek")))
        if c.xls:
            if not c.test.pallideta:
                li.append(('sooritaja.pallid', _("Testi max tulemus")))
                if c.test.max_pallid:
                    label = _("Testi tulemus (max {p}p)").format(p=self.h.fstr(c.test.max_pallid, 2))
                else:
                    label = _("Testi tulemus (p)")
                li.append(('sooritaja.pallid', label))
            if not c.test.protsendita:
                li.append(('sooritaja.tulemus_protsent', _("Testi tulemus (%)")))
        else:
            if not c.test.protsendita:
                li.append(('sooritaja.tulemus_protsent', _("Testi tulemus")))
        c.on_tase = len(c.test.testitasemed) > 0
        if c.on_tase:
            li.append(('sooritaja.keeletase_kood', _("Keeleoskuse tase")))
        for osa in c.testiosad:
            if len(c.testiosad) > 1:
                if c.xls:
                    if not c.test.pallideta:
                        buf = osa.nimi + ' (max %sp)' % self.h.fstr(osa.max_pallid)
                        li.append((None, buf))
                    if not c.test.protsendita:
                        buf = osa.nimi + ' (%)'
                        li.append((None, buf))
                else:
                    if not c.test.pallideta:
                        li.append((None, osa.nimi))                        
            if osa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):
                li.append((None, _("Sooritamise aeg")))
            li.append((None, _("Märkus")))
        return li

    def _prepare_item(self, rcd, n=None):
        c = self.c
        li = [rcd.eesnimi,
              rcd.perenimi,
              ]
        if not c.klass:
            if rcd.kool_koht_id == c.user.koht_id:
                li.append(model.KlassID(rcd.klass, rcd.paralleel).name)
            else:
                # sisseastumistestis näeb kool ka teiste koolide õpilasi, kui need kandideerivad siia kooli
                li.append(_("Muu kool"))
        li.append(rcd.staatus_nimi)
        if c.xls:
            if not c.test.pallideta:
                li.append(self.h.fround(rcd.max_pallid, 2))
                li.append(self.h.fround(rcd.pallid, 2))
            if not c.test.protsendita:
                li.append(self.h.fround(rcd.tulemus_protsent, 2))
        else:
            if not c.test.protsendita:
                li.append(rcd.get_tulemus(nl=False, digits=2))
        if c.on_tase:
            li.append(rcd.keeletase_nimi)
        
        q = (model.Session.query(model.Sooritus)
             .filter_by(sooritaja_id=rcd.id)
             )
        sooritused = {tos.testiosa_id: tos for tos in q.all()}
        tos1_id = None
        for osa in c.testiosad:
            tos = sooritused.get(osa.id)
            if tos and osa.seq==1:
                tos1_id = tos.id
            if len(c.testiosad) > 1:
                if c.xls:
                    if not c.test.pallideta:
                        li.append(tos and self.h.fround(tos.pallid, 2))
                    if not c.test.protsendita:
                        li.append(tos and self.h.fround(tos.tulemus_protsent, 2))
                else:
                    if not c.test.pallideta:
                        li.append(tos and tos.get_tulemus(digits=2) or '')
            if osa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):
                li.append(tos and self.h.strh_from_time(tos.ajakulu) or '')
            li.append(tos and tos.markus or '')
        if c.csv or c.xls:
            return li
        else:
            if rcd.staatus == const.S_STAATUS_TEHTUD and \
              model.Sooritaja.has_permission_ts(rcd.id, c.testimiskord):
                # kasutajal on õigus näha sooritaja individuaalset tagasisidet
                url = self.url('ktulemused_opetajatulemus', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=rcd.kursus_kood or '', id=rcd.id)
            else:
                url = None
            return li, url

    def __before__(self):
        c = self.c
        test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(test_id)
        c.testiosad = list(c.test.testiosad)
        testimiskord_id = self.request.matchdict.get('testimiskord_id')
        c.testimiskord = model.Testimiskord.get(testimiskord_id)
        c.kursus = self.request.matchdict.get('kursus') or ''
        c.FeedbackReport = FeedbackReport
        
    def _perm_params(self):
        c = self.c
        if not c.testimiskord.koondtulemus_avaldet:
            return False
        return {'test': c.test}
        
