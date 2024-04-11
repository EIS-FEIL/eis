from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.hindamiserinevused import HindamiserinevusedDoc

log = logging.getLogger(__name__)

class TugiisikudController(BaseResourceController):
    """Tugiisikute päring
    """
    _permission = 'aruanded-tugiisikud'
    _INDEX_TEMPLATE = 'ekk/otsingud/tugiisikud.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/tugiisikud_list.mako'
    _ignore_default_params = ['csv']
    _actions = 'index'
    
    @property
    def _DEFAULT_SORT(self):
        if self.c.kokku:
            return 'toimumisaeg.tahised'
        else:
            return 'toimumisaeg.tahised,kasutaja.nimi,sooritaja.eesnimi,sooritaja.perenimi'
    
    def _query(self):
        q = model.Session.query(model.Test.id,
                                model.Test.nimi,
                                model.Toimumisaeg.tahised,
                                model.Sooritaja.eesnimi,
                                model.Sooritaja.perenimi,
                                model.Sooritus.tahised,
                                model.Kasutaja.nimi)
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        c.prepare_header = self._prepare_header
        c.prepare_item = self._prepare_item
        if not c.test_id and not c.isikukood:
            if c.otsi:
                self.error(_("Palun sisestada testi ID või isikukood"))
            return
        
        if c.kokku:
            # tugiisikuga soorituste arv kokku
            q = (model.Session.query(model.Test.id,
                                     model.Test.nimi,
                                     model.Toimumisaeg.tahised,
                                     sa.func.count(model.Sooritus.id)))
        q = (q.join(model.Sooritaja.test)
             .join(model.Sooritaja.sooritused)
             .outerjoin(model.Sooritus.toimumisaeg)
             .join(model.Sooritus.tugiisik_kasutaja)
             )
        # päringu kiirendamiseks rõhutame tingimust
        q = q.filter(model.Sooritus.tugiisik_kasutaja_id!=None)

        if c.test_id:
            q = q.filter(model.Sooritaja.test_id==c.test_id)
        if c.kord_tahis:
            q = q.join(model.Sooritaja.testimiskord)
            q = q.filter(model.Testimiskord.tahis==c.kord_tahis)
        if c.testiliik:
            q = q.filter(model.Test.testiliik_kood==c.testiliik)
        if c.isikukood:
            usp = validators.IsikukoodP(c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))

        if c.kokku:
            q = q.group_by(model.Test.id,
                           model.Test.nimi,
                           model.Toimumisaeg.tahised)
        if c.csv:
            return self._index_csv(q)
        return q

    def _order_able(self, q, field):
        if self.c.kokku:
            return field  in ('test.id',
                              'test.nimi',
                              'toimumisaeg.tahised')
        else:
            return super()._order_able(q, field)
        
    def _prepare_header(self):
        c = self.c
        if c.kokku:
            header = [('test.id', _("Testi ID")),
                      ('test.nimi', _("Test")),
                      ('toimumisaeg.tahised', _("Toimumisaja tähis")),
                      (None, _("Tugiisikuga soorituste arv")),
                      ]
        else:
            header = [('test.id', _("Testi ID")),
                      ('test.nimi', _("Test")),
                      ('toimumisaeg.tahised', _("Toimumisaja tähis")),
                      ('sooritus.tahis', _("Soorituse tähis")),
                      ('sooritaja.eesnimi,sooritaja.perenimi', _("Sooritaja")),
                      ('kasutaja.nimi', _("Tugiisik")),
                      ]
            
        return header
    
    def _prepare_item(self, rcd, n):
        c = self.c
        if c.kokku:
            # tugiisikuga soorituste arv
            t_id, t_nimi, ta_tahised, cnt = rcd
            item = [t_id,
                    t_nimi,
                    ta_tahised,
                    cnt]
        else:
            # tugiisikuga sooritused
            t_id, t_nimi, ta_tahised, j_eesnimi, j_perenimi, s_tahis, ti_nimi = rcd
            item = [t_id,
                    t_nimi,
                    ta_tahised,
                    s_tahis,
                    f'{j_eesnimi} {j_perenimi}',
                    ti_nimi]
        return item
