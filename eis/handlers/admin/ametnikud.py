from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from .kasutajad import KasutajadController
log = logging.getLogger(__name__)

class AmetnikudController(KasutajadController):
    "Eksamikeskuse kasutajad"

    _MODEL = model.Kasutaja
    _SEARCH_FORM = forms.admin.AmetnikudForm
    _ITEM_FORM = forms.admin.AmetnikForm
    _INDEX_TEMPLATE = '/admin/ametnikud.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = '/admin/ametnik.mako' # muutmisvormi mall
    _LIST_TEMPLATE = '/admin/ametnikud_list.mako'
    _DEFAULT_SORT = 'perenimi'

    _permission = 'ametnikud'

    def _query(self):
        q = model.SessionR.query(model.Kasutaja)
        return q
    
    def _search_default(self, q):
        self.c.amkehtib = 1
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.isikukood:
            q = q.filter(eis.forms.validators.IsikukoodP(c.isikukood).filter(model.Kasutaja))
            item = q.first()
            if item and not item.on_ametnik:
                self.error(_("See isik ei ole eksamikeskuse kasutaja"))

        elif not c.roll_id:
            q = q.filter(model.Kasutaja.on_ametnik==True)

        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))

        if c.roll_id or c.aine or c.oigus_id or c.rollisikukood or c.jira_nr:
            stmt = (sa.sql.exists()
                    .where(model.Kasutajaroll.kasutaja_id==model.Kasutaja.id)
                    .where(model.Kasutajaroll.kasutajagrupp.has(
                        model.Kasutajagrupp.tyyp.in_(
                            (const.USER_TYPE_EKK, const.USER_TYPE_AV))))
                    )
            if c.roll_id:
                stmt = stmt.where(model.Kasutajaroll.kasutajagrupp_id==c.roll_id)
            if c.oigus_id:
                stmt = stmt.where(sa.and_(
                    model.Kasutajaroll.kasutajagrupp_id==model.Kasutajagrupp_oigus.kasutajagrupp_id,
                    model.Kasutajagrupp_oigus.kasutajaoigus_id==c.oigus_id))
            if not c.kehtetu:
                stmt = stmt.where(sa.and_(model.Kasutajaroll.kehtib_kuni>=date.today(),
                                          model.Kasutajaroll.kehtib_alates<=date.today()))
            elif c.kehtetu and not c.kehtib:
                stmt = stmt.where(sa.or_(model.Kasutajaroll.kehtib_kuni<date.today(),
                                         model.Kasutajaroll.kehtib_alates>date.today()))                
            if c.aine:
                stmt = stmt.where(model.Kasutajaroll.aine_kood==c.aine)

            if c.rollisikukood or c.jira_nr:
                fkrl1 = fkrl2 = None
                if c.rollisikukood:
                    qr = (model.Kasutaja.query
                          .filter(eis.forms.validators.IsikukoodP(c.rollisikukood)
                                  .filter(model.Kasutaja))
                          )
                    muutjak = qr.first()
                    muutjak_id = muutjak and muutjak.id or -1
                    fkrl1 = (model.Kasutajarollilogi.muutja_kasutaja_id==muutjak_id)
                if c.jira_nr:
                    fkrl2 = (model.Kasutajarollilogi.jira_nr==c.jira_nr)
                fkrl = fkrl1 and fkrl2 and sa.and_(fkrl1, fkrl2) or fkrl1 or fkrl2
                stmt = stmt.where(model.Kasutajaroll.kasutajarollilogid.any(fkrl))
                
            q = q.filter(stmt)

        if c.rollita:
            tyybid = (const.USER_TYPE_EKK, const.USER_TYPE_AV)
            q = q.filter(~ model.Kasutaja.kasutajarollid.any(
                   sa.and_(model.Kasutajaroll.kasutajagrupp.has(
                               model.Kasutajagrupp.tyyp.in_(tyybid)),
                           model.Kasutajaroll.kehtib_kuni>=date.today())
                ))
        if c.amkehtib:
            tyybid = (const.USER_TYPE_EKK, const.USER_TYPE_AV)
            q = q.filter(model.Kasutaja.kasutajarollid.any(
                   sa.and_(model.Kasutajaroll.kasutajagrupp.has(
                               model.Kasutajagrupp.tyyp.in_(tyybid)),
                           model.Kasutajaroll.kehtib_kuni>=date.today())
                ))
        if c.csv:
            return self._index_csv(q)
        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item
        return q

    def _prepare_header(self):
        header = [('kasutaja.isikukood', _("Isikukood")),
                  ('kasutaja.eesnimi', _("Eesnimi")),
                  ('kasutaja.perenimi', _("Perekonnanimi")),
                  (None, _("Olek")),
                  ('kasutaja.viimati_ekk', _("Viimati sisse loginud")),
                  ]
        return header
    
    def _prepare_item(self, row, n):
        rcd = row
        item = [rcd.isikukood,
                rcd.eesnimi,
                rcd.perenimi,
                rcd.kehtiv_str,
                self.h.str_from_datetime(rcd.viimati_ekk),
                ]
        return item

    def _edit(self, item):
        self.c.can_set_pwd = self._can_set_pwd(item)
        if not item.on_ametnik:
            if not item.id:
                # uue kasutaja lisamine
                item.on_ametnik = True
        
    def _update(self, item):      
        is_new = not item.id
        item.from_form(self.form.data, 'k_')
        self._save_ik(item)
        parool = self.form.data.get('parool')
        if parool:
            if is_new or self._can_set_pwd(item):
                item.set_password(parool, True)
            else:
                self.error(_("Puudub õigus selle kasutaja parooli muutmiseks"))

    def _has_permission(self):
        rc = KasutajadController._has_permission(self)
        if rc and self.c.item and self.c.is_edit:
            # Admini rolliga kasutajat saab muuta ainult admin
            if self.c.item.on_kehtiv_roll(const.GRUPP_ADMIN):
                if not self.c.user.on_admin:
                    return False
        return rc
