from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class TestidController(BaseResourceController):
    """Kasutamise ajalugu
    """
    _permission = 'ylesanded'
    _no_paginate = True
    _MODEL = model.Ylesanne
    _INDEX_TEMPLATE = 'ekk/ylesanded/testid.mako'
    _ITEM_FORM = None #forms.ekk.ylesanded.MuutjadForm 
    _DEFAULT_SORT = 'test.id,toimumisaeg.tahised' # vaikimisi sortimine
    _UNIQUE_SORT = 'test.id,toimumisaeg.id,komplekt.tahis'
    
    def _query(self):
        return model.Session.query(model.Test.id,
                                   model.Test.nimi,
                                   model.Test.testityyp,
                                   model.Toimumisaeg.id,
                                   model.Toimumisaeg.tahised,
                                   model.Komplekt.tahis,
                                   sa.func.count(model.Ylesandevastus.id),
                                   sa.func.avg(model.Ylesandevastus.pallid))

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        q = (q.join(model.Test.valitudylesanded)
             .filter(model.Valitudylesanne.ylesanne_id==self.c.ylesanne.id)
             .join(model.Valitudylesanne.komplekt)
             .outerjoin((model.Ylesandevastus,
                         sa.and_(model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id,
                                 model.Ylesandevastus.pallid!=None)))
             .outerjoin((model.Sooritus, model.Ylesandevastus.sooritus_id==model.Sooritus.id))
             .outerjoin(model.Sooritus.toimumisaeg)
             )
        q = q.group_by(model.Test.id,
                       model.Test.nimi,
                       model.Test.testityyp,
                       model.Toimumisaeg.id,
                       model.Toimumisaeg.tahised,
                       model.Komplekt.tahis)
        return q

    def _paginate(self, q):
        items1 = []
        items2 = []
        max_p = self.c.item.max_pallid
        total_cnt = 0
        total_prot = None
        
        def add_weighted(new_prot, new_cnt):
            if total_prot is None:
                return new_prot
            elif new_prot is None or not new_cnt:
                return total_prot
            else:
                return (total_cnt*total_prot + new_cnt*new_prot)/(total_cnt+new_cnt)
        #model.log_query(q)
        for rcd in q.all():
            test_id, test_nimi, testityyp, ta_id, ta_tahised, k_tahis, r_cnt, r_avg = rcd
            if max_p and r_avg is not None:
                prot = r_avg / max_p * 100
            else:
                prot = None
            row = (test_id, test_nimi, ta_id, ta_tahised, k_tahis, r_cnt, prot)
            if testityyp == const.TESTITYYP_EKK:
                items1.append(row)
                total_prot = add_weighted(prot, r_cnt)
                total_cnt += r_cnt
            else:
                items2.append(row)

        if len(items1) > 1:
            self.c.total = {'lahendatavus': total_prot,
                            'sooritajate_arv': total_cnt,
                            }
        self.c.items1 = items1
        self.c.items2 = items2
        return items1
        
    # def create(self):
    #     """Kanname ühe testimiskorra statistika ülesande üldandmetesse"""
    #     rc = False
    #     suffix = None
    #     for key in self.request.params:
    #         if key.startswith('kasuta_'):
    #             suffix = key[len('kasuta_'):]
    #             break
    #     if suffix:
    #         lahendatavus = self.request.params.get(f'lahendatavus_{suffix}')
    #         if lahendatavus:
    #             self.c.ylesanne.lahendatavus = float(lahendatavus)
    #             model.Session.commit()
    #             self.success(_("Lahendatavus on kantud ülesande üldandmete lehele"))

    #     return self._redirect('index')        

    def __before__(self):
        ylesanne_id = self.request.matchdict.get('ylesanne_id')
        self.c.item = self.c.ylesanne = model.Ylesanne.get(ylesanne_id)

    def _perm_params(self):
        return {'obj':self.c.ylesanne}
