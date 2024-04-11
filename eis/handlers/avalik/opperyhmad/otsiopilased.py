from cgi import FieldStorage
from eis.lib.baseresource import *
from eis.lib.xtee import ehis
from eis.forms import validators
log = logging.getLogger(__name__)
_ = i18n._

class OtsiopilasedController(BaseResourceController):
    """Õpilaste rühma jaoks uute liikmete otsimine dialoogiaknas.
    """
    _permission = 'omanimekirjad'
    _MODEL = model.Opperyhmaliige
    _INDEX_TEMPLATE = '/avalik/opperyhmad/otsiopilased.ik.mako'
    _get_is_readonly = False
    
    def index(self):
        sub = self.request.params.get('sub')
        if sub == 'fail':
            return self._index_fail()
        elif sub == 'ehis':
            return self._index_ehis()
        else: # 'ik'
            return self._index_ik()

    def _index_ik(self):
        "Otsing EHISest"
        rc = True
        isikukood = self.request.params.get('isikukood')
        if isikukood:
            isikukood = validators.IsikukoodP(isikukood).isikukood
            if not isikukood:
                self.error(_("Vigane isikukoodi formaat"))
        self.c.isikukood = isikukood
        if isikukood:
            # vajadusel uuendame EHISest andmeid
            kasutaja = model.Kasutaja.get_by_ik(isikukood)
            err = ehis.uuenda_opilased(self, [isikukood])
            if err:
                self.error(err)
                rc = False
            else:
                model.Session.commit()
                opilane = model.Opilane.get_by_ik(isikukood)

            item = None
            if rc:
                # kui EHISe päring ei andnud vigu või kui EHISe päringut polnud vaja teha
                if opilane:
                    item = opilane
                elif kasutaja:
                    item = kasutaja
                # kui EHISes ei ole andmeid ja EISis ka pole, siis küsime RRist
                if not opilane and not kasutaja:
                    # teeme päringu RRist
                    item = xtee.set_rr_pohiandmed(self, None, isikukood)
                    if item:
                        # salvestame leitud isiku
                        model.Session.commit()

            if item:
                self.c.items = [item]

        return self.render_to_response('avalik/opperyhmad/otsiopilased.ik.mako')

    def _index_ehis(self):
        "Otsing EHISest"
        # kasutaja õppeasutus
        c = self.c
        if 'klass' in self.request.params:
            c.klass = self.request.params.get('klass')
            c.paralleel = self.request.params.get('paralleel')
            if c.paralleel:
                c.paralleel = c.paralleel.upper()
            if not c.klass:
                self.error(_('Palun sisesta klass, mille õpilasi pärid'))
            else:
                klass, ryhm_id = model.Klass.klass_ryhm(c.klass)
                kool_id = c.user.koht.kool_id
                c.user.uuenda_klass(kool_id, klass, c.paralleel)
                        
                q = model.Opilane.query.filter_by(kool_id=kool_id)
                if klass:
                    q = q.filter_by(klass=klass)
                    if c.paralleel:
                        q = q.filter_by(paralleel=c.paralleel)
                elif ryhm_id:
                    q = q.filter_by(ryhm_id=ryhm_id)
                c.items = q.order_by(model.Opilane.perenimi,
                                     model.Opilane.eesnimi).all()

                if not len(c.items) and not self.has_errors():
                    self.error(_('Õpilasi ei leitud!'))
        return self.render_to_response('avalik/opperyhmad/otsiopilased.ehis.mako')

    def _index_fail(self):
        return self.render_to_response('avalik/opperyhmad/otsiopilased.fail.mako')

    def _create(self):            
        """Isiku lisamine ryhma liikmeks
        Parameetrites on olemas isikukoodid ja nimed
        Kasutaja on isiku leidnud kas otsides isikukoodi järgi
        või küsides EHISest klassi järgi.
        """
        isikukoodid = self.request.params.getall('oigus')
        cnt_olemas = 0
        for ik in isikukoodid:
            kasutaja = self._give_kasutaja(ik)
            if kasutaja:
                if not self._append_opilane(kasutaja):
                    cnt_olemas += 1

        if cnt_olemas:
            if len(isikukoodid) == 1:
                self.notice(_('Õpilane oli juba rühmas olemas'))
            else:
                self.notice(_('{d} õpilast oli juba rühmas olemas').format(d=cnt_olemas))

        return self.c.opperyhm

    def _create_fail(self):            
        """Failist isikute lisamine sooritajaks
        Failis on ainult isikukoodid, tuleb küsida Rahvastikuregistrist nimed ka
        """
        value = self.request.params.get('ik_fail')
        koht = self.c.user.koht

        if isinstance(value, FieldStorage):
            # value on FieldStorage objekt
            value = value.value
            settings = self.request.registry.settings
            csv_data = int(settings.get('csv.data',0))
            # failis on iga sooritaja jaoks üks rida
            # reas võib olla mitu veergu, eraldatuna semikooloniga
            # esimeses veerus on isikukood
            # teised veerud võivad puududa või olla: eesnimi, perekonnanimi, klass, paralleel
            li_ik = []
            for line in value.splitlines():
                line = utils.guess_decode(line)
                li = [s.strip() for s in line.split(';')]
                isikukood = li[0]
                if isikukood:
                    usp = validators.IsikukoodP(isikukood)
                    if not usp.isikukood:
                        self.error(_("Esitati vigane isikukood {s}").format(s=isikukood))
                        return self._after_update(None)                        
                    li_ik.append(isikukood)

            # EHISe päring
            lisada_isikukoodid = []
            uuendada_isikukoodid = []

            # vaatame isikukoodid üle, kas on neid, kelle andmeid ei pea uuendama
            err = ehis.uuenda_opilased(self, li_ik)
            if err:
                self.error(err)
                return self._after_update(None)
            model.Session.commit()
            
            # lisame ryhmaliikme
            cnt_olemas = 0
            puuduvad_isikukoodid = []
            for isikukood in li_ik:
                kasutaja = self._give_kasutaja(isikukood)
                if not kasutaja: 
                    puuduvad_isikukoodid.append(isikukood)
                else:
                    if not self._append_opilane(kasutaja):
                        cnt_olemas += 1

            # teatame isikukoodidest, millele vastavaid õpilasi ei leitud
            if len(puuduvad_isikukoodid):
                buf = ', '.join(puuduvad_isikukoodid)
                if len(puuduvad_isikukoodid) == 1:
                    self.error(_('Isikukoodiga {s} õpilast ei leitud!').format(s=buf))
                else:
                    self.error(_('Isikukoodidega {s} õpilasi ei leitud!').format(s=buf))

            if cnt_olemas:
                self.notice(_('{d} õpilast oli juba rühmas olemas').format(d=cnt_olemas))

            model.Session.commit()

        return self._after_update(None)

    def _give_kasutaja(self, isikukood):
        """Leitakse sooritaja kasutaja kirje
        """
        opilane = None
        kasutaja = model.Kasutaja.get_by_ik(isikukood)
        if not kasutaja:
            opilane = model.Opilane.get_by_ik(isikukood)
            if opilane:
                kasutaja = opilane.give_kasutaja()
            else:
                # uus isik
                kasutaja = xtee.set_rr_pohiandmed(self, None, isikukood)
            model.Session.flush()
        return kasutaja

    def _append_opilane(self, kasutaja):
        """Lisatakse sooritaja või muudetakse olemasolevat.
        """
        rl = (model.Session.query(model.Opperyhmaliige)
              .filter_by(opperyhm_id=self.c.opperyhm.id)
              .filter_by(kasutaja_id=kasutaja.id)
              .first())
        if not rl:
            rl = model.Opperyhmaliige(opperyhm_id=self.c.opperyhm.id,
                                      kasutaja_id=kasutaja.id)
            return True

    def _after_update(self, id):
        return HTTPFound(location=self.h.url('edit_opperyhm', id=self.c.opperyhm.id))

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self.h.url('edit_opperyhm', id=self.c.opperyhm.id))

    def __before__(self):
        self.c.opperyhm_id = self.request.matchdict.get('opperyhm_id')
        self.c.opperyhm = model.Opperyhm.get(self.c.opperyhm_id)
    
    def _perm_params(self):
        if not self.c.opperyhm:
            return False
        return {'obj':self.c.opperyhm}
