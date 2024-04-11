"Küsimuse hindamismaatriksi täiendamine sooritajate antud vastustega"
import math
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from eis.handlers.ekk.ylesanded.hindamismaatriksid import HindamismaatriksidController
log = logging.getLogger(__name__)

class AnalyysmaatriksidController(HindamismaatriksidController):
    _permission = 'vastusteanalyys'

    _MODEL = model.Hindamismaatriks
    _ITEM_FORM = forms.ekk.hindamine.AnalyyskysimusForm

    def _set_list_url(self):
        c = self.c
        c.is_sp_analysis = True
        c.is_edit = False

        c.hm_list_url = self.url_current('index', kysimus_id=c.kysimus.id, maatriks=c.maatriks, prefix=c.prefix)

    def _search(self, q):
         # et ei kuvaks hindamismaatriksi juures h3 pealkirja (nupp on juba olemas)
        self.c.hm_caption_off = True
        return super()._search(q)
        
    def _create(self):
        # hindamismaatriksisse ridade lisamine

        tulemus = self.c.kysimus.give_tulemus()
        pallid = self.form.data['pallid']
        if tulemus.baastyyp == const.BASETYPE_MATH:
            hm_vastused = [model.fixlatex(r.kood1) for r in tulemus.hindamismaatriksid]
            hm_vastused1 = hm_vastused
        else:
            hm_vastused = [(r.kood1, r.kood2) for r in tulemus.hindamismaatriksid]
            hm_vastused1 = [r[0] for r in hm_vastused]
        cnt = 0
        for kst_id in self.request.params.getall('kst_id'):
            kst = model.Kvstatistika.get(kst_id)
            if not kst:
                continue
            rcd = None
            if [v for v in [kst.sisu, kst.kood1, kst.kood2] if v and len(v) > 2000]:
                self.error(_("Vastus on hindamismaatriksisse panemiseks liiga pikk"))
                continue

            if tulemus.baastyyp == const.BASETYPE_MATH:
                resp = model.stdlatex(kst.sisu)
                fixr = model.fixlatex(resp)
                try:
                    n = hm_vastused.index(fixr)
                except ValueError:
                    rcd = model.Hindamismaatriks(kood1=resp,
                                                 pallid=pallid)
                    hm_vastused.append(resp)
                else:
                    self.error(_("Vastus on juba maatriksis real {n}").format(n=n+1))
            elif kst.tyyp == const.RTYPE_STRING:
                resp = kst.sisu
                try:
                    n = hm_vastused1.index(resp)
                except ValueError:
                    rcd = model.Hindamismaatriks(kood1=kst.sisu,
                                                 pallid=pallid)
                    hm_vastused1.append(resp)
                else:
                    self.error(_("Vastus on juba maatriksis real {n}").format(n=n+1))
            elif kst.tyyp == const.RTYPE_IDENTIFIER:
                resp = kst.kood1
                try:
                    n = hm_vastused1.index(resp)
                except ValueError:
                    rcd = model.Hindamismaatriks(kood1=kst.kood1,
                                                 pallid=pallid)
                    hm_vastused1.append(resp)
                else:
                    self.error(_("Vastus on juba maatriksis real {n}").format(n=n+1))
            elif kst.tyyp in (const.RTYPE_PAIR, const.RTYPE_POINT):
                resp = (kst.kood1, kst.kood2)
                if resp not in hm_vastused:
                    hm_vastused.append(resp)
                    rcd = model.Hindamismaatriks(kood1=kst.kood1,
                                                 kood2=kst.kood2,
                                                 pallid=pallid)
            if rcd:
                tulemus.hindamismaatriksid.append(rcd)
                cnt += 1
        if cnt:
            self.success(_("Lisatud {n} vastust").format(n=cnt))
       
        model.Session.commit()
        return self._after_update(None)

    def _delete(self, item):
        assert item.tulemus == self.c.kysimus.tulemus, _("Teise küsimuse maatriks")
        item.delete()
        #self.c.page = self.request.params.get('page')
        model.Session.commit()
        
    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        self.get_items()
        return self.render_to_response(self._INDEX_TEMPLATE)            

    def _after_delete(self, parent_id=None):
        """Mida teha peale õnnestunud salvestamist
        """
        self.get_items()
        return self.render_to_response(self._LIST_TEMPLATE)            

    def get_items(self):
        q = self._order(self._search(self._query()))
        return self._paginate(q)                

    def _has_permission(self):
        # leitakse, kas on õigus antud tegevusele,
        # ning seatakse c.can_edit_hm - kas on muutmisõigus

        perm = self._permission # vastusteanalyys
        can_show = self.c.user.has_permission(perm, const.BT_SHOW, obj=self.c.test)
        can_edit_hm = self._can_edit_hm(self.c.user, self.c.test, self.c.kysimus)

        self.c.can_edit_hm = can_edit_hm
        if self._is_modify():
            return can_edit_hm
        else:
            return can_show
    
    def _can_edit_hm(self, user, test, kysimus):
        perm = 'vastusteanalyys'
        can_show = user.has_permission(perm, const.BT_SHOW, obj=test)
        can_edit_hm = False
        if user.has_permission(perm, const.BT_UPDATE, obj=test):
            # kasutajal on rolli kaudu yldine muutmise õigus
            can_edit_hm = True
        elif can_show:
            # kui kasutajal on testi koostaja grupp
            # ja samal ajal ylesande koostaja grupp,
            # siis ta võib maatriksit muuta
            if user.has_group(const.GRUPP_T_KOOSTAJA, test) or \
              user.has_group(const.GRUPP_T_OMANIK, test):
                ylesanne = kysimus.sisuplokk.ylesanne
                if user.has_group(const.GRUPP_Y_KOOSTAJA, ylesanne):
                    can_edit_hm = True
        return can_edit_hm
    
    def __before__(self):
        c = self.c
        c.toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(self.c.toimumisaeg_id)
        c.test = c.toimumisaeg.testiosa.test
        kysimus_id = self.request.matchdict.get('kysimus_id')
        c.kysimus = model.Kysimus.get(kysimus_id)
        c.maatriks = self.request.params.get('maatriks') or 1
        c.prefix = self.request.params.get('prefix')
