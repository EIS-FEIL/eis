import pickle
import urllib.request, urllib.parse, urllib.error
from eis.lib.baseresource import *
from eis.lib.block import BlockController
_ = i18n._

log = logging.getLogger(__name__)

class KoostamineController(BaseResourceController):
    """Koostamine
    """
    _permission = 'ylesanded'

    _MODEL = model.Ylesanne
    _EDIT_TEMPLATE = 'ekk/ylesanded/koostamine.mako'
    _ITEM_FORM = None #forms.ekk.ylesanded.MuutjadForm 

    def _edit_olek(self, id):
        self.c.item = model.Ylesanne.get(id)
        return self.render_to_response('ekk/ylesanded/koostamine.olek.mako')

    def _edit_secret(self, id):
        """Salasta
        """
        self.c.item = model.Ylesanne.get(id)
        self.c.sub = 'secret'
        return self.render_to_response('ekk/ylesanded/koostamine.sala.mako')

    def _edit_nosecret(self, id):
        """Salasta
        """
        self.c.item = model.Ylesanne.get(id)
        self.c.sub = 'nosecret'
        return self.render_to_response('ekk/ylesanded/koostamine.sala.mako')

    def _edit_decrypt(self, id):
        """Kasutaja vajutas nuppu "Krüpti lahti" põhiaknas.
        Kuvame dialoogiakna krüptitud faili alla laadimiseks
        ja lahti krüptitud andmete üles laadimiseks.
        """
        self.c.item = model.Ylesanne.get(id)
        self.c.sub = 'decrypt'
        return self.render_to_response('ekk/ylesanded/koostamine.sala.mako')

    def _edit_logitase(self, id):
        self.c.item = model.Ylesanne.get(id)
        return self.render_to_response('ekk/ylesanded/koostamine.logitase.mako')

    def _edit_mail(self, id):
        self.c.item = model.Ylesanne.get(id)
        data = {'ylesanne_nimi': self.c.item.nimi,
                'ylesanne_id': self.c.item.id,
                'user_nimi': self.c.user.fullname,
                }
        self.c.subject, self.c.body = self.render_mail('mail/ylesande.koostajale.mako', data)

        return self.render_to_response('ekk/testid/koostamine.mail.mako')

    def _check(self, ylesanne, staatus):
        c = self.c
        # korrastatakse
        ylesanne.check(self)
        model.Session.commit()
        # tehakse kontrollid
        c.rc, c.y_errors, c.sp_errors, c.k_errors, c.k_warnings = BlockController.check_ylesanne(self, ylesanne, staatus)
        if not c.rc:
            # leiti vigu
            c.item = ylesanne
            self.error(_("Ülesande olekut ei saa muuta, sest see ei vasta nõuetele"))
            return self.render_to_response('ekk/ylesanded/kontroll.mako')

    def _update_olek(self, id):
        ylesanne = self._MODEL.get(id)
        staatus = int(self.request.params.get('staatus'))
        if ylesanne.staatus == staatus:
            self.error(_("Olekut ei muudetud"))
        else:
            if staatus not in (const.Y_STAATUS_KOOSTAMISEL,
                               const.Y_STAATUS_ARHIIV):
                res = self._check(ylesanne, staatus)
                if res:
                    # leiti vigu
                    return res

            ylesanne.logi(_("Oleku muutmine"),
                          ylesanne.staatus_nimi,
                          model.Klrida.get_str('Y_STAATUS', str(staatus)) + \
                              '\n' + (self.request.params.get('markus') or ''),
                          const.LOG_LEVEL_GRANT)
            ylesanne.staatus = staatus
            ylesanne.set_cache_valid()            
            if staatus == const.Y_STAATUS_YLEANDA:
                # saadame ainespetsialistidele meili
                self._status_mail(ylesanne)
                
            model.Session.commit()
            self.success(_("Ülesande olek on muudetud"))
            if not self.c.user.has_permission('ylesanded',const.BT_SHOW, ylesanne):
                # seoses oleku muutmisega ei ole kasutajal enam ligipääsu ylesandele
                return HTTPFound(location=self.url('ylesanded'))
            
        return self._redirect('edit', id)

    def _update_secret(self, id):
        """Salastamine
        """
        ylesanne = self._MODEL.get(id)
        if not ylesanne.has_permission('ylesanded', const.BT_VIEW, None, self.c.user, True):
            # salastada ei saa isik, kes ei või peale salastamist enam ligi saada
            self.error(_("Salastatust ei muudetud"))
            return self._redirect('edit', id)            
        
        alg_salastatud = ylesanne.salastatud
        rc = True
        message = ''
        encrypt = self.request.params.get('encrypt')
        if encrypt:
            # kryptida
            isikukoodid = self.request.params.getall('oigus')
            if len(isikukoodid) == 0:
                self.error(_("Palun vali isikud, kes saavad lahti krüptida"))
                rc = False

            if rc:
                cnt = (model.Ylesandevastus.query
                       .join((model.Valitudylesanne,
                              model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
                       .filter(model.Valitudylesanne.ylesanne_id==ylesanne.id)
                       .count()
                       )
                if cnt > 0:
                    self.error(_("Ülesannet {id} ei saa krüpteerida, sest selle sooritamist on alustatud").format(id=ylesanne.id))
                    rc = False

            if rc:
                data = ylesanne.pack_crypt()
                data = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)

                message = self._error(e, _("Ei saa krüptida. "))
                rc = False
            if rc:
                ylesanne.save_encrypted(encrypted_password, encrypted_data, isikukoodid)
            else:
                self.error(message)
            salastatud = const.SALASTATUD_KRYPTITUD
        else:
            salastatud = const.SALASTATUD_LOOGILINE

        if alg_salastatud == salastatud:
            self.error(_("Salastatust ei muudetud"))
            rc = False

        if rc:
            if message:
                message = '\n' + message
            ylesanne.logi(_("Salastamine"),
                          ylesanne.salastatud_nimi(),
                          ylesanne.salastatud_nimi(salastatud) + \
                          message + \
                          '\n' + (self.request.params.get('markus') or ''),
                          const.LOG_LEVEL_GRANT)
            ylesanne.set_salastatud(salastatud)
            model.Session.commit()
            if encrypt:
                self.notice(_("Ülesanne on salastatud ja krüptitud. ") + message)
            else:
                self.notice(_("Ülesanne on salastatud"))

        return self._redirect('edit', id)

    def _update_nosecret(self, id):
        ylesanne = self._MODEL.get(id)
        if ylesanne.salastatud == const.SALASTATUD_LOOGILINE:
            ylesanne.logi(_("Salastatuse muutmine"),
                          ylesanne.salastatud_nimi(),
                          ylesanne.salastatud_nimi(const.SALASTATUD_POLE) + \
                          '\n' + (self.request.params.get('markus') or ''),
                          const.LOG_LEVEL_GRANT)
            ylesanne.set_salastatud(const.SALASTATUD_POLE)
            model.Session.commit()
            self.success(_("Ülesanne pole enam salastatud"))

        return self._redirect('edit', id)

    def download(self):
        """Krüptitud andmete alla laadimine lahti krüptimiseks kasutaja arvutis.
        """
        id = self.request.matchdict.get('id')
        ylesanne = self._MODEL.get(id)
        if ylesanne.salaylesanne:
            data = ylesanne.salaylesanne.parool
            #data = data.decode('base64')
            filename = 'ylesanne_%s.cdoc' % ylesanne.id
            mimetype = const.CONTENT_TYPE_CDOC
            #mimetype = 'application/octet-stream'
            return utils.download(data.encode('utf-8'), filename, mimetype)
        else:
            raise NotFound('Kryptitud andmeid pole')                    

    def _update_decrypt(self, id):
        """Kasutaja postitab lahti krüptitud andmed serverisse.
        """
        rc = False
        ylesanne = self._MODEL.get(id)
        if ylesanne.salastatud == const.SALASTATUD_KRYPTITUD and ylesanne.salaylesanne:
            # kasutaja on DigiDoc Crypto programmiga parooli lahti kryptinud
            password = self.request.params.get('parool')
            if not password:
                self.error(_("Palun esita lahti krüptitud andmefaili sisu"))
            else:
                # pyyame lahti kryptida
                rc = self._decrypt(ylesanne, password)

        if rc:
            # lahti kryptimine õnnestus, kuvame pealehe
            model.Session.commit()
            self.success(_("Ülesanne on lahti krüptitud, kuid jätkuvalt salastatud."))
            return self._redirect('edit', id)
        else:
            # lahti kryptimine ebaõnnestus, kuvame dialoogiakna uuesti
            return self._edit_decrypt(id)

    def _decrypt(self, ylesanne, password):
        """Ülesande dekrüptimine parooliga
        """
        ddoc = Ddoc(self.request.registry.settings)
        data = ddoc.decrypt(ylesanne.salaylesanne.data, password)
        if ddoc.error:
            # vist polnud õige parool
            self.error(ddoc.error)
            return False

        data = pickle.loads(data)
        ylesanne.depack_crypt(data)
        salastatud = const.SALASTATUD_LOOGILINE
        
        ylesanne.logi(_("Salastatuse muutmine"),
                      ylesanne.salastatud_nimi(),
                      ylesanne.salastatud_nimi(salastatud) + \
                          '\n' + (self.request.params.get('markus') or ''),
                      const.LOG_LEVEL_GRANT)
        ylesanne.set_salastatud(salastatud)
        return True
   
    def _update_logitase(self, id):
        ylesanne = self._MODEL.get(id)
        logitase_muudatused = bool(self.request.params.get('logitase_muudatused'))
        logitase = logitase_muudatused and const.LOG_LEVEL_CHANGE or const.LOG_LEVEL_GRANT
        if ylesanne.logitase == logitase:
            self.error(_("Andmeid ei muudetud"))
        else:
            ylesanne.logi(_("Logitaseme muutmine"),
                          ylesanne.logitase_nimi(),
                          ylesanne.logitase_nimi(logitase) + \
                              '\n' + (self.request.params.get('markus') or ''),
                          const.LOG_LEVEL_GRANT)
            ylesanne.logitase = logitase
            model.Session.commit()
            self.success(_("Logitaset muudeti"))

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

    def _update_mail(self, id):
        self.form = Form(self.request, schema=forms.ekk.ylesanded.KoostamineMailForm)
        if not self.form.validate():
            self.c.dialog_mail = True
            html = self.form.render(self._EDIT_TEMPLATE,
                                    extra_info=self._edit_d())            
            return Response(html)
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

    def _update_avalukk(self, id):
        ylesanne = self._MODEL.get(id)
        if ylesanne.lukus:
            ylesanne.lukus = None
            ylesanne.set_cache_valid()            
            model.Session.commit()
            lukus = ylesanne.get_lukustusvajadus()
            if lukus:
                self.success(_("Ülesanne on lukust lahti võetud. Ole nüüd ettevaatlik!"))
            else:
                self.success(_("Ülesanne on lukust lahti võetud"))
        return self._redirect('edit', id)

    def _update_taastalukk(self, id):
        ylesanne = self._MODEL.get(id)

        if not ylesanne.lukus:
            ylesanne.lukus = ylesanne.get_lukustusvajadus()
            if ylesanne.lukus:
                ylesanne.set_cache_valid()                
                model.Session.commit()
                self.success(_("Ülesanne on lukustatud"))
            else:
                self.success(_("Ülesannet polegi vaja lukustada"))
        else:
            self.success(_("Ülesanne on juba lukus"))
        return self._redirect('edit', id)
    
    def __before__(self):
        self.c.ylesanne = model.Ylesanne.get(self.request.matchdict.get('id'))

    def _perm_params(self):
        return {'obj':self.c.ylesanne}

