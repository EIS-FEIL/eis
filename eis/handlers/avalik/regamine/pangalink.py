from eis.lib.base import *
from eis.lib.pangalink import Pangalink
_ = i18n._
log = logging.getLogger(__name__)

class PangalinkController(BaseController):

    _authorize = False # pangast tulles võib olla seansi cookie kadunud
    _get_is_readonly = False
    _log_params_post = True
    _log_params_get = True
    
    def new(self):
        """Panka suunatava päringu moodustamine
        ja panka suunatava vormi kuvamine
        """
        kasutaja = self.c.kasutaja
        if not kasutaja:
            raise NotAuthorizedException('login')

        self.c.pank_id = self.request.matchdict.get('pank_id')
        sooritaja_id = self.request.matchdict.get('sooritaja_id') or None
        tasu, mille_eest, ret_url = self._get_ret_url()

        if not tasu:
            self.error(_('Ei olegi millegi eest tasuda!'))
            return self._after_return(sooritaja_id)

        self.c.pank = Pangalink.get_instance(self.c.pank_id)
        if not self.c.pank.is_configured():
            self.error(_('Valitud pangaga on EISi ühendus seadistamata'))
            self._after_return(sooritaja_id)

        makse = model.Makse(kasutaja_id=kasutaja.id,
                            amount=tasu,
                            msg=mille_eest,
                            saadud=False)
        model.Session.flush()
        makse.stamp = stamp = self.c.pank.gen_stamp(makse.id)
        self.c.vk_data = self.c.pank.gen_1012(kasutaja.id, tasu, mille_eest, ret_url, stamp)
        model.Session.commit()

        html = self.render('avalik/regamine/pangalink.mako')
        encoding = self.c.pank.encoding.lower()
        resp = Response(html.encode(encoding), charset=encoding)

        return resp

    def _get_ret_url(self):
        kasutaja = self.c.kasutaja
        li_eest = []
        sooritaja_id = self.request.matchdict.get('sooritaja_id')
        if sooritaja_id:
            self.c.sooritaja = model.Sooritaja.get(sooritaja_id)
            assert self.c.sooritaja.kasutaja_id == kasutaja.id, 'Vale kasutaja'
            ret_url = self.url('regamine_return_pangalink', 
                               sooritaja_id=sooritaja_id, 
                               pank_id=self.c.pank_id,
                               pw_url=True)
            if not self.c.sooritaja.tasu or self.c.sooritaja.tasutud:
                tasu = 0
            else:
                tasu = self.c.sooritaja.tasu
                li_eest.append(self.c.sooritaja.testimiskord.tahised)
        else:
            testiliik = self.request.params.get('testiliik')
            ret_url = self.url('regamine_avaldus_return_pangalink', 
                               pank_id=self.c.pank_id,
                               testiliik=testiliik,
                               pw_url=True)            
            tasu = 0
            for sooritaja in kasutaja.get_reg_sooritajad():
                if sooritaja.tasu and not sooritaja.tasutud:
                    li_eest.append(sooritaja.testimiskord.tahised)
                    tasu += sooritaja.tasu
        if len(li_eest) == 1:
            mille_eest = _('Testile registreerimine {s1} ({s2})').format(s1=kasutaja.isikukood or kasutaja.nimi, s2=', '.join(li_eest))
        else:
            mille_eest = _('Testidele registreerimine {s1} ({s2})').format(s1=kasutaja.isikukood or kasutaja.nimi, s2=', '.join(li_eest))
        return tasu, mille_eest, ret_url

    def returned_post(self):
        """Pangast saadud tagasiside
        """
        # EISi seansi cookie samesite=Lax tõttu ei ole pangast postitatud päringus seansi infot.
        # Kui Beaker näeb, et cookie puudub, siis annab brauserile korralduse uus cookie teha.
        # Kustutame selle korralduse ja suuname ise uuesti, et brauser annaks kaasa vana cookie.
        session_key = self.request.registry.settings.get('session.key')
        def prevent_new_session(request, response):
            try:
                response.unset_cookie(session_key)
            except KeyError as ex:
                log.debug('unset_cookie error: %s' % ex)

        self.request.add_response_callback(prevent_new_session)

        return self.returned()

    def returned(self):
        """Pangast saadud tagasiside
        Toimub kaks korda:
        1) VK_AUTO=Y panga poolt makse teostamisel
        2) VK_AUTO=N kasutaja saabumisel
        """
        pank_id = self.request.matchdict.get('pank_id')
        sooritaja_id = self.request.matchdict.get('sooritaja_id')

        errno = self.request.params.get('eiserrno')
        if not errno:
            # esimest korda siin, töötleme panga vastust
            pank = Pangalink.get_instance(pank_id)
            # maksekviitungi saatja kontrollimine
            rc, message, params = pank.verify(self.request)
            is_auto = self.request.params.get('VK_AUTO') == 'Y'
            #log.info('RETURN:rc=%s,message=%s,params=%s' % (rc,message, params))
            if not rc:
                log.error(message)
                if is_auto:
                    return Response(message)
                self._show_msg('4')
            else:
                # maksekviitungi kontrollimine
                makse = self._get_makse()
                if not makse:
                    if is_auto:
                        return Response("error 2")
                    self._show_msg('2')
                elif not makse.saadud:
                    # maksekviitung on kontrollitud
                    makse.saadud = True
                    self._set_paid(makse)
                    model.Session.commit()
                if is_auto:
                    return Response("OK")
        elif self.c.user.id:
            # teist korda siin, et kuvada teade
            self._show_msg(errno)

        return self._after_return(sooritaja_id)

    def _show_msg(self, errno):
        error = msg = None
        if errno == '1':
            msg = _("Makse on sooritatud!")
        elif errno == '2':
            error = _("Kviitungile vastavat makset ei leitud")
        elif errno == '3':
            error = _("Kasutatud kviitung")
        elif errno == '4':
            error = _("Maksetehing ebaõnnestus")
        else:
            return
        
        log.debug(error or msg)
        if self.c.user.id:
            # on olemas seanss, kus kuvada teateid
            if error:
                self.error(error)
            else:
                self.success(msg)
        else:
            # äsja pangast POSTiga tuli ja seansi cookie puudub, kasutajaseanss puudub
            # suuname siia tagasi - samast serverist tulles ilmub seanss            
            raise HTTPFound(location=self.url_current(eiserrno=errno))                    

    def _get_makse(self):
        "Pangast tulles leitakse makse kirje"
        stamp = self.request.params.get('VK_STAMP')
        if stamp:
            q = model.Makse.query.filter(model.Makse.stamp==stamp)
            rcd = q.first()
            return rcd
        
    def _set_paid(self, makse):
        kasutaja_id = makse.kasutaja_id
        msg = makse.msg
        log.debug('set_paid %s' % makse.stamp)
        sooritaja_id = self.request.matchdict.get('sooritaja_id')
        if sooritaja_id:
            # tasuti yhe registreeringu eest
            sooritaja = model.Sooritaja.get(sooritaja_id)
            assert sooritaja.kasutaja_id == kasutaja_id, 'Vale kasutaja'
            log.debug(f'tasutud sooritaja {sooritaja.id} eest')
            self._set_sooritaja_paid(sooritaja)
            self.c.testiliik = sooritaja.test.testiliik_kood
        else:
            # tasuti kõigi tasumata registreeringute eest
            li = re.findall(r'.*\((.*)\).*', msg)
            log.debug(f'tasutud {msg} eest: {li}')
            if len(li):
                mille_eest = li[0]
                tahised = [t.strip() for t in mille_eest.split(',')]
                for t in tahised:
                    try:
                        test_id, tkord_tahis = t.split('-')
                        test_id = int(test_id)
                    except Exception as ex:
                        log.error(f'Ei saa aru, mille eest maksti: {t}\n{ex}')
                        continue
                    else:
                        q = (model.Session.query(model.Sooritaja)
                             .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
                             .join(model.Sooritaja.testimiskord)
                             .filter(model.Testimiskord.test_id==test_id)
                             .filter(model.Testimiskord.tahis==tkord_tahis)
                             )
                        sooritaja = q.first()
                        if sooritaja:
                            self._set_sooritaja_paid(sooritaja)                            
                            self.c.testiliik = sooritaja.test.testiliik_kood

    def _set_sooritaja_paid(self, sooritaja):
        sooritaja.tasutud = True
        if sooritaja.staatus == const.S_STAATUS_TASUMATA:
            sooritaja.staatus = const.S_STAATUS_REGATUD
            for tos in sooritaja.sooritused:
                if tos.staatus == const.S_STAATUS_TASUMATA:
                    tos.staatus = const.S_STAATUS_REGATUD
                            
    def _after_return(self, sooritaja_id):
        testiliik = self.request.params.get('testiliik')
        if testiliik and re.match(r'[a-zA-Z]+$', testiliik):
            url = self.url('regamine_avaldus_kinnitatud', testiliik=testiliik)
        else:
            url = self.url('regamised')
        return HTTPFound(location=url)

    def _log_params_end(self):
        # pangast POSTi teel tulles ei ole kasutaja autenditud
        # leiame makse infost kasutaja isikukoodi ja kasutame seda logimisel
        userid = None
        if not self.c.user.id:
            try:
                makse = self._get_makse()            
                userid = makse.kasutaja.isikukood
            except:
                pass
        return super()._log_params_end(isikukood=userid)
    
    def __before__(self):
        self.c.kasutaja = self.c.user.get_kasutaja()
