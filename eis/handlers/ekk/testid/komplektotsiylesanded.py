from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class KomplektOtsiylesandedController(BaseResourceController):

    _permission = 'ekk-testid'
    _MODEL = model.Testiylesanne
    _EDIT_TEMPLATE = 'ekk/testid/komplekt.otsiylesanded.mako'
    _INDEX_TEMPLATE = 'ekk/testid/komplekt.otsiylesanded.mako'
    _LIST_TEMPLATE = 'ekk/testid/komplekt.otsiylesanded_list.mako'
    _ITEM_FORM = forms.ekk.testid.KomplektOtsiylesandedForm 
    _DEFAULT_SORT = 'ylesanne.id' # vaikimisi sortimine

    def _showlist(self):
        """Otsingu tulemuste kuvamine.
        """
        return self.render_to_response(self._LIST_TEMPLATE)

    def _query(self):
        return model.Ylesanne.query

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.

        Testiülesandeks lisatav ülesanne peab vastama järgmistele tingimustele:

        - ülesande olek on "testi kandidaat", "ankur" või "eeltesti kandidaat"
        - testi toimumiskordade soorituskeeled peavad olema olema
        ülesande põhikeele ja tõlkekeelte hulgas
        - ülesande vastamise vorm ja sobivus tavatestiks / sobivus e-testiks
        vastab testiosa kohta määratud vastamise vormiga ja lahendamise liigiga
        - ülesanne ei ole ülesandekomplekti ülesannete hulgas.

        - mille õppeaine võrdub testi õppeainega
        - mille testi liikide hulgas on testi testiliik
        - mida ei ole üheski testis kasutatud (välja arvatud eeltestid),
        - mis vastvad testiülesande juures esitatud ja otsinguvormil märgitud parameetritele
        (teema, valdkond, mõtlemistasand, kasutusmäär, kooliaste,
        hindepallide arv, raksus, eristusjõud, tüüp)
        """
        
        if self.c.ylesanne_id:
            q = q.filter(model.Ylesanne.id==int(self.c.ylesanne_id))
            item = model.Ylesanne.get(self.c.ylesanne_id)
            if not item:
                self.error(_("Valitud ID-ga ülesannet ei ole"))
                return None
            if item:
                # kontrollitakse vastavust tingimustele
                q = filter_y_st(self, q, self.c.test, False)
                if q.count() == 0:
                    self.error(_("Valitud ID-ga ülesanne pole kättesaadav"))
                    # rohkem ei selgita
                    return q
                
                for vy in item.valitudylesanded:
                    if vy.komplekt == self.c.komplekt:
                        self.error(_("Valitud ID-ga ülesanne on juba selles komplektis kasutusel"))
                        return None
                ty = model.Testiylesanne.get(self.c.testiylesanne_id)
                rc, message = check_ylesanne(self, item, ty, self.c.komplekt)
                if message:
                    self.error(message)
                if rc:
                    return q
                else:
                    return None

        return filter_ylesanne(self,
                               q,
                               self.c.test,
                               self.c.komplekt,
                               aine=self.c.aine,
                               valdkond=self.c.valdkond,
                               teema=self.c.teema,
                               keeletase=self.c.keeletase,
                               mote=self.c.mote,                              
                               aste=self.c.aste,
                               max_pallid=self.c.max_pallid,
                               tyyp=self.c.tyyp,
                               kasutusmaar=self.c.kasutusmaar,
                               hindamine=self.c.hindamine,
                               arvutihinnatav=self.c.arvutihinnatav)

    def show(self):
        return 'Viga'

    def edit(self):
        # suures aknas parajasti otsingus kasutusel olev komplekt_id,
        # hoiame meeles, et hiljem (peale ylesande salvestamist)
        # suurt akent kuvades seda kasutada
        id = self.request.matchdict.get('id')

        self.c.komplekt_id2 = self.request.params.get('komplekt_id2')

        testiylesanne_id = self.request.matchdict.get('testiylesanne_id')
        self.c.testiylesanne = model.Testiylesanne.get(testiylesanne_id)

        komplekt_id = self.request.matchdict.get('komplekt_id')
        self.c.komplekt = model.Komplekt.get(komplekt_id)

        return self.render_to_response(self._EDIT_TEMPLATE)

    def update(self):
        """id on seq
        """
        id = self.request.matchdict.get('id')
        
        # ylesande pesa
        testiylesanne_id = self.request.matchdict.get('testiylesanne_id')
        ty = self.c.testiylesanne = model.Testiylesanne.get(testiylesanne_id)

        # komplekt
        komplekt = model.Komplekt.get(self.c.komplekt_id)
        testiosa_id = ty.testiosa_id

        # valitudylesanne
        v = ty.give_valitudylesanne(komplekt, id)
        ## f_ylesanne_id on sisestusväli, ylesanne_id on checkbox
        for key in self.request.params:
            # submit-nupu "Vali" nimi oli "ylesanne_id_ID", siit saame lisatava ylesande ID
            prefix = 'ylesanne_id_'
            if key.startswith(prefix):
                ylesanne_id = int(key[len(prefix):])

        ylesanne = model.Ylesanne.get(ylesanne_id)
        if ylesanne.max_pallid is None:
            ylesanne.max_pallid = ylesanne.get_max_pallid()
        if ylesanne.salastatud and not ylesanne._has_use_permission(self.c.user.get_kasutaja()):
            self.error(_("Puudub õigus salastatud ülesande testi lisamiseks"))
        else:
            # eemaldame vanalt ülesandelt lukustuse
            old_ylesanne = v.ylesanne_id and model.Ylesanne.get(v.ylesanne_id)
            v.ylesanne_id = ylesanne_id
            if ty.max_pallid is None:
                # testiylesande pallid määratakse esimese valitud ülesande pallidega
                if not ty.testiosa.lotv:
                    ty.max_pallid = ylesanne.max_pallid or 0
                self.c.test.arvuta_pallid()

            v.update_koefitsient(ty)

            model.Session.commit()
            self.success()
        
        komplekt_id2 = self.request.params.get('komplekt_id2')
        komplektivalik_id = self.request.params.get('komplektivalik_id')
        return HTTPFound(location=self.url('test_valitudylesanded', 
                                           test_id=self.c.test.id, 
                                           komplekt_id=komplekt_id2,
                                           komplektivalik_id=komplektivalik_id,
                                           testiosa_id=testiosa_id))

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.komplekt_id = self.request.matchdict.get('komplekt_id')
        self.c.komplekt = model.Komplekt.get(self.c.komplekt_id)
        self.c.komplektivalik = self.c.komplekt.komplektivalik
        self.c.komplektivalik_id = self.c.komplektivalik.id
        self.c.testiylesanne_id = self.request.matchdict.get('testiylesanne_id')
        self.c.seq = self.request.matchdict.get('id')
        self.c.test = model.Test.get(test_id)

        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}

def filter_y_st(handler, q, test, valmis):
    "Kontrollitakse ylesande oleku sobivust"
    if test.testityyp == const.TESTITYYP_EKK:
        if valmis:
            # tingimuste järgi otsides peab olema valmis ylesanne
            q = q.filter(model.Ylesanne.staatus.in_((const.Y_STAATUS_TEST,
                                                     const.Y_STAATUS_ANKUR,
                                                     const.Y_STAATUS_EELTEST)))
        else:
            # ID järgi otsides võivad olla igasugused EKK ylesanded, ka pooleliolevad
            q = q.filter(~ model.Ylesanne.staatus.in_(const.Y_ST_AV))

    elif test.testityyp == const.TESTITYYP_AVALIK:
        # võib kasutada neid ylesandeid, kus ise on koostaja
        # või mis on avalik
        # või mis on pedagoogidele lubatud, kui ise on kuskil pedagoog
        today = date.today()
        user = handler.c.user
        f_minu = sa.and_(
            model.Ylesanne.staatus.in_(const.Y_ST_AV),
            model.Ylesanne.ylesandeisikud.any(sa.and_(
                model.Ylesandeisik.kasutajagrupp_id==const.GRUPP_Y_KOOSTAJA,
                model.Ylesandeisik.kasutaja_id==user.id,
                model.Ylesandeisik.kehtib_alates<=today,
                model.Ylesandeisik.kehtib_kuni>=today))
            )
        f_st = sa.or_(f_minu, model.Ylesanne.staatus==const.Y_STAATUS_AVALIK)
        if user.on_pedagoog:
            f_st = sa.or_(f_st, model.Ylesanne.staatus==const.Y_STAATUS_PEDAGOOG)
        q = q.filter(f_st)

    return q

def filter_ylesanne(handler, q, test, komplekt, **args):
    """Tingimused, millele valitud ülesanne peab vastama.
    """
    c_aine = args.get('aine')
    c_valdkond = args.get('valdkond')
    c_teema = args.get('teema')
    c_keeletase = args.get('keeletase')
    c_mote = args.get('mote')
    c_aste = args.get('aste')
    c_max_pallid = _float_or_none(args.get('max_pallid'))
    c_tyyp = args.get('tyyp')
    c_kasutusmaar = _int_or_none(args.get('kasutusmaar'))
    c_hindamine = args.get('hindamine')
    c_arvutihinnatav = args.get('arvutihinnatav') and True or False
    salastamata = args.get('salastamata') and True or False
    if salastamata:
        q = q.filter(model.Ylesanne.salastatud==const.SALASTATUD_POLE)
    
    # kontrollime, et ylesanne juba ei esineks selles komplektis
    q = q.filter(~ model.Ylesanne.valitudylesanded.any(model.Valitudylesanne.komplekt_id==komplekt.id))
    q = filter_y_st(handler, q, test, True)
                        
    testiosa = komplekt.komplektivalik.testiosa
    q = q.filter(model.Ylesanne.vastvorm_kood==testiosa.vastvorm_kood) # kirjalik, suuline
    # kui on kirjalik, siis peab sobima la lahendamise liik
    if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
        q = q.filter(model.Ylesanne.etest==True)
    elif testiosa.vastvorm_kood == const.VASTVORM_KP:
        q = q.filter(model.Ylesanne.ptest==True)

    for lang in komplekt.keeled:
        q = q.filter(model.Ylesanne.skeeled.like('%' + lang + '%'))

    f_aine = model.Ylesandeaine.aine_kood==c_aine
    if c_valdkond:
        if c_teema:
            f_teema = (model.Ylesandeaine.ylesandeteemad
                       .any(sa.and_(model.Ylesandeteema.teema_kood==c_valdkond,
                                    model.Ylesandeteema.alateema_kood==c_teema)
                            )
                       )
        else:
            f_teema =(model.Ylesandeaine.ylesandeteemad
                      .any(model.Ylesandeteema.teema_kood==c_valdkond))
        f_aine = sa.and_(f_aine, f_teema)
    q = q.filter(model.Ylesanne.ylesandeained.any(f_aine))
    
    if c_keeletase:
        q = q.filter_by(keeletase_kood=c_keeletase)
    if c_mote:
        q = q.filter(model.Ylesanne.motlemistasandid\
                     .any(model.Motlemistasand.kood==c_mote))
    if c_aste:
        aste_bit = model.Opt.aste_bit(c_aste) or 0
        q = q.filter(model.Ylesanne.aste_mask.op('&')(aste_bit) > 0)                                                

    if c_max_pallid:
        # komakohtadega arvu korral ei pruugi = toimida
        diff = 1e-12
        q = q.filter(model.Ylesanne.max_pallid>c_max_pallid - diff).\
            filter(model.Ylesanne.max_pallid<c_max_pallid + diff)
    if c_tyyp:
        q = q.filter(model.Ylesanne.sisuplokid\
                         .any(model.Sisuplokk.tyyp==c_tyyp))
    if c_arvutihinnatav:
        q = q.filter_by(arvutihinnatav=True)
    else:
        q = q.filter_by(arvutihinnatav=False)

    if c_hindamine:
        q = q.filter_by(hindamine_kood=c_hindamine)
    if c_kasutusmaar:
        q = q.filter(model.Ylesanne.kasutusmaar<=int(c_kasutusmaar))
    return q

def check_ylesanne(handler, item, ty, komplekt, check_all=False):
    """Kontrollitakse, kas antud ülesanne vastab tingimustele.
    item - ylesanne
    ty - testiylesanne
    komplekt - komplekt
    check_all - kas kontrollida kõigi testiylesande parameetrite täidetust
    """
    def _quot(s):
        request = handler.request
        return s and '"%s"' % s or _("määramata")

    testiosa = ty.testiosa
    test = handler.c.test
    rc = True

    li = []
    yained = list(item.ylesandeained)
    if testiosa.test.aine_kood not in [yaine.aine_kood for yaine in yained]:
        aine_nimed = ', '.join([yaine.aine_nimi for yaine in yained if yaine.aine_nimi])
        li.append(_("õppeaine on ") + ' ' + aine_nimed)
    if test.testityyp == const.TESTITYYP_EKK:
        if item.staatus not in (const.Y_STAATUS_TEST,
                                const.Y_STAATUS_ANKUR,
                                const.Y_STAATUS_EELTEST):
            li.append(_("olek on ") + ' "%s"' % item.staatus_nimi)
    if item.vastvorm_kood != testiosa.vastvorm_kood:
        li.append(_("vastamise vorm on ") + _quot(item.vastvorm_nimi))
    if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I) and not item.etest:
        li.append(_("pole sobiv e-testiks"))
    elif testiosa.vastvorm_kood == const.VASTVORM_KP and not item.ptest:
        li.append(_("pole sobiv p-testiks"))

    if not set(komplekt.keeled).issubset(set(item.keeled)):
        s = ', '.join(item.keeled)
        li.append(_("keel on ") + _quot(s))

    # testiülesande parameetrite kontroll
    missing = _("määramata")
    if (check_all or handler.c.valdkond) and ty.teema_kood:
        found = False
        values = []
        for yaine in yained:
            if ty.teema_kood in [t.teema_kood for t in yaine.ylesandeteemad]:
                found = True
                break
            values.extend([t.teema_nimi or '' for t in yaine.ylesandeteemad if t.teema_kood])
        if not found:
            s = ', '.join(set(values))
            li.append(_("teema on ") + _quot(s))

    if (check_all or handler.c.teema) and ty.alateema_kood:
        found = False
        values = []
        for yaine in yained:
            if ty.alateema_kood in [t.alateema_kood for t in yaine.ylesandeteemad]:
                found = True
                break
            values.extend([t.alateema_nimi or '' for t in yaine.ylesandeteemad if t.alateema_kood])
        if not found:
            s = ', '.join(set(values))
            li.append(_("alateema on ") + _quot(s))

    if (check_all or handler.c.keeletase) and ty.keeletase_kood and \
           ty.keeletase_kood != item.keeletase_kood:
        if item.keeletase_kood:
            li.append(_("keeleoskuse tase on ") + _quot(item.keeletase_kood))
        else:
            li.append(_("keeleoskuse tase puudub"))

    if (check_all or handler.c.mote) and ty.mote_kood \
            and ty.mote_kood not in [t.kood for t in item.motlemistasandid]:
        s = ', '.join(set([t.nimi or '' for t in item.motlemistasandid]))
        li.append(_("mõtlemistasand on ") + _quot(s))

    if (check_all or handler.c.aste) and ty.aste_kood \
           and not (model.Opt.aste_bit(ty.aste_kood, testiosa.test.aine_kood) & (item.aste_mask or 0)):
        li.append(_("kooliaste on ") + _quot(item.aste_nimed))

    if (check_all or handler.c.hindamine) and ty.hindamine_kood \
            and ty.hindamine_kood != item.hindamine_kood:
        li.append(_("hindamise liik on ") + _quot(item.hindamine_nimi))

    if (check_all or handler.c.arvutihinnatav) and ty.arvutihinnatav \
            and not item.arvutihinnatav:
        li.append(_("pole arvutiga hinnatav"))
        rc = False
    elif (check_all or not handler.c.arvutihinnatav) and not ty.arvutihinnatav \
            and item.arvutihinnatav:
        li.append(_("ülesanne on arvutiga hinnatav"))

    if (check_all or handler.c.max_pallid) and ty.max_pallid is not None \
            and ty.max_pallid != item.max_pallid:
        li.append(_("pallide arv on ") + _quot(handler.h.fstr(item.max_pallid)))

    #if (check_all or handler.c.raskus) and ty.raskus is not None \
    #        and ty.raskus != item.raskus:
    #    li.append(_("raskusindeks on ") + _quot(handler.h.fstr(item.raskus)))

    #if (check_all or handler.c.eristusindeks) and ty.eristusindeks is not None \
    #        and ty.eristusindeks != item.eristusindeks:
    #    li.append(_("eristusindeks on ") + _quot(handler.h.fstr(item.eristusindeks)))

    if (check_all or handler.c.tyyp) and ty.tyyp \
            and ty.tyyp not in [p.tyyp for p in item.sisuplokid]:
        s = ', '.join(set([p.tyyp_nimi for p in item.sisuplokid]))
        li.append(_("tüüp on ") + _quot(s))

    if (check_all or handler.c.kasutusmaar) and ty.kasutusmaar is not None \
            and ty.kasutusmaar != item.kasutusmaar:
        li.append(_("kasutusmäär on ") + _quot(item.kasutusmaar))

    if len(li):
        if len(li) == 1:
            buf = li[0]
        else:
            buf = ', '.join(li[:-1])
            buf += _(" ja ") + li[-1]
        message = _("Ülesanne {id} ei vasta tingimustele, sest {s}").format(id=item.id, s=buf)
    else:
        message = None
    return rc, message

def _float_or_none(s):
    if s:
        if isinstance(s, str):
            s = s.replace(',','.')
        return float(s)

def _int_or_none(s):
    if s:
        return int(s)
