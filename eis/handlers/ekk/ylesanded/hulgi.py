from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
import eis.lib.raw_export as raw_export
_ = i18n._

log = logging.getLogger(__name__)

class HulgiController(BaseResourceController):

    _permission = 'ylesanded'

    _EDIT_TEMPLATE = 'ekk/ylesanded/hulgi.mako' 
    _ITEM_FORM = forms.ekk.ylesanded.HulgiForm

    def new(self):
        if self.request.params.get('export'):
            return self._export(self.c.yl_id)
        else:
            return BaseResourceController.new(self)
   
    def _new_d(self):
        self._edit()
        return self.response_dict

    def edit(self):
        self.c.sub = self._get_sub()
        if self.c.sub:
            id = self.request.matchdict.get('id')
            template = eval('self._edit_t_%s' % self.c.sub)(id)
            return self.render_to_response(template)
        d = self._edit_d()
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _edit_d(self):
        id = self.request.matchdict.get('id')
        self._edit()
        return self.response_dict

    def _edit(self, item=None):
        
        q = model.Session.query(model.Ylesandeisik, model.Kasutaja.nimi).\
            filter(model.Ylesandeisik.ylesanne_id.in_(self.c.yl_id)).\
            join(model.Ylesandeisik.kasutaja).\
            order_by(model.Kasutaja.nimi,model.Kasutaja.id, model.Ylesandeisik.kasutajagrupp_id)
        data = list()
        prev_kasutaja_id = prev_grupp_id = None
        for yisik, nimi in q.all():
            if prev_kasutaja_id != yisik.kasutaja_id or prev_grupp_id != yisik.kasutajagrupp_id:
                prev_row = [yisik.kasutaja_id, yisik.kasutajagrupp_id, nimi, [yisik]]
                data.append(prev_row)
                prev_kasutaja_id = yisik.kasutaja_id
                prev_grupp_id = yisik.kasutajagrupp_id
            else:
                prev_row[3].append(yisik)
                
        self.c.ylesandeisikud = data

    def _edit_t_aine(self, id):
        self.c.sub = 'aine'
        return 'ekk/ylesanded/hulgi.aine.mako'

    def _edit_t_teema(self, id):
        self.c.sub = 'teema'
        return 'ekk/ylesanded/hulgi.aine.mako'

    def _edit_t_opitulemus(self, id):
        self.c.sub = 'opitulemus'
        return 'ekk/ylesanded/hulgi.aine.mako'

    def _edit_t_kogu(self, id):
        return 'ekk/ylesanded/hulgi.kogu.mako'

    def _edit_t_kvaliteet(self, id):
        return 'ekk/ylesanded/hulgi.kvaliteet.mako'

    def _edit_t_disain(self, id):
        return 'ekk/ylesanded/hulgi.disain.mako'

    def _edit_t_tolge(self, id):
        q = (model.Session.query(model.Ylesanne.skeeled)
             .filter(model.Ylesanne.id.in_(self.c.yl_id)))
        # leiame keeled, mis on kõigis ylesannetes olemas ja mida ei saa enam lisada
        keeled = None
        for skeeled, in q.all():
            li = (skeeled or '').split()
            if keeled is None:
                keeled = li
            else:
                keeled = [r for r in keeled if r in li]
        self.c.keeled = keeled
        return 'ekk/ylesanded/hulgi.tolge.mako'

    def _edit_t_olek(self, id):
        return 'ekk/ylesanded/hulgi.olek.mako'

    def _edit_t_autor(self, id):
        return 'ekk/ylesanded/hulgi.autor.mako'

    def _edit_t_aste(self, id):
        return 'ekk/ylesanded/hulgi.aste.mako'

    def _edit_t_testiliik(self, id):
        return 'ekk/ylesanded/hulgi.testiliik.mako'

    def _edit_t_kasutus(self, id):
        return 'ekk/ylesanded/hulgi.kasutus.mako'
    
    def _edit_t_secret(self, id):
        """Salasta
        """
        self.c.sub = 'secret'
        return 'ekk/ylesanded/hulgi.sala.mako'

    def _edit_t_nosecret(self, id):
        """Salasta
        """
        self.c.sub = 'nosecret'
        return 'ekk/ylesanded/hulgi.sala.mako'

    def _edit_t_logitase(self, id):
        return 'ekk/ylesanded/hulgi.logitase.mako'

    def _delete_isik(self, id):
        kasutaja_id = self.request.params.get('kasutaja_id')
        grupp_id = self.request.params.get('grupp_id')
        q = model.Ylesandeisik.query.\
            filter(model.Ylesandeisik.ylesanne_id.in_(self.c.yl_id)).\
            filter(model.Ylesandeisik.kasutajagrupp_id==grupp_id).\
            filter(model.Ylesandeisik.kasutaja_id==kasutaja_id)
        cnt = 0
        for isik in q.all():
            ylesanne = isik.ylesanne
            if self.c.user.has_permission('ylesanderoll', const.BT_UPDATE, ylesanne):
                ylesanne.logi(_("Isiku eemaldamine"),
                              '%s\n%s\n%s' % (isik.kasutajagrupp.nimi,
                                              isik.kasutaja.nimi,
                                              isik.kasutaja.isikukood),
                              None,
                              const.LOG_LEVEL_GRANT)
                isik.delete()
                ylesanne.set_cache_valid()
                cnt += 1
        if cnt:
            model.Session.commit()
            self.success(_("Isik on eemaldatud {n} ülesandest").format(n=cnt))
        return self._redirect('edit', id)

    def update(self):
        id = self.request.matchdict.get('id')
        self.c.sub = self._get_sub()
        err = False
        self.form = Form(self.request, schema=self._ITEM_FORM)
        if self.form.validate():
            try:
                return eval('self._update_%s' % self.c.sub)(id)
            except ValidationError as e:
                self.form.errors = e.errors
                err = True
        if self.form.errors or err:
            model.Session.rollback()
            return self._error_update()

    def _error_update(self):
        id = self.request.matchdict.get('id')
        sub = self._get_sub()
        template = eval('self._edit_t_%s' % sub)(id)
        html = self.form.render(template, extra_info=self.response_dict)
        return Response(html)

    def _update_aine(self, id):
        data = self.form.data.get('ya')
        for item in self.c.ylesanded:
            yained = {r.aine_kood: r for r in item.ylesandeained}
            for ind, rcd in enumerate(data):
                aine = rcd['aine_kood']
                try:
                    yaine = yained.pop(aine)
                    # aine oli juba olemas
                except KeyError:
                    # lisame uue aine
                    yaine = model.Ylesandeaine(ylesanne=item,
                                               aine_kood=aine)
                yaine.seq = ind

                if self.c.sub == 'teema':
                    # salvestame teemad ja valdkonnad
                    teemad2 = rcd['teemad2']
                    for r in list(yaine.ylesandeteemad):
                        key = r.teema_kood
                        if r.alateema_kood:
                            key += '.' + r.alateema_kood
                        try:
                            teemad2.remove(key)
                            # teema oli juba olemas
                        except ValueError:
                            r.delete()
                    for key in teemad2:
                        koodid = key.split('.')
                        r = model.Ylesandeteema(teema_kood=koodid[0],
                                                alateema_kood=len(koodid) > 1 and koodid[1] or None)
                        yaine.ylesandeteemad.append(r)

                elif self.c.sub == 'opitulemus':
                    # salvestame õpitulemused
                    opitulemused = rcd['opitulemused']
                    for r in list(yaine.ylopitulemused):
                        try:
                            opitulemused.remove(r.opitulemus_klrida_id)
                            # oli alles
                        except ValueError:
                            r.delete()
                    for klrida_id in opitulemused:
                        r = model.Ylopitulemus(opitulemus_klrida_id=klrida_id)
                        yaine.ylopitulemused.append(r)

            # kustutame liigsed ained
            for yaine in yained.values():
                yaine.delete()
        model.Session.commit()
        self.success()
        return self._redirect('edit', id)

    def _update_teema(self, id):
        self.c.sub = 'teema'
        return self._update_aine(id)
    
    def _update_opitulemus(self, id):
        self.c.sub = 'opitulemus'
        return self._update_aine(id)
    
    def _update_kogu(self, id):
        kogud_id = list(map(int, self.request.params.getall('kogud_id') or []))
        kogud = [{'ylesandekogu_id': kogu_id} for kogu_id in kogud_id]
        err = None
        for ylesanne in self.c.ylesanded:
            if ylesanne.adaptiivne:
                err = _("Diagnostilise testi ülesanne ei saa kuuluda e-kogudesse")
            else:
                ctrl = BaseGridController(ylesanne.koguylesanded,
                                          model.Koguylesanne, None, self, pkey='ylesandekogu_id')
                ctrl.save(kogud)
        model.Session.commit()
        if err:
            self.error(err)
        self.success()
        return self._redirect('edit', id)

    def _update_tolge(self, id):
        keeled = self.request.params.getall('skeel')
        for ylesanne in self.c.ylesanded:
            for lang in keeled:
                if not ylesanne.has_lang(lang):
                    if not ylesanne.lang:
                        ylesanne.lang = lang
                    ylesanne.skeeled = (ylesanne.skeeled or '') + ' ' + lang
        model.Session.commit()
        self.success()
        return self._redirect('edit', id)
           
    def _update_olek(self, id):
        staatus = int(self.request.params.get('staatus'))
        cnt = 0
        for ylesanne in self.c.ylesanded:
            ylesanne.check(self)
            model.Session.commit()
            if ylesanne.staatus != staatus:
                ylesanne.logi(_("Oleku muutmine"),
                              ylesanne.staatus_nimi,
                              model.Klrida.get_str('Y_STAATUS', str(staatus)) + \
                              '\n' + (self.request.params.get('markus') or ''),
                              const.LOG_LEVEL_GRANT)
                ylesanne.staatus = staatus
                cnt += 1
                ylesanne.set_cache_valid()
                if staatus == const.Y_STAATUS_YLEANDA:
                    # saadame ainespetsialistidele meili
                    self._status_mail(ylesanne)
                
        model.Session.commit()
        self.success(_("{n} ülesande olek on muudetud").format(n=cnt))

        if not self.c.can_ylhulgi:
            for ylesanne in self.c.ylesanded:
                if not self.c.user.has_permission('ylesanded',const.BT_SHOW, ylesanne):
                    # seoses oleku muutmisega ei ole kasutajal enam ligipääsu ylesandele
                    return HTTPFound(location=self.url('ylesanded'))

        return self._redirect('edit', id)

    def _update_autor(self, id):
        autor = self.request.params.get('autor')[:128]
        for ylesanne in self.c.ylesanded:
            ylesanne.autor = autor
        model.Session.commit()
        self.success()
        return self._redirect('edit', id)

    def _update_kvaliteet(self, id):
        kvaliteet = self.request.params.get('kvaliteet_kood')
        for ylesanne in self.c.ylesanded:
            if self.c.user.has_permission('ylkvaliteet', const.BT_UPDATE, ylesanne):
                ylesanne.kvaliteet_kood = kvaliteet or None
        model.Session.commit()
        self.success()
        return self._redirect('edit', id)

    def _update_secret(self, id):
        """Salastamine
        """
        rc = True
        message = ''
        encrypt = False
        salastatud = const.SALASTATUD_LOOGILINE
        
        if rc:
            if message:
                message = '\n' + message

            cnt = 0
            for ylesanne in self.c.ylesanded:
                if encrypt and not ylesanne.is_encrypted or \
                   not encrypt and ylesanne.salastatud != salastatud:
                    if self.c.can_ylhulgi or ylesanne.has_permission('ylesanded', const.BT_VIEW, None, self.c.user, True):
                        cnt += 1
                        ylesanne.logi(_("Salastamine"),
                                      ylesanne.salastatud_nimi(),
                                      ylesanne.salastatud_nimi(salastatud) + \
                                      message + \
                                      '\n' + (self.request.params.get('markus') or ''),
                                      const.LOG_LEVEL_GRANT)
                        ylesanne.set_salastatud(salastatud)
            model.Session.commit()
            if encrypt:
                self.notice(_("{n} ülesannet on salastatud ja krüptitud.").format(n=cnt) + message)
            else:
                self.notice(_("{n} ülesannet on salastatud").format(n=cnt))

        return self._redirect('edit', id)

    def _update_nosecret(self, id):
        cnt = 0
        for ylesanne in self.c.ylesanded:
            if ylesanne.salastatud in (const.SALASTATUD_LOOGILINE, const.SALASTATUD_SOORITATAV):
                cnt += 1
                ylesanne.logi(_("Salastatuse muutmine"),
                              ylesanne.salastatud_nimi(),
                              ylesanne.salastatud_nimi(const.SALASTATUD_POLE) + \
                              '\n' + (self.request.params.get('markus') or ''),
                              const.LOG_LEVEL_GRANT)
                ylesanne.set_salastatud(const.SALASTATUD_POLE)
        model.Session.commit()
        self.success(_("{n} ülesannet pole enam salastatud").format(n=cnt))
        return self._redirect('edit', id)

    def _update_aste(self, id):
        peamine_aste_kood = self.request.params.get('f_aste_kood')
        kooliastmed = self.request.params.getall('v_aste_kood')
        if peamine_aste_kood not in kooliastmed:
            kooliastmed = kooliastmed + [peamine_aste_kood]
        mask = 0
        for kood in kooliastmed:
            mask += self.c.opt.aste_bit(kood) or 0
            
        cnt = 0
        for ylesanne in self.c.ylesanded:
            if ylesanne.aste_kood != peamine_aste_kood:
                ylesanne.aste_kood = peamine_aste_kood
            if mask != ylesanne.aste_mask:
                ylesanne.aste_mask = mask
        model.Session.commit()
        self.success()
        return self._redirect('edit', id)

    def _update_testiliik(self, id):
        liigid = self.request.params.getall('tl.kood')
        for item in self.c.ylesanded:
            olemas_liigid = [] 
            for subitem in item.testiliigid:
                kood = subitem.kood
                if kood not in liigid:
                    subitem.delete()
                else:
                    olemas_liigid.append(kood)
            for kood in liigid:
                if kood not in olemas_liigid:
                    subitem = model.Testiliik(kood=kood)
                    item.testiliigid.append(subitem)        

        model.Session.commit()
        self.success()
        return self._redirect('edit', id)

    def _update_kasutus(self, id):
        kasutliigid = [{'kasutliik_kood': r} for r in self.request.params.getall('kasutliik_kood')]
        for item in self.c.ylesanded:
            ctrl = BaseGridController(item.kasutliigid, model.Kasutliik, None, self, pkey='kasutliik_kood')        
            ctrl.save(kasutliigid)        

        model.Session.commit()
        self.success()
        return self._redirect('edit', id)

    def _status_mail(self, ylesanne):
        """Ainespetsialistidele saadetakse kiri selle kohta, et 
        mingi ülesanne on üleandmise olekusse jõudnud.
        """
        aine_koodid = []
        aine_nimed = []
        for ya in ylesanne.ylesandeained:
            aine_koodid.append(ya.aine_kood)
            aine_nimed.append(ya.aine_nimi)
        q = (model.Session.query(model.Kasutaja.id, model.Kasutaja.epost)
             .filter(model.Kasutaja.kasutajarollid.any(
                 sa.and_(model.Kasutajaroll.kasutajagrupp_id==const.GRUPP_AINESPETS,
                         model.Kasutajaroll.aine_kood.in_(aine_koodid),
                         model.Kasutajaroll.kehtib_alates<=datetime.now(),
                         model.Kasutajaroll.kehtib_kuni>=datetime.now())
                 ))
             )
        ained_nimi = ', '.join(aine_nimed)
        kasutajad = [(k_id, epost) for (k_id, epost) in q.all() if epost]
        li_epost = [rcd[1] for rcd in kasutajad]
        if len(li_epost):
            to = li_epost
            data = {'ylesanne_nimi': ylesanne.nimi,
                    'ylesanne_id': ylesanne.id,
                    'aine_nimi': ained_nimi.lower(),
                    'y_url': self.h.url('ylesanne', id=ylesanne.id, pw_url=True),
                    'user_nimi': self.c.user.fullname,
                    }
            subject, body = self.render_mail('mail/ylesanne.yleanda.mako', data)

            body = Mailer.replace_newline(body)
            if not Mailer(self).send(to, subject, body):
                log.debug(_("Saadetud kiri {s1} aadressidele {s2}").format(s1=subject, s2=to))
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                for k_id, epost in kasutajad:
                    model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
                model.Session.commit()
        else:
            log.debug(_("Ülesande {id} üleandmise kirja ei saadeta, sest aines {s} ei ole ühtegi meiliaadressiga ainespetsialisti").format(
                id=ylesanne.id, s=ained_nimi))

    def _update_isik(self, id):            
        """Isiku lisamine ülesandega seotuks
        """
        kasutajagrupp_id = int(self.request.params.get('kasutajagrupp_id'))
        kasutajagrupp = model.Kasutajagrupp.get(kasutajagrupp_id)
        kehtib_kuni = self.form.data['kehtib_kuni']
        isikukoodid = self.request.params.getall('oigus')
        not_added = []
        added = False
        for ik in isikukoodid:
            kasutaja = model.Kasutaja.get_by_ik(ik)
            if kasutaja:
                for ylesanne in self.c.ylesanded:
                    if self.c.user.has_permission('ylesanderoll', const.BT_UPDATE, ylesanne):
                        if ylesanne._on_ylesandeisik(kasutaja.id, kasutajagrupp_id):
                            not_added.append(kasutaja.nimi)
                        else:
                            added = True
                            isik = model.Ylesandeisik(kasutaja=kasutaja,
                                                      kasutajagrupp_id=kasutajagrupp_id,
                                                      kehtib_alates=date.today(),
                                                      kehtib_kuni=kehtib_kuni or const.MAX_DATE)
                            ylesanne.ylesandeisikud.append(isik)
                            ylesanne.set_cache_valid()
                            ylesanne.logi(_("Isiku lisamine"),
                                          None,
                                          '%s %s\n%s\n%s' % (kasutajagrupp.nimi,
                                                             self.h.str_from_date(kehtib_kuni) or '',
                                                             kasutaja.nimi,
                                                             kasutaja.isikukood),
                                          const.LOG_LEVEL_GRANT)

                            if kasutajagrupp_id == const.GRUPP_Y_TOIMETAJA:
                                #const.GRUPP_Y_TOLKIJA, const.GRUPP_Y_KUJUNDAJA
                                versioon = model.Ylesandeversioon.add(ylesanne)
                            
            model.Session.commit()
        if added:
            model.Session.commit()
            self.success()
        return self._redirect('edit', id)
            
    def _update_avalukk(self, id):
        cnt = 0
        for ylesanne in self.c.ylesanded:
            if ylesanne.lukus:
                ylesanne.lukus = None
                ylesanne.set_cache_valid()
                cnt += 1
        if cnt:            
            model.Session.commit()
            self.success(_("{n} ülesannet on lukust lahti võetud. Ole nüüd ettevaatlik!").format(n=cnt))
        return self._redirect('edit', id)

    def _update_taastalukk(self, id):
        cnt = 0
        for ylesanne in self.c.ylesanded:
            if not ylesanne.lukus:
                ylesanne.lukus = ylesanne.get_lukustusvajadus()
                if ylesanne.lukus:
                    ylesanne.set_cache_valid()
                    cnt += 1
        if cnt:
            model.Session.commit()
            self.success(_("{n} ülesannet on lukustatud").format(n=cnt))
        else:
            self.success(_("Ühtki ülesannet polnud vaja lukustada"))

        return self._redirect('edit', id)

    def _update_disain(self, id):
        try:
            disain_ver = int(self.request.params.get('disain_ver'))
        except:
            disain_ver = None
        if disain_ver:
            for ylesanne in self.c.ylesanded:
                if ylesanne.disain_ver != disain_ver:
                    ylesanne.disain_ver = disain_ver
        model.Session.commit()
        self.success()
        return self._redirect('edit', id)

    def _export(self, ylesanded_id):
        "Valitud ylesannete eksportimine, käivitatakse otsingust"
        err = None
        li = []
        for y_id in ylesanded_id:
            item = model.Ylesanne.get(y_id)
            if not item:
                err = _("Valitud ID-ga ülesannet ei ole") + ' (%s)' % y_id
                break
            elif not self.c.user.has_permission('ylesanded', const.BT_VIEW, obj=item):
                err = _("Puudub ligipääsuõigus ülesandele {id}").format(id=item.id)
                break
            else:
                li = raw_export.add_to_export(li, item)

        if not err and not li:
            err = _("Valitud ID-ga ülesannet ei ole")
        if err:
            self.error(err)
            return HTTPFound(location=self.h.url('ylesanded'))
        filename = 'ylesanded%sjt.raw' % ylesanded_id[0]
        filedata = raw_export.export_dump(li)
        mimetype = 'application/binary'
        return utils.download(filedata, filename, mimetype)

    def __before__(self):
        ylesanded_id = self.request.matchdict.get('id')
        if ylesanded_id:
            # edit
            self.c.ylesanded_id = ylesanded_id
            self.c.yl_id = ylesanded_id.split('-')
        else:
            # new
            self.c.yl_id = self.request.params.getall('yl_id')
            self.c.ylesanded_id = '-'.join(self.c.yl_id)
        self.c.ylesanded = [model.Ylesanne.get(yl_id) for yl_id in self.c.yl_id]
        self.c.can_ylhulgi = self.c.user.has_permission('ylhulgi', const.BT_UPDATE)

    def _has_permission(self):
        if self.c.can_ylhulgi:
            return True
        
        # vajaliku õiguse nimi
        permission = self._get_permission()
        # kas toimub muutmine või vaatamine?
        perm_bit = const.BT_UPDATE
        rc = False
        for ylesanne in self.c.ylesanded:
            rc = self.c.user.has_permission(permission, perm_bit, obj=ylesanne)
            if not rc:
                # ei lubatud ligipääsu
                self._miss_perm = _("Ülesanne {id}").format(id=ylesanne.id)
                break
            
        return rc
                              
