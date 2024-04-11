from cgi import FieldStorage
from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.ekk.korraldamine.valjastus import create_toimumisprotokollid
from eis.handlers.ekk.otsingud.labiviijateated import send_labiviija_maaramine
from eis.lib.testsaga import TestSaga
from eis.lib.examclient import ExamClient
log = logging.getLogger(__name__)

class KorradController(BaseResourceController):
    """Testimiskorrad
    """
    _permission = 'testimiskorrad'

    _MODEL = model.Testimiskord
    _EDIT_TEMPLATE = 'ekk/testid/korrad.testimiskord.mako'
    _INDEX_TEMPLATE = 'ekk/testid/korrad.testimiskord.mako'
    _ITEM_FORM = forms.ekk.testid.TestimiskordForm 
    _get_is_readonly = False

    def _index_d(self):
        res = BaseResourceController._index_d(self)
        return res

    def new(self, format='html'):
        mall_id = self.request.params.get('mall_id')
        if mall_id:
            return self._new_malliga(mall_id)
        copy_id = self.request.params.get('id')
        if copy_id:
            return self._new_copied(copy_id)
        else:
            return BaseResourceController.new(self)

    def _new_malliga(self, mall_id):
        # mallist võtta:
        # - testimiskorra ja toimumisaja seaded,
        # - piirkonnad,
        # - ymbrike nimetused ja mahud,
        # - hindamis- ja sisestuskogumid
        
        def cp_sisestuskogumid(testiosa, m_testiosa):
            # sisestuskogumid
            li = list(testiosa.sisestuskogumid)
            if not li:
                # sisestuskogumid kopeerime siis, kui neid veel pole
                for m_sk in m_testiosa.sisestuskogumid:
                    cp_sk = m_sk.copy()
                    testiosa.sisestuskogumid.append(cp_sk)
                    li.append(cp_sk)
            map_sk = {}
            for ind, m_sk in enumerate(m_testiosa.sisestuskogumid):
                if ind < len(li):
                    map_sk[m_sk.id] = li[ind]
                else:
                    break
            return map_sk

        def set_ty_hk(m_hk, cp_hk, testiosa, map_alatest):
            "Ülesannete määramine hindamiskogumisse jäiga struktuuriga testiosas"
            # vastav testiylesanne leitakse alatesti jrk nr ja ty jrk nr järgi
            komplektivalik_id = None
            for m_ty in m_hk.testiylesanded:
                m_alatest_id = m_ty.alatest_id
                if m_alatest_id:
                    # alatestidega 
                    alatest = map_alatest.get(m_alatest_id)
                    if not alatest:
                        # ei kopeeri, alatest puudub
                        continue
                    if not komplektivalik_id:
                        # esimese ylesande lisamine hk-sse
                        komplektivalik_id = alatest.komplektivalik_id
                        cp_hk.komplektivalik_id = komplektivalik_id
                    elif komplektivalik_id != alatest.komplektivalik_id:
                        # ei kopeeri, kui on teine kv
                        continue
                    ty_list = alatest.testiylesanded
                    cp_hk.kursus_kood = alatest.kursus_kood
                else:
                    # alatestideta
                    ty_list = testiosa.testiylesanded
                                        
                for ty in ty_list:
                    if ty.seq == m_ty.seq:
                        ty.hindamiskogum = cp_hk
                        ty.update_koefitsient()
                        break

        def map_alatestid(testiosa, m_testiosa):
            map_alatest = {}
            li = list(testiosa.alatestid)
            for ind, m_alatest in enumerate(m_testiosa.alatestid):
                if ind < len(li):
                    map_alatest[m_alatest.id] = li[ind]
                else:
                    break
            return map_alatest
        
        def map_komplektivalikud(testiosa, m_testiosa, lotv):
            # komplektivalikute ja komplektide vastavus
            map_kv = {}
            map_komplekt = {}
            li = list(testiosa.komplektivalikud)
            for ind, m_kv in enumerate(m_testiosa.komplektivalikud):
                if ind < len(li):
                    kv = li[ind]
                    map_kv[m_kv.id] = kv
                    if lotv:
                        li_k = list(kv.komplektid)
                        for ind_k, m_komplekt in enumerate(m_kv.komplektid):
                            if ind_k < len(li_k):
                                map_komplekt[m_komplekt.id] = li_k[ind_k]
                            else:
                                break
                else:
                    break
            return map_kv, map_komplekt
                    
        def set_vy_hk(m_hk, cp_hk, testiosa, map_alatest, map_kv, map_komplekt):
            "Ülesannete määramine hindamiskogumisse lõdva struktuuriga testiosas"
            # vastav vy leitakse komplektisisese jrk järgi

            komplektivalik_id = None
            for m_vy in m_hk.valitudylesanded:
                m_komplekt = m_vy.komplekt
                komplekt = map_komplekt.get(m_komplekt.id)
                if not komplekt:
                    # vastavat komplekti ei leidu
                    continue
                
                # leiame m_vy jrk nr oma komplektis
                for ind_y, r in enumerate(m_komplekt.valitudylesanded):
                    if r == m_vy:
                        break

                # leiame sama jrk nr-ga vy vastavas komplektis
                li = list(komplekt.valitudylesanded)
                if ind_y < len(li):
                    vy = li[ind_y]
                else:
                    # vastavat ylesannet ei leidu
                    continue

                # määrame hindamiskogumisse
                vy.hindamiskogum = cp_hk
                    
        def cp_hindamiskogumid(testiosa, m_testiosa, map_sk, map_kv, map_komplekt, lotv):
            # esmalt loome alatestide vastavuse
            map_alatest = map_alatestid(testiosa, m_testiosa)

            # kas testiosa hindamiskogumid on juba loodud?
            li_hk = [hk for hk in testiosa.hindamiskogumid if hk.staatus]
            on_hk = len(li_hk) > 0

            map_hk = {}
            for m_kv in m_testiosa.komplektivalikud:
                kv = map_kv.get(m_kv.id)
                if kv:
                    # ei kopeeri siis, kui vastav komplektivalik puudub
                    li = [hk for hk in kv.hindamiskogumid if hk.staatus]
                    m_li = [hk for hk in m_kv.hindamiskogumid if hk.staatus]
                    for ind_hk, m_hk in enumerate(m_li):
                        m_sk_id = m_hk.sisestuskogum_id
                        sk = map_sk.get(m_sk_id)
                        if sk or not m_sk_id:
                            cp_hk = None
                            # ei kopeeri siis, kui vastav sisestuskogum puudub
                            if m_hk.vaikimisi:
                                cp_hk = kv.give_default_hindamiskogum()
                            elif not on_hk:
                                # hindamiskogumid kopeerime siis, kui neid veel pole
                                cp_hk = m_hk.copy()
                                cp_hk.sisestuskogum = sk
                                cp_hk.komplektivalik = kv
                                testiosa.hindamiskogumid.append(cp_hk)
                                if lotv:
                                    set_vy_hk(m_hk, cp_hk, testiosa, map_alatest, map_kv, map_komplekt)
                                else:
                                    set_ty_hk(m_hk, cp_hk, testiosa, map_alatest)
                                model.Session.flush()
                                cp_hk.arvuta_pallid(lotv)
                            else:
                                # hindamiskogumid on olemas, loome ainult vastavuse
                                if len(li) > ind_hk:
                                    cp_hk = li[ind_hk]

                            if cp_hk:
                                # leiti vastav hindamiskogum
                                map_hk[m_hk.id] = cp_hk
            return map_hk

        def cp_testikohad(ta, m_ta):
            # TE/SE korral soorituskohtade ja läbiviijate kopeerimine
            m_labiviijad = []
            testikohad_seq = 0
            for m_testikoht in m_ta.testikohad:
                testikohad_seq = max(testikohad_seq, int(m_testikoht.tahis))

                # lisame testikoha
                uus_testikoht = ta.give_testikoht(m_testikoht.koht_id)
                uus_testikoht.tahis = m_testikoht.tahis
                uus_testikoht.set_tahised()

                # lisame testiruumid
                map_testiruum = {}
                for m_testiruum in m_testikoht.testiruumid:
                    uus_testiruum = uus_testikoht.give_testiruum(m_testiruum.ruum_id, m_testiruum.tahis)
                    uus_testiruum.toimumispaev_id = None
                    uus_testiruum.nimekiri_id = None
                    map_testiruum[m_testiruum.id] = uus_testiruum

                # lisame läbiviijad
                for m_lv in m_testikoht.labiviijad:
                    grupid_id = (const.GRUPP_INTERVJUU,
                                 const.GRUPP_HIND_INT,
                                 const.GRUPP_VAATLEJA,
                                 const.GRUPP_KOMISJON,
                                 const.GRUPP_KOMISJON_ESIMEES,
                                 const.GRUPP_T_ADMIN,
                                 const.GRUPP_KONSULTANT)
                    if m_lv.kasutajagrupp_id in grupid_id:
                        m_testiruum_id = m_lv.testiruum_id
                        if m_testiruum_id:
                            uus_testiruum = map_testiruum[m_testiruum_id]
                            lv = uus_testiruum.create_labiviija(m_lv.kasutajagrupp_id)
                        else:
                            lv = uus_testikoht.create_labiviija(m_lv.kasutajagrupp_id)

                        lv.liik = m_lv.liik
                        lv.lang = m_lv.lang
                        lv.planeeritud_toode_arv = m_lv.planeeritud_toode_arv
                        lv.testikoht = uus_testikoht
                        lv.testiruum = uus_testiruum
                        lv.aktiivne = m_lv.aktiivne
                        kasutaja = m_lv.kasutaja
                        if kasutaja:
                            lv.set_kasutaja(kasutaja)
                            model.Session.flush()
                            m_labiviijad.append(lv.id)
                            
            ta.testikohad_seq = testikohad_seq

            # läbiviijaks määramise teadete saatmine
            for lv_id in m_labiviijad:
                lv = model.Labiviija.get(lv_id)
                if lv.kasutaja_id:
                    k = lv.kasutaja
                    send_labiviija_maaramine(self, lv, k, ta)
        
        mall = model.Testimiskord.get(mall_id)
        # kopeerime kõik andmed peale kuupäevade ja testsessiooni
        cp_tkord = model.Testimiskord(
            test=self.c.test,
            tahis='--autouniq', # et flushi ajal oleks unikaalne
            reg_sooritaja=mall.reg_sooritaja,
            reg_xtee=mall.reg_xtee,
            reg_kool_ehis=mall.reg_kool_ehis,
            reg_kool_eis=mall.reg_kool_eis,
            reg_kool_valitud=mall.reg_kool_valitud,
            reg_ekk=mall.reg_ekk,
            cae_eeltest=mall.cae_eeltest,
            kordusosalemistasu=mall.kordusosalemistasu,
            osalemistasu=mall.osalemistasu,
            arvutada_hiljem=mall.arvutada_hiljem,
            tulemus_kinnitatud=False,
            tulemus_kontrollitud=False,
            osalemise_naitamine=mall.osalemise_naitamine,
            prot_vorm=mall.prot_vorm,
            on_helifailid=mall.on_helifailid,
            on_turvakotid=mall.on_turvakotid,
            analyys_eraldi=mall.analyys_eraldi,
            tulemus_koolile=mall.tulemus_koolile,
            tulemus_admin=mall.tulemus_admin,
            on_avalik_vaie=mall.on_avalik_vaie,
            kool_testikohaks=mall.kool_testikohaks,
            sisestus_isikukoodiga=mall.sisestus_isikukoodiga,
            skeeled=mall.skeeled,
            tutv_hindamisjuhend_url=mall.tutv_hindamisjuhend_url)

        cp_tkord.tahis = cp_tkord.gen_tahis_new()
        
        for r in mall.regkohad:
            cp_tkord.regkohad.append(r)
        for r in mall.piirkonnad:
            cp_tkord.piirkonnad.append(r)

        toimumisajad = list(mall.toimumisajad)
        len_m = len(toimumisajad)
        for ind_osa, testiosa in enumerate(self.c.test.testiosad):
            m_testiosa = None
            if ind_osa < len_m:               
                # otsime sama jrk nr-ga testiosa
                m_ta = toimumisajad[ind_osa]
                m_testiosa = m_ta.testiosa
                if testiosa.vastvorm_kood != m_testiosa.vastvorm_kood:
                    # testiosad ei vasta teineteisele
                    m_testiosa = None

            if m_testiosa:
                # leiti vastav testiosa
                m_lotv = m_testiosa.lotv
                m_on_alatestid = m_testiosa.on_alatestid
                    
                lotv = testiosa.lotv
                on_alatestid = testiosa.on_alatestid

                if lotv == m_lotv and on_alatestid == m_on_alatestid:
                    # sisestus- ja hindamiskogumeid ei kopeeri siis,
                    # kui yks on lõtv ja teine mitte
                    # või kui yks on alatestidega ja teine mitte
                    map_kv, map_komplekt = map_komplektivalikud(testiosa, m_testiosa, lotv)
                    map_sk = cp_sisestuskogumid(testiosa, m_testiosa)
                    map_hk = cp_hindamiskogumid(testiosa, m_testiosa, map_sk, map_kv, map_komplekt, lotv)
                else:
                    # hindamiskogumite vastavust ei ole võimalik luua
                    map_hk = {}
                    map_kv = {}
                    map_komplekt = {}
                    
                cp_ta = model.Toimumisaeg(
                    testiosa=testiosa,
                    testimiskord=cp_tkord,
                    vaatleja_maaraja=m_ta.vaatleja_maaraja,
                    hindaja1_maaraja=m_ta.hindaja1_maaraja,
                    hindaja2_maaraja=m_ta.hindaja2_maaraja,
                    intervjueerija_maaraja=m_ta.intervjueerija_maaraja,
                    admin_maaraja=m_ta.admin_maaraja,
                    on_arvuti_reg=m_ta.on_arvuti_reg,
                    kahekordne_sisestamine=m_ta.kahekordne_sisestamine,
                    esimees_maaraja=m_ta.esimees_maaraja,
                    komisjoniliige_maaraja=m_ta.komisjoniliige_maaraja,
                    reg_labiviijaks=m_ta.reg_labiviijaks,
                    ruumide_jaotus=m_ta.ruumide_jaotus,
                    ruum_voib_korduda=m_ta.ruum_voib_korduda,
                    labiviijate_jaotus=m_ta.labiviijate_jaotus,
                    kohad_avalikud=m_ta.kohad_avalikud,
                    kohad_kinnitatud=m_ta.kohad_kinnitatud,
                    hinnete_sisestus=m_ta.hinnete_sisestus,
                    oma_prk_hindamine=m_ta.oma_prk_hindamine,
                    oma_kooli_hindamine=m_ta.oma_kooli_hindamine,
                    sama_kooli_hinnatavaid=m_ta.sama_kooli_hinnatavaid,
                    protok_ryhma_suurus=m_ta.protok_ryhma_suurus,
                    samaaegseid_vastajaid=m_ta.samaaegseid_vastajaid,
                    tulemus_kinnitatud=False,
                    aja_jargi_alustatav=m_ta.aja_jargi_alustatav,
                    jatk_voimalik=m_ta.jatk_voimalik,
                    eelvaade_admin=m_ta.eelvaade_admin,
                    nimi_jrk=m_ta.nimi_jrk,
                    valjastuskoti_maht=m_ta.valjastuskoti_maht,
                    tagastuskoti_maht=m_ta.tagastuskoti_maht,
                    komplekt_valitav=m_ta.komplekt_valitav,
                    komplekt_valitav_y1=m_ta.komplekt_valitav_y1,
                    vaatleja_tasu=m_ta.vaatleja_tasu,
                    vaatleja_lisatasu=m_ta.vaatleja_lisatasu,
                    komisjoniliige_tasu=m_ta.komisjoniliige_tasu,
                    esimees_tasu=m_ta.esimees_tasu,
                    konsultant_tasu=m_ta.konsultant_tasu,
                    admin_tasu=m_ta.admin_tasu,
                    on_kogused=m_ta.on_kogused,
                    on_ymbrikud=m_ta.on_ymbrikud,
                    on_hindamisprotokollid=m_ta.on_hindamisprotokollid)
                
                cp_ta.set_tahised()
                model.Session.flush()
                
                for m_k in m_ta.komplektid:
                    cp_k = map_komplekt.get(m_k.id)
                    if cp_k:
                        cp_ta.komplektid.append(cp_k)
                for r in m_ta.valjastusymbrikuliigid:
                    cp_r = r.copy()
                    cp_r.toimumisaeg = cp_ta
                    cp_ta.valjastusymbrikuliigid.append(cp_r)
                for r in m_ta.tagastusymbrikuliigid:
                    cp_r = r.copy(toimumisaeg=cp_ta)
                    cp_ta.tagastusymbrikuliigid.append(cp_r)
                    for m_hk in r.hindamiskogumid:
                        m_hk_id = m_hk.id
                        cp_hk = map_hk.get(m_hk_id)
                        if cp_hk:
                            cp_r.hindamiskogumid.append(cp_hk)
                            
                if self.c.test.on_tseis:
                    # TE/SE korral lisada ka soorituskohad ja läbiviijad
                    cp_testikohad(cp_ta, m_ta)
            else:
                # kui sama jrk nr-ga testiosa pole, siis pole midagi kopeerida
                cp_ta = cp_tkord.give_toimumisaeg(testiosa)

        model.Session.commit()
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _new_copied(self, copy_id):
        # tehakse koopia olemasolevast testimiskorrast
        item = model.Testimiskord.get(copy_id)
        self.c.item = item.copy(True)
        model.Session.commit()
        self.success(_("Testimiskord on kopeeritud!"))
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _new(self, item):
        item.testsessioon_id = model.Testsessioon.get_default(self.c.test.testiliik_kood)
        t_keeled = self.c.test.keeled
        if len(t_keeled) == 1:
            item.skeeled = self.c.test.lang
            
    def _check_unique(self):
        # kontrollime, et tähis on unikaalne
        tk = (model.Session.query(model.Testimiskord)
              .filter(model.Testimiskord.test_id==self.c.test.id)
              .filter(model.Testimiskord.tahis==self.form.data['f_tahis'])
              .first())
        if tk:
            raise ValidationError(self, {'f_tahis': _("Sellise tähisega testimiskord on juba olemas")})

    def _create(self, **kw):
        self._check_unique()
        return BaseResourceController._create(self, **kw)

    def _update(self, item, lang=None):
        self._bind_parent(item)
        vana_tahis = item.tahis
        vana_prot_tulemusega = item.prot_tulemusega
        if item.id and item.tahis != self.form.data['f_tahis']:
            self._check_unique()
        item.from_form(self.form.data, self._PREFIX, lang=lang)
        if item.on_mall and not item.nimi:
            item.nimi = '%s %s' % (self.c.test.nimi, item.tahis)
        item.arvutada_hiljem = not self.form.data['arvutada_kohe']
        #if not item.prot_vorm:
        #    item.prot_vorm = const.PROT_VORM_DOKNR
        if item.tahis:
            item.tahis = item.tahis.upper()
        if vana_tahis and item.tahis != vana_tahis:
            for ta in item.toimumisajad:
                ta.set_tahised()
        #item.reg_kool_kuni = utils.night_datetime(item.reg_kool_kuni)
        #item.reg_sooritaja_kuni = utils.night_datetime(item.reg_sooritaja_kuni)
        self._update_lang(item)
        if not item.skeeled:
            raise ValidationError(self, {'lang_err': _("puudub")})
        item.give_toimumisajad()

        if not item.reg_kool_valitud:
            for r in list(item.regkohad):
                item.regkohad.remove(r)
                
        peidus_kuni = self.form.data['peidus_kuni']
        if peidus_kuni:
            kell = self.form.data['peidus_kell'] or (7, 0)
            item.sooritajad_peidus_kuni = datetime.combine(peidus_kuni, time(kell[0], kell[1]))
        else:
            item.sooritajad_peidus_kuni = None

        if vana_prot_tulemusega != item.prot_tulemusega:
            for ta in item.toimumisajad:
                if ta.on_hindamisprotokollid:
                    err = create_toimumisprotokollid(self, ta)
                    if err:
                        raise ValidationError(self, {'f_prot_vorm': err})
            
        model.Testileping.give_for(item)

    def _update_lang(self, item):
        """Keeled
        """
        param_keeled = self.form.data.get('lang')
        item.skeeled = ' '.join([r for r in param_keeled if r in self.c.test.keeled])
        
    def _after_commit(self, item):
        if not item.tahis:
            item.tahis = item.id

    def _edit_prk(self, id):
        self.c.item = model.Testimiskord.get(id)
        return self.render_to_response('ekk/testid/piirkonnad.mako')

    def _update_prk(self, id):
        item = model.Testimiskord.get(id)
        rcd_list = [rcd for rcd in item.piirkonnad]
        
        piirkonnad = (self.request.params.get('piirkonnad') or '').split(',')

        for piirkond_id in piirkonnad:
            if not piirkond_id:
                continue
            rcd = model.Piirkond.get(piirkond_id)
            if rcd:
                if rcd in rcd_list:
                    # juba olemas, andmebaasis ei muuda midagi
                    rcd_list.remove(rcd)
                else:
                    # lisame
                    item.piirkonnad.append(rcd)

        for rcd in rcd_list:
            # eemaldame
            item.piirkonnad.remove(rcd)

        model.Session.commit()
        self.success()
        return self._redirect('edit', id)

    def _edit_eksam(self, id):
        self.c.item = model.Testimiskord.get(id)
        self.c.eksamid_id = [r.kons_testimiskord_id for r in self.c.item.konskorrad]
        q = model.Session.query(model.Testimiskord.id, 
                                model.Test.id, 
                                model.Testimiskord.tahis, 
                                model.Test.nimi)
        q = q.filter(model.Testimiskord.testsessioon_id==self.c.item.testsessioon_id).\
            join(model.Testimiskord.test).\
            filter(model.Test.aine_kood==self.c.item.test.aine_kood).\
            filter(model.Test.testityyp==const.TESTITYYP_KONS)
        testitase = self.c.item.test.keeletase_kood
        if testitase:
            q = q.filter(model.Test.testitasemed.any(model.Testitase.keeletase_kood==testitase))

        self.c.items = q.all()
        return self.render_to_response('ekk/konsultatsioonid/kons.eksamid.mako')

    def _update_eksam(self, id):
        item = model.Testimiskord.get(id)
        id_list = [r.kons_testimiskord_id for r in item.konskorrad]

        posted_id_list = list(map(int, self.request.params.getall('kord_id')))
        for kord_id in posted_id_list:
            if kord_id in id_list:
                # juba olemas, andmebaasis ei muuda midagi
                id_list.remove(kord_id)
            else:
                # lisame
                rcd = model.Testikonsultatsioon(eksam_testimiskord_id=item.id,
                                                kons_testimiskord_id=kord_id)
                item.konskorrad.append(rcd)

        for kord_id in id_list:
            # eemaldame
            rcd = (model.Testikonsultatsioon.query
                   .filter_by(eksam_testimiskord_id=item.id)
                   .filter_by(kons_testimiskord_id=kord_id)
                   .first())
            if rcd:
                rcd.delete()

        model.Session.commit()
        self.success()
        return self._redirect('edit', id)

    def _edit_regkoht(self, id):
        "Valitud registreerimiskohtade lisamine"
        self.c.item = model.Testimiskord.get(id)
        self.c.sub = 'regkoht'
        return self.render_to_response('ekk/testid/kord.regkohad.mako')

    def _update_regkoht(self, id):
        "Valitud registreerimiskohtade lisamine"
        self.c.sub = 'regkoht'
        self.c.item = model.Testimiskord.get(id)
        self.c.item.reg_kool_valitud = True
        self.c.item.reg_kool_eis = False
        self._save_regkohad(self.c.item.regkohad)
        return self.render_to_response('ekk/testid/kord.regkohad.saved.mako')        

    def _save_regkohad(self, collection):
        "Regkohtade valiku ja vastuvõtvate kohtade salvestamine"
        err = None
        vanad_id = [r.id for r in collection]

        fkoolid = self.request.params.get('fkoolid')
        if isinstance(fkoolid, FieldStorage):
            # koolide loetelu anti CSV failina
            # failis on EHISe kool_id;kooli nimi
            uued_id, err = self._load_file(fkoolid.value)
        else:
            # koolid sisestati käsitsi
            uued_id = list(map(int, self.request.params.getall('koht_id')))
        if uued_id is not None:
            log.debug('vanad_id=%s' % vanad_id)
            log.debug('uued_id=%s' % uued_id)
            for koht_id in uued_id:
                if koht_id not in vanad_id:
                    # lisame
                    koht = model.Koht.get(koht_id)
                    if not koht:
                        log.error('koht %s puudub' % koht_id)
                    collection.append(koht)

            for koht_id in vanad_id:
                if koht_id not in uued_id:
                    # eemaldame
                    koht = model.Koht.get(koht_id)
                    collection.remove(koht)

            model.Session.commit()
        if err:
            self.error(err)
        
    def _load_file(self, filedata):
        "Failist koolide valiku lugemine"
        res = []
        li_err = []
        for ind, line in enumerate(filedata.splitlines()):
            err = None
            line = utils.guess_decode(line)
            li = [s.strip() for s in line.split(';')]
            try:
                kool_id, nimi = li
                kool_id = int(kool_id)
            except:
                err = 'Viga real %d. Failis peavad olema veerud: ehise ID; kooli nimi' % (ind+1)
                return None, err
            koht = model.Koht.query.filter(model.Koht.kool_id==kool_id).first()
            if not koht:
                err = 'Viga real %d: andmebaasis pole kooli %s' % (ind+1, kool_id)
            elif koht.nimi != nimi:
                err = 'Viga real %d: kooli ID %d ja nimi ei lange kokku (andmebaasis on kooli nimi "%s")' % (ind+1, kool_id, koht.nimi)
            if err:
                li_err.append(err)
            else:
                res.append(koht.id)
        return res, '\n'.join(li_err)

    def _delete(self, item):
        
        if self.c.user.has_permission('tkorddel', const.BT_DELETE):
            # kustutame kirjed eksamiserveritest
            q = (model.SessionR.query(sa.func.distinct(model.Sooritaja.klaster_id))
                 .filter_by(testimiskord_id=item.id)
                 .filter(model.Sooritaja.klaster_id!=None))
            for klaster_id, in q.all():
                host = model.Klaster.get_host(klaster_id)
                if host:
                    ExamClient(self, host).delete_test(item.test_id, item.id)

            # kustutame kirjed põhibaasist
            model.delete_testimiskord_sooritajad(item.id)
            model.delete_testimiskord_statistika(item.id)
            model.delete_testimiskord_testikohad(item.id)            
            model.Session.flush()

            item.delete()
            TestSaga(self).test_check_lukus(self.c.test)
            model.Session.commit()
            self.success(_("Andmed on kustutatud"))

    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        
        BaseResourceController.__before__(self)

    def _perm_params(self):
        if self.c.action == 'delete':
            # igat tyypi teste saab kustutada ainult tkorddel õigusega admin,
            # testi õigust ei arvestata
            return
        return {'obj':self.c.test}
