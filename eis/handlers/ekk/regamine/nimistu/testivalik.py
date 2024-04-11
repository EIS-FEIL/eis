# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._

log = logging.getLogger(__name__)

class TestivalikController(BaseResourceController):
    """Testide valik
    """
    _permission = 'regamine'
    _MODEL = model.Testimiskord
    _INDEX_TEMPLATE = 'ekk/regamine/nimistu.testivalik.mako'
    _LIST_TEMPLATE = 'ekk/regamine/nimistu.testivalik_list.mako'
    _DEFAULT_SORT = 'test.nimi' # vaikimisi sortimine

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.korrad_id:
            self.c.korrad_id = [r for r in self.c.korrad_id.split('-') if r]

        if self.c.testiliik:
            q = q.filter(model.Test.testiliik_kood==self.c.testiliik)
        if self.c.sessioon:
            q = q.filter(model.Testimiskord.testsessioon_id==self.c.sessioon)

        #liigid = self.c.user.get_testiliigid(self._permission)
        #if None not in liigid:
        #    q = q.filter(model.Test.testiliik_kood.in_(liigid))
                         
        ained = self.c.user.get_ained(self._permission)
        if None not in ained:
            q = q.filter(model.Test.aine_kood.in_(ained))

        if self.c.korrad_id:
            for kord_id in self.c.korrad_id:
                kord = model.Testimiskord.get(kord_id)
                if kord:
                    if not kord.reg_ekk:
                        self.error(_("Eksamikeskuses ei registreerita sooritajaid testimiskorrale {s}").format(s=kord.tahised))
                    elif kord.kuni and kord.kuni < date.today():
                        self.error(_("Testimiskorrale {s} registreerimine on läbi").format(s=kord.tahised))
        return q

    def _search_default(self, q):
        self.c.testiliik = const.TESTILIIK_RIIGIEKSAM
        return None

    def _query(self):
        d = date.today()
        return (model.Testimiskord.query
                .join(model.Testimiskord.test)
                .filter(model.Testimiskord.reg_ekk==True)
                .filter(model.Testimiskord.kuni>=d)
                )
        # ei kontrolli reg lõpu kuupäeva, sest 
        # REKK võib registreerida sooritajaid ka peale seda

    def create(self):
        # kasutaja vajutas testimiskordade loetelus nupule "Vali"
        testiliik = self.request.params.get('testiliik')
        sessioon = self.request.params.get('sessioon')
        korrad_id = self.request.params.getall('kord_id')
        korrad_id='-'.join(korrad_id)
        return HTTPFound(location=self.url('regamine_nimistu_edit_yksikasjad', 
                                           korrad_id=korrad_id,
                                           testiliik=testiliik,
                                           sessioon=sessioon))        
