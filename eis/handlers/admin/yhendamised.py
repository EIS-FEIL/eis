from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class YhendamisedController(BaseResourceController):
    "Mitme isikukirje ühendamine (kui pole isikukoodi, siis võib samale isikule mitu kirjet olla loodud)"
    
    _permission = 'eksaminandid'
    _MODEL = model.Kasutaja
    _INDEX_TEMPLATE = 'admin/eksaminand.yhendamised.mako' # otsinguvormi mall
    _index_after_create = True # et peale volitamata muutmiskatset mindaks indeksisse

    def _search_default(self, q):
        yhendatav = model.Kasutaja.get(self.c.yhendatav_id)

        self.c.synnikpv = yhendatav.synnikpv
        self.c.eesnimi = yhendatav.eesnimi
        self.c.perenimi = yhendatav.perenimi
        return self._search(q)

    def _search(self, q):
        c = self.c
        q = q.filter(model.Kasutaja.id!=c.yhendatav_id)
        if c.yhendaja_ik:
            c.isikukood = c.yhendaja_ik
            usp = validators.IsikukoodP(c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
            return q
        elif not c.synnikpv and not c.perenimi:
            self.error(_("Palun anda ette vähemalt sünnikuupäev või perekonnanimi"))
            return
        if c.isikukood:
            usp = validators.IsikukoodP(c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
        if c.synnikpv:
            q = q.filter(model.Kasutaja.synnikpv==c.synnikpv)
        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))

        return q

    def update(self):
        # isikute yhendamine
        kasutaja_id = self.request.matchdict.get('id')
        item = self._MODEL.get(kasutaja_id)

        yhendatav = model.Kasutaja.get(self.c.yhendatav_id)
        
        if not item.epost and yhendatav.epost:
            item.epost = yhendatav.epost
        if not item.aadress_id and yhendatav.aadress_id:
            item.aadress_id = yhendatav.aadress_id
        if not item.postiindeks and yhendatav.postiindeks:
            item.postiindeks = yhendatav.postiindeks
        if not item.telefon and yhendatav.telefon:
            item.telefon = yhendatav.telefon
        if not item.sugu and yhendatav.sugu:
            item.sugu = yhendatav.sugu

        if not item.tunnistus_nr and yhendatav.tunnistus_nr:
            item.tunnistus_nr = yhendatav.tunnistus_nr
        if not item.tunnistus_kp and yhendatav.tunnistus_kp:
            item.tunnistus_kp = yhendatav.tunnistus_kp
        if not item.lopetamisaasta and yhendatav.lopetamisaasta:
            item.lopetamisaasta = yhendatav.lopetamisaasta
        if not item.kool_nimi and yhendatav.kool_nimi:
            item.kool_nimi = yhendatav.kool_nimi
        if not item.oppekeel and yhendatav.oppekeel:
            item.oppekeel = yhendatav.oppekeel
        if not item.kodakond_kood and not item.isikukood and yhendatav.kodakond_kood:
            item.kodakond_kood = yhendatav.kodakond_kood
        if not item.lisatingimused and yhendatav.lisatingimused:
            item.lisatingimused = yhendatav.lisatingimused
        if not item.markus and yhendatav.markus:
            item.markus = yhendatav.markus

        # kas yhendatav ja item on regatud mõlemad samale testile
        Sooritaja1 = sa.orm.aliased(model.Sooritaja)
        Sooritaja2 = sa.orm.aliased(model.Sooritaja)
        q = (model.Session.query(Sooritaja1, Sooritaja2)
             .join((Sooritaja2, Sooritaja1.testimiskord_id==Sooritaja2.testimiskord_id))
             .filter(Sooritaja1.kasutaja_id==yhendatav.id)
             .filter(Sooritaja2.kasutaja_id==item.id))

        li = []
        for r in q.all():
            sooritaja1, sooritaja2 = r
            # kui mõni registreering on tyhistatud, siis saame selle kustutada
            del_j = None
            if sooritaja1.staatus == const.S_STAATUS_TYHISTATUD:
                del_j = sooritaja1
            elif sooritaja2.staatus == const.S_STAATUS_TYHISTATUD:
                del_j = sooritaja2
            if del_j:
                # saab kustutada
                del_j.delete()
            else:
                li.append(sooritaja1.testimiskord.tahised)

        if len(li):
            if len(li) == 1:
                buf = _("Mõlemad isikukirjed on registreeritud testimiskorrale {s}. Palun liigsed registreeringud enne kirjete ühendamist tühistada.")
            else:
                buf = _("Mõlemad isikukirjed on registreeritud testimiskordadele {s}. Palun liigsed registreeringud enne kirjete ühendamist tühistada.")
            buf = buf.format(s=', '.join(li))
            self.error(buf)
            model.Session.rollback()
            return self.index()

        for r in list(yhendatav.sooritajad):
            r.kasutaja = item
        for r in list(yhendatav.kasutajaajalood):
            r.kasutaja = item
        for r in list(yhendatav.tunnistused):
            r.kasutaja = item
        for r in list(yhendatav.kirjasaajad):
            r.kasutaja = item
        for r in list(yhendatav.esitatud_sooritajad):
            r.esitaja_kasutaja = item
        for r in list(yhendatav.esitaja_nimekirjad):
            r.esitaja_kasutaja = item
        for r in list(yhendatav.volitatu_volitused):
            r.volitatu_kasutaja = item
        for r in list(yhendatav.opilane_volitused):
            r.opilane_kasutaja = item
        self._yhenda_profiil(item, yhendatav)

        q = model.Session.query(model.Kiri).filter_by(saatja_kasutaja_id=yhendatav.id)
        for r in q.all():
            r.saatja_kasutaja = item
        try:
            yhendatav.refresh()
            yhendatav.delete()
            model.Session.commit()
            self.success(_("Isikukirjed ühendati"))
            return HTTPFound(location=self.url('admin_eksaminand', id=kasutaja_id))
        except sa.exc.IntegrityError as e:
            raise
            # esineb seoseid mingite muude tabelitega 
            # ilmselt on yhendataval mingid eriõigused
            # igaks juhuks ei luba teda yhendada
            msg = _("Seda isikukirjet ei saa ühendada ")
            log.info('%s [%s] %s' % (msg, self.request.url, str(e)))            
            self.error(msg)
            model.Session.rollback()
            return self.index()

    def _yhenda_profiil(self, item, yhendatav):
        r = yhendatav.profiil
        if r:
            profiil = item.profiil
            if not profiil:
                r.kasutaja = item
            else:
                profiil.on_vaatleja = profiil.on_vaatleja or r.on_vaatleja
                for lang in (r.v_skeeled or '').split(' '):
                    if lang:
                        profiil.set_v_lang(lang)
                profiil.v_koolitusaeg = _date_max(profiil.v_koolitusaeg, r.v_koolitusaeg)
                profiil.v_kaskkirikpv = _date_max(profiil.v_kaskkirikpv, r.v_kaskkirikpv)
                for lang in (r.s_skeeled or '').split(' '):
                    if lang:
                        profiil.set_s_lang(lang)                
                for lang in (r.k_skeeled or '').split(' '):
                    if lang:
                        profiil.set_k_lang(lang)
                profiil.on_testiadmin = profiil.on_testiadmin or r.on_testiadmin
                if not profiil.arveldusarve and r.arveldusarve:
                    profiil.arveldusarve = r.arveldusarve
                for rlv in list(r.ainelabiviijad):
                    found = False
                    for alv in profiil.ainelabiviijad:
                        if alv.aine_kood == rlv.aine_kood:
                            found = True
                            break
                    if found:
                        rlv.delete()
                    else:
                        rlv.profiil = profiil
                r.delete()

        for r in list(yhendatav.aineprofiilid):
            alv = item.get_aineprofiil(r.aine_kood,
                                       r.kasutajagrupp_id,
                                       r.keeletase_kood)
            if not alv:
                r.kasutaja = item
            else:
                r.delete()
        for r in yhendatav.kasutajakohad:
            r.kasutaja = item
        for r in yhendatav.kasutajapiirkonnad:
            r.kasutaja = item
        for r in yhendatav.kasutajarollid:
            r.kasutaja = item
        for r in model.Kasutajarollilogi.query.filter_by(kasutaja_id=yhendatav.id).all():
            r.kasutaja = item
        for r in model.Testiisik.query.filter_by(kasutaja_id=yhendatav.id).all():
            r.kasutaja = item
        for r in model.Ylesandeisik.query.filter_by(kasutaja_id=yhendatav.id).all():
            r.kasutaja = item
        for r in model.Tookogumik.query.filter_by(kasutaja_id=yhendatav.id).all():
            r.kasutaja = item                                                

    def __before__(self):
        self.c.yhendatav_id = self.request.matchdict.get('yhendatav_id')

def _date_max(d1, d2):
    if d1 and d2:
        return d1 > d2 and d1 or d2
    elif d1:
        return d1
    else:
        return d2
