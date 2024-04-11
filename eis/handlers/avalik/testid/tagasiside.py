from eis.lib.baseresource import *
from eis.lib.feedbackreport import FeedbackReport
from eis.lib.resultentry import ResultEntry

log = logging.getLogger(__name__)

class TagasisideController(BaseResourceController):

    _permission = 'omanimekirjad'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'avalik/testid/tulemused.tagasiside.mako'
    _LIST_TEMPLATE = 'avalik/testid/tulemused.tagasiside_list.mako'
    _EDIT_TEMPLATE = 'avalik/testid/tulemused.tagasiside_sooritaja.mako' 
    _DEFAULT_SORT = 'sooritaja.eesnimi,sooritaja.perenimi'
    _no_paginate = True
    _get_is_readonly = False
    _ignore_default_params = ['pdf','partial']
    _actions = 'index,show,download,update' # võimalikud tegevused
    
    def _query(self):
        q = model.SessionR.query(model.Sooritaja).join(model.Sooritaja.sooritused)
        return q

    def _search_default(self, q):
        return self._search(q)

    def _filter(self, q, valitud=True):
        q = q.filter(model.Sooritus.testiruum_id==self.c.testiruum.id)
        if valitud:
            sooritajad_id = self.request.params.getall('ja_id')
            if sooritajad_id:
                q = q.filter(model.Sooritus.sooritaja_id.in_(sooritajad_id))
        return q

    def _dflt_lang(self):
        if 'lang' not in self.request.params:
            if len(self.c.test.keeled) > 1:
                # kui keelt pole valitud ja sooritajaid on ainult yhes keeles,
                # siis kasutame vaikimisi sooritajate keelt
                ql = (model.SessionR.query(model.Sooritaja.lang).distinct()
                    .join(model.Sooritaja.sooritused)
                    .filter(model.Sooritus.testiruum_id==self.c.testiruum.id))
                if ql.count() == 1:
                    lang, = ql.first()
                    return lang
        return self.c.lang or self.c.test.lang
    
    def _search(self, q):
        self.c.lang = self._dflt_lang()
        if not self.c.partial:
            self._search_stat(q)
        q = self._filter(q, False)

        self.c.test_keeled = self._get_test_keeled()
        return q

    def _get_test_keeled(self):
        c = self.c
        keeled = c.test.keeled
        if len(keeled) > 1:
            q = (model.SessionR.query(model.Sooritaja.lang).distinct()
                 .join(model.Sooritaja.sooritused)
                 .filter(model.Sooritus.testiruum_id==c.testiruum_id)
                 )
            keeled2 = [r for r, in q.all()]
            if const.LANG_ET in keeled and const.LANG_ET not in keeled2:
                keeled = [const.LANG_ET] + keeled2
            else:
                keeled = keeled2
        return keeled
        
    def _search_stat(self, q):
        c = self.c
        q = self._filter(q)
        c.cnt_tehtud = q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD).count()
        c.cnt_pooleli = q.filter(model.Sooritaja.staatus==const.S_STAATUS_POOLELI).count()
        c.cnt_alustamata = q.filter(model.Sooritaja.staatus.in_((const.S_STAATUS_ALUSTAMATA, const.S_STAATUS_REGATUD))).count()

        q = q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)

        # sooritamise kuupäev
        algus, lopp = (q.with_entities(sa.func.min(model.Sooritaja.algus),
                                       sa.func.max(model.Sooritaja.algus))
                       .first())
        if algus and lopp:
            s_algus = self.h.str_from_date(algus)
            s_lopp = self.h.str_from_date(lopp)
            if s_algus != s_lopp:
                c.millal = '%s-%s' % (s_algus, s_lopp)
            else:
                c.millal = s_algus

        # keskmine ajakulu
        q = q.with_entities(sa.func.avg(model.Sooritus.ajakulu))
        avg_ajakulu = q.scalar()
        if avg_ajakulu:
            c.avg_ajakulu = int(round(float(avg_ajakulu) / 60.))

        self._gen_grupp()

    def _gen_grupp(self, pdf=False):
        # bugzilla 624 tagasiside tabel
        c = self.c
        fr = FeedbackReport.init_osalejatetulemused(self, c.test, c.lang, c.kursus)
        if fr:
            eeltest = c.test.eeltest
            if eeltest and not eeltest.tagasiside_koolile:
                # eeltesti testimiskord, kus korraldaja ei tohi tagasisidet näha
                return
            sooritajad_id = self.request.params.getall('ja_id')
            if pdf:
                filedata = fr.generate_pdf(None,
                                           testiruum_id=c.testiruum.id,
                                           nimekiri_id=c.testiruum.nimekiri_id,
                                           sooritajad_id=sooritajad_id)
                return filedata
            else:
                err, c.tagasiside_html = fr.generate(None,
                                                     testiruum_id=c.testiruum.id,
                                                     nimekiri_id=c.testiruum.nimekiri_id,
                                                     sooritajad_id=sooritajad_id)

    def _show(self, item, format=None):
        c = self.c
        c.sooritaja = item
        c.lang = self.params_lang()
        c.download_by_sooritaja = True
        if item.staatus == const.S_STAATUS_TEHTUD and \
               item.nimekiri_id == c.nimekiri.id and \
               item.hindamine_staatus == const.H_STAATUS_HINNATUD:
            test = item.test
            eeltest = test.eeltest
            if eeltest and not eeltest.tagasiside_koolile:
                # eeltesti testimiskord, kus korraldaja ei tohi tagasisidet näha
                return
            fr = FeedbackReport.init_opetaja(self, test, c.lang, item.kursus_kood)
            if not fr and not test.opetajale_peidus:
                fr = FeedbackReport.init_opilane(self, test, c.lang, item.kursus_kood)
            if fr:
                if format == 'pdf':
                    filedata = fr.generate_pdf(item)
                    if filedata:
                        return utils.download(filedata, 'tagasiside.pdf', const.CONTENT_TYPE_PDF)
                elif format == 'xls':
                    c.is_xls = True
                    filedata = fr.generate_xls(item)
                    if filedata:
                        return utils.download(filedata, 'tagasiside.xlsx', const.CONTENT_TYPE_XLS)
                else:
                    err, c.tagasiside_html = fr.generate(item)                

    def _download(self, id, format=None):
        """Näita faili"""        
        if id == '0':
            # grupi tagasiside
            self.c.lang = self.params_lang() or self._dflt_lang()
            filedata = self._gen_grupp(True)
            filename = f'tagasiside.pdf'
            return utils.download(filedata, filename, const.CONTENT_TYPE_PDF)
        else:
            try:
                id = int(id)
            except:
                return utils.download(b'URL', 'error.txt', const.CONTENT_TYPE_TXT)
            item = model.Sooritaja.get(id)
            res = self._show(item, format)
            return res

    def update(self):
        "Tulemuse üle arvutamine"
        sooritaja_id = int(self.request.matchdict.get('id'))
        sooritus_id = self.request.params.get('sooritus_id')
        sooritaja = model.Sooritaja.get(sooritaja_id)
        tos = sooritus_id and model.Sooritus.get(sooritus_id)
        resultentry = ResultEntry(self, None, self.c.test, tos.testiosa)
        resultentry.arvutayle(sooritaja, tos, None)
        model.Session.commit()
        return self._redirect('show', id=sooritaja_id)
        
    def __before__(self):
        self.c.testiruum_id = self.request.matchdict.get('testiruum_id')
        self.c.testiruum = model.Testiruum.get(self.c.testiruum_id)
        self.c.nimekiri = self.c.testiruum.nimekiri
        self.c.testiosa = self.c.testiruum.testikoht.testiosa
        self.c.test = self.c.testiosa.test
        self.c.test_id = self.request.matchdict.get('test_id')

    def _perm_params(self):
        nimekiri = self.c.testiruum.nimekiri
        if not nimekiri:
            return False
        return {'obj':nimekiri}
