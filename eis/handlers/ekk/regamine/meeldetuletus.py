# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class MeeldetuletusController(BaseResourceController):
    """Registreerunutele kirja saatmine
    """
    _permission = 'regamine'
    _MODEL = model.Sooritaja
    _EDIT_TEMPLATE = 'ekk/regamine/meeldetuletus.mail.mako'
    actions = 'new,create'

    def new(self):
        c = self.c
        sooritajad_id = self.request.params.getall('j_id')
        self._get_to_list(sooritajad_id)
        rcd = model.Tyyptekst.query.filter_by(tyyp=model.Kiri.TYYP_MEELDETULETUS).first()
        if rcd:
            c.subject = rcd.teema
            c.body = rcd.sisu
        return self.render_to_response(self._EDIT_TEMPLATE)
        
    def _get_to_list(self, sooritajad_id):
        c = self.c
        c.to_list = []
        c.miss_list = []
        li_sooritajad_id = []
        
        for sooritaja_id in sooritajad_id:
            sooritaja = model.Sooritaja.get(sooritaja_id)
            k = sooritaja.kasutaja
            to = k.epost
            if to:
                li_sooritajad_id.append(sooritaja_id)
                c.to_list.append(to)
            else:
                c.miss_list.append(k.nimi)
        c.sooritajad_id = ','.join(li_sooritajad_id)
        if not c.to_list:
            self.error(_("Pole e-posti aadresse"))
        if c.miss_list:
            self.error(_("Pole e-posti aadresse") + ': ' + ', '.join(c.miss_list))


    def _create(self):
        sooritajad_id = self.request.params.get('sooritajad_id') or ''
        li_sooritajad_id = sooritajad_id.split(',')
        self.form = Form(self.request, schema=forms.ekk.regamine.MeeldetuletusForm)
        if not self.form.validate():
            self._get_to_list(li_sooritajad_id)
            html = self.form.render(self._EDIT_TEMPLATE,
                                    extra_info=self.response_dict)            
            return Response(html)
        subject = self.form.data['subject']
        body = self.form.data['body']

        if self.form.data.get('setdef'):
            rcd = model.Tyyptekst.query.filter_by(tyyp=model.Kiri.TYYP_MEELDETULETUS).first()
            if not rcd:
                rcd = model.Tyyptekst(tyyp=model.Kiri.TYYP_MEELDETULETUS)
            rcd.teema = subject
            rcd.sisu = body
            model.Session.commit()
            
        miss_list = []
        to_list = []
        for sooritaja_id in li_sooritajad_id:
            if not sooritaja_id:
                continue
            sooritaja = model.Sooritaja.get(sooritaja_id)
            kasutaja = sooritaja.kasutaja
            to = kasutaja.epost
            if not to:
                miss_list.append(kasutaja.nimi)
            else:
                body = Mailer.replace_newline(body)
                if not Mailer(self).send(to, subject, body):
                    sooritaja.meeldetuletusaeg = datetime.now()
                    kiri = model.Kiri(saatja_kasutaja_id=self.c.user.id,
                                      tyyp=model.Kiri.TYYP_MEELDETULETUS,
                                      sisu=body,
                                      teema=subject,
                                      teatekanal=const.TEATEKANAL_EPOST)
                    model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)
                    model.Kirjasaaja(kiri=kiri, kasutaja=kasutaja, epost=to)
                    
                    log.debug(_("Saadetud kiri aadressile {s}").format(s=to))
                    #self.success(_(u"Saadetud kiri aadressile %s") % (to))
                    to_list.append(to)
                    model.Session.commit()
        if to_list:
            self.success(_("Saadetud kiri aadressile {s}").format(s=', '.join(to_list)))
                
        if miss_list:
            self.error(_("Pole e-posti aadresse") + ': ' + ', '.join(miss_list))
            
        return HTTPFound(location=self.url('regamised'))
