from simplejson import dumps
from eis.lib.baseresource import *
from eis.lib.xtee import ehis
_ = i18n._
import eis.lib.pdf as pdf
log = logging.getLogger(__name__)

class LopetamisedController(BaseResourceController):
    """Lõpetamise kontroll
    """
    _permission = 'lopetamised'
    _MODEL = model.Kasutaja
    _INDEX_TEMPLATE = 'ekk/muud/lopetamised.mako'
    _LIST_TEMPLATE = 'ekk/muud/lopetamised_list.mako'
    _DEFAULT_SORT = 'kasutaja.perenimi,kasutaja.eesnimi' # vaikimisi sortimine
    _SEARCH_FORM = forms.ekk.muud.LopetamisedForm
    _ITEM_FORM = forms.ekk.muud.LopetamisedForm     
    _index_after_create = True

    def _query(self):
        return None
    
    def _search_default(self, q):
        return self._search(q)

    def _arvud(self, aasta):
        q = (model.SessionR.query(sa.func.count(model.Kasutaja.id))
             .filter(model.Kasutaja.lopetamisaasta==aasta))
        self.c.mitu_lopetajat = (q.filter(sa.or_(model.Kasutaja.lopetanud==True,
                                                 model.Kasutaja.lopetanud_kasitsi==True))
                                 .scalar())
        self.c.mitu_lopetamata = (q.filter(model.Kasutaja.lopetanud==False)
                                  .filter(sa.or_(model.Kasutaja.lopetanud_kasitsi==False,
                                                 model.Kasutaja.lopetanud_kasitsi==None))
                                  .scalar())
        
    def _search(self, q1):
        if not self.c.aasta:
            self.c.aasta = date.today().year

        self._arvud(self.c.aasta)
        self._get_protsessid()

        if self.request.params.get('lopetamata') or self.request.params.get('partial'):
            # vajutati nupule "Lõpetamata"
            q = (model.SessionR.query(model.Kasutaja.nimi, model.Kasutaja.isikukood, model.Koht.nimi)
                 .outerjoin(model.Kasutaja.kool_koht)
                 .filter(model.Kasutaja.lopetamisaasta==self.c.aasta)
                 .filter(model.Kasutaja.lopetanud==False)
                 .filter(sa.or_(model.Kasutaja.lopetanud_kasitsi==False,
                                model.Kasutaja.lopetanud_kasitsi==None))
                 )
            return q
        else:
            # ei soovita nimekirja
            return None

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            self.success()
        return self._redirect('index', aasta=self.request.params.get('aasta'))

    def _create(self):
        """Arvutusprotsessi käivitamine
        """
        aasta = self.form.data['aasta']
        if not aasta:
            self.error(_("Puudub aasta"))
            return

        isikukood = self.form.data.get('isikukood')
        if self.request.params.get('debug') or isikukood:
            # ei käivita eraldi protsessi
            rcd = None
            self._kontroll(rcd, aasta, isikukood)
            model.Session.commit()
            return self._redirect('index', aasta=aasta, isikukood=isikukood)

        params = {'aasta': aasta,
                  'liik': model.Arvutusprotsess.LIIK_LOPETAMINE,
                  'kirjeldus': 'Lõpetamise kontroll'}
        childfunc = lambda protsess: self._kontroll(protsess, aasta)
        model.Arvutusprotsess.start(self, params, childfunc)

        # deemon käivitatud, naaseme kasutaja juurde
        self.success(_("Arvutusprotsess on käivitatud"))
        return self._redirect('index', aasta=aasta)

    def _kontroll(self, protsess, aasta, isikukood=None):
        "Lõpetamise kontrolli läbiviimine"

        today = date.today()
        if aasta == today.year and today.month < 9:
            # jooksva aasta kontrollimisel määratakse vajadusel lõpetamisaasta
            self._maara_lopetamisaasta(aasta)

        q = model.Kasutaja.query
        q = q.filter(model.Kasutaja.lopetamisaasta==aasta)
        if isikukood:
            # erandjuhtum, kus kontrollitakse yhtainust lõpetajat
            usp = validators.IsikukoodP(isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
            
        total = model.SessionR.query(sa.func.count(model.Kasutaja.id)).\
                filter(model.Kasutaja.lopetamisaasta==aasta).\
                scalar()

        if aasta <= 2013:
            self._uuenda_opilased(q, protsess)

        if protsess:
            algus = protsess.edenemisprotsent
            progress_step = total / 100 or 1
            log.debug('Kokku %d, samm %d' % (total, progress_step))

        for n, k in enumerate(q.all()):
            if protsess and n % progress_step == 0:
                protsess.edenemisprotsent = algus + n * (100 - algus) / total
                if n:
                    model.Session.commit()

            log.debug('%d. Kontroll: %d %s %s' % (n, k.id, k.nimi, k.isikukood))
            kontrollida = True
            if aasta <= 2013:
                # EH-250
                # kui on EHISe andmetel lõpetanud, siis teeme märke, et on lõpetanud
                if len([opilane for opilane in k.opilased if opilane.on_lopetanud]):
                    k.lopetanud = True
                    continue

            all_errors = bool(isikukood)
            k.lopetanud, err = self._kontroll_kasutaja(k, all_errors)
            if err:
                log.debug(err)
            if isikukood:
                if err:
                    self.notice(err)
                elif k.lopetanud:
                    self.notice(_("Isikul {s} on lõpetamise tingimused täidetud").format(s=isikukood))                    

        if isikukood and not q.count():
            self.notice(_("Isik ei lõpeta sel aastal"))

    def _uuenda_opilased(self, q, protsess):
        """Uuendatakse nende õpilaste kirjed EHISest, kelle andmed pole värsked,
        et teada saada, kes varasemate aastate õpilastest on EHISe andmetel juba lõpetanud.
        """
        
        def _uuenda(reg, isikukoodid, call_cnt, call_total):
            # teeme EHISe päringu
            message, oppimised = reg.oppurid_ik(isikukoodid)
            if message:
                self.error(message)
                return False
            else:
                model.Opilane.update_opilased(oppimised, isikukoodid)
                if protsess:
                    # õpilaste uuendamine olgu 15% protsessist
                    protsess.edenemisprotsent = (call_cnt + 1) * 15 / call_total
                model.Session.commit()
                return True
            
        reg = ehis.Ehis(handler=self)
        cache_hours = float(self.request.registry.settings.get('ehis.cache.opilane',1))
        MAX_COUNT = 500
        if cache_hours != -1:
            seisuga = datetime.now() - timedelta(hours=cache_hours)

            # leiame õpilased, kelle lõpetamise andmed tuleks EHISest üle kontrollida
            q_kontroll = q.filter(sa.or_(model.Kasutaja.opilane_seisuga==None,
                                         model.Kasutaja.opilane_seisuga<seisuga))
            call_total = q_kontroll.count() / MAX_COUNT + 1
            
            isikukoodid = []
            cnt = call_cnt = 0
            for k in q_kontroll.all():
                isikukoodid.append(k.isikukood)
                cnt += 1
                if cnt >= MAX_COUNT:
                    if not _uuenda(reg, isikukoodid, call_cnt, call_total):
                        return False                   
                    call_cnt += 1
                    cnt = 0
                    isikukoodid = []
                    
            if isikukoodid:
                if not _uuenda(reg, isikukoodid, call_cnt, call_total):
                    return False

        return True

    def _maara_lopetamisaasta(self, aasta):
        # jooksva aasta lõpetamise kontrollimisel määrab süsteem ise lõpetamisaasta nendele,
        # kes on EISi teada lõpetamata ning on registreeritud jooksva aasta
        # riigieksamite või rahvusvaheliste eksamite testsessioonidel mõnele testile
        # ja kelle klassi tähis on G3 või G12.
        q = (model.SessionR.query(model.Testsessioon.id)
             .filter(model.Testsessioon.oppeaasta==aasta)
             .filter(model.Testsessioon.testiliik_kood.in_((const.TESTILIIK_RIIGIEKSAM,
                                                            const.TESTILIIK_RV))
                     )
             )
        testsessioonid_id = [s_id for s_id, in q.all()]
        if testsessioonid_id:
            q = (model.Kasutaja.query
                 .join(model.Kasutaja.opilased)
                 .filter(model.Opilane.on_lopetanud==False)
                 .filter(model.Opilane.seisuga>date(aasta-1, 11, 1)) # eelmise aasta 1.nov
                 .filter(model.Opilane.klass.in_(('G3','G12')))
                 .filter(sa.or_(model.Kasutaja.lopetanud==False,
                                model.Kasutaja.lopetanud==None))
                 .filter(sa.or_(model.Kasutaja.lopetamisaasta==None,
                                model.Kasutaja.lopetamisaasta<aasta))
                 .filter(sa.exists().where(
                     sa.and_(
                         model.Kasutaja.id==model.Sooritaja.kasutaja_id,
                         model.Sooritaja.klass.in_(('G3','G12')),
                         model.Sooritaja.testimiskord_id==model.Testimiskord.id,
                         model.Testimiskord.testsessioon_id.in_(testsessioonid_id))
                     ))
                 )
            n = 0
            for kasutaja in q.all():
                kasutaja.lopetamisaasta = aasta
                if kasutaja.lopetanud_kasitsi is None:
                    kasutaja.lopetanud_kasitsi = False
                n += 1
            log.info('%d õpilasele seatud lõpetamisaasta %d' % (n, aasta))
            model.Session.commit()
        
    def _kontroll_kasutaja(self, k, all_errors):
        """Tingimused alates 2014 (EH-202)
        
        Peab olema sooritatud järgmiste ainete riigi- või rahvusvahelised eksamid.
        1)	Eesti keel või eesti keel teise keelena riigieksam või eesti keele tasemeeksam C1-tase või kõrgtase
        2)	Matemaatika
        3)	Võõrkeel (peab olema täidetud vähemalt üks tingimus)
        -	Inglise, saksa, vene või prantsuse keele riigieksam
        -	Saksa, vene või prantsuse keele rahvusvaheline eksam B1- või B2-tasemel
            (tulemus vähemalt 1%, tase ei pea olema saavutatud)
        -	Õpilane on esitanud rahvusvaheliselt tunnustatud võõrkeeleeksami tunnistuse ning
        selle andmed on kantud EIS-i vastavasse registrisse, kus märkeruudus „Arvestatakse lõpetamise“ on linnuke sees.

        Õpilane saab lõpetada, kui eksamitulemus on:
        Alates 2014. a – 1% maksimaalsest tulemusest,
        2002-2012. a – 20 punkti,
        1997-2001. a – 1 punkt.
        """
        errors = []
        
        # kontrollime lõpetamise tingimusi
        q = model.SessionR.query(model.Sooritaja.pallid,
                                model.Sooritaja.tulemus_protsent,
                                model.Testimiskord.aasta).\
            filter(model.Sooritaja.kasutaja_id==k.id).\
            filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD).\
            join(model.Sooritaja.test).\
            join(model.Sooritaja.testimiskord).\
            filter(model.Testimiskord.tulemus_kinnitatud==True)
       
        def check_riigieksam(pallid, protsent, aasta):
            if aasta >= 2014:
                return protsent >= 1
            elif aasta >= 2002:
                return pallid >= 20
            elif aasta < 2002:
                return pallid >= 1

        # kas on eesti keel või eesti keel teise keelena riigieksam sooritatud
        rc = False
        q1 = q.filter(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM).\
             filter(model.Test.aine_kood.in_((const.AINE_ET, const.AINE_ET2)))
        for r in q1.all():
            pallid, protsent, aasta = r
            if check_riigieksam(pallid, protsent, aasta):
                rc = True
                break
        if not rc:
            # kas on eesti keele tasemeeksam sooritatud
            tasemed = (const.KEELETASE_C1, const.KEELETASE_KORG)
            q1 = q.filter(model.Test.testiliik_kood==const.TESTILIIK_TASE).\
                 filter(model.Sooritaja.keeletase_kood.in_(tasemed)).\
                 filter(model.Sooritaja.tulemus_piisav==True)
            for r in q1.all():
                rc = True
                break
        if not rc:
            err = _("Eesti keele eksam sooritamata")
            if all_errors:
                errors.append(err)
            else:
                return False, err

        # kas on matemaatika riigieksam sooritatud
        rc = False
        q1 = q.filter(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM).\
             filter(model.Test.aine_kood==const.AINE_M)
        for r in q1.all():
            pallid, protsent, aasta = r
            if check_riigieksam(pallid, protsent, aasta):
                rc = True
                break
        
        if not rc:
            err = _("Matemaatika riigieksam sooritamata")
            if all_errors:
                errors.append(err)
            else:
                return False, err

        # kas on võõrkeeleeksam sooritatud
        rc = False
        # kas on võõrkeele riigieksam sooritatud
        q1 = q.filter(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM).\
             filter(model.Test.aine_kood.in_((const.AINE_EN, const.AINE_DE, const.AINE_RU, const.AINE_FR)))
        for r in q1.all():
            pallid, protsent, aasta = r
            if check_riigieksam(pallid, protsent, aasta):
                rc = True
                break

        if not rc:
            # kas on rahvusvaheline eksam sooritatud (vähemalt 1%)
            tasemed = (const.KEELETASE_B1, const.KEELETASE_B2)
            q1 = q.filter(model.Test.testiliik_kood==const.TESTILIIK_RV).\
                 filter(model.Test.aine_kood.in_((const.AINE_DE, const.AINE_RU, const.AINE_FR))).\
                 filter(model.Test.testitasemed.any(model.Testitase.keeletase_kood.in_(tasemed)))
            for r in q1.all():
                pallid, protsent, aasta = r
                if check_riigieksam(pallid, protsent, aasta):
                    rc = True
                    break

        if not rc:
            # kas on rahvusvahelise keeletunnistuse saanud
            q1 = model.SessionR.query(model.Rvsooritaja.id).\
                join(model.Rvsooritaja.tunnistus).\
                filter(model.Tunnistus.kasutaja_id==k.id).\
                filter(model.Rvsooritaja.arvest_lopetamisel==True)
            for r in q1.all():
                rc = True
                break
            
        if not rc:
            err = _("Võõrkeele eksam sooritamata")
            if all_errors:
                errors.append(err)
            else:
                return False, err

        if errors:
            return False, ', '.join(errors)
        return True, None

    def _search_protsessid(self, q):
        q = (q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_LOPETAMINE)
             .filter(model.Arvutusprotsess.aasta==self.c.aasta)
             )
        return q

    def _paginate_protsessid(self, q):
        # ei pagineeri
        return q.all()
