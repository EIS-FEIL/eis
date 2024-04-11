# Safe Exam Browser
import plistlib
import uuid
import hashlib
import eis.lib.sebconfig as sebconfig
from eis.lib.examclient import ExamClient
from eis.lib.examsaga import ExamSaga
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class SebController(BaseController):
    _authorize = False
    _get_is_readonly = False
    _log_params_post = True
    _log_params_get = True

    def start(self):
        "SEB faili allalaadimine tavalises brauseris"
        c = self.c
        if not c.user.id:
            raise NotAuthorizedException('avaleht')
        
        test_id = self.request.matchdict.get('test_id')
        sooritus_id = self.convert_id(self.request.matchdict.get('sooritus_id'))
        q = (model.SessionR.query(model.Sooritus.sooritaja_id,
                                  model.Sooritus.staatus,
                                  model.Sooritus.toimumisaeg_id,
                                  model.Sooritus.testiosa_id,
                                  model.Sooritus.testiruum_id,
                                  model.Sooritaja.klaster_id,
                                  model.Sooritus.klastrist_toomata)
             .filter(model.Sooritus.id==sooritus_id)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritaja.kasutaja_id==c.user.id))
        r = q.first()
        if not r:
            # kirje puudub või pole õige kasutaja
            raise NotAuthorizedException('avaleht')            
        sooritaja_id, staatus, toimumisaeg_id, testiosa_id, testiruum_id, klaster_id, toomata = r

        if not toimumisaeg_id or \
           staatus not in (const.S_STAATUS_POOLELI,
                           const.S_STAATUS_KATKESTATUD,
                           const.S_STAATUS_ALUSTAMATA,
                           const.S_STAATUS_REGATUD):
            # muude olekutega kindlasti ei saa alustada, nendega võib saada
            # täpsem kontroll juba sooritus.py sees
            url = self.url('sooritamine_alustamine', test_id=test_id, sooritaja_id=sooritaja_id)
            raise HTTPFound(location=url)

        # leiame toimumisaja SEB konfi
        q = (model.SessionR.query(model.Toimumisaeg.verif_seb,
                                  model.Toimumisaeg.seb_konf)
             .filter_by(id=toimumisaeg_id))
        r = q.first()
        if not r or not r[0]:
            # SEB pole vajalik
            url = self.url('sooritamine_alustamine', test_id=test_id, sooritaja_id=sooritaja_id)
            raise HTTPFound(location=url)            
        else:
            # toimumisaja SEB konf, mille põhjal tehakse individuaalne konf
            seb_konf = r[1]

        sooritus = model.Sooritus.get(sooritus_id)
        # leiame sooritaja eksamiklastri
        exapi_host = model.Klaster.get_host(klaster_id)
        if not exapi_host or not sooritus.klastrist_toomata:
            # klastrit pole määratud või ei ole enam aktiivne
            sooritaja = model.Sooritaja.get(sooritaja_id)
            exapi_host = ExamSaga(self).init_klaster(sooritus, sooritaja)
            klaster_id = sooritaja.klaster_id
            
        # salvestame SEB konfi väljastamise kirje
        remote_addr = self.request.remote_addr
        namespace = self.request.session.id
        for n in range(2):
            # esimesel korral eeldame, et soorituse kirje on klastris olemas
            # seda ei ole siis, kui klaster on muutunud
            r = ExamClient(self, exapi_host).add_seblog(sooritus_id, remote_addr, namespace)
            if r.get('errcode') == 'NODATA':
                sooritaja = model.Sooritaja.get(sooritaja_id)
                ExamSaga(self).init_klaster(sooritus, sooritaja)
                # proovime teist korda
                continue
            url_key = r.get('url_key')
            assert url_key, 'seblog kirjet ei loodud'
            break
                
        # genereerime konfi
        # edastame kypsiste nõusoleku
        cconsent = self.request.cookies.get('eis-cookieconsent')
        start_url = self.url('seb_start1',
                             test_id=test_id,
                             testiosa_id=testiosa_id,
                             sooritaja_id=sooritaja_id,
                             sooritus_id=sooritus_id,
                             klaster_id=klaster_id,
                             url_key=url_key,
                             cconsent=cconsent,
                             pw_url=True)
        quit_url = self.url('login', action='signout', pw_url=True)

        settings = plistlib.loads(seb_konf)
        settings['startURL'] = start_url
        settings['quitURL'] = quit_url
        settings['browserUserAgent'] = sebconfig.user_agent(sooritus_id, testiruum_id)
        # et CKEditor töötaks
        settings['browserUserAgentWinDesktopMode'] = 0
        log.debug(f'seb start url={start_url}')
        # admin parool konfi vaatamiseks ja mida keegi ära ei arva
        admin_pw = uuid.uuid4().hex
        if self.is_test:
            admin_pw = 'lihtne'
        settings['hashedAdminPassword'] = hashlib.sha256(admin_pw.encode('utf-8')).hexdigest().upper()
        dataxml = plistlib.dumps(settings)
        filedata = sebconfig.compress_plain(dataxml)
        mimetype = 'application/octet-stream'
        filename = 'test%s-%s.seb' % (test_id, testiosa_id)
        if c.user.isikukood == 'TEST11':
            # koormustesti skripti koostamiseks
            html = f'<html><body><a href="{start_url}">start</a></body></html>'
            return Response(html)
        
        return utils.download(filedata, filename, mimetype, inline=True)

    def start1(self):
        "SEB maandumisleht"
        response = error = None
        c = self.c
        test_id = self.request.matchdict.get('test_id')
        sooritaja_id = self.convert_id(self.request.matchdict.get('sooritaja_id'))
        s_sooritus_id = self.request.matchdict.get('sooritus_id')
        sooritus_id = self.convert_id(s_sooritus_id)

        is_testuser = s_sooritus_id[0] == 'T'
        if is_testuser:
            # testsooritaja klastrit ei saa URList
            q = (model.SessionR.query(model.Sooritaja.klaster_id)
                 .filter_by(id=sooritaja_id))
            klaster_id = q.scalar()
        else:
            klaster_id = self.request.matchdict.get('klaster_id')
        
        url_key = self.request.matchdict['url_key']

        # kontrollitakse seblog kirje olemasolu ja tehakse sellele avamise märge
        exapi_host = model.Klaster.get_host(klaster_id)
        res = ExamClient(self, exapi_host).get_seblog(sooritus_id, sooritaja_id, url_key)
        error = res.get('error')
        if not error:
            # seblog kirje leiti
            r_remote_addr = res['remote_addr']
            testiruum_id = res['testiruum_id']
            namespace = res['namespace']
            agent = sebconfig.user_agent(sooritus_id, testiruum_id)
            user_agent = self.request.environ.get('HTTP_USER_AGENT')
            remote_addr = self.request.remote_addr

            if r_remote_addr != remote_addr:
                error = f'IP {r_remote_addr} > {remote_addr}'
            else:
                # kõik on korras, kasutaja on olemas
                kasutaja_id = res['kasutaja_id']
                kasutaja = model.Kasutaja.getR(kasutaja_id)
                if agent not in user_agent:
                    ik = kasutaja and kasutaja.isikukood
                    if not ik or not ik.startswith('TEST'):
                        error = f'HTTP_USER_AGENT {user_agent}'
                
                User.from_seb(self, kasutaja, sooritaja_id, sooritus_id, namespace)

                # suuname testi sooritama
                staatus = res['staatus']
                testiosa_id = res['testiosa_id']
                if staatus == const.S_STAATUS_POOLELI or staatus == const.S_STAATUS_KATKESTATUD:
                    url = self.url('sooritamine_jatka_osa', test_id=test_id, testiosa_id=testiosa_id, id=sooritus_id)
                else:
                    url = self.url('sooritamine_alusta_osa', test_id=test_id, testiosa_id=testiosa_id, id=sooritus_id)
                response = HTTPFound(location=url)

        if not response:
            # mingi viga
            error = f'SEB error s {sooritus_id}: {error}'
            log.error(error)
            self._error_log(error)
            self.error(_("Seadistus ei kehti"))    
            response = HTTPFound(location=self.url('seb_notauthorized'))

        # jätkame eelmise brauseri küpsiste nõusoleku kasutamist
        value = self.request.params.get('cconsent')
        if value:
            # vt index.py#cookieconsent
            if self.is_test:
                # devel
                response.set_cookie('eis-cookieconsent', value=value, max_age=31536000, samesite='lax', httponly=True)
            else:
                response.set_cookie('eis-cookieconsent', value=value, max_age=31536000, samesite='lax', secure=True, httponly=True)

        return response

    def notauthorized(self):
        "Kui SEB kasutaja proovib minna kuhugi, kuhu pole õigust, siis jõuab siia"
        self.c.hide_header_footer = True
        return self.render_to_response('avalik/sooritamine/seb.exit.mako')
    
