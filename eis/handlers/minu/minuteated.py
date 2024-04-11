"Kasutaja saab vaadata talle saadetud teateid"
from eis.lib.baseresource import *
log = logging.getLogger(__name__)
_ = i18n._
class MinuteatedController(BaseResourceController):
    _permission = 'minu'
    _get_is_readonly = False
    _actions = 'index,show,create,download'
    _INDEX_TEMPLATE = 'minu/minuteated.mako'
    _EDIT_TEMPLATE = 'minu/minuteade.mako' 
    _LIST_TEMPLATE = 'minu/minuteated_list.mako'
    _MODEL = model.Kirjasaaja
    _DEFAULT_SORT = '-kirjasaaja.id'
    _SEARCH_FORM = forms.minu.MinuteatedForm 
    
    def _query(self):
        c = self.c
        q = (model.Session.query(model.Kirjasaaja, model.Kiri)
             .filter(model.Kirjasaaja.kasutaja_id==c.user.id)
             .join(model.Kirjasaaja.kiri))
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        self._set_6m_read()
        
        if not c.staatus:
            c.staatus = [const.KIRI_UUS, const.KIRI_LOETUD]
        q = q.filter(model.Kirjasaaja.staatus.in_(c.staatus))

        if c.teatekanal:
            q = q.filter(model.Kiri.teatekanal==c.teatekanal)

        c.user.get_new_msg(self.request.session, 0)

        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item
        return q

    def _set_6m_read(self):
        "Rohkem kui 6 kuud vanad lugemata kirjad märgime loetud kirjadeks"
        c = self.c
        m6 = datetime.now() - timedelta(days=180)
        upd = (model.Kirjasaaja.__table__.update()
               .values(staatus=const.KIRI_LOETUD)
               .where(sa.and_(model.Kirjasaaja.kasutaja_id==c.user.id,
                              model.Kirjasaaja.staatus==const.KIRI_UUS,
                              model.Kirjasaaja.created < m6))
               )
        cnt = model.Session.execute(upd).rowcount
        if cnt:
            model.Session.commit()

    def _prepare_header(self):
        header = [('kiri.teatekanal', _("Edastuskanal")),
                  ('kirjasaaja.epost', _("Aadress")),
                  ('kirjasaaja.created', _("Saatmise või koostamise aeg")),
                  ('kiri.teema,kiri.tyyp', _("Teema")),
                  ]
        return header
    
    def _prepare_item(self, row, n):
        ks, kiri = row
        item = [kiri.teatekanal_nimi,
                ks.epost,
                self.h.str_from_datetime(ks.created),
                kiri.teema or kiri.tyyp_nimi,
                ]
        return item

    def create(self):
        "Kirjade oleku muutmine"
        c = self.c
        params = self.request.params
        if params.get('loetuks'):
            staatus = const.KIRI_LOETUD
        elif params.get('uueks'):
            staatus = const.KIRI_UUS
        elif params.get('arhiivi'):
            staatus = const.KIRI_ARHIIV
        elif params.get('arhiivist'):
            staatus = const.KIRI_LOETUD
        else:
            staatus = None
        if staatus:
            kss_id = params.getall('ks_id')
            for ks_id in kss_id:
                ks = model.Kirjasaaja.get(ks_id)
                if ks.kasutaja_id == c.user.id:
                    ks.staatus = staatus
            model.Session.commit()
            c.user.get_new_msg(self.request.session, 0)
        return self._redirect('index')

    def _show(self, item):
        c = self.c
        if item.kasutaja_id != c.user.id:
            return Response(_("Puudub ligipääsuõigus"))
        c.ks = item
        c.kiri = item.kiri
        if item.staatus == const.KIRI_UUS:
            # kui kiri on uus, siis märgime loetuks
            item.staatus = const.KIRI_LOETUD
            model.Session.commit()
            c.user.get_new_msg(self.request.session, 0)
            c.just_loeti = True
            
    def _download(self, id, format=None):
        ks = model.Kirjasaaja.get(id)
        kiri = ks and ks.kiri
        if not kiri or not kiri.has_file or ks.kasutaja_id != self.c.user.id:
            raise NotFound('Kirjet %s ei leitud' % id)
        return utils.download(kiri.filedata, kiri.filename, kiri.mimetype)

        
