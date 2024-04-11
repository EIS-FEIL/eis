from cgi import FieldStorage
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class KlassiopilasedController(BaseResourceController):
    """EHISe õpilaste puhvri sisu laadimine failist (ATS) 
    """
    _permission = 'paroolid'
    _INDEX_TEMPLATE = 'admin/klassiopilased.fail.mako'

    def index(self):
        return self._showlist()

    def _create_fail(self):            
        """Failist isikute lisamine klassi
        """
        value = self.request.params.get('ik_fail')
        err = None
        if isinstance(value, FieldStorage):
            # value on FieldStorage objekt
            value = value.value
            settings = self.request.registry.settings
            # failis on iga sooritaja jaoks üks rida
            # first name;surname;sex(M/F);birthdate (dd.mm.yyyy)
            li_ik = []
            for ind_l, line in enumerate(value.splitlines()):
                line = utils.guess_decode(line).strip()
                li = [s.strip() for s in line.split(';')]
                if not self._load_opilane(li):
                    self.error(_("Vigane rida {s}").format(s=ind_l+1) + ': %s' % line)
                    break
            if not err:
                model.Session.commit()
        else:
            self.error(_("Fail puudub"))
            
        return self._after_update(None)

    def _load_opilane(self, li):
        klass = self.request.params.get('klass')
        paralleel = self.request.params.get('paralleel')
        if paralleel:
            paralleel = paralleel.upper()
        koht = self.c.user.koht

        if not klass:
            self.error(_("Klass on valimata"))
            return
        
        if len(li) != 5:
            self.error(_("Iga rida peab sisaldama 5 semikoolonitega eraldatud välja"))
            return

        strip = lambda x: x.strip()
        userid, eesnimi, perenimi, sugu, s_synnikpv = list(map(strip, li))

        try:
            day, month, year = s_synnikpv.split('.')
            synnikpv = date(int(year), int(month), int(day))
        except:
            self.error(_("Palun esitada sünniaeg kujul pp.kk.aaaa"))
            return
        
        opilane = None
        userid = userid.replace(' ','').replace('*','')
        if userid:
            opilane = model.Opilane.get_by_ik(userid)
            if opilane:
                if opilane.koht_id != koht.id:
                    self.error(_("Õpilane {s} õpib teises koolis").format(s=userid))
                    return
                if opilane.synnikpv and opilane.synnikpv != synnikpv:
                    self.error(_("Õpilane {s} on andmebaasis, kuid erineva sünniajaga").format(s=userid))
                    return                    
            else:
                kasutaja = model.Kasutaja.get_by_ik(userid)
                if kasutaja:
                    self.error(_("Kasutajatunnus {s} on juba kasutusel").format(s=userid))
                    return
        else:
            userid = model.Kasutaja.gen_userid(eesnimi, perenimi)

        if not eesnimi or len(eesnimi) > 50:
            self.error(_("Eesnimi ei tohi olla pikem kui 50 sümbolit"))
            return
        if not perenimi or len(perenimi) > 50:
            self.error(_("Perekonnanimi ei tohi olla pikem kui 50 sümbolit"))
            return

        if sugu == 'F':
            sugu = const.SUGU_N
        elif sugu == 'M':
            sugu = const.SUGU_M
        else:
            self.error(_("Palun esitada sugu kujul M või F"))
            return
        
        if not opilane:
            opilane = model.Opilane(isikukood=userid,
                                    eesnimi=eesnimi,
                                    perenimi=perenimi,
                                    koht_id=koht.id,
                                    synnikpv=synnikpv,
                                    sugu=sugu,
                                    on_ehisest=False,
                                    on_lopetanud=False)
        else:
            opilane.eesnimi = eesnimi
            opilane.perenimi = perenimi
            opilane.synnikpv = synnikpv
            opilane.sugu = sugu
        opilane.seisuga = datetime.now()
        opilane.klass = klass
        opilane.paralleel = paralleel or None
        opilane.give_kasutaja()
        opilane.flush()
        return True

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        if not self.has_errors():
            self.success()
        return HTTPFound(location=self.url('admin_klassiparoolid', klass=self.c.klass, paralleel=self.c.paralleel))

    def __before__(self):
        self.c.klass = self.request.params.get('klass')
        self.c.paralleel = self.request.params.get('paralleel')
