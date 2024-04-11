from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class TagastusymbrikudController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Tagastusymbrik
    _INDEX_TEMPLATE = '/ekk/korraldamine/tagastus.ymbrikud.mako' 
    _LIST_TEMPLATE = '/ekk/korraldamine/tagastus.ymbrikud_list.mako'
    _DEFAULT_SORT = '-tagastusymbrik.id'

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.testikoht_id:
            q = q.filter(model.Testikoht.id==int(self.c.testikoht_id))
        elif self.c.piirkond_id:
            f = []
            prk = model.Piirkond.get(self.c.piirkond_id)
            for prk_id in prk.get_alamad_id():
                f.append(model.Koht.piirkond_id==prk_id)
            q = q.filter(sa.or_(*f))

        if self.c.staatus:
            q = q.filter(model.Tagastusymbrik.staatus==int(self.c.staatus))
            
        return q

    def _query(self):       
        staatused = [const.M_STAATUS_LOODUD,
                     const.M_STAATUS_VALJASTATUD,
                     const.M_STAATUS_TAGASTAMISEL,
                     const.M_STAATUS_TAGASTATUD,
                     const.M_STAATUS_HINDAJA,
                     const.M_STAATUS_HINNATUD,
                     ]
        self.c.opt_staatus = [(s, self.c.opt.M_STAATUS.get(s)) for s in staatused]

        q = model.SessionR.query(model.Tagastusymbrik,
                                model.Tagastusymbrikuliik.nimi,
                                model.Testipakett.lang,
                                model.Koht.nimi,
                                model.Kasutaja.nimi)
        q = q.join(model.Tagastusymbrik.testipakett).\
            outerjoin(model.Tagastusymbrik.testiprotokoll).\
            join(model.Testipakett.testikoht).\
            filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id).\
            join(model.Testikoht.koht).\
            outerjoin(model.Tagastusymbrik.tagastusymbrikuliik).\
            outerjoin(model.Tagastusymbrik.labiviija).\
            outerjoin(model.Labiviija.kasutaja)
        
        return q

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))

    def _perm_params(self):
        return {'obj':self.c.toimumisaeg.testiosa.test}
