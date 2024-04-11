# Veriff integration settings
# Callback URL: https://eis.ekk.edu.ee/eis/veriff/returned
# Webhook events URL: https://eis.ekk.edu.ee/eis/veriff/eventhook/tartu
# Webhook decisions URL: https://eis.ekk.edu.ee/eis/veriff/decision/tartu
#
# Testimine (admin): https://eis.ekk.edu.ee/eis/veriff/start/0?int_id=test-tartu

import requests
import json
import hashlib
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class VeriffController(BaseController):

    _authorize = False
    _get_is_readonly = False
    _log_params_post = True
    _log_params_get = True
    
    def start(self):
        """Suuna edasi Veriffile"""
        c = self.c

        if not c.user.is_authenticated:
            raise NotAuthorizedException('login')

        def _get_integration(sooritus_id):
            integration_id = sooritus = sooritaja = None
            if sooritus_id == 0:
                # testimine
                k = c.user.get_kasutaja()
                if not k.has_permission('admin', const.BT_UPDATE):
                    # ainult admin võib testida
                    raise NotAuthorizedException('avaleht')
                integration_id = self.request.params.get('int_id')
            else:
                # enese tuvastamine enne testi sooritamist
                sooritus = model.Sooritus.get(sooritus_id)
                if not sooritus:
                    error = _("Test ei ole sooritamiseks suunatud")
                    raise NotAuthorizedException('avaleht', message=error)
                sooritaja = sooritus.sooritaja
                if sooritaja.kasutaja_id != c.user.id:
                    error = _("Test ei ole sooritamiseks suunatud")
                    raise NotAuthorizedException('avaleht', message=error)            

                error = None
                if sooritus.staatus not in (const.S_STAATUS_ALUSTAMATA,
                                            const.S_STAATUS_KATKESTATUD,
                                            const.S_STAATUS_POOLELI) \
                       and not sooritus.saab_alustada():
                    error = _("Testi sooritamise olek ei võimalda isiku tõendamist läbi viia")
                elif sooritus.luba_veriff:
                    error = _("Isiku tõendamine ei ole vajalik, võib testi alustada")
                elif c.user.verified_id:
                    error = _("Isiku tõendamine on juba tehtud, võib testi alustada")
                if error:
                    url = self.url('sooritamine_alustamine', test_id=sooritaja.test_id, sooritaja_id=sooritaja.id)
                    raise HTTPFound(location=url)

                # leiame toimumisaja seadetest, millist Veriffi integratsiooni kasutada
                q = (model.Session.query(model.Toimumisaeg.verif_param)
                     .filter_by(verif=const.VERIF_VERIFF)
                     .filter_by(id=sooritus.toimumisaeg_id))
                r = q.first()
                if r:
                    integration_id = r[0]
            return sooritus, sooritaja, integration_id

        sooritus_id = int(self.request.matchdict.get('sooritus_id'))
        sooritus, sooritaja, integration_id = _get_integration(sooritus_id)
                
        settings = self.request.registry.settings
        pub_key = settings.get(f'veriff.{integration_id}.pub_key')
        secret = settings.get(f'veriff.{integration_id}.secret')

        if not pub_key or not secret:
            self.error(_("Isiku tõendamine ei ole praegu võimalik"))
            if sooritus_id:
                url = self.url('sooritamine_alustamine', test_id=sooritaja.test_id, sooritaja_id=sooritaja.id)
            else:
                url = self.url('avaleht')
            raise HTTPFound(location=url)

        # Veriffi koormuse vähendamiseks kasutame võimalusel vana URLi,
        # kui verifitseerimist on juba alustatud, aga mitte lõpuni tehtud
        item_id = self.request.session.get('VERIFF_ATTEMPT_ID')
        if item_id:
            item = model.Verifflog.get(item_id)
            url = None
            if item and not item.submitted and item.created > datetime.now() - timedelta(minutes=10) \
                   and item.sooritus_id == sooritus_id and item.kasutaja_id == c.user.id:
                try:
                    r = json.loads(item.sess_data)
                    verif = r['verification']
                    url = verif['url']
                except:
                    pass
            if url:
                raise HTTPFound(location=url)
            
        # Loome uue verifitseerimise seansi
        item = model.Verifflog(sooritus_id=sooritus_id,
                               kasutaja_id=c.user.id)
        model.Session.flush()
        callback_url = self.url('veriff_returned', id=item.id, pw_url=True)
        data = {
            "verification": {
                "callback": callback_url,
                "person": {
                    "idNumber": c.user.isikukood,
                    "firstName": c.user.eesnimi,
                    "lastName": c.user.perenimi,
                    },
                "vendorData": str(item.id),
                "lang": "et",
                "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
           
        payload = json.dumps(data)
        headers = {
            'X-AUTH-CLIENT': pub_key,
            'X-SIGNATURE': _generate_signature(payload, secret),
            'Content-Type': 'application/json'
            }

        http_proxy = settings.get('http_proxy')
        kw = {}
        if http_proxy:
            kw['proxies'] = {'https': http_proxy }

        #url = 'https://stationapi.veriff.com/v1/sessions/'
        url = 'https://api.flamingo-eu.veriff.me/v1/sessions/'
        resp = requests.request('POST', url, data=payload, headers=headers, **kw)
        r = resp.json()
        
        # {
        #     "status": "success",
        #     "verification":{
        #         "id":"f04bdb47-d3be-4b28-b028-............",
        #         "url": "https://alchemy.veriff.com/v/sample-url.................",
        #         "sessionToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJh............",
        #         "baseUrl": "https://alchemy.veriff.com"
        #         }
        #     }
        # }
        if r['status'] != 'success':
            err = _("Verifitseerimisseansi alustamine ei õnnestu")
            self.error(err)
            log.error(err + str(r))
            self._error_log(err, str(r))
            if sooritus_id:
                sooritaja = sooritus.sooritaja
                url = self.url('sooritamine_alustamine', test_id=sooritaja.test_id, sooritaja_id=sooritaja.id)
            else:
                url = self.url('avaleht')
            raise HTTPFound(location=url)

        self.request.session['VERIFF_ATTEMPT_ID'] = item.id
        self.request.session.changed()
        
        verif = r['verification']
        url = verif['url']
        session_id = verif['id']

        item.session_id = session_id
        item.sess_data = json.dumps(r)
        model.Session.commit()
        raise HTTPFound(location=url)

    def returned(self):
        "Veriff saadab peale verifitseerimist kasutaja tagasi"
        c = self.c
        if not c.user.is_authenticated:
            raise NotAuthorizedException('login')

        id = self.request.matchdict.get('id')
        item = model.Verifflog.get(id)
        if not item:
            error = _("Viga")
            raise NotAuthorizedException('avaleht', message=error)

        sooritus_id = item.sooritus_id
        if sooritus_id == 0:
            # testimine
            if not item.submitted:
                self.error(_("Testi sooritamiseks on vaja läbida isiku tõendamise protsess lõpuni"))
            else:
                self.notice(_("Isiku tõendamise protsess on lõpuni läbitud"))
            url = self.url('avaleht')
            raise HTTPFound(location=url)
            
        sooritus = model.Sooritus.get(item.sooritus_id)
        if not sooritus:
            error = _("Test ei ole enam sooritamiseks suunatud")
            raise NotAuthorizedException('avaleht', message=error)            
            
        sooritaja = sooritus.sooritaja
        test_id = sooritaja.test_id
        testiosa_id = sooritus.testiosa_id

        if sooritaja.kasutaja_id != c.user.id:
            error = _("Test ei ole sooritamiseks suunatud")
            raise NotAuthorizedException('avaleht', message=error)            
        if sooritus.staatus not in (const.S_STAATUS_ALUSTAMATA,
                                    const.S_STAATUS_REGATUD,
                                    const.S_STAATUS_KATKESTATUD,
                                    const.S_STAATUS_POOLELI):
            self.error(_("Testi sooritamise olek ei võimalda isiku tõendamist läbi viia"))
            url = self.url('sooritamine_alustamine', test_id=test_id, sooritaja_id=sooritaja.id)
            raise HTTPFound(location=url)

        if not item.submitted and not item.code:
            self.error(_("Testi sooritamiseks on vaja läbida isiku tõendamise protsess lõpuni"))
            if sooritus_id:
                url = self.url('sooritamine_alustamine', test_id=test_id, sooritaja_id=sooritaja.id)
            else:
                url = self.url('avaleht')
            raise HTTPFound(location=url)
        
        c.user.set_verified(self.request, item.id)
        post_mako = 'avalik/sooritamine/veriff.returned.mako'
        if sooritus.saab_alustada():
            self.c.test_url = self.url('sooritamine_alusta_osa', test_id=test_id, testiosa_id=testiosa_id, id=sooritus.id)
            return self.render_to_response(post_mako)
        elif sooritus.staatus == const.S_STAATUS_POOLELI or sooritus.staatus == const.S_STAATUS_KATKESTATUD:
            self.c.test_url = self.url('sooritamine_jatka_osa', test_id=test_id, testiosa_id=testiosa_id, id=sooritus.id)
            return self.render_to_response(post_mako)
        else:
            self.error(_("Testi sooritamist ei saa veel alustada"))
            url = self.url('sooritamine_alustamine', test_id=sooritaja.test_id, sooritaja_id=sooritaja.id)
            raise HTTPFound(location=url)                

    @action(renderer='json')
    def eventhook(self):
        "Webhook verifitseerimise alguse või lõppemise kohta teate saamiseks"
        rc = False
        payload = self._check_webhook_input()
        data = json.loads(payload)
        # {
        #     "id": "45700917-4dce-41b1-a1b2-3a3deb4b4a12",
        #     "code": 7001/7002,
        #     "action": "started"/"submitted",
        #     "feature": "selfid",
        #     "attemptId": "91d0f6f0-6d8a-4ca9-b8dc-83514f522744"
        # }
        #log.debug('Veriff event hook: %s' % data)
        session_id = data['id']
        q = (model.Session.query(model.Verifflog)
             .filter_by(session_id=session_id))
        item = q.first()
        if item:
            self.request._log_userid = item.creator
            code = data['code']
            if code == 7001:
                item.started = datetime.now()
            elif code == 7002:
                item.submitted = datetime.now()
            model.Session.commit()
            rc = True
        return {'accepted': rc}

    @action(renderer='json')
    def decision(self):
        "Webhook verifitseerimise otsuse saamiseks"
        rc = False
        payload = self._check_webhook_input()
        if payload:
            data = json.loads(payload)        
            #log.debug('Veriff decision: %s' % data)
            if data:
                verif = data['verification']
                vendorData = verif['vendorData']
                # otsuse korral ei saa kirjet leida session_id järgi,
                # sest resubi korral on Veriffil uus session_id, mida me ei tea
                try:
                    verifflog_id = int(vendorData)
                except:
                    verifflog_id = None
                item = None
                if verifflog_id:
                    # variant 1: vendorData on verifflog.id (mille seansi loomisel saatsime)
                    item = model.Verifflog.get(verifflog_id)
                    if not item:
                        # variant 2: vendorData on enne 7.apr saadetud sooritus.id, leiame session_id järgi
                        session_id = verif['id']
                        q = (model.Session.query(model.Verifflog)
                             .filter_by(session_id=session_id))
                        item = q.first()
                else:
                    # variant 3: vendorData on algse sessiooni ID
                    session_id = vendorData
                    q = (model.Session.query(model.Verifflog)
                        .filter_by(session_id=session_id))
                    item = q.first()

                if not item:
                    log.error(f'Webhook: verifikatsioon puudub vendorData {vendorData}, data: {data}')
                else:
                    # kirje leitud
                    self.request._log_userid = item.creator                    
                    status = verif['status'] # declined
                    person = verif['person']
                    document = verif['document']

                    item.dec_data = payload
                    item.code = code = verif['code']
                    item.isikukood = idNumber = person.get('idNumber')
                    item.riik = country = document['country']

                    #verif.get('status') # declined
                    #verif.get('reason') # Name entered does not match name on document
                    #verif.get('reasonCode') # 104

                    ik = None
                    q = (model.Session.query(model.Kasutaja.isikukood)
                         .filter_by(id=item.kasutaja_id))
                    for r in q.all():
                        ik = r[0]
                        break

                    item.rc = code == 9001 and country == 'EE' and idNumber == ik
                    model.Session.commit()
                    rc = True
        return {'accepted': rc}

    def _check_webhook_input(self):
        integration_id = self.request.matchdict.get('int_id')
        settings = self.request.registry.settings
        pub_key = settings.get(f'veriff.{integration_id}.pub_key')
        secret = settings.get(f'veriff.{integration_id}.secret')

        # testimise jaoks
        # bash scripts/test_veriff_decision.sh
        #pub_key = '8e4f7cd8-7a19-4d7d-971f-a076407ee03c'
        #secret = '3c184872-6929-43d9-91d5-9e68468b5aa1'

        item = None
        payload = self.request.body.decode('utf-8')
        x_auth_client = self.request.headers.get('x-auth-client')
        x_signature = self.request.headers.get('x-signature')
        sig = _generate_signature(payload, secret)
        if x_auth_client != pub_key:
            log.error('Vale x-auth-client {s}'.format(s=x_auth_client))
        elif sig != x_signature:
            log.error('Vale x-signature {s}'.format(s=x_signature))
        else:
            return payload

    def _log_params_end(self, isikukood=None):
        try:
            # webhooki logimisel kasutame sooritaja isikukoodi
            userid = self.request._log_userid
            tyyp = const.LOG_WEBHOOK
        except:
            userid = None
            tyyp = const.LOG_USER
        return super()._log_params_end(userid, tyyp=tyyp)

def _generate_signature(payload, secret):
    sha_signature = hashlib.sha256(f'{payload}{secret}'.encode()).hexdigest()
    #print(f'{payload}{secret}')
    #print(sha_signature)
    return sha_signature
        
