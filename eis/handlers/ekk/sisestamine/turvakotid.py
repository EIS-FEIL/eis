# -*- coding: utf-8 -*- 
# $Id: turvakotid.py 9 2015-06-30 06:34:46Z ahti $

from eis.lib.baseresource import *
from eis.lib.basegrid import *
#from eis.lib.block import BlockController
_ = i18n._

log = logging.getLogger(__name__)

class TurvakotidController(BaseResourceController):
    """Toimumisaja otsing turvakottide numbrite sisestamiseks
    """
    _permission = 'sisestamine'
    _MODEL = model.Toimumisaeg
    _INDEX_TEMPLATE = 'ekk/sisestamine/turvakotid.otsing.mako'
    _LIST_TEMPLATE = 'ekk/sisestamine/turvakotid.otsing_list.mako'
    _DEFAULT_SORT = 'toimumisaeg.id' # vaikimisi sortimine
    _SEARCH_FORM = forms.ekk.sisestamine.TurvakotidForm # valideerimisvorm otsinguvormile

    def _query(self):
        q = model.Toimumisaeg.query.\
            join(model.Toimumisaeg.testiosa).\
            join(model.Testiosa.test).\
            filter(model.Test.avaldamistase==const.AVALIK_EKSAM).\
            join(model.Toimumisaeg.testimiskord)
        return q

    def _search_default(self, q):
        return None
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.ta_tahised:
            rcd = model.Toimumisaeg.query.\
                filter(model.Toimumisaeg.tahised==self.c.ta_tahised.upper()).\
                first()
            if rcd:
                return HTTPFound(location=self.url('sisestamine_turvakotinumbrid', toimumisaeg_id=rcd.id))
            else:
                self.error(_('Sisestatud tähisega toimumisaega ei leitud'))

        if self.c.sessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==self.c.sessioon_id)
        if self.c.test_id:
            q = q.filter(model.Test.id==self.c.test_id)

        liigid = self.c.user.get_testiliigid(self._permission)
        if None not in liigid:
            q = q.filter(model.Test.testiliik_kood.in_(liigid))

        return q
