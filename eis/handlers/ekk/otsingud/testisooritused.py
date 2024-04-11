from eis.lib.baseresource import *
_ = i18n._
from eis.lib.feedbackreport import FeedbackReport
from eis.lib.resultentry import ResultEntry

log = logging.getLogger(__name__)

class TestisooritusedController(BaseResourceController):
    """Soorituste otsimine
    """
    _permission = 'aruanded-testisooritused'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'ekk/otsingud/testisooritused.otsing.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/testisooritused_list.mako'
    _EDIT_TEMPLATE = 'ekk/otsingud/tulemus.mako'
    _DEFAULT_SORT = 'sooritaja.id'
    _SEARCH_FORM = forms.ekk.otsingud.TestisooritusedForm 
    _ignore_default_params = ['csv']
    _actions = 'index,download,show,update,downloadfile'
    
    def _search_default(self, q):
        return None

    def _query_fields(self):
        c = self.c
        testiaeg = sa.func.coalesce(model.Sooritaja.algus, model.Testimiskord.alates).label('testiaeg')
        flds = [model.Sooritaja, 
                testiaeg,
                model.Kasutaja.isikukood, 
                model.Test.nimi,
                model.Test.testiliik_kood,
                model.Testimiskord.tahis,
                model.Testimiskord.alates,
                model.Testimiskord.kuni,
                model.Vaie.id,
                model.Kasutaja.synnikpv,
                model.Koht.nimi]
        if c.soorituskoht:
            # kui on tehtud märge, et kuvada soorituskoht
            self.Soorituskoht1 = sa.orm.aliased(model.Koht, name='soorituskoht')
            flds.append(self.Soorituskoht1.nimi)
        if c.csv:
            self.Esitaja = sa.orm.aliased(model.Kasutaja, name='esitaja')
            flds.append(self.Esitaja.nimi)
            
        # kui test_id on antud, siis lisame veriffiga osade jaoks veerud
        c.map_osa = []
        if c.test_id and c.kord_tahis:
            q1 = (model.Session.query(model.Toimumisaeg.testiosa_id, model.Testiosa.seq)
                 .join(model.Toimumisaeg.testimiskord)
                 .filter(model.Testimiskord.test_id==c.test_id)
                 .filter(model.Testimiskord.tahis==c.kord_tahis)
                 .filter(model.Toimumisaeg.verif==const.VERIF_VERIFF)
                 .join(model.Toimumisaeg.testiosa)
                 .order_by(model.Testiosa.seq))
            for osa_id, osa_seq in q1.all():
                tblalias = 'verifflog%d' % osa_seq
                VerifflogOsa = sa.orm.aliased(model.Verifflog, name=tblalias)
                flds.extend([VerifflogOsa.code,
                             VerifflogOsa.rc,
                             VerifflogOsa.id,
                             VerifflogOsa.session_id])
                c.map_osa.append((osa_id, osa_seq, tblalias, VerifflogOsa))
        return flds

    def _search(self, q1):
        c = self.c
        if not c.test_id and not c.epost and \
                not c.isikukood and not c.eesnimi and not c.perenimi and \
                not c.staatus and not c.vastvorm and not c.sooritus_id and not c.sooritaja_id and not c.kvst_id:
            self.error(_("Palun esita otsinguparameetrid"))
            return

        c.prepare_item = self._prepare_item
        c.prepare_header = self._prepare_header

        flds = self._query_fields()
        q = (model.Session.query(*flds)
             .join(model.Sooritaja.kasutaja)
             .join(model.Sooritaja.test)
             .outerjoin(model.Sooritaja.testimiskord)
             .outerjoin((model.Vaie, sa.and_(model.Vaie.sooritaja_id==model.Sooritaja.id,
                                             model.Vaie.staatus != const.V_STAATUS_ESITAMATA)))
             .outerjoin(model.Sooritaja.kool_koht)
             )
        # jätame välja testi eelvaates sooritamised
        q = q.filter(model.Sooritaja.regviis_kood!=const.REGVIIS_EELVAADE)

        if c.soorituskoht:
            # lisame I testiosa soorituskoha
            Sooritus1 = sa.orm.aliased(model.Sooritus)
            Testiosa1 = sa.orm.aliased(model.Testiosa)
            q = (q.join((Sooritus1, Sooritus1.sooritaja_id==model.Sooritaja.id))
                 .join((Testiosa1, sa.and_(Testiosa1.id==Sooritus1.testiosa_id,
                                           Testiosa1.seq==1)))
                                            .outerjoin(Sooritus1.testikoht)
                 .outerjoin((self.Soorituskoht1, self.Soorituskoht1.id==model.Testikoht.koht_id))
                 )
        if c.csv:
            q = q.outerjoin((self.Esitaja, self.Esitaja.id==model.Sooritaja.esitaja_kasutaja_id))
        if not self.is_devel and not c.user.on_admin:
            q = q.filter(sa.or_(model.Test.testiliik_kood==None,
                                model.Test.testiliik_kood!=const.TESTILIIK_KOOLIPSYH))

        # kui test_id on antud, siis joinime veriffiga osad ja veriffi tulemused
        if c.map_osa:
            for osa_id, osa_seq, tblalias, VerifflogOsa in c.map_osa:
                SooritusOsa = sa.orm.aliased(model.Sooritus, name='osa%d' % osa_seq)
                q = q.outerjoin((SooritusOsa,
                                 sa.and_(SooritusOsa.sooritaja_id==model.Sooritaja.id,
                                         SooritusOsa.testiosa_id==osa_id)))
                q = q.outerjoin((VerifflogOsa, VerifflogOsa.id==SooritusOsa.verifflog_id))

        if c.test_id:
            q = q.filter(model.Sooritaja.test_id==c.test_id)
        if c.kord_tahis:
            q = q.filter(model.Testimiskord.tahis==c.kord_tahis)
        if c.testiliik:
            q = q.filter(model.Test.testiliik_kood==c.testiliik)
        if c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
        if c.epost:
            q = q.filter(model.Kasutaja.epost.ilike(c.epost))
        if c.eesnimi:
            q = q.filter(model.Sooritaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Sooritaja.perenimi.ilike(c.perenimi))
        if c.vercode or c.vercode == model.Verifflog.DEC_NONE:
            f_v = sa.and_(model.Sooritus.sooritaja_id==model.Sooritaja.id,
                          model.Sooritus.verifflog_id==model.Verifflog.id)
            if c.vercode == model.Verifflog.DEC_NONE:
                f_v = sa.and_(f_v, model.Verifflog.code==None)
            elif c.vercode == model.Verifflog.DEC_9001_OK:
                f_v = sa.and_(f_v,
                              model.Verifflog.code==9001,
                              model.Verifflog.rc==True)
            elif c.vercode == model.Verifflog.DEC_9001_NOK:
                f_v = sa.and_(f_v,
                              model.Verifflog.code==9001,
                              model.Verifflog.rc==False)
            else:
                f_v = sa.and_(f_v, model.Verifflog.code==c.vercode)
            q = q.filter(sa.exists().where(f_v))
            
        if c.tahised:
            q = q.filter(model.Sooritaja.sooritused.any(
                model.Sooritus.tahised==c.tahised))
        if c.vastvorm:
            q = q.filter(model.Test.testiosad.any(
                model.Testiosa.vastvorm_kood==c.vastvorm))
        if c.staatus:
            if c.testiosa_id:
                # testiosasoorituse olek
                Sooritus2 = sa.orm.aliased(model.Sooritus)
                q = (q.join((Sooritus2, Sooritus2.sooritaja_id==model.Sooritaja.id))
                     .filter(Sooritus2.testiosa_id==c.testiosa_id)
                     .filter(Sooritus2.staatus==c.staatus))
            else:
                # testisoorituse olek
                q = q.filter(model.Sooritaja.staatus==c.staatus)
        if c.sooritus_id:
            q = q.filter(model.Sooritaja.sooritused.any(
                model.Sooritus.id==c.sooritus_id))
        if c.sooritaja_id:
            q = q.filter(model.Sooritaja.id==c.sooritaja_id)
        if c.valim == '1':
            q = q.filter(model.Sooritaja.valimis==True)
        elif c.valim == '0':
            q = q.filter(model.Sooritaja.valimis==False)
        if c.kvst_id:
            # otsing kvstatistika.id järgi
            kvst = model.Kvstatistika.get(c.kvst_id)
            if not kvst:
                self.error('Ei leitud statistika kirjet')
            else:
                kst = kvst.kysimusestatistika
                q = q.filter(sa.exists().where(sa.and_(
                    model.Sooritus.sooritaja_id==model.Sooritaja.id,
                    model.Sooritus.id==model.Ylesandevastus.sooritus_id,
                    model.Ylesandevastus.id==model.Kysimusevastus.ylesandevastus_id,
                    model.Kysimusevastus.kysimus_id==kst.kysimus_id,
                    model.Kysimusevastus.id==model.Kvsisu.kysimusevastus_id,
                    model.Kvsisu.sisu==kvst.sisu,
                    model.Kvsisu.kood1==kvst.kood1,
                    model.Kvsisu.kood2==kvst.kood2)))
        if c.csv:
            # väljastame CSV
            q = self._order(q)
            data, filename = self._render_csv(q)
            mimetype = const.CONTENT_TYPE_CSV
            return utils.download(data, filename, mimetype)            
        return q

    def _prepare_header(self):
        header = [('test.nimi sooritaja.kursus_kood', _("Test")),
                  ('test.id', _("ID")),
                  (None, _("Testi liik")),
                  (None, _("Testimiskord")),
                  ('kasutaja.isikukood kasutaja.synnikpv', _("Isikukood või sünniaeg")),
                  ('sooritaja.perenimi', _("Nimi")),
                  ('testiaeg', _("Testi aeg")),
                  ('sooritaja.staatus', _("Olek")),
                  ('sooritaja.pallid', _("Tulemus")),
                  ('sooritaja.hinne', _("Hinne")),
                  ('sooritaja.tulemus_aeg', _("Hindamise aeg")),
                  ('koht.nimi', _("Õppeasutus")),                                    
                  ]
        if self.c.soorituskoht:
            header.append(('soorituskoht.nimi', _("Soorituskoht")))
        if self.c.csv:
            header.append(('esitaja.nimi', _("Registreerija")))
        header.append((None, _("Vaidlustus")))

        if self.c.map_osa:
            for osa_id, osa_seq, tblalias, VerifflogOsa in self.c.map_osa:
                header.append((tblalias + '.code', "Veriff (%d)" % osa_seq))
                if self.c.csv:
                    header.append((None, "verification_id"))
        return header

    def _prepare_item(self, rcd, n=None):
        """Päringutulemuste paigutamine väljastamiseks sobivale kujule"""
    
        def millal(alates, kuni):
            buf = ''
            if alates:
                buf = alates.strftime('%d.%m.%Y')
                if kuni and kuni != alates:
                    buf += '–' + kuni.strftime('%d.%m.%Y')
            return buf

        def testiliik_nimi(testiliik_kood):
            request = self.request
            if testiliik_kood:
                return model.Klrida.get_str('TESTILIIK', testiliik_kood)
            else:
                return _("Avaliku vaate test")

        rcd_ix = 11
        sooritaja, algus, kasutaja_ik, test_nimi, testiliik_kood, tk_tahis, tk_alates, tk_kuni, \
                   vaie_id, synnikpv, kool_nimi = rcd[:rcd_ix]
        if sooritaja.kursus_kood:
            test_nimi = '%s (%s)' % (test_nimi, sooritaja.kursus_nimi)

        tulem = ''
        if sooritaja.hindamine_staatus == const.H_STAATUS_HINNATUD \
               and sooritaja.staatus == const.S_STAATUS_TEHTUD:
            tulem = self.h.fstr(sooritaja.pallid)
            if sooritaja.yhisosa_pallid is not None and tulem is not None:
                tulem += _(" (sh ühisosa {s})").format(s=self.h.fstr(sooritaja.yhisosa_pallid))

        algus = self.h.str_from_date(sooritaja.algus) or tk_alates and millal(tk_alates, tk_kuni)
        item = [test_nimi,
                sooritaja.test_id,
                testiliik_nimi(testiliik_kood),
                tk_tahis and '%s-%s' % (sooritaja.test_id, tk_tahis) or '',
                kasutaja_ik or self.h.str_from_date(synnikpv),
                sooritaja.nimi,
                algus,
                sooritaja.staatus_nimi,
                tulem or '',
                self.h.fstr(sooritaja.hinne) or '',
                self.h.str_from_date(sooritaja.tulemus_aeg) or '',
                kool_nimi or '',
                ]
        if self.c.soorituskoht:
            soorituskoht_nimi = rcd[rcd_ix]
            item.append(soorituskoht_nimi or '')
            rcd_ix += 1

        if self.c.csv:
            labiviija = rcd[rcd_ix]
            item.append(labiviija)
            rcd_ix += 1
            
        item.append(self.h.sbool(vaie_id))

        if self.c.map_osa:
            for r in enumerate(self.c.map_osa):
                code = rcd[rcd_ix]
                rc = rcd[rcd_ix+1]
                verifflog_id = rcd[rcd_ix+2]
                verification_id = rcd[rcd_ix+3]
                rcd_ix += 4
                if code:
                    item.append(model.Verifflog.dec_desc(code, rc) or code)
                elif verifflog_id:
                    item.append(_("otsus puudub"))
                else:
                    item.append(None)
                if self.c.csv:
                    item.append(verification_id)
        return item

    def _render_csv(self, q):
        header, items = self._prepare_items(q)
        data = ';'.join([r[1] for r in header]) + '\r\n'
        for item in items:
            item = [s and str(s) or '' for s in item]
            data += ';'.join(item) + '\r\n'

        data = utils.encode_ansi(data)
        filename = 'testisooritused.csv'
        return data, filename

    def _show(self, item):
        c = self.c
        c.test = item.test
        tk = item.testimiskord
        self.set_debug()

        if c.app_ekk:
            fr = FeedbackReport.init_opetaja(self, item.test, item.lang, item.kursus_kood)
            if not fr:
                fr = FeedbackReport.init_opilane(self, item.test, item.lang, item.kursus_kood)
            if fr:
                # genereerida item jaoks
                err, c.tagasiside_html = fr.generate(item)

            c.toovaatajad = self._get_toovaatajad(item.id)

    def _get_toovaatajad(self, sooritaja_id):
        "Leitakse töö vaatamise õigusega isikud"
        q = (model.Session.query(model.Toovaataja.id,
                                 model.Kasutaja.nimi,
                                 model.Toovaataja.kehtib_kuni)
             .filter(model.Toovaataja.sooritaja_id==sooritaja_id)
             .join(model.Toovaataja.kasutaja)
             .order_by(model.Kasutaja.nimi)
             )
        li = [(tv_id, nimi, kuni) for (tv_id, nimi, kuni) in q.all()]
        return li

    def _download(self, id, format=None):
        """Näita faili"""
        sooritus = model.Sooritus.get(id)
        if sooritus:
            item = sooritus.sooritaja
            fr = FeedbackReport.init_opetaja(self, item.test, item.lang, item.kursus_kood)
            if not fr:
                fr = FeedbackReport.init_opilane(self, item.test, item.lang, item.kursus_kood)
            if fr:
                if format == 'xls':
                    filedata = fr.generate_xls(item)
                    return utils.download_xls_file(filedata, 'tagasiside.xlsx')                
                else:
                    filedata = fr.generate_pdf(item)
                    filename = 'tagasiside.pdf'
                    return utils.download(filedata, filename, const.CONTENT_TYPE_PDF)            
        raise NotFound('Faili ei leitud')

    def _downloadfile(self, id, file_id, format):
        "Vastuse fail"
        try:
            rtype, f_id = file_id.split('-')
        except:
            pass
        else:
            if rtype == 'hvf':
                r = model.Helivastusfail.get(f_id)
                if r:
                    return utils.download_obj(r)
        raise NotFound('Faili ei leitud')
    
    def _get_sub(self):
        sub = super()._get_sub()
        if sub == 'arvuta' and self.c.action == 'show':
            # ainult POST sub
            sub = None
        return sub
    
    def _show_detail(self, id):
        c = self.c
        c.item = model.Sooritaja.get(id)
        c.ExamSaga = ExamSaga
        return self.render_to_response('/avalik/tulemused/tulemus.ylesandevastused.mako')
    
    def _show_yv(self, id):
        """Ylesande vastuste kuvamine arendaja jaoks"""
        params = self.request.params
        c = self.c
        sooritaja = model.Sooritaja.get(id)
        c.ylesandevastus = model.Ylesandevastus.get(params.get('yv_id'))
        if c.ylesandevastus:
            sooritus = c.ylesandevastus.sooritus
            if sooritus.sooritaja_id != int(id):
                c.ylesandevastus = None
            c.vy = c.ylesandevastus.valitudylesanne
            c.ty = c.ylesandevastus.testiylesanne
            c.testiosa = sooritus.testiosa
        return self.render_to_response('/avalik/tulemused/ylesanne.kvastused.mako')
    
    def update(self):
        "Tulemuse üle arvutamine Innove vaates"
        sooritaja_id = int(self.request.matchdict.get('id'))
        sooritus_id = self.request.params.get('sooritus_id')
        if not self.c.app_ekk:
            return self._redirect('show', id=sooritaja_id)
        yv_id = self.request.params.get('ylesandevastus_id')
        sooritaja = model.Sooritaja.get(sooritaja_id)
        tos = sooritus_id and model.Sooritus.get(sooritus_id)
        resultentry = ResultEntry(self, None, sooritaja.test, tos.testiosa)
        resultentry.arvutayle(sooritaja, tos, yv_id)
        model.Session.commit()
        return self._redirect('show', id=sooritaja_id, detail=1)
    
    def _index_osa(self):
        "Testiosade valikvälja täitmine testi ID järgi"
        li = []
        try:
            test_id = int(self.request.params.get('test_id'))
        except:
            pass
        else:
            test = model.Test.get(test_id)
            if test:
                li = test.opt_testiosad
        data = [{'id':a[0],'value':a[1]} for a in li]
        return Response(json_body=data)
        
