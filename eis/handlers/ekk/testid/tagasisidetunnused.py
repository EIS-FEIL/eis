from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
from eis.lib.npcalc import get_np_task_locals, get_dummy_osa_np
_ = i18n._

log = logging.getLogger(__name__)

class TagasisidetunnusedController(BaseResourceController):
    """Testiosa normipunktid (profiililehe seaded)
    """
    _permission = 'ekk-testid'
    _MODEL = model.Normipunkt
    _INDEX_TEMPLATE = 'ekk/testid/tagasiside.tunnused.mako'
    _EDIT_TEMPLATE = 'ekk/testid/normipunkt.mako'
    #_index_after_create = True
   
    @property
    def _ITEM_FORM(self):
        if self.request.params.get('op') == 'jrk':
            # normipunktide järjekorra ja gruppide salvestamine
            return forms.ekk.testid.TagasisideTunnusedForm
        elif self.c.lang:
            return forms.ekk.testid.TranTagasisideTunnusForm
        else:
            return forms.ekk.testid.TagasisideTunnusForm

    def _new(self, item):
        copy_id = self.request.params.get('copy_id')
        if copy_id:
            # kopeerime olemasoleva tunnuse
            orig = model.Normipunkt.get(copy_id)
            assert orig.testiosa_id == self.c.testiosa.id, 'vale testiosa'

            kood = None
            if orig.kood:
                # genereerime uue koodi
                npkoodid = [np.kood for np in self.c.testiosa.normipunktid]
                for n in range(1, 100):
                    kood = f'{orig.kood}_{n}'
                    if kood not in npkoodid:
                        break
            self.c.item = orig.copy()
            self.c.item.kood = kood
            return
        
        # kasutame vaikimisi vahemikke, kui need on seatud
        params = self._get_default_params('test_normipunkt_d2')
        if params:
            li = params.get('ns_range')
            if li:
                for tehe, vaartus in li:
                    ns = model.Nptagasiside(tingimus_tehe=tehe,
                                            tingimus_vaartus=vaartus)
                    item.nptagasisided.append(ns)
            item.normityyp = params.get('normityyp')
            item.kysimus_kood = params.get('kysimus_kood')

    def _create(self, **kw):
        if self.request.params.get('op') == 'jrk':
            self._create_jrk()
            return HTTPFound(location=self.url_current('index'))
        else:
            item = model.Normipunkt(testiosa_id=self.c.testiosa.id)
            item.testiosa = self.c.testiosa
            self._update(item)
            return item

    def _create_jrk(self):
        "Normipunktide järjekorra ja gruppide salvestamine"
  
        order = []
        for key in self.request.params:
            # järjestus vastavalt lohistamise tulemusele
            m = re.match(r'normid-(\d+)\.id', key)
            if m:
                ind = int(m.groups()[0])
                order.append(ind)
            
        normid = self.form.data.get('normid')
        for ind_r, r in enumerate(normid):
            if ind_r in order:
                r['seq'] = order.index(ind_r)

        # uute normipunktide loomist siin ei toimu
        BaseGridController(self.c.testiosa.normipunktid,
                           model.Normipunkt,
                           parent_controller=self).save(normid)
        log.debug(order)
        model.Session.commit()

    def _set_ting(self):
        # jätame meelde, kas kuvada tingimusi
        self.c.ting = ting = int(self.request.params.get('ting') or 1)
        self._set_default_params({'ting': ting}, 'test_tagasiside_tunnused_ting')
    
    def _get_ting(self):
        # kas kuvada tingimusi
        params = self._get_default_params('test_tagasiside_tunnused_ting') or {}
        ting = params.get('ting') # kas kuvada tingimused
        self.c.ting = ting is None and 1 or ting

    def _index_d(self):
        if self.request.params.get('ting'):
            self._set_ting()
        else:
            self._get_ting()
        
        if self.c.test.diagnoosiv:
            errors = {}
            for np in self.c.testiosa.normipunktid:
                rootprefix = 'np%d' % np.id
                self._kontroll_diag_np(np, errors, rootprefix)
            if errors:
                self.c.errors = errors
            log.debug(errors)
        return self.response_dict

    def _index_tree(self):
        "Diagnoosiva testi tagasiside puu"
        return self.render_to_response('/ekk/testid/normipunktid.diag.tree.mako')
    
    def _kontroll_diag_np(self, np, errors, rootprefix):
        "Tingimuste kontroll diagnoosiva testi korral"
        h_request = self.request # tõlkimise jaoks 
        grupp = np.ylesandegrupp or np.testiylesanne
        if not grupp:
            errors['%s.testiylesanne_id' % rootprefix] = _("puudub")
            return
        min_val = max_val = 0
        on_valik = on_valem = False
        if np.kysimus_kood and np.normityyp != const.NORMITYYP_VALEM:
            ty = np.testiylesanne
            if not ty:
                errors['%s.normityyp' % rootprefix] = _("Vigane väärtus")
                return
            q = (model.Session.query(model.Valitudylesanne.ylesanne_id)
                 .filter(model.Valitudylesanne.testiylesanne_id==ty.id)
                 .filter(model.Valitudylesanne.ylesanne_id!=None))
            ylesanded_id = [y_id for y_id, in q.all()]
            kysimus = (model.Session.query(model.Kysimus)
                       .join(model.Kysimus.sisuplokk)
                       .filter(model.Kysimus.kood==np.kysimus_kood)
                       .filter(model.Sisuplokk.ylesanne_id.in_(ylesanded_id))
                       .first())
            if kysimus:
                if np.normityyp == const.NORMITYYP_VASTUS:
                    # valikvastustega kysimus
                    on_valik = True
                    valikud = [v.kood for v in kysimus.valikud]
                elif np.normityyp == const.NORMITYYP_PUNKTID:
                    # kysimuse toorpunktid
                    tulemus = kysimus.tulemus
                    max_val = tulemus.get_max_pallid() or 0
            else:
                if np.normityyp == const.NORMITYYP_VASTUS:
                    # tabamuste loendur
                    q = (model.Session.query(sa.func.count(model.Hindamismaatriks.id))
                         .filter(model.Hindamismaatriks.tahis==np.kysimus_kood)
                         .join(model.Hindamismaatriks.tulemus)
                         .filter(model.Tulemus.ylesanne_id.in_(ylesanded_id)))
                    max_val = q.scalar()

            if not kysimus and not max_val:
                errors['%s.kysimus_kood' % rootprefix] = _("Küsimust ei leitud")
                return
        elif np.normityyp == const.NORMITYYP_VALEM:
            # valemi min ja max ei ole teada
            on_valem = True
        elif np.normityyp == const.NORMITYYP_PALLID:
            max_val = grupp.max_pallid or 0
        elif np.normityyp == const.NORMITYYP_PROTSENT:
            max_val = 100

        is_float_eq = np.normityyp == const.NORMITYYP_PROTSENT # kas arvestada komakohtadega arve
        diff = 1e-7

        fstr = self.h.fstr
        ahelad = {}
        class Ahel(object):
            def __init__(self):
                self.u_min = min_val # vähim väärtus, mis ei saa tagasisidet
                self.u_max = max_val # suurim väärtus, mis ei saa tagasisidet
                self.min_eq = True # kas vähim väärtus, mis ei saa tagasisidet, on täpne vahemiku ots
                self.max_eq = True # kas suurim väärtus, mis ei saa tagasisidet, on täpne vahemiku ots
                self.equals = [] # võrdusmärgiga väärtused
                self.tabatud_valikud = []

            def __repr__(self):
                buf = '%s%s-%s%s' % (self.min_eq and '[' or '(',
                                     fstr(self.u_min),
                                     fstr(self.u_max),
                                     self.max_eq and ']' or ')')
                if self.equals:
                    buf += ' [%s]' % (', '.join([fstr(r) for r in self.equals]))
                return f'Ahel {buf}'

            @classmethod
            def give_ahel(cls, ty_id):
                ahel = ahelad.get(ty_id)
                if not ahel:
                    ahelad[ty_id] = ahel = Ahel()
                    if ty_id:
                        # uue ahela algväärtuseks ilma ahelata variant
                        ahel0 = ahelad.get(None)
                        if ahel0:
                            ahel.u_min = ahel0.u_min
                            ahel.u_max = ahel0.u_max
                            ahel.min_eq = ahel0.min_eq
                            ahel.max_eq = ahel0.max_eq
                            ahel.equals = list(ahel0.equals)
                            ahel.tabatud_valikud = list(ahel0.tabatud_valikud)
                return ahel

        def _get_ty_ahelad():
            # leitakse kõik mitte-vaikimisi ahelad
            for k, v in list(ahelad.items()):
                if k:
                    yield v

        def _check_ns(ns, on_valik, ahel, is_ahel0):
            request = h_request
            err = None
            is_reachable = False
            tehe = ns.tingimus_tehe
            value = ns.tingimus_vaartus
            valik = ns.tingimus_valik
            if on_valik:
                if valik is None:
                    err = _("Valikvastus sisestamata")
                elif valik not in valikud:
                    err = _("Vastust ei leitud")
                else:
                    for r in valikud:
                        if r not in ahel.tabatud_valikud:
                            if ns.tingimus_tehe == '>' and r > valik or \
                               ns.tingimus_tehe == '>=' and r >= valik or \
                               ns.tingimus_tehe == '==' and r == valik or \
                               ns.tingimus_tehe == '<=' and r <= valik or \
                               ns.tingimus_tehe == '<' and r < valik:
                                ahel.tabatud_valikud.append(r)
                                is_reachable = True

            elif not on_valem:
                if (value - diff > max_val) or (value + diff < min_val):
                    err = _("Väärtus on võimalikust vahemikust väljas")

                err = None
                if ahel.u_min > ahel.u_max or \
                        ahel.u_min == ahel.u_max and not ahel.min_eq and not ahel.max_eq:
                    # pole saavutatav
                    pass

                elif tehe == '<':
                    if value > ahel.u_min:
                        ahel.u_min = value
                        ahel.min_eq = True
                        is_reachable = True

                elif tehe == '<=':
                    if value + diff > ahel.u_min:
                        ahel.u_min = value
                        ahel.min_eq = False
                        is_reachable = True

                elif tehe == '>':
                    if value < ahel.u_max:
                        ahel.u_max = value
                        ahel.max_eq = True
                        is_reachable = True

                elif tehe == '>=':
                    if value - diff < ahel.u_max:
                        ahel.u_max = value
                        ahel.max_eq = False
                        is_reachable = True

                elif tehe == '==':
                    if value - diff < ahel.u_max and \
                           value + diff > ahel.u_min:
                        if value not in ahel.equals:
                            is_reachable = True
                            ahel.equals.append(value)
                            if round(value) != value:
                                is_float_eq = True

            if is_ahel0:
                # kui on vaikimisi ahela tingimus, siis kontrollime ka kõiki muid ahelaid
                for ahel1 in _get_ty_ahelad():
                    err1 = _check_ns(ns, on_valik, ahel1, False)
                    if not err1:
                        # leidsime teise ahela, kus ei tingimus ei andnud viga ehk oli saavutatav
                        is_reachable = True

            if not is_reachable and not err and not on_valem:
                err = _("Pole saavutatav")
            return err

        for ns in np.nptagasisided:
            ahel = Ahel.give_ahel(ns.ahel_testiylesanne_id)
            is_ahel0 = not ns.ahel_testiylesanne_id
            err = _check_ns(ns, on_valik, ahel, is_ahel0)
            if err:
                prefix = '%s.ns%d' % (rootprefix, ns.id)
                errors[prefix + '.tagasiside'] = err

        for ahel_ty_id, ahel in ahelad.items():
            err = None
            #log.debug(ahel)
            if on_valik:
                tabamata = [r for r in valikud if r not in ahel.tabatud_valikud]
                if tabamata:
                    err = _("Valikud {s} ei ole kaetud").format(s=', '.join(tabamata))

            elif on_valem:
                pass
            elif ahel.u_min < ahel.u_max or \
                     ahel.u_min == ahel.u_max and ahel.min_eq and ahel.max_eq:
                srange = '%s%s, %s%s' % (ahel.min_eq and '[' or '(', self.h.fstr(ahel.u_min),
                                         self.h.fstr(ahel.u_max), ahel.max_eq and ']' or ')')
                if ahel.equals:
                    sequals = ', '.join([fstr(r) for r in ahel.equals])
                    err = _("Vahemik {s} ei ole kaetud (välja arvatud {s2})").format(s=srange, s2=sequals)
                else:
                    err = _("Vahemik {s} ei ole kaetud").format(s=srange)
                if round(ahel.u_min) != ahel.u_min or round(ahel.u_max) != ahel.u_max:
                    # kui vahemikes on kasutatud komaga arve, siis arvestame reaalarve
                    is_float_eq = True

                if ahel.u_min == ahel.u_max and ahel.u_min in ahel.equals:
                    # katmata vahemik koosneb yhest arvust, mille kohta on võrdus olemas
                    err = None
                elif not is_float_eq:
                    # kui on ainult täisarvud ja kõik täisarvud on võrdusmärgiga olemas, siis pole probleemi
                    r_min = int(ahel.u_min)
                    if not ahel.min_eq:
                        r_min += 1
                    r_max = int(ahel.u_max)
                    if not ahel.max_eq:
                        r_max -= 1
                    rng = [v for v in range(r_min, r_max+1) if v not in ahel.equals]
                    if not rng:
                        err = None

            if err:
                if ahel_ty_id:
                    r = (model.Session.query(model.Valitudylesanne.ylesanne_id)
                         .filter_by(testiylesanne_id=ahel_ty_id)
                         .first())
                    ahel_y_id = r and r[0] or None
                    err += ' (%s %s)' % (_("ahel"), ahel_y_id)
                key = rootprefix + '.id'
                if not errors.get(key) or not ahel_ty_id:
                    # kui seal juba on viga märgitud,
                    # siis kirjutame selle yle ainult vaikimisi ahela vea korral
                    errors[key] = err
    
    def _get_opt_k_valik(self, ty_id, alatest_id):
        "Ylesande kysimuste loetelu ja valikkysimuste valikud"
        opt_kood = []
        valikud = {}
        if ty_id or alatest_id: 
            q = (model.SessionR.query(model.Valitudylesanne.ylesanne_id)
                 .filter(model.Valitudylesanne.ylesanne_id!=None)
                 )
            if ty_id:
                q = q.filter_by(testiylesanne_id=ty_id)
            else:
                q = (q.join(model.Valitudylesanne.testiylesanne)
                     .filter_by(alatest_id=alatest_id))
            for ylesanne_id, in q.all():
                # kysimuste punktid
                q = (model.SessionR.query(model.Kysimus.id,
                                         model.Kysimus.kood,
                                         model.Sisuplokk.tyyp,
                                         model.Tulemus.max_pallid,
                                         model.Tulemus.max_pallid_arv)
                     .join(model.Kysimus.sisuplokk)
                     .filter(model.Kysimus.kood!=None)
                     .join(model.Kysimus.tulemus)
                     #.filter(model.Kysimus.naita_p_dtestis==True)
                     .filter(model.Sisuplokk.ylesanne_id==ylesanne_id)
                     .order_by(model.Sisuplokk.seq, model.Kysimus.seq))
                for k_id, k_kood, sp_tyyp, max_p, max_p_a in q.all():
                    key = k_kood
                    if max_p is None:
                        max_p = max_p_a
                    s_max_p = self.h.fstr(max_p)
                    label = _("Küsimus {s} ({p}p)").format(s=k_kood, p=s_max_p)
                    opt_kood.append((key, label))

                    # valikvastused
                    if ty_id and sp_tyyp == const.INTER_CHOICE:
                        kysimus = model.Kysimus.get(k_id)
                        k_valikud = [(v.kood, v.kood) for v in kysimus.valikud]
                        valikud[key] = k_valikud

                # lisame tabamuste loendurid
                q = (model.SessionR.query(model.Hindamismaatriks.tahis)
                     .distinct()
                     .filter(model.Hindamismaatriks.tahis!=None)
                     .filter(model.Hindamismaatriks.tahis!='')
                     .join(model.Hindamismaatriks.tulemus)
                     .filter(model.Tulemus.ylesanne_id==ylesanne_id)
                     .order_by(model.Hindamismaatriks.tahis))
                for loendur, in q.all():
                    key = loendur
                    label = _("Tabamuste loendur {s}").format(s=loendur)
                    opt_kood.append((key, label))
                        
        return opt_kood, valikud
    
    def _index_valik(self):
        "Ylesande valikkysimuste loetelu"
        params = self.request.params
        ty_id = params.get('ty_id')
        if ty_id:
            ty_id = int(ty_id)
        alatest_id = params.get('alatest_id')
        if alatest_id:
            alatest_id = int(alatest_id)
        opt_kood, valikud = self._get_opt_k_valik(ty_id, alatest_id)
        data = {'koodid': opt_kood, 'valikud': valikud}
        log.debug(data)
        return Response(json_body=data)

    def _index_ahel(self):
        "Ahelas eespool olevate ylesannete loetelu"
        ty_id = int(self.request.params.get('ty_id') or 0)
        grupp_id = int(self.request.params.get('grupp_id') or 0)
        data = self._leia_ahelas_eelmised(ty_id, grupp_id,0)
        log.debug(data)
        return Response(json_body=data)

    def _leia_ahelas_eelmised(self, testiylesanne_id, ylesandegrupp_id, level):
        # leiame kõik ahelates eespool olevad jätkuylesanded
        ahelas0 = [] # jooksev ylesanne
        ahelas = [] # jooksev ylesanne ja kõik eelmised
        # igaks juhuks piirame võimalikku sygavust
        if level < 100:
            # leiame jooksva normipunkti vahetuks aluseks olevad ylesanded
            if testiylesanne_id:
                ahelas.append(testiylesanne_id)
            if ylesandegrupp_id:
                q = (model.SessionR.query(model.Valitudylesanne.testiylesanne_id)
                     .join(model.Valitudylesanne.grupiylesanded)
                     .filter(model.Grupiylesanne.ylesandegrupp_id==ylesandegrupp_id)
                    )
                for ty_id, in q.all():
                    ahelas.append(ty_id)

            # leiame normipunktid, mille tagasiside suunab antud ylesannetele
            q = (model.SessionR.query(model.Normipunkt.testiylesanne_id,
                                     model.Normipunkt.ylesandegrupp_id)
                 .filter(model.Normipunkt.nptagasisided.any(
                     model.Nptagasiside.uus_testiylesanne_id.in_(ahelas)))
                 )
            if level == 0:
                # esimesel väljakutsel ei lisa jooksvaid ylesandeid ahela listi,
                # vaid väljastame need eraldi muutujas
                ahelas0 = ahelas
                ahelas = []
            for ty_id, grupp_id in q.all():
                ahelas1 = self._leia_ahelas_eelmised(ty_id, grupp_id, level+1)
                ahelas.extend(ahelas1)
        if level == 0:
            return ahelas, ahelas0
        else:
            return ahelas
            
    def _edit(self, item):
        c = self.c
        c.normipunkt = item
        c.ahelas_data = self._leia_ahelas_eelmised(item.testiylesanne_id, item.ylesandegrupp_id, 0)
        
    def _update(self, item):
        c = self.c
        rootprefix = 'np'
        rcd = self.form.data[rootprefix]
        if c.lang:
            return self._update_tran(item, rcd)
        
        on_diag2 = c.test.diagnoosiv
        
        errors = {}

        item.normityyp = normityyp = rcd['normityyp']
        item.kysimus_kood = rcd['kysimus_kood']
        e_locals = get_np_task_locals(self, None, c.test)

        # lisame teised sama testiosa normipunktid
        e_locals.update(get_dummy_osa_np(c.test, c.testiosa.seq, item.seq))
        
        if normityyp == const.NORMITYYP_VASTUS:
            # peab olema yhe kysimuse kood (või mitu koodi?)
            kkood = item.kysimus_kood
            if not kkood:
                raise ValidationError(self,
                                      {'np.kysimus_kood': _("puudub")})

        elif normityyp == const.NORMITYYP_VALEM:
            # pole koolipsyh test
            avaldis = item.kysimus_kood
            if not avaldis:
                raise ValidationError(self,
                                      {'np.avaldis': _("puudub")})
            value, err0, err, buf = model.eval_formula(avaldis, e_locals)
            if err:
                raise ValidationError(self,
                                      {'np.avaldis': err})

        if c.test.tagasiside_mall == const.TSMALL_OPIP:
            # õpipädevus
            # eraldi väljade asemel on vormil üks min_max väli
            # eraldame min_max väljalt min_vaartus ja max_vaartus
            # min_max on kujul min_vaartus-max_vaartus või min_vaartus,...,max_vaartus
            min_vaartus = max_vaartus = None
            min_max = rcd.get('min_max') 
            if min_max:
                m = re.match(r'(-?\d+).*', min_max)
                if m:
                    min_vaartus = int(m.groups()[0])
                m = re.match(r'.*(\d+)', min_max)
                if m:
                    max_vaartus = m.groups()[0]
            rcd['min_vaartus'] = min_vaartus
            rcd['max_vaartus'] = max_vaartus

        item.from_form(rcd, '')
        self._save_protsentiilid(item, rcd)
        self._save_sooritusryhmad(item, rcd)

        if c.test.diagnoosiv:
            # diagnoosivas testis saab kasutada ainult juba tehtud ylesandeid,
            # mitte kogu alatesti või testiosa tulemust
            if not item.ylesandegrupp_id and not item.testiylesanne_id:
                err = _("Diagnoosivas testis saab kasutada ainult juba tehtud ülesandeid, mitte kogu alatesti ega testiosa tulemust")
                raise ValidationError(self,
                                      {'np.testiylesanne_id': err})
            
        # jätame koodi meelde võimalike valemite testimiseks
        kood = rcd.get('kood')
        if kood:
            e_locals[kood] = 0

        if not errors:
            self._save_nptagasisided(item, rcd, errors)
        if errors:
            raise ValidationError(self, errors)

        lang = None
        item.count_tahemargid(lang)
        c.test.sum_tahemargid_lang(lang)

    def _save_protsentiilid(self, item, rcd):
        # psyh
        normityyp = item.normityyp
        pooratud = item.pooratud
        
        protsentiilid = []
        prev_protsentiil = None
        for ind_rp, rp in enumerate(rcd.get('protsentiilid') or []):
            prefix = 'np.protsentiilid-%d' % (ind_rp)
            protsentiil = rp['protsentiil']
            if protsentiil is not None:
                if normityyp == const.NORMITYYP_PALLID:                        
                    item1 = rcd['testiylesanne_id'] and model.Testiylesanne.get(rcd['testiylesanne_id']) or \
                           rcd['alatest_id'] and model.Alatest.get(rcd['alatest_id']) or \
                           self.c.testiosa
                    if item1.max_pallid is not None and protsentiil > item1.max_pallid:
                        raise ValidationError(self,
                                              {'%s.protsentiil' % prefix: _("Viga")},
                                              _("Ei tohi olla suurem kui {n}").format(n=self.h.fstr(item1.max_pallid)))
                elif normityyp == const.NORMITYYP_SUHE:
                    if protsentiil > 1:
                        raise ValidationError(self,
                                              {'%s.protsentiil' % prefix: _("Viga")},
                                              _("Ei tohi olla suurem kui {n}").format(n=1))
                            
                if prev_protsentiil is not None:
                    if protsentiil < prev_protsentiil and not pooratud:
                        raise ValidationError(self,
                                              {'%s.protsentiil' % prefix: _("Viga")},
                                              _("Protsentiilid peavad olema kasvavas järjekorras"))
                    elif protsentiil > prev_protsentiil and pooratud:
                        raise ValidationError(self,
                                              {'%s.protsentiil' % prefix: _("Viga")},
                                              _("Pööratud protsentiilid peavad olema kahanevas järjekorras"))
                prev_protsentiil = protsentiil
                protsentiilid.append(rp)

        ctrl = BaseGridController(item.normiprotsentiilid, model.Normiprotsentiil)
        ctrl.save(protsentiilid)

    def _save_sooritusryhmad(self, item, rcd):
        # õpipädevus
        sooritusryhmad = []
        prev_lavi = None
        for ind_rp, rp in enumerate(rcd.get('sryhmad') or []):
            prefix = 'np.sryhmad-%d' % (ind_rp)
            lavi = rp['lavi']
            if lavi is not None:
                if ind_rp == 0:
                    # esimene vahemik algab alati miinimumväärtusega
                    lavi = rp['lavi'] = rcd['min_vaartus'] or 0
                if prev_lavi is not None and not (ind_rp == 1 and lavi is None):
                    # välja arvatud siis, kui sisestatud arve ei ole
                    if lavi < prev_lavi:
                        raise ValidationError(self,
                                              {'%s.lavi' % prefix: _("Viga"),
                                               'err_sryhmad': _("Väärtused peavad olema kasvavas järjekorras")})
                prev_lavi = lavi
                sooritusryhmad.append(rp)

        if len(sooritusryhmad) == 1:
            # kui ei ole sisestatud arve (on vaid hidden 0 esimese rühma kohta)
            sooritusryhmad = []
        # kui on õpip
        ctrl = BaseGridController(item.sooritusryhmad, model.Sooritusryhm)
        ctrl.save(sooritusryhmad)        

    def _save_nptagasisided(self, item, rcd, errors):
        # kui on diagnoosiv
        npts = self.form.list_in_posted_order('npts', rcd, 'np.')
        if npts:
            # märgime järjekorra
            for ind, r in enumerate(npts):
                r['seq'] = ind
                r['new_seq'] = True
                
            # leiame kõik ahelates eespool olevad jätkuylesanded
            def _leia_ahelas_eelmised(testiylesanne_id, ylesandegrupp_id, level):
                ahelas = []
                # igaks juhuks piirame võimalikku sygavust
                if level < 100:
                    # leiame jooksva normipunkti vahetuks aluseks olevad ylesanded
                    if testiylesanne_id:
                        ahelas.append(testiylesanne_id)
                    if ylesandegrupp_id:
                        q = (model.SessionR.query(model.Valitudylesanne.testiylesanne_id)
                             .join(model.Valitudylesanne.grupiylesanded)
                             .filter(model.Grupiylesanne.ylesandegrupp_id==ylesandegrupp_id)
                            )
                        for ty_id, in q.all():
                            ahelas.append(ty_id)

                    # leiame normipunktid, mille tagasiside suunab antud ylesannetele
                    q = (model.SessionR.query(model.Normipunkt.testiylesanne_id,
                                             model.Normipunkt.ylesandegrupp_id)
                         .filter(model.Normipunkt.nptagasisided.any(
                             model.Nptagasiside.uus_testiylesanne_id.in_(ahelas)))
                         )
                    for ty_id, grupp_id in q.all():
                        ahelas1 = _leia_ahelas_eelmised(ty_id, grupp_id, level+1)
                        ahelas.extend(ahelas1)
                return ahelas

            ahelas = _leia_ahelas_eelmised(item.testiylesanne_id, item.ylesandegrupp_id, 0)
            for ind, r in enumerate(npts):
                ty_id = r.get('uus_testiylesanne_id')
                if ty_id in ahelas:
                    key = 'np.npts-%d.uus_testiylesanne_id' % (ind)
                    errors[key] = _("See ülesanne on juba ahelas eespool olemas")

                # # kui tagasiside on tühi kirev tekst, siis muudame tyhjaks ja ei kasuta seda
                # txt = r.get('tagasiside')
                # if txt and not utils.html2plain(txt).strip():
                #     r['tagasiside'] = ''
                    
        ctrl = BaseGridController(item.nptagasisided, model.Nptagasiside)
        ctrl.save(npts)

        if self.request.params.get('set_default_range'):
            # salvestame sama vahemiku sessioonis järgmiste tunnuste tagasisidede
            # juures vaikimisi kasutamiseks
            li = []
            for ns in item.nptagasisided:
                li.append((ns.tingimus_tehe, ns.tingimus_vaartus))
            default_params = {'ns_range': li,
                              'normityyp': item.normityyp,
                              'kysimus_kood': item.kysimus_kood,
                              }
            self._set_default_params(default_params, 'test_normipunkt_d2')
            model.Session.flush()
        
    def _update_tran(self, item, rcd):
        npts = rcd.get('npts') or []
        ctrl = BaseGridController(item.nptagasisided, model.Nptagasiside)
        ctrl.save(npts, lang=self.c.lang, update_only=True)
        model.Session.flush()           

        data = self.form.data['np']
        item.from_form(data, '', lang=self.c.lang)

        lang = self.c.lang or None
        item.count_tahemargid(lang)
        self.c.test.sum_tahemargid_lang(lang)
            
    def _after_create(self, id):
        """Mida teha peale õnnestunud lisamist - kuvame indeksi
        """        
        url = self.url_current('index', lang=self.c.lang, anchor='drnp%s' % id)
        return Response(json_body={'redirect': url})
        
    def _after_update(self, id):
        """Mida teha peale õnnestunud muutmist - kuvame ainult selle normipunkti
        """        
        if not self.has_errors():
            self.success()
        self.c.item = self.c.normipunkt = model.Normipunkt.get(id)
        if self.c.test.diagnoosiv:
            errors = {}
            rootprefix = 'np'            
            self._kontroll_diag_np(self.c.normipunkt, errors, rootprefix)
            if errors:
                self.c.errors = errors

        self.c.is_edit = False
        self._get_ting()
        return self.render_to_response(self._EDIT_TEMPLATE)
   
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)

        testiosa_id = int(self.request.matchdict.get('testiosa_id'))
        if testiosa_id:
            self.c.testiosa = model.Testiosa.get(testiosa_id)
            if self.c.testiosa.test_id != self.c.test.id:
                self.c.testiosa = None
        if not self.c.testiosa:
            for self.c.testiosa in self.c.test.testiosad:
                break
            
        self.c.lang = self.params_lang()
        if self.c.test:
            if self.c.lang and (self.c.lang == self.c.test.lang or self.c.lang not in self.c.test.keeled):
                self.c.lang = None
        else:
            self.c.lang = None
        
    def _perm_params(self):
        return {'obj':self.c.test}

