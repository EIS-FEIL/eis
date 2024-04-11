# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class EttepanekudController(BaseResourceController):
    _permission = 'ettepanemine'
    _MODEL = model.Ettepanek
    _EDIT_TEMPLATE = 'avalik/ettepanek.mako'
    _ITEM_FORM = forms.avalik.ettepanek.EttepanekForm

    def _new(self, item):
        kasutaja = self.c.user.get_kasutaja()
        if kasutaja:
            item.epost = kasutaja.epost
            item.kasutaja_id = kasutaja.id

    def _create(self, **kw):
        kasutaja = self.c.user.get_kasutaja()
        referer = (self.request.environ.get('HTTP_REFERER') or '')[:150]
        item = model.Ettepanek(kasutaja_id=kasutaja.id,
                               koht_id=self.c.user.koht_id or None,
                               saatja=self.c.user.fullname,
                               epost=self.form.data['epost'],
                               teema=self.form.data['teema'],
                               sisu=self.form.data['sisu'],
                               ootan_vastust=self.form.data['ootan_vastust'],
                               url=referer)
        self.c.item = item
        try:
            body = Mailer.replace_newline(item.sisu)
            kust = item.epost or ''
            koht = self.c.user.koht
            if koht:
                kust += ", %s" % koht.nimi
                
            body += "<hr/><i>Kirja on saatnud %s (%s) EISi kaudu, viibides leheküljel %s.<br/>\n Pöörduja %s.</i>" % \
                    (item.saatja, kust, referer, item.ootan_vastust and _("ootab vastust") or _("ei oota vastust"))
            Mailer(self).send_ettepanek(item.saatja, item.epost, item.teema, body)
        except Exception as e:
            msg = self._error(e, _("Ei saa kirja saata"))
            self.error(_("Kirja saatmine ebaõnnestus"))
        else:
            log.debug(_("Saadetud ettepanek {s1} kasutajalt {s2}").format(s1=item.teema, s2=item.saatja))

        return item

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            self.c.saadetud_ok = True
        return self.render_to_response(self._EDIT_TEMPLATE)
