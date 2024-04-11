# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class EttepanekudController(BaseResourceController):
    _permission = 'ettepanekud'

    _MODEL = model.Ettepanek
    _SEARCH_FORM = forms.ekk.muud.EttepanekudForm
    _ITEM_FORM = forms.ekk.muud.EttepanekForm
    _INDEX_TEMPLATE = 'ekk/muud/ettepanekud.mako' # otsinguvormi mall
    _LIST_TEMPLATE = 'ekk/muud/ettepanekud_list.mako'
    _EDIT_TEMPLATE = 'ekk/muud/ettepanek.mako'
    _DEFAULT_SORT = '-ettepanek.id' # vaikimisi sortimine
    
    def _query(self):
        q = (model.SessionR.query(model.Ettepanek, model.Koht.nimi)
             .outerjoin(model.Ettepanek.koht))
        self.c.header = self._prepare_header()
        return q
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.alates:
            q = q.filter(model.Ettepanek.created >= self.c.alates)
        if self.c.kuni:
            q = q.filter(model.Ettepanek.created < self.c.kuni + timedelta(1))
        if self.c.teema:
            q = q.filter(model.Ettepanek.teema.ilike(self.c.teema))
        if self.c.sisu:
            q = q.filter(model.Ettepanek.sisu.ilike(self.c.sisu))
        if self.c.saatja:
            q = q.filter(model.Ettepanek.saatja.ilike(self.c.saatja))
        if self.c.csv:
            return self._index_csv(q)
        return q

    def _prepare_header(self):
        "Loetelu päis"
        li = [('ettepanek.created', _("Aeg")),
              ('ettepanek.saatja', _("Esitaja")),
              ('ettepanek.epost', _("E-post")),
              ('koht.nimi', _("Kool")),
              ('ettepanek.url', _("URL")),
              ('ettepanek.teema', _("Teema")),
              ]
        if self.c.csv:
            li.append(('ettepanek.sisu', _("Sisu")))
        li.extend([('ettepanek.ootan_vastust', _("Ootab vastust")),
                   ('ettepanek.on_vastatud', _("Vastatud")),
                   ])
        if self.c.csv:
            li.append(('ettepanek.vastus', _("Vastus")))
        return li
        
    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        h = self.h
        rcd, koht_nimi = rcd
        return [h.str_from_datetime(rcd.created),
                rcd.saatja,
                rcd.epost,
                koht_nimi,
                rcd.url,
                rcd.teema,
                rcd.sisu,
                h.sbool(rcd.ootan_vastust),
                h.sbool(rcd.on_vastatud),
                rcd.vastus,
                ]

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            self.success()
            return self._redirect('index')
        else:
            return self._redirect('edit', id)
