from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class SooritajateolekController(BaseResourceController):
    """Antud testi sooritajate oleku päring
    """
    _permission = 'aruanded-sooritajatearv'
    _INDEX_TEMPLATE = 'ekk/otsingud/sooritajateolekud.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/sooritajateolekud_list.mako'
    _SEARCH_FORM = forms.ekk.otsingud.SooritajateolekForm 
    _ignore_default_params = ['csv','otsi']
    _actions = 'index'
    _no_paginate = True
    _DEFAULT_SORT = 'testiosa.seq,sooritus.staatus'
    
    def _query(self):
        return 

    def _search(self, q1):
        c = self.c

        if not c.test_id:
            return
        test = model.Test.get(c.test_id)
        if not test:
            self.error(_("Testi ei leitud!"))
            return
        tk_id = None
        if c.kord_tahis:
            qtk = (model.Session.query(model.Testimiskord.id)
                   .filter_by(test_id=test.id)
                   .filter_by(tahis=c.kord_tahis))
            tk_id = qtk.scalar()
            if not tk_id:
                self.error(_("Testimiskorda ei leitud!"))
                return
        
        q = (model.Session.query(model.Sooritus.testiosa_id,
                                 model.Testiosa.nimi,
                                 model.Testiosa.seq,
                                 model.Sooritus.staatus,
                                 sa.func.count(model.Sooritus.id))
             .join(model.Sooritus.sooritaja)
             .join(model.Sooritus.testiosa)
             .filter(model.Sooritaja.test_id==test.id)
             )
        if tk_id:
            q = q.filter(model.Sooritaja.testimiskord_id==tk_id)

        q = q.group_by(model.Sooritus.testiosa_id,
                       model.Testiosa.nimi,
                       model.Testiosa.seq,
                       model.Sooritus.staatus)
        
        c.prepare_item = self._prepare_item
        c.prepare_header = self._prepare_header
        if c.csv:
            # väljastame CSV
            return self._index_csv(q)
        return q
    
    def _prepare_header(self):
        header = [(None, _("Testiosa")),
                  (None, _("Olek")),
                  (None, _("Sooritajate arv")),
                  ]       
        return header

    def _prepare_item(self, rcd, n=None):
        c = self.c
        h = self.h
        osa_id, osa_nimi, osa_seq, staatus, cnt = rcd
        st_nimi = self.c.opt.S_STAATUS.get(staatus) or staatus
        item = [osa_nimi, st_nimi, cnt]
        return item
