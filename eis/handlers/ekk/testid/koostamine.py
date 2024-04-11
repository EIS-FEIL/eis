# -*- coding: utf-8 -*- 
import pickle
import urllib.request, urllib.parse, urllib.error

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class KoostamineController(BaseResourceController):
    """Testi koostamise parameetrid
    """
    _permission = 'ekk-testid'
    _MODEL = model.Test
    _EDIT_TEMPLATE = 'ekk/testid/koostamine.mako'

    def _edit(self, item):
        # kuvame märkuste logi
        q = (model.Session.query(model.Testilogi)
             .filter(model.Testilogi.test_id==self.c.test.id)
             .filter(model.Testilogi.tyyp==model.Testilogi.TESTILOGI_TYYP_OLEK)
             .filter(model.Testilogi.uued_andmed!=None)
             .order_by(sa.desc(model.Testilogi.id))
             )
        self.c.testilogid = [r for r in q.all()]

        if self.c.test.testiliik_kood == const.TESTILIIK_TKY:
            tky = self.c.test.opilase_taustakysitlus
            if tky:
                test2 = tky.opetaja_test
                if test2.avaldamistase != self.c.test.avaldamistase \
                  or test2.staatus != self.c.test.staatus:                
                    self.error(_("Seotud testi {id} olek erineb").format(id=test2.id))
            tky = self.c.test.opetaja_taustakysitlus
            if tky:
                test2 = tky.opilase_test
                if test2.avaldamistase != self.c.test.avaldamistase \
                  or test2.staatus != self.c.test.staatus:
                    self.error(_("Seotud testi {id} olek erineb").format(id=test2.id))
        
    def _edit_olek(self, id):
        self.c.item = model.Test.get(id)
        return self.render_to_response('ekk/testid/koostamine.olek.mako')

    def _edit_secret(self, id):
        """Salasta
        """
        self.c.item = self.c.test
        self.c.sub = 'secret'
        return self.render_to_response('ekk/testid/koostamine.sala.mako')

    def _edit_nosecret(self, id):
        """Salasta
        """
        self.c.item = self.c.test
        self.c.sub = 'nosecret'
        return self.render_to_response('ekk/testid/koostamine.sala.mako')

    def _edit_decrypt(self, id):
        """Kasutaja vajutas nuppu "Krüpti lahti" põhiaknas.
        Kuvame dialoogiakna krüptitud faili alla laadimiseks
        ja lahti krüptitud andmete üles laadimiseks.
        """
        self.c.item = self.c.test
        self.c.sub = 'decrypt'
        return self.render_to_response('ekk/testid/koostamine.sala.mako')

    def _edit_mail(self, id):
        self.c.item = self.c.test
        data = {'test_nimi': self.c.test.nimi,
                'test_id': self.c.test.id,
                'user_nimi': self.c.user.fullname,
                }
        self.c.subject, self.c.body = self.render_mail('mail/testi.koostajale.mako', data)
        return self.render_to_response('ekk/testid/koostamine.mail.mako')
            
    def _update_olek(self, id):
        self.form = Form(self.request, schema=forms.ekk.testid.KoostamineOlekForm)
        if not self.form.validate():
            self.c.item = self.c.test
            return Response(self.form.render('ekk/testid/koostamine.olek.mako',
                                             extra_info=self.response_dict))

        rc = True
        test = self.c.test
        staatus = self.form.data['staatus']
        avaldamistase = self.form.data['avaldamistase']
        avalik_alates = self.form.data['t_avalik_alates']
        avalik_kuni = self.form.data['t_avalik_kuni']
        markus = self.form.data['markus']
        
        rc, msg = set_test_staatus(self, test, staatus, avaldamistase, markus, avalik_alates, avalik_kuni)
        if rc:
            model.Session.commit()
            self.success(_("Testi olek on muudetud"))
            if msg:
                self.notice(msg)
        else:
            self.error(msg)
        return self._redirect('edit', id)

    def _update_secret(self, id):
        """Salastamine
        """
        test = self.c.test
        alg_salastatud = test.salastatud
        rc = True
        message = ''
        if self.request.params.get('secret1'):
            salastatud = const.SALASTATUD_SOORITATAV
        else:
            salastatud = const.SALASTATUD_LOOGILINE
        if test.salastatud == salastatud:
            self.error(_("Salastatust ei muudetud"))
            rc = False
        else:
            markus = self.request.params.get('markus')
            rc, err = set_test_secret(self, test, salastatud, markus)
            if rc:
                model.Session.commit()
                self.notice(_("Test on salastatud"))
            else:
                self.error(err)
        return self._redirect('edit', id)

    def _update_nosecret(self, id):
        test = self.c.test
        if test.salastatud in (const.SALASTATUD_LOOGILINE, const.SALASTATUD_SOORITATAV):
            markus = self.request.params.get('markus')
            salastatud = const.SALASTATUD_POLE
            rc, err = set_test_secret(self, test, salastatud, markus)
            if rc:
                model.Session.commit()
                self.success(_("Test pole enam salastatud"))
            else:
                self.error(err)
                
        return self._redirect('edit', id)

    def download(self):
        """Krüptitud andmete alla laadimine lahti krüptimiseks kasutaja arvutis.
        """
        id = self.request.matchdict.get('id')
        test = self._MODEL.get(id)
        if test.salatest:
            data = test.salatest.parool
            filename = 'test_%s.cdoc' % test.id
            mimetype = const.CONTENT_TYPE_CDOC
            #mimetype = 'application/octet-stream'
            return utils.download(data.encode('utf-8'), filename, mimetype)
        else:
            raise NotFound(_("Krüptitud andmeid pole"))                    
   
    def _update_mail(self, id):
        self.form = Form(self.request, schema=forms.ekk.testid.KoostamineMailForm)
        if not self.form.validate():
            self.c.dialog_mail = True
            return Response(self.form.render(self._EDIT_TEMPLATE,
                                             extra_info=self.response_dict))

        kasutajad = []
        for k_id in self.form.data['k_id']:
            k = model.Kasutaja.get(k_id)
            if k.epost:
                kasutajad.append((k.id, k.epost))
        to = [r[1] for r in kasutajad]
            
        subject = self.form.data['subject']
        body = self.form.data['body']

        body = Mailer.replace_newline(body)
        if not Mailer(self).send(to, subject, body):
            self.success('Teade on saadetud')
            kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                              sisu=body,
                              teema=subject,
                              teatekanal=const.TEATEKANAL_EPOST)
            for k_id, epost in kasutajad:
                model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
            model.Session.commit()
        return self._redirect('show', id)

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('id')
        self.c.test = model.Test.get(test_id)
        
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}

def set_test_staatus(handler, test, staatus, avaldamistase, markus, avalik_alates, avalik_kuni):
    "Testi oleku ja avaldamistaseme muutmine"
    msg = None
    if staatus == const.T_STAATUS_KOOSTAMISEL:
        for to in test.testiosad:
            for kvalik in to.komplektivalikud:
                for k in kvalik.komplektid:
                    if k.lukus and k.lukus > const.LUKUS_KINNITATUD:
                        msg = _("Testi {id} struktuuri ei tohi muuta, kuna mõni ülesandekomplekt on juba lukustatud").format(id=test.id)
                        break
            if msg:
                break
        if msg and not handler.c.user.has_permission('lukustlahti', const.BT_UPDATE):
            # ainult admin võib muuta sooritatud testi oleku koostamisel olekuks
            return False, msg

    if not staatus:
        staatus = test.staatus

    if test.diagnoosiv and staatus in (const.T_STAATUS_KOOSTAMISEL,
                                       const.T_STAATUS_KINNITATUD):
        # diagnoosiva testi korral muudame ka komplekti olekut
        for osa in test.testiosad:
            for kv in osa.komplektivalikud:
                for k in kv.komplektid:
                    if staatus == const.T_STAATUS_KOOSTAMISEL:
                        k.staatus = const.K_STAATUS_KOOSTAMISEL
                    elif staatus == const.T_STAATUS_KINNITATUD:
                        k.staatus = const.K_STAATUS_KINNITATUD
        
    if avaldamistase in (const.AVALIK_SOORITAJAD, const.AVALIK_OPETAJAD, const.AVALIK_MAARATUD) and \
           test.avaldamistase != avaldamistase:            
        if staatus == const.T_STAATUS_KOOSTAMISEL:
            msg = _("Testi ei saa avalikus vaates kasutamiseks anda, kui see on koostamisel")
            return False, msg
        # kontroll, et igas komplektivalikus on olemas vähemalt 1 kinnitatud komplekt
        for osa in test.testiosad:
            komplektivalikud = list(osa.komplektivalikud)
            if not komplektivalikud:
                msg = _("Testi ei saa avalikus vaates kasutamiseks anda, kui ülesanded puuduvad")
                return False, msg
            for kv in komplektivalikud:
                found = False
                for k in kv.komplektid:
                    if k.staatus == const.K_STAATUS_KINNITATUD:
                        found = True
                        break
                if not found:
                    msg = _("Testi ei saa avalikus vaates kasutamiseks anda, kui puudub kinnitatud ülesandekomplekt")
                    return False, msg
                
    if avaldamistase is None:
        avaldamistase = test.avaldamistase

    if avaldamistase not in (const.AVALIK_SOORITAJAD, const.AVALIK_OPETAJAD, const.AVALIK_MAARATUD):
        test.avalik_alates = test.avalik_kuni = None
    elif avalik_alates != 0 and avalik_kuni != 0:
        # kui ei tulda hulgi muutmiselt ja on avalik avaldamistase
        test.avalik_alates = avalik_alates
        test.avalik_kuni = avalik_kuni
    if avalik_alates or avalik_kuni:
        ajavahemik = '%s-%s' % (handler.h.str_from_date(avalik_alates) or '',
                                handler.h.str_from_date(avalik_kuni) or '')
    else:
        ajavahemik = ''

    test.logi(_("Oleku muutmine"),
              '%s %s' % (test.staatus_nimi, test.avaldamistase_nimi),
              '%s %s %s\n%s' % (model.Klrida.get_str('T_STAATUS', staatus) or '',
                                handler.c.opt.AVALIK.get(avaldamistase),
                                ajavahemik,
                                markus or ''),
              const.LOG_LEVEL_GRANT,
              model.Testilogi.TESTILOGI_TYYP_OLEK)
    test.staatus = staatus
    test.avaldamistase = avaldamistase
    return True, msg

def set_test_secret(handler, test, salastatud, markus):
    rc = False
    if salastatud == const.SALASTATUD_POLE:
        # salastuse maha võtmine
        test.set_salastatud(const.SALASTATUD_POLE)
        rc, err = _set_test_secret_yl(test, salastatud)
        liik = _("Salastuse muutmine")
    else:
        # salastamine
        rc, err = _set_test_secret_yl(test, salastatud)        
        liik = _("Salastamine")
        if rc:
            test.set_salastatud(salastatud)
    if rc:
        test.logi(liik,
                  test.salastatud_nimi(),
                  test.salastatud_nimi(salastatud) + \
                  '\n' + (markus or ''),
                  const.LOG_LEVEL_GRANT,
                  model.Testilogi.TESTILOGI_TYYP_OLEK)                      
    return rc, err

def _set_test_secret_yl(test, salastatud):
    """Testis olevate ülesannete salastatuse seadmine

    salastatud == const.SALASTATUD_POLE:
    Kui soovime salastatuse lõpetada, siis peab
    ülesannete salastatus olema loogiline või puuduma,
    sest krüptimisest siin ei vabastata.

    salastatud == const.SALASTATUD_LOOGILINE:
    Kui soovime salastada loogiliselt, siis peab
    ülesannete salastatus puuduma või olema loogiline.

    Krüptimise salastatust siin ei seata, seda seab test.pack_crypt()
    """
    for to in test.testiosad:
        for kvalik in to.komplektivalikud:
            for k in kvalik.komplektid:
                for vy in k.valitudylesanded:
                    if vy.ylesanne:
                        ylesanne = vy.ylesanne

                        if ylesanne.is_encrypted:
                            msg = _("Ülesanne {id} on krüptitud.").format(id=ylesanne.id) + ' \n' + \
                                  _("Jätkamiseks tuleb see ülesanne esmalt lahti krüptida.")
                            return False, msg

                        ylesanne.logi(_("Testi {id} salastamine").format(id=test.id),
                                      ylesanne.salastatud_nimi(),
                                      ylesanne.salastatud_nimi(salastatud),
                                      const.LOG_LEVEL_GRANT)
                        ylesanne.set_salastatud(salastatud)
    return True, None
