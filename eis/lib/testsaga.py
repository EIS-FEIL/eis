import random
from simplejson import dumps
import sqlalchemy as sa
import logging
from datetime import datetime, date
import eiscore.const as const
import eiscore.i18n as i18n
_ = i18n._
import eis.model as model
from eis.lib.helpers import fstr, str_from_date
import eis.lib.utils as utils
log = logging.getLogger(__name__)

class TestSaga:
    def __init__(self, handler):
        self.handler = handler

    def test_check_lukus(self, test):
        "Kontrollitakse komplektide lukustus (kasutada peale soorituste kustutamist)"
        for osa in test.testiosad:
            for kv in osa.komplektivalikud:
                for k in kv.komplektid:
                    self.komplekt_set_lukus(k)
        #model.Session.flush()

    def komplekt_set_lukus_tk(self, komplekt, tk):
        if (komplekt.lukus or 0) < const.LUKUS_SOORITATUD:
            on_katse = tk and tk.tahis == 'KATSE'
            lukus = on_katse and const.LUKUS_KATSE_SOORITATUD or const.LUKUS_SOORITATUD
            self.komplekt_set_lukus(komplekt, lukus)
        
    def komplekt_set_lukus(self, komplekt, lukus=None):
        if lukus:
            # lukkupanek (lukustuse suurendamine)
            if not komplekt.lukus or komplekt.lukus < lukus:
                komplekt = model.Komplekt.get(komplekt.id)
                komplekt.lukus = lukus
                return True

        # võimalik lukustuse vähendamine,
        # leitakse uus lukustusvajadus

        # kas on päris testil hinnatud
        if komplekt.staatus > const.K_STAATUS_KOOSTAMISEL:
            q = (model.SessionR.query(model.Hindamisolek.id)
                  .filter_by(komplekt_id=komplekt.id)
                  .filter(model.Hindamisolek.staatus==const.H_STAATUS_HINNATUD)
                  .join(model.Hindamisolek.sooritus)
                  .join(model.Sooritus.sooritaja)
                  .filter(model.Sooritaja.regviis_kood!=const.REGVIIS_EELVAADE)
                  .outerjoin(model.Sooritus.toimumisaeg)
                  .outerjoin(model.Toimumisaeg.testimiskord)
                  .filter(sa.or_(model.Testimiskord.id==None,
                                 model.Testimiskord.tahis!='KATSE'))
                 )
            if q.count():
                lukus = const.LUKUS_HINNATUD

        if not lukus:
            # kas on päris testil sooritatud
            q = (model.SessionR.query(model.Soorituskomplekt.id)
                 .filter_by(komplekt_id=komplekt.id)
                 .join((model.Sooritus,
                        model.Sooritus.id==model.Soorituskomplekt.sooritus_id))
                 .join(model.Sooritus.sooritaja)
                 .filter(model.Sooritaja.regviis_kood!=const.REGVIIS_EELVAADE)
                 .outerjoin(model.Sooritus.toimumisaeg)
                 .outerjoin(model.Toimumisaeg.testimiskord)
                 .filter(sa.or_(model.Testimiskord.id==None,
                                model.Testimiskord.tahis!='KATSE'))
                        )
            if q.count():
                lukus = const.LUKUS_SOORITATUD

        if not lukus and komplekt.staatus > const.K_STAATUS_KOOSTAMISEL:
            # kas on katsetamisel hinnatud
            q = (model.SessionR.query(model.Hindamisolek.id)
                 .filter_by(komplekt_id=komplekt.id)
                 .filter(model.Hindamisolek.staatus==const.H_STAATUS_HINNATUD)
                 )
            if q.count():
                lukus = const.LUKUS_KATSE_HINNATUD

        if not lukus:
            # kas on katsetamisel sooritatud
            q = (model.SessionR.query(model.Soorituskomplekt.id)
                 .filter_by(komplekt_id=komplekt.id))
            if q.count():
                lukus = const.LUKUS_KATSE_SOORITATUD

        if komplekt.lukus != lukus:
            komplekt.lukus = lukus
            return True
        # edasi käivitub triger, mis muudab ylesannete lukustust
    
    def get_sooritaja_for(self, test, kasutaja_id):
        """Otsitakse testimiskord antud kasutaja jaoks
        Tagastatakse testitavus ja sooritaja kirje.
        """
        now = datetime.now()
        if test.salastatud in (const.SALASTATUD_LOOGILINE, const.SALASTATUD_KRYPTITUD):
            return None, None, _("Test on salastatud")

        if test.staatus != const.T_STAATUS_KINNITATUD:
            return None, None, _("Test on {s}").format(s=test.staatus_nimi)
        
        # kas on sooritaja kirje olemas?
        q = (model.Sooritaja.queryR.filter_by(kasutaja_id=kasutaja_id)
             .filter(model.Sooritaja.regviis_kood!=const.REGVIIS_EELVAADE)
             .filter_by(test_id=test.id))

        # otsime pooleliolevaid sooritusi ja ka regatud sooritusi (mis võivad olla alustamise loa ootel)
        tehtavad = (const.S_STAATUS_ALUSTAMATA,
                    const.S_STAATUS_POOLELI,
                    const.S_STAATUS_KATKESTATUD,
                    const.S_STAATUS_REGATUD)
        q1 = (q.filter(model.Sooritaja.staatus.in_(tehtavad))
              .order_by(sa.desc(model.Sooritaja.staatus))
              )
        alates = kuni = None
        for rcd in q1.all():
            nimekiri = rcd.nimekiri
            if nimekiri:
                if nimekiri.alates and nimekiri.alates > date.today():
                    alates = nimekiri.alates
                    continue
                if nimekiri.kuni and nimekiri.kuni < date.today():
                    kuni = nimekiri.kuni
                    continue
            return True, rcd, None

        # pooleli oleva sooritamise kirjet polnud
        # vaatame, kas testi võib ilma suunamiseta igaüks lahendada
        today = date.today()
        if test.avaldamistase != const.AVALIK_SOORITAJAD:
            if alates:
                return None, None, _("Testi sooritamise ajavahemik algab {d}").format(d=str_from_date(alates))
            if kuni:
                return None, None, _("Testi sooritamise ajavahemik lõppes {d}").format(d=str_from_date(kuni))
            return None, None, _("Test pole kõigile sooritamiseks")
        elif test.avalik_alates and test.avalik_alates > today:
            return None, None, _("Test pole veel kõigile sooritamiseks lubatud")
        elif test.avalik_kuni and test.avalik_kuni < today:
            return None, None, _("Test pole enam kõigile sooritamiseks lubatud")
        
        if q.count() > 0 and not test.korduv_sooritamine:
            return None, None, _("Korduv sooritamine pole lubatud")

        return True, None, None

