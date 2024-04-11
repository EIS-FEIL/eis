from eis.lib.baseresource import *
log = logging.getLogger(__name__)
_ = i18n._

class LaadimineController(BaseResourceController):
    """Väljaspool EISi digiallkirjastatud tunnistuste salvestamine EISi andmebaasi
    """
    _permission = 'skannid'
    _MODEL = model.Sooritus
    _INDEX_TEMPLATE = 'ekk/muud/skannid.laadimine.mako'
    _EDIT_TEMPLATE = 'ekk/muud/skannid.laadimine.mako'    
    _index_after_create = True

    def _get_current_upath(self):
        "Tegevuse tunnus, mille järgi jäetakse meelde vaikimisi parameetrid"
        # sama create ja index korral
        return '/muud/skannid/laadimised'

    def _create(self):
        params = self.request.params
        dp = {'sessioon_id': params.get('sessioon_id'),
              'test_id': params.get('test_id'),
              'toimumisaeg_id': params.get('toimumisaeg_id'),
              }
        self._set_default_params(dp)
        value = params.get('file')
        res = {}
        if value != None and value != b'' and value.file:
            fname = _fn_local(value.filename)
            item, err = self._get_sooritus(fname)
            if item:
                sf = item.skannfail
                if not sf:
                    sf = model.Skannfail(sooritus_id=item.id)
                sf.filename = fname
                sf.filedata = value.value
                model.Session.commit()
                msg, err = send_skann_epost(self, item, sf)
                res['msg'] = msg
            res['filename'] = fname
            res['error'] = err
        return Response(json_body=res)

    def _get_sooritus(self, fname):
        sooritus = err = None
        toimumisaeg_id = self.request.params.get('toimumisaeg_id')
        try:
            tookood, ext = fname.split('.')[-2:]
        except:
            tookood = ext = None

        if not tookood or not re.match(r'^\d{1,3}-\d{1,3}$', tookood):
            err = _("Failinimest ei leitud töökoodi")
        elif not ext or ext.lower() != 'pdf':
            err = _("Fail ei ole PDF")
        else:
            q = (model.Session.query(model.Sooritus)
                 .filter(model.Sooritus.toimumisaeg_id==toimumisaeg_id)
                 .filter(model.Sooritus.tahised==tookood)
                 )
            sooritus = q.first()

        if not sooritus:
            err = _("Tööd koodiga {s} ei leitud").format(s=tookood)
        elif not sooritus.soovib_skanni:
            sooritus = None
            err = _("Sooritaja pole faili tellinud")
        return sooritus, err

def send_skann_epost(handler, sooritus, sf):
    err = msg = None
    request = handler.request
    sooritaja = sooritus.sooritaja
    test = sooritaja.test
    kasutaja = sooritaja.kasutaja
    to = kasutaja.epost
    if to:
        pw_host = request.registry.settings.get('eis.pw.url')
        url = '%s/eis/tulemused/%d' % (pw_host, sooritaja.id)
        juhend_url = sooritaja.testimiskord.tutv_hindamisjuhend_url
        data = {'isik_nimi': kasutaja.nimi,
                'test_nimi': test.nimi,
                'url': url,
                'juhend_url': juhend_url,
                }
        mako = 'mail/skann.laaditud.mako'
        subject, body = handler.render_mail(mako, data)
        body = Mailer.replace_newline(body)
        err = Mailer(handler).send(to, subject, body, out_err=False)
        if not err:
            sf.teatatud = datetime.now()
            kiri = model.Kiri(saatja_kasutaja_id=handler.c.user.id,
                              tyyp=model.Kiri.TYYP_SKANN_LAADITUD,
                              sisu=body,
                              teema=subject,
                              teatekanal=const.TEATEKANAL_EPOST)
            model.Kirjasaaja(kiri=kiri, kasutaja_id=kasutaja.id, epost=to)
            model.Session.commit()
            log.debug('Kiri saadetud %s' % to)
            msg = _("Kiri saadetud")
    return msg, err

        
def _fn_local(fnPath):
    """
    Rajast eraldatakse failinimi.
    """
    pos = max(fnPath.rfind('\\'), fnPath.rfind('/'))
    if pos > -1:
        return fnPath[pos + 1:]
    else:
        return fnPath
        
