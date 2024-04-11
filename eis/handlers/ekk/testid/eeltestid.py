from cgi import FieldStorage
import formencode
from eis.forms import validators
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.resultstat import ResultStat

log = logging.getLogger(__name__)

class EeltestidController(BaseResourceController):
    _permission = 'ekk-testid'
    _MODEL = model.Eeltest
    _EDIT_TEMPLATE = 'ekk/testid/eeltestid.mako'
    _INDEX_TEMPLATE = 'ekk/testid/eeltestid.mako'
    _ITEM_FORM = forms.ekk.testid.EeltestForm
    _get_is_readonly = False

    def _show(self, item):
        self.c.korraldaja_id = self.request.params.get('korraldaja_id')
        if self.c.avalik_test:
            self.c.sooritajad = _get_sooritajad(self.c.avalik_test, self.c.korraldaja_id)
        else:
            self.c.avalik_test = NewItem(avalik_alates=datetime.now())
       
    def _create(self, **kw):
        komplektid_id = self.request.params.getall('komplekt_id')
        if not komplektid_id:
            raise ValidationError(self, {}, _("Palun valida eeltestimisele minevad ülesandekomplektid"))

        test = self.c.test
        test_id = test.id # flush?
        
        # loome eeltestimiseks loodava testi kirje
        model.Session.autoflush = False # integrity errori pärast
        avalik_test = model.EntityHelper.copy(test)
        tts = test.testitagasiside
        if tts:
            cp_tts = tts.copy(ignore=['test_id'])
            avalik_test.testitagasiside = cp_tts
        avalik_test.staatus = const.T_STAATUS_KINNITATUD
        avalik_test.avaldamistase = const.AVALIK_MAARATUD
        avalik_test.salastatud = const.SALASTATUD_POLE

        # valitud komplektid, mis antakse eeltestimisele
        komplektid = [model.Komplekt.get(k_id) for k_id in komplektid_id]
        testiosad = list(test.testiosad)
        for osa in testiosad:
            osa_komplektid = []
            for komplekt in komplektid:
                if komplekt.komplektivalik.testiosa_id == osa.id:
                    osa_komplektid.append(komplekt)
            if osa_komplektid:
                # kui mõni valitud komplekt on selles testiosas
                cp_testiosa = osa.copy(avalik_test, osa_komplektid)
                avalik_test.testiosad.append(cp_testiosa)
                # lubame eeltestis yhtainust osa,
                # sest vastuste statistika PDF on yksainus fail
                break
        if len(testiosad) == 1:
            # tagasisidevorm kopeeritakse ainult siis, kui kõik testiosad kopeeriti
            # ES-2616
            for tv in test.tagasisidevormid:
                cp_tv = tv.copy(ignore=['test_id'])
                avalik_test.tagasisidevormid.append(cp_tv)
            # kopeerime kõik tagasisidefailid
            for tf in test.tagasisidefailid:
                cp_tf = tf.copy(ignore=['test_id'], test=avalik_test)

        model.Session.autoflush = True # integrity errori pärast        
        model.Session.flush()
        # loome eeltesti - vahekirje vana testi komplekti ja eeltestimiseks loodava testi vahel
        eeltest = model.Eeltest(algne_test=test, avalik_test_id=avalik_test.id)
        for komplekt in komplektid:
            eeltest.komplektid.append(komplekt)
        avalik_test.eeltest = eeltest

        model.Session.flush()
        avalik_test.logi(_("Loomine koopiana"),
                         _("Test") + ' %s' % self.c.test.id, 
                         None, 
                         const.LOG_LEVEL_GRANT)

        # jooksev kasutaja saab eeltesti koostajaks
        avalik_test.add_testiisik(const.GRUPP_T_KOOSTAJA)            
        self.c.test.logi(_("Eeltest avalikus vaates"),
                         _("Avalik test {id}").format(id=avalik_test.id),
                         None,
                         const.LOG_LEVEL_GRANT)
        self._update(eeltest)
        return eeltest

    def _update(self, item):
        avalik_test = item.avalik_test
        tk = avalik_test.give_testimiskord()
        tk.copy_lang(avalik_test)
        tk.tahis = 'EELTEST'
        tk.reg_kool_eis = True
        tk.give_toimumisajad(komplektid=True)
        for ta in tk.toimumisajad:
            ta.jatk_voimalik = True
            ta.on_arvuti_reg = False
        item.from_form(self.form.data, 'e_')
        avalik_test.from_form(self.form.data, 't_')
        model.Session.commit()

    def _delete_korraldaja(self, id):
        isik_id = self.request.params.get('isik_id')
        isik = model.Testiisik.get(isik_id)
        if isik and isik.test_id == self.c.avalik_test.id and isik.kasutajagrupp == self.c.korraldaja_grupp:
            sooritajad = _get_sooritajad(self.c.avalik_test, isik.kasutaja_id)
            if len(sooritajad):
                self.error(_("Korraldajat ei saa eemaldada, kuna ta on juba registreerinud sooritajaid"))
            else:
                self.c.avalik_test.logi(_("Isiku eemaldamine"),
                                        '%s\n%s\n%s' % (isik.kasutajagrupp.nimi,
                                                        isik.kasutaja.nimi,
                                                        isik.kasutaja.isikukood),
                                        None,
                                        const.LOG_LEVEL_GRANT)
                isik.delete()
                model.Session.commit()
                self.success(_("Andmed on kustutatud"))
        return self._redirect('edit', id)

    def _update_korraldaja(self, id):            
        """Isiku lisamine korraldajaks
        """
        params = self.request.params
        kk_id = [(k_id, None) for k_id in params.getall('oigus')]
        self._lisa_korraldajad(kk_id, params)
        return self._redirect('show', id)
    
    def _update_file(self, id):
        """Isikute lisamine korraldajaks CSV-faili kaudu
        """
        err = None
        kk_id = []
        f = self.request.params.get('ik_fail')
        if not isinstance(f, FieldStorage):
            err = _("Palun sisestada fail")
        else:
            # value on FieldStorage objekt
            value = f.value
            for ind, line in enumerate(value.splitlines()):
                line = utils.guess_decode(line).strip()
                if line:
                    row = line.split(',')
                    if row:
                        userid = row[0]
                        if userid:
                            usp = eis.forms.validators.IsikukoodP(userid)
                            kk_id.append((None, usp.isikukood))
        if not err and not kk_id:
            err = _("Fail on tühi")
        if err:
            self.error(err)
        else:
            self._lisa_korraldajad(kk_id)
        return self._redirect('show', id)

    def _lisa_korraldajad(self, kk_id, params=None):
        test = self.c.test

        not_added = []
        added = False
        for k_id, ik in kk_id:
            if k_id:
                kasutaja = model.Kasutaja.get(k_id)
            elif ik:
                kasutaja = model.Kasutaja.get_by_ik(ik)
                if not kasutaja and self.request.is_ext():
                    kasutaja = xtee.set_rr_pohiandmed(self, None, ik)
                    model.Session.flush()
            if kasutaja:
                isik = self.c.avalik_test._on_testiisik(kasutaja.id, self.c.korraldaja_grupp.id)
                if isik:
                    not_added.append(kasutaja.nimi)
                else:
                    added = True
                    isik = model.Testiisik(test=self.c.avalik_test,
                                           kasutaja=kasutaja,
                                           kasutajagrupp=self.c.korraldaja_grupp,
                                           kehtib_alates=self.c.avalik_test.avalik_alates or const.MIN_DATE,
                                           kehtib_kuni=self.c.avalik_test.avalik_kuni or const.MAX_DATE)
                    self.c.avalik_test.testiisikud.append(isik)

                    self.c.avalik_test.logi(_("Korraldaja lisamine"),
                                            None,
                                            '%s\n%s' % (kasutaja.nimi, kasutaja.isikukood),
                                            const.LOG_LEVEL_GRANT)
                    
                    if not kasutaja.epost and params:
                        # kui kasutajale veel pole sisestatud e-posti aadressi, siis saab sisestada
                        epost = params.get('i%s_epost' % ik)
                        if epost:
                            kasutaja.epost = epost
        if not_added:
            buf = _("Kasutaja {s} on juba korraldajaks lisatud").format(s=', '.join(not_added))
            self.error(buf)
        if added:
            model.Session.commit()
            self.success()

    def _edit_mail(self, id):
        data = {'test_nimi': self.c.avalik_test.nimi,
                'test_id': self.c.avalik_test.id,
                'user_nimi': self.c.user.fullname,
                }
        self.c.subject, self.c.body = self.render_mail('mail/eeltestiteade.mako', data)
        return self.render_to_response('ekk/testid/eeltest.mail.mako')

    def _update_mail(self, id):
        self.form = Form(self.request, schema=forms.ekk.testid.EeltestMailForm)
        if not self.form.validate():
            self.c.dialog_mail = True
            return Response(self.form.render(self._EDIT_TEMPLATE,
                                             extra_info=self.response_dict))

        to = self.form.data['mailto']
        subject = self.form.data['subject']
        body = self.form.data['body']
        body = Mailer.replace_newline(body)
        if not Mailer(self).send(to, subject, body):
            self.success('Teade on saadetud')
        return self._redirect('show', id)

    def _edit_statistika(self, id):
        """Statistika kuvamine
        """
        # arvutame statistika
        resultstat = ResultStat(self, None, False)
        resultstat.calc_test_y(self.c.avalik_test)
        model.Session.commit()

        # pärime statistika kirjed
        q = model.Session.query(model.Ylesanne,
                                model.Valitudylesanne,
                                model.Testiylesanne,
                                model.Ylesandestatistika)

        testiosa = self.c.avalik_test.testiosad[0]

        q = q.join(model.Ylesanne.valitudylesanded).\
            join(model.Valitudylesanne.testiylesanne).\
            filter(model.Testiylesanne.testiosa_id==testiosa.id).\
            outerjoin((model.Ylesandestatistika,
                       sa.and_(
                        model.Ylesandestatistika.valitudylesanne_id==model.Valitudylesanne.id,
                        model.Ylesandestatistika.testiruum_id==None,
                        model.Ylesandestatistika.toimumisaeg_id==None)))

        self.c.items = q.order_by(model.Testiylesanne.seq).all()
        return self.render_to_response('ekk/testid/eeltestid.statistika.mako')

    def _show_markus(self, id):
        """Märkuste vaatamine
        """
        self.c.eeltest = self.c.avalik_test
        return self.render_to_response('ekk/testid/eeltestimarkused.mako')

    def _download(self, id, format=None):
        """Näita faili"""
        item = self.c.item
        if not item or not item.stat_filedata:
            raise NotFound('Kirjet %s ei leitud' % id)        
        fn = 'statistika%s.pdf' % item.avalik_test_id
        return utils.download(item.stat_filedata, fn, const.CONTENT_TYPE_PDF)

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)       
        eeltest_id = self.request.matchdict.get('id')
        self.c.item = eeltest_id and model.Eeltest.get(eeltest_id)
        self.c.avalik_test = self.c.item and self.c.item.avalik_test
        self.c.korraldaja_grupp = model.Kasutajagrupp.get(const.GRUPP_T_KORRALDAJA)
        self.c.get_sooritajad = _get_sooritajad
        BaseResourceController.__before__(self)

    def _perm_params(self):
        if self.c.is_edit and self.c.item and not self.c.avalik_test:
            # eeltest kustutatud
            return False
        return {'obj':self.c.test}

def _get_sooritajad(avalik_test, korraldaja_id):
    q = model.Sooritaja.query.\
        filter(model.Sooritaja.test_id==avalik_test.id)
    if korraldaja_id:
        q = q.join(model.Sooritaja.nimekiri).\
            filter(model.Nimekiri.esitaja_kasutaja_id==int(korraldaja_id))
    #log.debug('GET_SOORITAJAD:%s' % str(q))
    return q.order_by(model.Sooritaja.id).all()
