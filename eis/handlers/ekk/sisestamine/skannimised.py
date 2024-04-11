# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.resultscan import ResultScan
_ = i18n._
log = logging.getLogger(__name__)

class SkannimisedController(BaseResourceController):
    """Skannitud andmete laadimine
    """
    _permission = 'sisestamine'
    _MODEL = model.Toimumisaeg
    _INDEX_TEMPLATE = 'ekk/sisestamine/skannimised.otsing.mako'
    _EDIT_TEMPLATE = 'ekk/sisestamine/skannimised.otsing.mako'
    #_LIST_TEMPLATE = 'ekk/sisestamine/skannimised.otsing_list.mako'
    _ITEM_FORM = forms.ekk.sisestamine.SkannimineForm
    _DEFAULT_SORT = 'sooritus.tahised'
    _get_is_readonly = False
    _index_after_create = True

    def _query(self):
        self.c.opt_sessioon = self.c.opt.testsessioon

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        if self.c.ta_tahised and self.c.otsi:
            # on antud toimumisaja tähis ja vajutati nupule Otsi
            # (mitte ei valitud loetelust toimumisaega)
            self.c.ta_tahised = self.c.ta_tahised.strip().replace('+','-').upper()
            li_ta = self.c.ta_tahised.split('-')
            if len(li_ta) != 3:
                self.error(_('Sisesta toimumisaja tähis 3-osalisena'))
            else:
                ta = model.Toimumisaeg.query.filter_by(tahised=self.c.ta_tahised).first()
                if not ta:
                    self.error(_('Sellise tähisega toimumisaega ei leitud'))
                else:
                    self.c.toimumisaeg_id = ta.id

        ta = None
        if self.c.toimumisaeg_id:
            # toimumisaeg on valitud - kas valikust või tähisega
            self.c.toimumisaeg = ta = model.Toimumisaeg.get(self.c.toimumisaeg_id)
            if ta:
                self.c.ta_tahised = ta.tahised
                skogumid = [sk for sk in ta.testiosa.sisestuskogumid if sk.on_skannimine]
                self.c.opt_sisestuskogum = [(sk.id, '%s - %s' % (sk.tahis, sk.nimi)) \
                                            for sk in skogumid]
                if not self.c.sisestuskogum_id and len(skogumid):
                    self.c.sisestuskogum_id = skogumid[0].id
                #if not self.c.sessioon_id:
                self.c.sessioon_id = ta.testimiskord.testsessioon_id

        if self.c.sessioon_id:
            self.c.opt_toimumisaeg = model.Toimumisaeg.get_opt(self.c.sessioon_id, 
                                                               vastvorm_kood=const.VASTVORM_KP)

        if ta:
            liigid = self.c.user.get_testiliigid(self._permission)
            if None not in liigid:
                if ta.testiosa.test.testiliik_kood not in liigid:
                    self.error(_('Toimumisaeg {s} kuulub sellisele testile, mille testiliigi sisestamine pole kasutajale lubatud').format(s=ta.tahised))
                    return

        if self.request.params.get('laadi'):
            if not (ta and self.c.sisestuskogum_id):
                self.error(_('Palun vali toimumisaeg ja sisestuskogum'))
            elif not self.c.kataloog:
                self.error(_('Palun määra sisendkataloog, kus asuvad skannitud failid'))
            else:
                self._load_scan(ta, self.c.sisestuskogum_id, self.c.kataloog)

    def _load_scan(self, ta, sisestuskogum_id, kataloog):
        """Failide laadimine
        """
        sk = model.Sisestuskogum.get(sisestuskogum_id)
        if not sk:
            self.error(_('Sisestuskogum puudub'))
            return

        rs = ResultScan(self, ta, sk)
        error = rs.load_scan(kataloog)
        if error:
            self.error(error)
            model.Session.rollback()
        else:
            model.Session.commit()
            self.success(_('Laaditud {n} pildifaili').format(n=rs.cnt_img))

    def _edit(self, item):
        """update vigade korral tullakse siia
        """
        # kui tullakse update-ist, siis on olemas id
        self.c.toimumisaeg_id = item.id

        q = self._search(self._query())
        self.c.items = self._paginate(self._order(q))

        return self.response_dict

    # def _after_update(self, id):
    #     """Mida teha peale õnnestunud salvestamist
    #     """        
    #     return self._redirect('index')
    
