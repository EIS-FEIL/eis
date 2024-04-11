from eis.lib.base import *
_ = i18n._
from eis.handlers.avalik.sooritamine import sooritus

log = logging.getLogger(__name__)

class SooritusController(sooritus.SooritusController):
    """Tehtud töö vaatamine
    """
    _EDIT_TEMPLATE = 'avalik/tulemused/sooritus.mako'
    _actions = 'show'
    _actionstask = 'showtask,correct'

    def _show(self, item):
        self.c.read_only = True
        sooritus.SooritusController._show(self, item)

    def __before__(self):
        c = self.c
        c.test_id = self.request.matchdict['test_id']
        c.testiosa_id = self.request.matchdict['testiosa_id']
        c.sooritus_id = self.request.matchdict['id']
        c.sooritus = model.Sooritus.get(c.sooritus_id)
        c.sooritaja_id = c.sooritus.sooritaja_id
        try:
            c.alatest_id = int(self.request.matchdict.get('alatest_id'))
        except:
            c.alatest_id = ''
        
    def _has_permission(self):
        action = self.c.action
        # Soorituse kirje peab olema olemas
        id = self.request.matchdict.get('id')
        sooritus = model.Sooritus.get(id)
        if sooritus:
            sooritaja = sooritus.sooritaja
            if self.c.user.get_kasutaja().on_volitatud(sooritaja.kasutaja_id) and \
                   sooritus.staatus == const.S_STAATUS_TEHTUD:
                tk = sooritaja.testimiskord
                test = sooritaja.test
                if test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
                    return False
                if tk and not tk.ylesanded_avaldet:
                    return False
                if test.salastatud:
                    return False
                nk = sooritaja.nimekiri
                if nk and nk.vastus_peidus:
                    return False
                if not tk and test.osalemise_peitmine:
                    return False
                if tk and not tk.osalemise_naitamine:
                    return False

                ylesanne_id = self.request.matchdict.get('task_id')
                if ylesanne_id and not self._has_ylesanne_id(sooritus.id, ylesanne_id):
                    # sooritaja pole seda ylesannet lahendanud
                    return False
                return True
        return False

    def _has_ylesanne_id(self, sooritus_id, ylesanne_id):
        "Kontrollitakse, kas sooritaja on saanud seda ylesannet lahendada"
        q = (model.SessionR.query(sa.func.count(model.Valitudylesanne.id))
             .filter_by(ylesanne_id=ylesanne_id)
             .join((model.Hindamisolek,
                    sa.and_(model.Valitudylesanne.komplekt_id==model.Hindamisolek.komplekt_id,
                            model.Hindamisolek.sooritus_id==sooritus_id)))
             )
        rc = q.scalar()
        if rc == 0:
            # kas on vaja?
            q = (model.SessionR.query(sa.func.count(model.Valitudylesanne.id))
                 .filter_by(ylesanne_id=ylesanne_id)
                 .join((model.Ylesandevastus,
                        model.Ylesandevastus.valitudylesanne_id==model.Valitudylesanne.id))
                 .filter_by(sooritus_id=sooritus_id)
                 )
            rc = q.scalar()
        return rc > 0

    
