from eis.lib.base import *
_ = i18n._
from eis.handlers.avalik.sooritamine import sooritus
from eis.lib.feedbackreport import FeedbackReport
log = logging.getLogger(__name__)

class SooritusController(sooritus.SooritusController):
    """Testisoorituse vaatamine
    """
    _EDIT_TEMPLATE = 'avalik/ktulemused/sooritus.mako'
    _permission = 'avalikadmin,testiadmin'
    _actions = 'show'
    _actionstask = 'showtask,showtool,correct,images'
    
    def __before__(self):
        """Väärtustame testimiskorra id
        """
        c = self.c
        matchdict = self.request.matchdict
        c.test_id = int(matchdict.get('test_id'))
        c.test = model.Test.get(c.test_id)
        c.testimiskord = model.Testimiskord.get(matchdict.get('testimiskord_id'))
        c.testiosa_id = int(matchdict.get('testiosa_id'))
        c.testiosa = model.Testiosa.get(c.testiosa_id)
        sooritus_id = int(matchdict.get('id'))
        c.item = c.sooritus = model.Sooritus.get(sooritus_id)
        c.sooritaja = c.sooritus.sooritaja
        c.toimumisaeg = c.item and c.item.toimumisaeg
        c.ylesanded_avaldet = c.testimiskord.ylesanded_avaldet and not c.test.salastatud
        c.kursus = c.sooritaja.kursus_kood or ''
        c.alatest_id = self.request.matchdict.get('alatest_id') or ''
        if c.alatest_id:
            c.alatest_id = int(c.alatest_id)
            c.alatest = model.Alatest.get(c.alatest_id)
            c.atos = c.sooritus.getq_alatestisooritus(c.alatest_id)            
        c.FeedbackReport = FeedbackReport
        
    def _has_permission(self):
        c = self.c
        if not c.item: 
            return False
        if c.sooritus.testiosa_id != c.testiosa.id:
            return False
        if c.toimumisaeg.testimiskord_id != c.testimiskord.id:
            return False
        if c.testimiskord.test_id != c.test.id:
            return False
        sooritaja = c.item.sooritaja
        if c.test.testiliik_kood == const.TESTILIIK_SISSE:
            q = (model.Session.query(sa.func.count(model.Kandideerimiskoht.id))
                 .filter_by(sooritaja_id=sooritaja.id)
                 .filter_by(koht_id=c.user.koht_id))
            if q.scalar() == 0:
                return False
        elif sooritaja.kool_koht_id != c.user.koht_id:
            return False
        if c.item.staatus != const.S_STAATUS_TEHTUD:
            return False
        if not c.testimiskord.ylesanded_avaldet or c.test.salastatud:
            self.error(_("Ülesanded pole veel avalikud"))
            return False
        return model.Sooritaja.has_permission_ts(c.sooritaja.id, c.testimiskord)
