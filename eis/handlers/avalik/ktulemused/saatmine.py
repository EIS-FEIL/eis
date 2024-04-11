from eis.lib.baseresource import *
from eis.lib.feedbackreport import FeedbackReport
_ = i18n._

log = logging.getLogger(__name__)

class SaatmineController(BaseResourceController):
    "Tulemuste saatmine õpilastele"
    _permission = 'avalikadmin,testiadmin,aineopetaja'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'avalik/ktulemused/saatmine.mako'
    _LIST_TEMPLATE = 'avalik/ktulemused/saatmine.saajad_list.mako'
    _DEFAULT_SORT = 'sooritaja.eesnimi,sooritaja.perenimi' 
    _no_paginate = True
    _SEARCH_FORM = forms.avalik.testid.SaatmisnimekiriForm

    _EDIT_TEMPLATE = 'avalik/ktulemused/saatmine.kirjasisu.mako'
    _ITEM_FORM = forms.avalik.testid.KirjasisuForm
    _actions = 'index,create'
    
    def _query(self):
        c = self.c
        q = (model.Session.query(model.Sooritaja, model.Kasutaja.epost)
             .filter(model.Sooritaja.testimiskord_id==c.testimiskord.id)
             .join(model.Sooritaja.kasutaja)
             .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             )
        # oma kooli õpilane või on antud kooli sisseastumistest 
        if c.test.testiliik_kood == const.TESTILIIK_SISSE:
            q = q.filter(model.Sooritaja.kandideerimiskohad.any(
                    model.Kandideerimiskoht.koht_id==c.user.koht_id))
        else:
            q = q.filter(model.Sooritaja.kool_koht_id==c.user.koht_id)
        return q

    def _search_default(self, q):
        return self._search(q)

    def _get_klassid(self, q):
        q1 = (q.with_entities(model.Sooritaja.klass, model.Sooritaja.paralleel)
              .distinct()
              .order_by(model.Sooritaja.klass, model.Sooritaja.paralleel)
              )
        li = []
        for klass, paralleel in q1.all():
            li.append(model.KlassID(klass, paralleel))
        return li
            
    def _search(self, q):
        c = self.c
        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item
        if not c.partial:
            # dialoogi avamisel
            c.klassidID = self._get_klassid(q)
            c.kiri = self._init_mail()

        klassid_paralleel = [model.KlassID.from_id(r) for r in c.klassid_id]
        if klassid_paralleel:
            f = None
            for klassID in klassid_paralleel:
                fitem = sa.and_(model.Sooritaja.klass==klassID.klass,
                                model.Sooritaja.paralleel==klassID.paralleel)
                if f is None:
                    f = fitem
                else:
                    f = sa.or_(f, fitem)
            q = q.filter(f)

        return q

    def _init_mail(self):
        c = self.c
        mako = 'mail/tulemus.avaliktest.mako'
        k = c.user.get_kasutaja()
        data = {'user_nimi': k.nimi,
                'user_epost': k.epost,
                'koht_nimi': c.user.koht_nimi,
                'test_nimi': c.test.nimi,
                }
        subject, body = self.render_mail(mako, data)
        return NewItem(teema=subject, sisu=body)

    def _prepare_header(self):
        c = self.c
        li = [('sooritaja.eesnimi', _("Eesnimi")),
              ('sooritaja.perenimi', _("Perekonnanimi")),
              (None, _("Saadetud")),
              ('kasutaja.epost', _("E-post")),
              ('sooritaja.tulemus_protsent', _("Testi tulemus")),
              ]
        return li

    def _get_sooritajakiri(self, sooritaja):
        "Leitakse, millal sooritajale tulemused saadeti"
        q = (model.Session.query(model.Kiri, model.Kirjasaaja)
             .join(model.Kiri.kirjasaajad)
             .join(model.Kiri.sooritajakirjad)
             .filter(model.Sooritajakiri.sooritaja_id==sooritaja.id)
             .order_by(model.Kiri.created))
        li = []
        for kiri, ks in q.all():
            buf = '%s (%s)' % (self.h.str_from_datetime(kiri.created),
                             kiri.teatekanal_nimi)
            li.append(buf)
        return li

    def _prepare_item(self, rcd, n=None):
        c = self.c
        rcd, epost = rcd
        saadetud = '; '.join(self._get_sooritajakiri(rcd))
        li = [rcd.eesnimi,
              rcd.perenimi,
              saadetud,
              epost,
              rcd.get_tulemus(nl=False, digits=2),
              ]
        return li

    def _create(self):
        c = self.c
        sooritajad_id = list(map(int, [r for r in self.form.data['sooritajad_id'].split(',') if r]))
        if not sooritajad_id:
            raise ValidationError(_("Palun valida sooritajad, kellele teated saata!"))
        teema = self.form.data['teema']
        sisu = self.form.data['sisu']
        body = Mailer.replace_newline(sisu)
        op = self.form.data['op']
        self._send_mail(sooritajad_id, body, teema)

        c.kiri = NewItem(teema=teema, sisu=sisu)
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _send_mail(self, sooritajad_id, body, subject):
        errors = {}
        if not subject:
            errors['teema'] = _("Palun sisestada kirja pealkiri")
        if not body:
            errors['sisu'] = _("Palun sisestada kirja sisu")
        if errors:
            raise ValidationError(self, errors=errors)

        replyto = self.c.user.get_kasutaja().epost
        cnt_ok = cnt_err = 0
        for sooritaja_id in sooritajad_id:
            sooritaja = model.Sooritaja.get(sooritaja_id)
            kasutaja = sooritaja.kasutaja
            epost = kasutaja.epost
            if not epost:
                cnt_err += 1
            else:
                fr = FeedbackReport.init_opilane(self, self.c.test, sooritaja.lang, sooritaja.kursus_kood)
                if fr:
                    filedata = fr.generate_pdf(sooritaja)
                    attachments = [('tulemus.pdf', filedata)]
                else:
                    attachments = []
                try:
                    Mailer(self).send_ex(epost, subject, body, attachments, replyto=replyto)
                except Exception as ex:
                    log.error('ei saa kirja saata: "%s" %s' % (epost, ex))
                    cnt_err += 1
                else:
                    kiri = model.Kiri(saatja_kasutaja_id=self.c.user.id,
                                      tyyp=model.Kiri.TYYP_TULEMUS,
                                      sisu=body,
                                      teema=subject,
                                      teatekanal=const.TEATEKANAL_EPOST)
                    model.Sooritajakiri(sooritaja=sooritaja,
                                        kiri=kiri)
                    model.Kirjasaaja(kiri=kiri, kasutaja=kasutaja, epost=epost)
                    sooritaja.teavitatud_epost = datetime.now()
                    model.Session.commit()
                    cnt_ok += 1

        buf = _("Teade saadeti {n} sooritajale.").format(n=cnt_ok)
        if cnt_err:
            buf += ' ' + _("Ei saanud saata {n} sooritajale.").format(n=cnt_err)
        self.success(buf)

    def __before__(self):
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        testimiskord_id = self.request.matchdict.get('testimiskord_id')
        self.c.testimiskord = model.Testimiskord.get(testimiskord_id)
