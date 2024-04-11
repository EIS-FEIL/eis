from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.meeldetuletus import MeeldetuletusDoc
import eis.handlers.ekk.otsingud.kohateated as kt
import eis.lib.regpiirang as regpiirang

log = logging.getLogger(__name__)

class SooritajadController(BaseResourceController):
    """Eksamikeskuse poolt sooritajate määramine testile.
    """
    _permission = 'regamine'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'ekk/regamine/otsing.mako'
    _LIST_TEMPLATE = 'ekk/regamine/otsing_list.mako'
    _SHOW_TEMPLATE = 'ekk/regamine/regi.mako'
    _EDIT_TEMPLATE = 'ekk/regamine/regi_edit.mako'
    _DEFAULT_SORT = '-sooritaja.id'
    _SEARCH_FORM = forms.ekk.regamine.OtsingForm
    _get_is_readonly = False

    @property
    def _ITEM_FORM(self):
        item = self.c.sooritaja_id and model.Sooritaja.get(self.c.sooritaja_id)
        if item and item.testimiskord_id:
            return forms.ekk.regamine.RegavaldusForm
        else:
            return forms.ekk.regamine.RegavaldusAvalikForm

    def _search(self, q):
        if self.c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))                            
        if self.c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(self.c.eesnimi))
        if self.c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(self.c.perenimi))

        if self.c.test_id:
            q = q.filter(model.Testimiskord.test_id==self.c.test_id)
        if self.c.testimiskord_id:
            q = q.filter(model.Sooritaja.testimiskord_id==self.c.testimiskord_id)
        if self.c.sessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==self.c.sessioon_id)
        if self.c.testiliik:
            q = q.filter(model.Test.testiliik_kood==self.c.testiliik)
        else:
            liigid = self.c.user.get_testiliigid(self._permission)
            if None not in liigid:
                q = q.filter(model.Test.testiliik_kood.in_(liigid))
        if self.c.kool_id:
            q = q.filter(model.Sooritaja.esitaja_koht_id==self.c.kool_id)
        if self.c.reg_alates:
            q = q.filter(model.Sooritaja.reg_aeg>=self.c.reg_alates)
        if self.c.reg_kuni:
            q = q.filter(model.Sooritaja.reg_aeg<=self.c.reg_kuni)

        if self.c.regamata:
            q = q.filter(model.Sooritaja.staatus==const.S_STAATUS_REGAMATA)
        if self.c.tasumata:
            q = q.filter(model.Sooritaja.tasutud==False)
        if self.c.tyhistatud:
            q = q.filter(model.Sooritaja.staatus==const.S_STAATUS_TYHISTATUD)
        else:
            dt = date.today()
            oppeaasta = dt.month < 9 and dt.year or dt.year + 1            
            q = q.filter(sa.or_(model.Sooritaja.staatus != const.S_STAATUS_TYHISTATUD,
                                model.Testimiskord.testsessioon.has(
                                    model.Testsessioon.oppeaasta >= oppeaasta))
                         )
        if self.c.erivajadused:
            q = q.filter(model.Sooritaja.on_erivajadused==True)
        if self.c.lisatingimused:
            q = q.filter(model.Kasutaja.lisatingimused!=None)            
            q = q.filter(model.Kasutaja.lisatingimused!='')            

        # nimistu laadimiselt tullakse
        if self.c.nimekiri_id:
            q = q.filter(model.Sooritaja.nimekiri_id==int(self.c.nimekiri_id))
        # avalduse sisestamiselt tullakse
        if self.c.kasutaja_id:
            q = q.filter(model.Sooritaja.kasutaja_id==int(self.c.kasutaja_id))

        ained = self.c.user.get_ained(self._permission)
        if None not in ained:
            q = q.filter(model.Test.aine_kood.in_(ained))

        #log.debug(str(q))
        if self.c.xls:
            return self._index_xls(q)        
        return q

    def _search_default(self, q):
        return None

    def _query(self):
        q = (model.Sooritaja.query
             .join(model.Sooritaja.kasutaja)
             .join(model.Sooritaja.testimiskord)
             .join(model.Testimiskord.test)
             .filter(model.Sooritaja.staatus<=const.S_STAATUS_POOLELI)
             .filter(model.Sooritaja.regviis_kood!=const.REGVIIS_EELVAADE)
             )
        return q

    def _update_epost(self, id):
        """Meeldetuletuse saatmine/kuvamine
        """
        item = model.Sooritaja.get(id)
        to = item.kasutaja.epost
        if not to:
            self.error(_("Testisooritaja e-posti aadress pole teada"))
        elif not item.tasu:
            self.error(_("Testisooritajal pole midagi tasuda"))
        elif item.tasutud:
            self.error(_("Testisooritaja on juba tasunud"))
        else:
            self._send_epost(item, to)
                
        return HTTPFound(location=self.url('regamine', id=id))

    def _update_tpost(self, id):
        """Meeldetuletuse saatmine/kuvamine
        """
        item = model.Sooritaja.get(id)
        if not item.tasu:
            self.error(_("Testisooritajal pole midagi tasuda"))
        elif item.tasutud:
            self.error(_("Testisooritaja on juba tasunud"))
        else:
            return self._send_tpost(item)
                
        return HTTPFound(location=self.url('regamine', id=id))

    def _send_epost(self, item, to):
        subject, body = self.render_mail('mail/meeldetuletus.mako', 
                                          {'test_nimi': item.test.nimi,
                                           'isik_nimi': item.kasutaja.nimi, 
                                           'tasu': ('%.2f' % item.tasu).replace('.',','),
                                           'user_nimi': self.c.user.fullname,
                                           })
        body = Mailer.replace_newline(body)
        if not Mailer(self).send(to, subject, body):
            item.meeldetuletusaeg = datetime.now()
            kiri = model.Kiri(saatja_kasutaja_id=self.c.user.id,
                              tyyp=model.Kiri.TYYP_MEELDETULETUS,
                              sisu=body,
                              teema=subject,
                              teatekanal=const.TEATEKANAL_EPOST)
            model.Sooritajakiri(sooritaja=item, kiri=kiri)
            model.Kirjasaaja(kiri=kiri, kasutaja_id=item.kasutaja_id, epost=to)

            log.debug(_("Saadetud kiri aadressile {s}").format(s=to))
            self.success(_("Saadetud kiri aadressile {s}").format(s=to))
            model.Session.commit()
            
    def _send_tpost(self, item):
        doc = MeeldetuletusDoc(item)
        data = doc.generate()
        filename = 'meeldetuletus.pdf'
        mimetype = const.CONTENT_TYPE_PDF

        item.meeldetuletusaeg = datetime.now()
        kiri = model.Kiri(saatja_kasutaja_id=self.c.user.id,
                          tyyp=model.Kiri.TYYP_MEELDETULETUS,
                          filename=filename,
                          filedata=data,
                          teema="Meeldetuletus",
                          teatekanal=const.TEATEKANAL_POST)
        model.Sooritajakiri(sooritaja=item, kiri=kiri)
        model.Kirjasaaja(kiri=kiri, kasutaja_id=item.kasutaja_id)
        model.Session.commit()
        
        return utils.download(data, filename, mimetype)

    def _update(self, item):
        kasutaja = item.kasutaja
        # isikuandmed
        kasutaja.from_form(self.form.data, 'k_')
        # õppimisandmed
        kasutaja.from_form(self.form.data, 'ko_')
        model.Aadress.adr_from_form(kasutaja, self.form.data, 'a_')
        item.from_form(self.form.data, 'f_')
        if not kasutaja.isikukood_ee and item.kodakond_kood:
            kasutaja.kodakond_kood = item.kodakond_kood
        item.eesnimi = kasutaja.eesnimi
        item.perenimi = kasutaja.perenimi

        errors = {}
        if not kasutaja.epost:
            errors['k_epost'] = _("Palun sisestada e-posti aadress")
        if kasutaja.lopetanud_kasitsi and not kasutaja.lopetanud_pohjus:
            errors['ko_lopetanud_pohjus'] = _("Palun märkida põhjus, miks on lõpetamise lubamine käsitsi märgitud")
        if errors:
            raise ValidationError(self, errors)

    def update(self):
        params = self.request.params
        id = self.request.matchdict.get('id')
        item = self._MODEL.get(id)
        
        if params.get('tasutud'):
            if item.tasu:
                item.tasutud = True
                item.kinnita_reg()
            else:
                self.error(_("Test pole tasuline"))

            model.Session.commit()
            self.success()
            return self._redirect('show', id)            
        elif params.get('tyhista'):
            staatus = item.staatus
            if staatus in (const.S_STAATUS_REGATUD, const.S_STAATUS_TASUMATA, const.S_STAATUS_REGAMATA):
                item.logi_pohjus = params.get('pohjus')
                kt.send_tyhteade(self, item.kasutaja, item)
                item.tyhista()
                model.Session.commit()
                self.success()
            else:
                self.error(_("Seda registreeringut ei saa enam tühistada"))
            return self._redirect('show', id)                    
        elif params.get('taasta'):
            if item.staatus == const.S_STAATUS_TYHISTATUD:
                staatus = item.tasutud == False and const.S_STAATUS_TASUMATA or const.S_STAATUS_REGATUD
                for tos in item.sooritused:
                    tos.staatus = staatus

                item.logi_pohjus = params.get('pohjus')
                item.update_staatus()
                model.Session.commit()
                self.success()
            else:
                self.error(_("See taotlus ei ole tühistatud"))
            return self._redirect('show', id)                            
        else:
            return BaseResourceController.update(self)

    def _edit_rr(self, id):
        "Isiku päring Rahvastikuregistrist"
        sooritaja = model.Sooritaja.get(self.c.sooritaja_id)
        kasutaja = sooritaja.kasutaja
        res = xtee.rr_pohiandmed_js(self, kasutaja.isikukood)

        if kasutaja.set_kehtiv_nimi(res.get('eesnimi'), res.get('perenimi')):
            model.Session.commit()

        return Response(json_body=res)

    def _show(self, item):
        self.set_debug()
        return BaseResourceController._show(self, item)

    def _prepare_header(self):
        header = [_("Isikukood"),
                  _("Eesnimi"),
                  _("Perekonnanimi"),
                  _("Aadress"),
                  _("Telefon"),
                  _("E-posti aadress"),
                  _("Õppeasutus"),
                  _("Klass"),
                  _("Õppekeel"),
                  _("Test"),
                  _("Testi sooritamise keel"),
                  _("Kursus"),
                  _("Soorituspiirkond"),
                  _("Märkused"),
                  _("Registreerimise staatus"),
                  _("Sünnikoht (riik)"),
                  _("Sünnikoht"),
                  _("Dokumendi nr"),
                  _("Eesnimi vene keeles"),
                  _("Perekonnanimi vene keeles"),                  
                  _("Rahvus"),
                  ]
        if self.c.lisatingimused:
            header.append(_("Lisatingimused"))
        return header
    
    def _prepare_item(self, rcd, n):
        k = rcd.kasutaja
        #oppimiskoht = ', '.join([r.oppekoht_nimi for r in rcd.oppekohad])
        t = rcd.test
        kool = rcd.kool_koht
        piirkond = rcd.piirkond

        synnikoht_riik = rcd.synnikoht_kodakond_nimi
        synnikoht = rcd.synnikoht
        if not synnikoht_riik and synnikoht:
            # kui synnikoht on kohustuslik,
            # siis riigi kood saab puududa juhul,
            # kui synnikoha tekst on saadud RRist,
            # kus see on kujul: riik, maakond, asula
            li = k.synnikoht.split(',', 1)
            synnikoht_riik = li[0]
            synnikoht = len(li) > 1 and li[1].strip() or None

        item = [k.isikukood,
                rcd.eesnimi,
                rcd.perenimi,
                k.tais_aadress,
                k.telefon,
                k.epost,
                kool and kool.nimi,
                rcd.klass,
                rcd.oppekeel and const.EHIS_LANG_NIMI.get(rcd.oppekeel),
                t.nimi,
                rcd.lang_nimi,
                rcd.kursus_nimi,
                piirkond and piirkond.nimi,
                rcd.reg_markus,
                rcd.staatus_nimi,
                synnikoht_riik,
                synnikoht,
                rcd.doknr,
                rcd.eesnimi_ru,
                rcd.perenimi_ru,
                rcd.rahvus_nimi,
                ]
        if self.c.lisatingimused:
            item.append(k.lisatingimused or '')
        return item

    def _index_xls(self, q, fn='andmed.xlsx'):
        "Loetelu väljastamine Excelis"
        q = self._order(q)
        header, items = self._prepare_items(q)

        # 7 viimast veergu on rv eksamite lisaveerud
        # kui neid ei kasutata, siis eemaldame
        has_value = dict()
        for n in range(7):
            has_value[n] = False
        for item in items:
            for n in range(7):
                value = item[-1-n]
                has_value[n] |= not (value is None or value == '')
        remove = list()
        n1 = 0
        for n in range(7):
            n1 -= 1
            if not has_value[n]:
                remove.append(n1)
                n1 += 1
        if remove:
            for item in items:
                for n1 in remove:
                    del item[n1]
            for n1 in remove:
                del header[n1]

        return utils.download_xls(header, items, fn)

    def _create_kinnitamine(self):
        "Pooleli jäänud registreeringute kinnitamine"
        is_regteade = self.request.params.get('regteade')
        sooritajad_id = self.request.params.getall('j_id')
        cnt_status = cnt = cnt_mail = cnt_nomail = cnt_err = 0
        errors = {}
        warnings = {}
        for sooritaja_id in sooritajad_id:
            rcd = model.Sooritaja.get(sooritaja_id)
            if not rcd or rcd.staatus != const.S_STAATUS_REGAMATA:
                cnt_status += 1
            elif rcd.staatus == const.S_STAATUS_REGAMATA:
                test = rcd.test
                testiliik = test.testiliik_kood
                kasutaja = rcd.kasutaja
                err = warn = None
                if testiliik == const.TESTILIIK_RIIGIEKSAM:
                    err = regpiirang.reg_r_lisaeksam(self,
                                                     rcd.kasutaja_id,
                                                     test,
                                                     rcd.testimiskord,
                                                     rcd.id)
                elif testiliik == const.TESTILIIK_TASE:
                    # mitmele tasemeeksamile ei või korraga regada - hoiatus ES-1078
                    err = regpiirang.reg_te_piirang1(self,
                                                     rcd.kasutaja_id,
                                                     rcd.id,
                                                     app_ekk=True)
                if not err:
                    # Kui tavakirja aadress puudub, siis ei kinnita ja kuvame veateate
                    if not kasutaja.epost:
                        # teate saamise viis on e-post, aga e-posti aadress puudub
                        if not kasutaja.aadress_korras:
                            err = _("Aadress puudub või pole täpne")

                if not warn and test.aine_kood == const.AINE_ET2:
                    warn = regpiirang.reg_et2(self, kasutaja, test, kasutaja.opilane)
                if warn:
                    if warn not in warnings:
                        warnings[warn] = []
                    warnings[warn].append('%s %s %s' % (rcd.eesnimi, rcd.perenimi, kasutaja.isikukood))
                    
                if err:
                    # ei saa registreeringut kinnitada
                    cnt_err += 1
                    if err not in errors:
                        errors[err] = []
                    errors[err].append('%s %s %s' % (rcd.eesnimi, rcd.perenimi, kasutaja.isikukood))
                
                else:
                    # kinnitame registreeringu
                    if not rcd.reg_aeg:
                        rcd.reg_aeg = datetime.now()
                    rcd.set_ehis_data()
                    rcd.kinnita_reg(True)
                    model.Session.commit()
                    cnt += 1
                    
                    if is_regteade:
                        if kt.send_regteade(self, kasutaja, testiliik):
                            cnt_mail += 1
                            model.Session.commit()
                        else:
                            cnt_nomail += 1

        if cnt:
            self.notice(_("Kinnitati {n} registreeringut").format(n=cnt))
        if cnt_mail:
            self.notice(_("Registreerimisteated saadeti {n} sooritajale").format(n=cnt_mail))
        if cnt_nomail:
            self.notice(_("Registreerimisteateid ei saanud saata {n} sooritajale").format(n=cnt_nomail))
        if cnt_status:
            self.notice(_("{n} registreeringut ei olnud enam pooleli").format(n=cnt_status))
        if cnt_err:
            self.error(_("Ei saanud kinnitada {n} registreeringut").format(n=cnt_err))
            for msg in errors:
                buf = msg + '(' + ', '.join(errors[msg]) + ')'
                self.error(buf)

        if warnings:
            for msg in warnings:
                buf = msg + '(' + ', '.join(warnings[msg]) + ')'
                self.notice(buf)                

        return self.render_to_response('ekk/regamine/kinnitamine.mako')
        
    def __before__(self):
        self.c.sooritaja_id = self.request.matchdict.get('id')
