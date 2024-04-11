"URL, millele legacy-teenusega suunatakse eesti.ee portaalist siseneda sooviv kasutaja"

from eis.lib.base import *
_ = i18n._

log = logging.getLogger(__name__)

class LegacyController(BaseController):
    "Tullakse eesti.ee portaalist"
    _authorize = False
    _get_is_readonly = False
    
    def index(self):
        kood = self.request.params.get('id')

        # kustutame vanad kirjed
        now = datetime.now()
        model.Legacy.query.\
            filter(model.Legacy.aeg < now - timedelta(hours=1)).\
            delete()
        model.Session.commit()
        
        # leiame antud seansi kirje
        row = model.Legacy.query.filter_by(kood=kood).first()

        home = self.url('avaleht')
        if not row:
            self.error(_('Autentimisandmed on kehtetud'))
            log.info('legacy notfound %s' % kood)
        else:
            isikukood = row.risikukood
            diff = now - row.aeg
            row.delete()
            timeout = self.request.registry.settings.get('eis.legacy.timeout')
            if timeout and int(timeout) < diff.total_seconds():
                self.error(_('Autentimisandmed on juba aegunud, palun siseneda uuesti'))
                log.info('legacy timeout %s' % kood)
            else:
                log.info('legacy login %s' % kood)                
                user = User.login_legacy(self, isikukood)
                if row.param == const.TESTILIIK_TASE:
                    home = self.url('regamine_avaldus_testid_testiliik', testiliik=const.TESTILIIK_TASE)
                elif row.param == const.TESTILIIK_SEADUS:
                    home = self.url('regamine_avaldus_testid_testiliik', testiliik=const.TESTILIIK_SEADUS)
                else:
                    home = self.url('regamine_avaldus_testid')

            model.Session.commit()
        return HTTPFound(location=home)

