from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class YmbrikudController(BaseResourceController):

    _permission = 'hindamisanalyys'
    _MODEL = model.Tagastusymbrik
    _INDEX_TEMPLATE = 'ekk/hindamine/analyys.ymbrikud.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/analyys.ymbrikud_list.mako'
    _DEFAULT_SORT = 'tagastusymbrik.id' # vaikimisi sortimine

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.probleem == 'maaramata':
            q = q.filter(model.Tagastusymbrik.staatus < const.M_STAATUS_HINDAJA)
        elif self.c.probleem == 'tagastamata':
            q = q.filter(model.Tagastusymbrik.staatus==const.M_STAATUS_HINDAJA)
        else:
            q = q.filter(model.Tagastusymbrik.staatus!=const.M_STAATUS_HINNATUD)

        if self.c.csv:
            return self._index_csv(q)
        return q

    def _search_default(self, q):
        return self._search(q)

    def _query(self):
        q = model.SessionR.query(model.Tagastusymbrik, 
                                model.Testiprotokoll,
                                model.Testikoht,
                                model.Kasutaja.nimi)
        q = q.join(model.Tagastusymbrik.testiprotokoll).\
            filter(model.Testiprotokoll.tehtud_toodearv>0).\
            join(model.Testiprotokoll.testipakett).\
            join(model.Testipakett.testikoht).\
            filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id).\
            outerjoin(model.Tagastusymbrik.tagastusymbrikuliik).\
            join(model.Testikoht.koht).\
            outerjoin(model.Tagastusymbrik.labiviija).\
            outerjoin(model.Labiviija.kasutaja)

        return q

    def _prepare_header(self):
        header = [_("Soorituskoht"),
                  _("Ümbriku tähis"),
                  _("Ümbriku liik"),
                  _("Läbiviija"),
                  ]
        return header
    
    def _prepare_item(self, rcd, n):
        ymbrik, tpr, testikoht, hindaja_nimi = rcd
        item = [testikoht.koht.nimi,
                '%s-%s' % (tpr.tahised, ymbrik.tagastusymbrikuliik.tahis),
                ymbrik.tagastusymbrikuliik.nimi,
                hindaja_nimi,
                ]
        return item

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.test = self.c.toimumisaeg.testiosa.test
        
    def _perm_params(self):
        return {'obj': self.c.test}
