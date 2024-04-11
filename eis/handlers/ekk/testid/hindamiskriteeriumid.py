# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class HindamiskriteeriumidController(BaseResourceController):
    """Hindamiskogumi hindamiskriteeriumid
    """
    _permission = 'testimiskorrad'

    _MODEL = model.Hindamiskriteerium
    _EDIT_TEMPLATE = 'ekk/testid/kogum.hindamiskriteerium.mako'
    _LIST_TEMPLATE = 'ekk/testid/kogum.hindamiskriteeriumid.mako'
    _ITEM_FORM = forms.ekk.testid.HindamiskriteeriumForm 

    def _update(self, item, lang=None):
        old_seq = item.seq
        data = self.form.data
        data['a_aine_kood'], data['a_aspekt_kood'] = data['a_aspekt_kood'].split('.', 1)
        item.from_form(data, 'a_')
        if item.max_pallid == None:
            item.max_pallid = 0

        # salvestame punktide kirjeldused
        rows = data['pkirjeldus']
        kirjeldused = {r.punktid: r for r in item.kritkirjeldused}
        punktid = 0
        step = .5
        max_len = round(item.max_pallid / step) + 1
        for cnt in range(max_len):
            # kontroll, et vajalik rida on postitatud
            if len(rows) > cnt:
                row = rows[cnt]
                if row['kirjeldus']:
                    punktid = cnt * step
                    try:
                        # kas punkti kirjeldus on juba varasemast olemas
                        r = kirjeldused.pop(punktid)
                    except KeyError:
                        # lisame punktikirjelduse
                        r = model.Kritkirjeldus(punktid=punktid)
                        item.kritkirjeldused.append(r)
                    r.kirjeldus = row['kirjeldus']
        # alles on jäänud need punktikirjeldused, mida ei ole enam vaja
        for r in list(kirjeldused.values()):
            r.delete()

        # anname aspektidele uued järjekorranumbrid
        # nii, et kõik järjekorranumbrid on järjest ja praeguse aspekti järjekord säilib
        li = [ha for ha in self.c.hindamiskogum.hindamiskriteeriumid if ha != item]
        li.insert(item.seq-1, item)
        for seq, ha in enumerate(li):
            ha.seq = seq + 1

        for ty in self.c.hindamiskogum.testiylesanded:
            if ty.max_pallid:
                ty.max_pallid = None
                ty.update_koefitsient()
        self.c.hindamiskogum.arvuta_pallid(self.c.testiosa.lotv)
        self.c.hindamiskogum.testiosa.arvuta_pallid(True)
        self.c.test.arvuta_pallid(False)

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        self.success()
        self.c.item = self.c.hindamiskogum
        return self.render_to_response(self._LIST_TEMPLATE)            

    def _delete(self, item):
        item.delete()
        model.Session.commit()
        self.c.hindamiskogum.arvuta_pallid(self.c.testiosa.lotv)
        self.c.hindamiskogum.testiosa.arvuta_pallid(True)
        self.c.test.arvuta_pallid(False)

    def _after_delete(self, parent_id=None):
        c = self.c
        return HTTPFound(location=self.url('test_edit_hindamiskogum', test_id=c.test.id, id=c.hindamiskogum.id))
    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        hk_id = self.request.matchdict.get('hindamiskogum_id')
        self.c.hindamiskogum = model.Hindamiskogum.get(hk_id)
        self.c.testiosa = self.c.hindamiskogum.testiosa
        assert self.c.testiosa.test_id == self.c.test.id, 'Vale test'
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}

