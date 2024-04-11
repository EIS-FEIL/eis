from cgi import FieldStorage
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
from eis.handlers.ekk.otsingud.labiviijateated import send_labiviija_maaramine
from .valjastus import create_kogused, create_hindamisprotokollid, kontrolli
log = logging.getLogger(__name__)

class SoorituskohadController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Testiruum
    _INDEX_TEMPLATE = '/ekk/korraldamine/soorituskohad.mako' 
    _LIST_TEMPLATE = '/ekk/korraldamine/soorituskohad_list.mako'
    _DEFAULT_SORT = 'koht.nimi'

    def _query(self):
        q = (model.Session.query(model.Testiruum, model.Koht, model.Ruum)
             .join(model.Testiruum.testikoht)
             .join(model.Testikoht.koht)
             .outerjoin(model.Testiruum.ruum)
             .filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id)
             .outerjoin(model.Koht.aadress))
        return q

    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q):
        c = self.c
        # leiame kasutajale lubatud piirkondade loetelu
        piirkonnad_id = c.user.get_kasutaja().get_piirkonnad_id('korraldamine', const.BT_SHOW,
                                                                testiliik=c.test.testiliik_kood)
        # kas pole õigust kõigi piirkondade korraldamiseks?
        if None not in piirkonnad_id:
            # piirkondlik korraldaja ei või kõiki kohti vaadata, 
            # talle kuvatakse ainult nende piirkondade koolid, mis talle on lubatud
            q = q.filter(model.Koht.piirkond_id.in_(piirkonnad_id))
            c.on_piirkondlik = True
            c.piirkond_filtered = piirkonnad_id
        else:
            c.on_piirkondlik = False
            c.piirkond_filtered = None
        c.sooritajad_piirkonniti = self._get_sooritajad_piirkonniti()       
        c.prepare_item = self._prepare_item

        qcnt = (model.SessionR.query(model.sa.func.count(model.Sooritus.id))
                .filter(model.Sooritus.toimumisaeg_id==c.toimumisaeg.id)
                .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
                .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA)
                .join(model.Sooritus.sooritaja)
                )
        if c.on_piirkondlik:
            qcnt = qcnt.filter(model.Sooritaja.piirkond_id.in_(piirkonnad_id))
        c.maaramata = qcnt.filter(model.Sooritus.testikoht_id==None).scalar()
        c.maaratud = qcnt.filter(model.Sooritus.testikoht_id!=None).scalar()
        
        if c.piirkond_id:
            f = []
            prk = model.Piirkond.get(c.piirkond_id)
            for prk_id in prk.get_alamad_id():
                f.append(model.Koht.piirkond_id==prk_id)
            q = q.filter(sa.or_(*f))
        if c.maakond_kood:
            tase, kood = c.maakond_kood.split('.')
            q = q.filter(model.Aadress.kood1==kood)
        if c.nimi:
            q = q.filter(model.Koht.koolinimed.any(\
                    model.Koolinimi.nimi.ilike(c.nimi)))

        if c.kohtipuudu:
            q = q.filter(model.Testiruum.kohti<model.Testiruum.sooritajate_arv)            
        if c.sooritajatearv:
            q = q.filter(model.Testiruum.sooritajate_arv<=c.sooritajatearv)
        if c.vabadearv:
            q = q.filter(model.Testiruum.kohti-model.Testiruum.sooritajate_arv>=c.vabadearv)

        if c.pole_r:
            q = q.filter(model.Testiruum.ruum_id==None)

        def pole_hk_hindajat(q, liik):
            # otsime kohad, kus pole mitte-valimi hindajat mõnele hindamiskogumile
            f_hindaja = sa.and_(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAJA_K,
                                model.Labiviija.kasutaja_id!=None,
                                model.Labiviija.hindamiskogum_id==model.Hindamiskogum.id,
                                model.Labiviija.valimis==False)
            if liik:
                f_hindaja = sa.and_(f_hindaja, model.Labiviija.liik==liik)

            q = q.filter(sa.exists().where(
                sa.and_(model.Hindamiskogum.testiosa_id==c.toimumisaeg.testiosa_id,
                        model.Hindamiskogum.staatus==const.B_STAATUS_KEHTIV,
                        model.Hindamiskogum.arvutihinnatav==False,
                        ~ model.Testikoht.labiviijad.any(f_hindaja)
                        )
                ))
            # arvestame ainult neid kohti, kus on mitte-valimi sooritajaid
            q = q.filter(sa.exists().where(
                sa.and_(model.Sooritus.testikoht_id==model.Testikoht.id,
                        model.Sooritus.sooritaja_id==model.Sooritaja.id,
                        model.Sooritaja.valimis==False)))
            return q

        on_suuline = c.testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP)
        
        # puuduvate rollide filter
        for (rc, grupp_id) in ((c.pole_v, const.GRUPP_VAATLEJA),
                               (c.pole_h1 and on_suuline, const.GRUPP_HINDAJA_S),
                               (c.pole_i, const.GRUPP_INTERVJUU),
                               (c.pole_a, const.GRUPP_T_ADMIN),
                               (c.pole_k, const.GRUPP_KONSULTANT)):
            if rc:
                q = q.filter(model.Testiruum.labiviijad.any(
                        sa.and_(model.Labiviija.kasutajagrupp_id==grupp_id,
                                model.Labiviija.kasutaja_id==None)
                        ))
        if c.pole_h2:
            # otsime kohad, kus puudub II hindaja
            if on_suuline:
                q = q.filter(model.Testiruum.labiviijad.any(
                        sa.and_(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAJA_S2,
                                model.Labiviija.kasutaja_id==None)
                        ))
            else:
                q = pole_hk_hindajat(q, const.HINDAJA2)

        if c.pole_h1 and not on_suuline:
            q = pole_hk_hindajat(q, None)
            
        if c.pole_a1:
            # otsime ruumid, kus pole ühtki testiadministraatorit määratud
            q = q.filter(~ model.Testiruum.labiviijad.any(
                    sa.and_(model.Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN,
                            model.Labiviija.kasutaja_id!=None)
                ))

        if c.csv:
            return self._index_csv(q)

        if self.request.params.get('op') == 'kontrolli':
            # Kui midagi on puudu, siis kuvatakse nt, test on salastatud, kogused on arvutamata vms.
            li_err = kontrolli(self, c.toimumisaeg)
            c.kontroll_err = '<br/>'.join(li_err)
            if not c.kontroll_err:
                c.kontroll_ok = _("Toimumisaeg on testi läbiviimiseks valmis")

        # kui paljude koolide õpilased sooritavad muus koolis
        # (mitmele koolile saab saata muu soorituskoha teate)
        q1 = (model.SessionR.query(sa.func.count(model.Sooritaja.kool_koht_id.distinct()))
              .join(model.Sooritaja.sooritused)
              .filter(model.Sooritus.toimumisaeg_id==c.toimumisaeg.id)
              .filter(model.Sooritus.staatus.in_((const.S_STAATUS_REGATUD,
                                                  const.S_STAATUS_ALUSTAMATA)))
              .join(model.Sooritus.testikoht)
              .filter(model.Testikoht.koht_id!=model.Sooritaja.kool_koht_id)
              )
        c.cnt_muusk = q1.scalar()
                
        self._get_protsessid()
        return q

    def _search_protsessid(self, q):
        # valimi eraldamise protsessi loomine vt valim.py
        tkord = self.c.toimumisaeg.testimiskord
        q = (q.filter(model.Arvutusprotsess.test_id==tkord.test_id)
             .filter(model.Arvutusprotsess.testimiskord_id==tkord.id)
             .filter(model.Arvutusprotsess.liik.in_((model.Arvutusprotsess.LIIK_VALIM,
                                                     model.Arvutusprotsess.LIIK_MUUSK)))
             .filter(sa.or_(model.Arvutusprotsess.lopp==None,
                            model.Arvutusprotsess.lopp > datetime.now() - timedelta(seconds=60)))
             )
        return q
   
    def _prepare_header(self):
        c = self.c
        vastvorm_kood = self.c.testiosa.vastvorm_kood
        on_kons = vastvorm_kood == const.VASTVORM_KONS
        on_suuline = vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP)
        header = [_("Tähis"),
                  _("Soorituskoht"),
                  _("Asukoht"),
                  _("Testiruum"),
                  _("Ruum"),
                  _("Kohti"),
                  on_kons and _("Sooritajaid piirkonnas") or 'Sooritajaid',
                  _("Läbiviija määramata"),
                  not on_suuline and c.pole_h1 and _("Hindajata hindamiskogumid") or None,
                  _("Toimumise aeg"),
                  ]
        header = [r for r in header if r]
        return header
    
    def _prepare_item(self, rcd, n):
        testiruum, koht, ruum = rcd
        testikoht = testiruum.testikoht
        on_kons = self.c.testiosa.vastvorm_kood == const.VASTVORM_KONS
        on_suuline = self.c.testiosa.vastvorm_kood in (const.VASTVORM_SP, const.VASTVORM_SH)
        sooritajatearvud = testiruum.get_sooritajatearvud()

        item = ['%s-%s' % (testikoht.tahised, testiruum.tahis),
                koht.nimi,
                koht.tais_aadress,
                testiruum.tahis or _("Määramata"),
                ruum and ruum.tahis,
                ]
        if on_kons:
            item.append(testiruum.kohti)
            if koht.piirkond:
                soovijaid = 0
                for ylem_id in koht.piirkond.get_ylemad_id():
                    soovijaid += self.c.sooritajad_piirkonniti.get(ylem_id) or 0
                item.append(soovijaid)
        else:
            if testiruum.kohti:
                buf = '%s / vabu %s' % (testiruum.kohti, testiruum.vabukohti)
            else:
                buf = ''
            item.append(buf)


            total = sooritajatearvud.get('total')
            if total != testiruum.sooritajate_arv:
                testiruum.set_sooritajate_arv()
                model.Session.commit()
            buf = '%s' % (total)
            for lang in const.LANG_ORDER:
                if sooritajatearvud.get(lang):
                    buf += ' / %s %s' % (lang, sooritajatearvud[lang])
            item.append(buf)
            
        maaramata_cnt = (model.Labiviija.query
                         .filter(model.Labiviija.testiruum_id==testiruum.id)
                         .filter(model.Labiviija.kasutaja_id==None)
                         .count())
        maaramata = str(maaramata_cnt or '')
        item.append(maaramata)

        if self.c.pole_h1 and not on_suuline:
            q = (model.SessionR.query(model.Hindamiskogum.tahis)
                 .filter(model.Hindamiskogum.testiosa_id==self.c.toimumisaeg.testiosa_id)
                 .filter(model.Hindamiskogum.staatus==const.B_STAATUS_KEHTIV)
                 .filter(model.Hindamiskogum.arvutihinnatav==False)
                 .filter(~ sa.exists().where(
                     sa.and_(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAJA_K,
                             model.Labiviija.kasutaja_id!=None,
                             model.Labiviija.testikoht_id==testikoht.id,
                             model.Labiviija.hindamiskogum_id==model.Hindamiskogum.id))
                        )
                 .order_by(model.Hindamiskogum.tahis)
                )
            maaramata = ', '.join([tahis for tahis, in q.all()])
            item.append(maaramata or '')

        item.append(self.h.str_from_datetime(testiruum.algus, hour0=False))
        return item

    def _get_sooritajad_piirkonniti(self):
        q = (model.SessionR.query(sa.func.count(model.Sooritaja.id),
                                 model.Sooritaja.piirkond_id)
             .filter(model.Sooritaja.soovib_konsultatsiooni==True)
             .filter(model.Sooritaja.staatus > const.S_STAATUS_REGAMATA)
             .join((model.Testikonsultatsioon,
                    sa.and_(model.Testikonsultatsioon.eksam_testimiskord_id==model.Sooritaja.testimiskord_id,
                            model.Testikonsultatsioon.kons_testimiskord_id==self.c.toimumisaeg.testimiskord_id)))
             .group_by(model.Sooritaja.piirkond_id)
             )

        data = {}
        total = {}
        self.c.cnt_total = 0
        for cnt, piirkond_id in q.all():
            data[piirkond_id] = cnt
            self.c.cnt_total += cnt
        return data

    def new(self):
        "Soorituskohtade valiku dialoogiakna kuvamine"
        # leiame kasutajale lubatud piirkondade loetelu
        c = self.c
        testiliik = c.test.testiliik_kood
        kasutaja = c.user.get_kasutaja()
        piirkonnad_id = kasutaja.get_piirkonnad_id('korraldamine', const.BT_UPDATE, testiliik=testiliik)
        if None not in piirkonnad_id:
            c.piirkond_filtered = piirkonnad_id
        else:
            c.piirkond_filtered = None
        return self.render_to_response('/ekk/korraldamine/kohavalik.mako')

    def create(self):
        """Soorituskohtade lisamine toimumisajale
        """
        sub = self._get_sub()
        if sub:
            return eval('self._create_%s' % sub)()

        err = None
        fkoolid = self.request.params.get('fkoolid')
        if isinstance(fkoolid, FieldStorage):
            # koolide loetelu anti CSV failina
            # failis on EHISe kool_id;kooli nimi
            kohad_id, err = self._load_file(fkoolid.value)
        else:
            # koolid sisestati käsitsi
            kohad_id = list(map(int, self.request.params.getall('koht_id')))
        if err:
            self.error(err)
        elif not kohad_id:
            self.error(_("Soorituskohti ei valitud"))
        else:
            dt = datetime.now()
            cnt = 0
            for koht_id in kohad_id:
                tkoht = self.c.toimumisaeg.give_testikoht(koht_id)
                if not tkoht.id or not tkoht.created or tkoht.created > dt:
                    cnt += 1
                tkoht.gen_tahis()
                tkoht.give_testiruum().give_labiviijad()
            model.Session.commit()
            msg = _("Lisatud {n2} uut soorituskohta").format(n2=cnt)
            self.success(msg)

        return HTTPFound(location=self.url('korraldamine_soorituskohad', toimumisaeg_id=self.c.toimumisaeg.id))
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
    
    def _create_luba(self):
        """Lubade salvestamine (kas läbiviijaks regamine on lubatud, 
        kas soorituskohas ruumide määramine on lubatud)
        """
        params = self.request.params
        toimumisaeg = self.c.toimumisaeg
        toimumisaeg.reg_labiviijaks = params.get('reg_labiviijaks') is not None
        toimumisaeg.ruumide_jaotus = params.get('ruumide_jaotus') is not None
        toimumisaeg.labiviijate_jaotus = params.get('labiviijate_jaotus') is not None
        toimumisaeg.kohad_avalikud = params.get('kohad_avalikud') is not None
        kohad_kinnitatud = self.request.params.get('kohad_kinnitatud') is not None
        if kohad_kinnitatud != toimumisaeg.kohad_kinnitatud:
            toimumisaeg.kohad_kinnitatud = kohad_kinnitatud
            if not kohad_kinnitatud:
                # kinnitus võeti maha
                # uuendame testiruumide kohtade arvud, 
                # kuna ruumide kohtade muutmisel muudetakse
                # ainult kinnitamata kohtadega toimumisaegade testiruumide andmeid
                for testikoht in toimumisaeg.testikohad:
                    testikoht.koht.update_testiruumid(testikoht.id)
        model.Session.commit()
        self.success()
        return self._redirect('index')

    def _create_kogused(self):
        "Kutseeksami toimumisaja kinnitamine ehk arvuta kogused ja loo hindamiskirjed"
        c = self.c
        err = create_kogused(self, c.toimumisaeg, True)
        if not err:
            model.Session.flush()
            err = create_hindamisprotokollid(self, c.toimumisaeg)
        if err:
            self.error(err)
            return self._redirect('index')
        else:
            model.Session.commit()
            return self._redirect('index', op='kontrolli')

    def _index_kopeeri(self):
        """Teiste toimumisaegade valimine kopeerimiseks
        """
        # milliseid läbiviijaid saab antud toimumisajal määrata?
        self.c.lvrollid = self.c.toimumisaeg.get_labiviijagrupid_opt(False)
        lvr_id = [r[0] for r in self.c.lvrollid]
        self.c.ta_lvr_id = {}
        
        # leiame sama testimiskorra kõik toimumisajad
        self.c.tadata = []
        for ta in self.c.toimumisaeg.testimiskord.toimumisajad:
            osa = ta.testiosa
            self.c.tadata.append((osa, ta))

            # leiame antud toimumisaja ja praeguse toimumisaja läbiviijarollide ühisosa
            self.c.ta_lvr_id[ta.id] = [r[0] for r in ta.get_labiviijagrupid_opt() \
                                       if r[0] in lvr_id]
        
        return self.render_to_response('/ekk/korraldamine/kopeeri.toimumisajad.mako')

    def _create_kopeeri(self):
        """Teise toimumisaja andmete kopeerimine.
        Süsteem kopeerib valitud kopeeritava toimumisaja juurest 
        testisoorituskohad, -ruumid ja testiosasoorituste seosed testisoorituskohtadega 
        ja –ruumidega.
        Seejuures peab süsteem vältima topelt kirjete tekkimist 
        ja varem sisestatud andmete muutmist.
        """
        # leiame toimumisaja, mille andmed kopeerida
        ta_id = self.request.params.get('ta_id')
        ta = model.Toimumisaeg.get(ta_id)
        assert ta.testimiskord_id == self.c.toimumisaeg.testimiskord_id, _("Vale testimiskord")
        assert ta != self.c.toimumisaeg, _("Vale toimumisaeg")

        # kas kirjutada soorituskohtadele määramine üle
        koht_yle = self.request.params.get('koht_yle')
        # millised läbiviijarollid kopeerida
        lvrollid_id = list(map(int, self.request.params.getall('lvr_id')))
        
        if koht_yle:
            # kaotame olemasolevad suunamised
            for uus_sooritus in self.c.toimumisaeg.sooritused:
                if uus_sooritus.testikoht:
                    uus_sooritus.testikoht_id = None
                    uus_sooritus.testiruum_id = None
                    uus_sooritus.testiprotokoll_id = None
                uus_sooritus.reg_toimumispaev_id = None
                
            # kaotame olemasolevad protokolliryhmad, testiruumid ja testikohad
            for uus_testikoht in self.c.toimumisaeg.testikohad:
                uus_testikoht.delete()
            self.c.toimumisaeg.testikohad_seq = ta.testikohad_seq
            model.Session.flush()
        else:
            # peame meeles, millised tähised on millise koha jaoks seni kasutusel
            vanad_kohatahised = dict()
            for testikoht in self.c.toimumisaeg.testikohad:
                vanad_kohatahised[testikoht.tahis] = testikoht.koht_id

        # eri toimumisaegade toimumispäevade vastavus 
        map_tpv = {}
        for src, dst in zip(list(ta.toimumispaevad),
                            list(self.c.toimumisaeg.toimumispaevad)):
            map_tpv[src.id] = dst.id
                
        cnt_maaratud = 0 # mitu sooritajat suunatud
        testikohad_seq = self.c.toimumisaeg.testikohad_seq or 0
        m_labiviijad = []
        # tasemeeksam - kas kopeerida kirjaliku osa komisjoniesimees suulise osa hindajaks
        te_copy_lv = self.c.test.testiliik_kood == const.TESTILIIK_TASE \
          and self.c.testiosa.vastvorm_kood in (const.VASTVORM_SE, const.VASTVORM_SH, const.VASTVORM_SP) \
          and ta.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP)

        # kopeerime, käies kõik teise toimumisaja ruumid läbi
        for testikoht in ta.testikohad:
            koht_id = testikoht.koht_id
            if not koht_yle:
                vana_koht_id = vanad_kohatahised.get(testikoht.tahis)
                if vana_koht_id and vana_koht_id != koht_id:
                    self.error(_("Testikoha tähis {s} on juba kasutusel").format(s=testikoht.tahis))
                    return self._redirect('index')

            testikohad_seq = max(testikohad_seq, int(testikoht.tahis))
                    
            # leiame ja vajadusel loome testikoha
            uus_testikoht = self.c.toimumisaeg.give_testikoht(koht_id)
            uus_testikoht.tahis = testikoht.tahis
            uus_testikoht.set_tahised()

            li_lv, cnt = self._copy_testikoht(uus_testikoht, testikoht, self.c.toimumisaeg, ta, lvrollid_id, map_tpv, te_copy_lv, koht_yle)
            m_labiviijad.extend(li_lv)
            cnt_maaratud += cnt
            
        if not koht_yle:
            self.c.toimumisaeg.testikohad_seq = testikohad_seq

        # läbiviija määramise teadete saatmine
        for lv, k in m_labiviijad:
            send_labiviija_maaramine(self, lv, k, self.c.toimumisaeg)
            
        model.Session.commit()
        self.success(_("Toimumisaja andmed on kopeeritud"))
        return self._redirect('index')

    def _copy_testikoht(self, uus_testikoht, testikoht, uus_toimumisaeg, ta, lvrollid_id, map_tpv, te_copy_lv, koht_yle):
        "Testikoha kopeerimine"

        m_labiviijad = []
        cnt_maaratud = 0
        
        # kohaga seotud läbiviijate kopeerimine
        if lvrollid_id:
            li = self._copy_k_labiviijad(uus_toimumisaeg, uus_testikoht, testikoht, lvrollid_id)
            m_labiviijad.extend(li)

        # praegune testiosa
        testiosa_id = self.c.testiosa.id

        # testiruumide kopeerimine
        for testiruum in testikoht.testiruumid:
            # leiame toimumispäeva vaste teisel toimumisajal
            uus_tpv_id = map_tpv.get(testiruum.toimumispaev_id)
                    
            # leiame ja vajadusel loome testiruumi
            uus_testiruum = uus_testikoht.give_testiruum(testiruum.ruum_id, testiruum.tahis, uus_tpv_id)
                        
            # loome läbiviijate kirjed
            uus_testiruum.give_labiviijad()
            # ruumiga seotud läbiviijate kopeerimine
            if lvrollid_id:
                li = self._copy_r_labiviijad(uus_toimumisaeg, uus_testiruum, testiruum, lvrollid_id)
                m_labiviijad.extend(li)

            # tasemeeksami kirjaliku osa esimees suulise osa hindajaks
            if te_copy_lv:
                li = self._copy_r_labiviijad_te(uus_testiruum, testiruum)
                m_labiviijad.extend(li)
                
            # lisame sooritajad sinna ruumi
            for sooritus in testiruum.sooritused:
                sooritaja = sooritus.sooritaja
                if sooritaja.staatus < const.S_STAATUS_REGATUD:
                    # pooleli registreeringut ei kopeeri
                    continue                    
                # leiame sama sooritaja soorituse kirje praegusel toimumisajal
                uus_sooritus = sooritaja.give_sooritus(testiosa_id)
                if not uus_sooritus.testiruum_id and not uus_sooritus.testiruum:
                    # kui sooritus on veel on ruumi määramata, siis määrame ta samasse ruumi, 
                    # kus ta oli kopeeritaval toimumisajal
                    if uus_testiruum.kohti is None or \
                      uus_testiruum.kohti > (uus_testiruum.sooritajate_arv or 0):
                        # kui on kohti, siis suuname
                        uus_tpr = None
                        if koht_yle:
                            # peab sama testiprotokolli tähis jääma
                            tpr = sooritus.testiprotokoll
                            if tpr:
                                tpakett = tpr.testipakett
                                if tpakett:
                                    # p-test, keelepõhised paketid
                                    paketiruum = tpakett.testiruum and uus_testiruum or None
                                    uus_tpakett = uus_testikoht.give_testipakett(tpakett.lang, paketiruum)
                                else:
                                    uus_tpakett = None
                                uus_tpr = uus_testikoht.give_testiprotokoll(uus_testiruum, uus_tpakett, tpr.tahis)
                                
                        if not uus_sooritus.suuna(uus_testikoht, uus_testiruum, uus_tpr):
                            self.error(_("Suunamisi ei saa kopeerida (kontrollige protokollirühma suurust)"))
                            model.Session.rollback()
                            raise self._redirect('index')
                        cnt_maaratud += 1
            model.Session.flush()
            uus_testiruum.set_sooritajate_arv()

        if koht_yle:
            # säilitame soorituse tähised neile, kes sooritavad samas testikohas kui kopeeritaval toimumisajal
            VanaS = sa.orm.aliased(model.Sooritus)
            # leiame vana testikoha tähised neile, kes on samas testikohas
            q = (model.Session.query(model.Sooritus.id, VanaS.tahis)
                 .filter(model.Sooritus.testikoht_id==uus_testikoht.id)
                 .join((VanaS, sa.and_(VanaS.sooritaja_id==model.Sooritus.sooritaja_id,
                                       VanaS.testikoht_id==testikoht.id,
                                       VanaS.tahis!=None)))
                 )
            map_tahis = {s_id: tahis for (s_id, tahis) in q.all()}
            tahised = list(map_tahis.values())
            if map_tahis:
                # vanal toimumisajal olid tähised antud
                # eemaldame uue testikoha need tähised, mis olid ka vanas olemas
                for uus_sooritus in uus_testikoht.sooritused:
                    tahis = map_tahis.get(uus_sooritus.id)
                    if tahis and tahis == uus_sooritus.tahis:
                        # on juba sama tähis
                        map_tahis.pop(uus_sooritus.id)
                    elif uus_sooritus.tahis in tahised:
                        # tähis on vaja vabastada, et seda kasutada kellegi teise jaoks
                        uus_sooritus.tahis = uus_sooritus.tahised = None
                        
                # kopeerime tähised vanalt toimumisajalt
                for s_id, tahis in map_tahis.items():
                    uus_sooritus = model.Sooritus.get(s_id)
                    uus_sooritus.tahis = tahis
                    uus_sooritus.tahised = '%s-%s' % (uus_testikoht.tahis, tahis)
            model.Session.flush()
            # määrame testikoha tähiste järjekorra jooksva seisu
            q = (model.Session.query(sa.func.max(model.Sooritus.tahis))
                 .filter(model.Sooritus.testikoht_id==uus_testikoht.id))
            max_tahis = q.scalar()
            if max_tahis:
                uus_testikoht.sooritused_seq = int(max_tahis)
        
        return m_labiviijad, cnt_maaratud
    
    def _copy_k_labiviijad(self, uus_toimumisaeg, uus_testikoht, testikoht, lvrollid_id):
        "Koha läbiviijate kopeerimine (komisjoni esimees või liige)"
        added = []
        q = (model.Session.query(model.Labiviija)
             .filter(model.Labiviija.kasutajagrupp_id.in_(lvrollid_id))
             .filter(model.Labiviija.testiruum_id==None)
             .filter(model.Labiviija.testikoht_id==testikoht.id)
             .filter(model.Labiviija.kasutaja_id!=None))                 
        for lv in q.all():
            grupp_id = lv.kasutajagrupp_id
            k_id = lv.kasutaja_id
            # rolli päring
            q1 = (model.Session.query(model.Labiviija)
                  .filter(model.Labiviija.testiruum_id==None)
                  .filter(model.Labiviija.testikoht_id==uus_testikoht.id)
                  .filter(model.Labiviija.kasutajagrupp_id==grupp_id))
            # kas antud kasutaja on selles rollis juba?
            q2 = q1.filter(model.Labiviija.kasutaja_id==k_id)
            uus_lv = q2.first()
            if not uus_lv:
                # lisada kasutaja rolli
                k = model.Kasutaja.get(k_id)
                # kas leidub läbiviija kirje ilma kasutajata?
                uus_lv = q1.filter(model.Labiviija.kasutaja_id==None).first()
                if not uus_lv:
                    # loome uue läbiviija kirje
                    uus_lv = uus_testikoht.create_labiviija(grupp_id)
                uus_lv.set_kasutaja(k, uus_toimumisaeg)
                added.append((uus_lv, k))
                log.debug(f'kopeeritud k lv {grupp_id} {k.nimi}')
                model.Session.flush()
        return added

    def _copy_r_labiviijad(self, uus_toimumisaeg, uus_testiruum, testiruum, lvrollid_id):
        "Ruumi läbiviijate kopeerimine (testi admin, vaatleja, intervjueerija, suuline hindaja)"
        added = []
        q = (model.Session.query(model.Labiviija)
             .filter(model.Labiviija.kasutajagrupp_id.in_(lvrollid_id))
             .filter(model.Labiviija.testiruum_id==testiruum.id)
             .filter(model.Labiviija.kasutaja_id!=None))
        for lv in q.all():
            grupp_id = lv.kasutajagrupp_id
            k_id = lv.kasutaja_id
            # rolli päring
            q1 = (model.Session.query(model.Labiviija)
                  .filter(model.Labiviija.testiruum_id==uus_testiruum.id)
                  .filter(model.Labiviija.kasutajagrupp_id==grupp_id))
            # kas antud kasutaja on selles rollis juba?
            q2 = q1.filter(model.Labiviija.kasutaja_id==k_id)
            uus_lv = q2.first()
            if not uus_lv:
                # lisada kasutaja rolli
                k = model.Kasutaja.get(k_id)
                # kas leidub läbiviija kirje ilma kasutajata?
                uus_lv = q1.filter(model.Labiviija.kasutaja_id==None).first()
                if not uus_lv:
                    # loome uue läbiviija kirje
                    uus_lv = uus_testiruum.create_labiviija(grupp_id)
                uus_lv.set_kasutaja(k, uus_toimumisaeg)
                added.append((uus_lv, k))
                log.debug(f'kopeeritud r lv {grupp_id} {k.nimi}')                        
                model.Session.flush()
        return added
    
    def _copy_r_labiviijad_te(self, uus_testiruum, testiruum):
        "Tasemeeksam - kopeerida kirjaliku osa komisjoniesimees suulise osa hindajaks"
        added = []
        for lv in testiruum.labiviijad:
            if lv.kasutajagrupp_id == const.GRUPP_KOMISJON_ESIMEES and lv.kasutaja_id:
                # leitud komisjoni esimees
                for cp_lv in uus_testiruum.labiviijad:
                    if not cp_lv.kasutaja_id and cp_lv.staatus == const.L_STAATUS_MAARAMATA and \
                      cp_lv.kasutajagrupp_id in (const.GRUPP_HINDAJA_S, const.GRUPP_INTERVJUU):
                      # leitud määramata hindaja
                        lv_k = lv.kasutaja
                        cp_lv.set_kasutaja(lv_k)
                        added.append((cp_lv, lv_k))
                        break
        return added
    
    def _create_genereeri(self):
        """Lähtuvalt testisooritajate õppeasutusest luuakse automaatselt soorituskohad. 
        Sisuliselt lähtutakse sellest, et iga õppiv testisooritaja sooritab 
        teste oma õppeasutuses.

        Iga testisoorituse kohta, millega ei ole seotud testisoorituskohta 
        ja mille olek ei ole "tühistatud":
        - Kui sooritaja õppeasutust ei ole, siis see testisooritaja ei ole 
        praegu õppur ja selle testisooritajaga siin rohkem midagi ei tehta.
        - Kui leitud õppeasutusele vastav soorituskoht ei ole testisoorituskohtade 
        hulgas, siis süsteem loob uue  testisoorituskoha kirje.
        - Süsteem seob testisoorituse testisoorituskohaga
        """
        genereeri_oppurite_kohad(self, self.c.toimumisaeg)
        return self._redirect('index')

    def _create_jaota(self):
        """Iga testisoorituskohaga sidumata ja registreeritud olekus oleva 
        testiosasoorituse kohta süsteem loob seose 
        registreerimise käigus määratud piirkonna eelistuse alusel 
        (leiab testisooritaja poolt eelistatud piirkonda kuuluva testisoorituskoha, 
        kus on vabu kohti; 
        mitme sobiva hulgast valitakse eelistatult koht, 
        kus on juba olema sama soorituskeelega testisooritajaid, 
        mitme samaväärse testisoorituskoha vahel valitakse juhuslikult).
        """
        jaota_sooritajad(self)
        return self._redirect('index')

    def _create_muusk(self):
        """Muu soorituskoha teadete saatmine koolidele, mille õpilased sooritavad mujal
        """
        start_muusk(self, self.c.toimumisaeg)
        return self._redirect('index')
    
    def _create_suunamine(self):
        """Yhe või mitme soorituskoha kõigi sooritajate suunamine uude soorituskohta
        """
        testiruum = None
        for key in self.request.params:
            # submit-nupu "Vali" nimi oli "valik_id_ID", siit saame uue testikoha ID
            prefix = 'valik_id_'
            if key.startswith(prefix):
                testiruum_id = key[len(prefix):]
                testiruum = model.Testiruum.get(testiruum_id)
                break
        
        if not testiruum:
            self.error(_("Vali testiruum, kuhu suunata"))
            return self._redirect('index')

        testikoht = testiruum.testikoht
        assert testikoht.toimumisaeg_id == self.c.toimumisaeg.id, _("Vale toimumisaeg")
        suunatavad_tr_id = self.request.params.getall('tr_id')
        q_arv = model.SessionR.query(sa.func.sum(model.Testiruum.sooritajate_arv)).\
            filter(model.Testiruum.id.in_(suunatavad_tr_id))
        lisatakse = q_arv.scalar()

        vabukohti = testiruum.vabukohti
        if vabukohti is not None and vabukohti < lisatakse:
            self.error(_("Valitud ruumis on vabu kohti ainult {n}").format(n=vabukohti))
            return self._redirect('index')
        
        # koolisisesel ümbersuunamisel võib olla valitud ka protokollirühm
        tpr_id = self.request.params.get('tpr_id')
        tpr = tpr_id and model.Testiprotokoll.get(tpr_id)

        testiruumid = set([testiruum])

        cnt = 0
        for suunatav_tr_id in suunatavad_tr_id:
            suunatav_testiruum = model.Testiruum.get(suunatav_tr_id)
            if suunatav_testiruum:
                testiruumid.add(suunatav_testiruum)
                q_tos = model.Session.query(model.Sooritus.id).\
                    filter_by(testiruum_id=suunatav_testiruum.id)
                sooritused_id = [r[0] for r in q_tos.all()]
                for sooritus_id in sooritused_id:
                    rcd = model.Sooritus.get(sooritus_id)
                    if rcd.staatus > const.S_STAATUS_REGAMATA:
                        cnt += 1
                        if not rcd.suuna(testikoht, testiruum, tpr=tpr):
                            self.error(_("Soovitud protokollirühma ei saa suunata (kontrollige protokollirühma suurust)"))
                            model.Session.rollback()
                            return self._redirect('index')                            
                    else:
                        # tyhistatud, ei vii yle
                        rcd.testiruum = None
                        rcd.testikoht = None
        if cnt:
            for testiruum in testiruumid:
                testiruum.set_sooritajate_arv()
            model.Session.commit()
            if cnt == 1:
                self.success(_("Suunatud 1 sooritaja"))
            else:
                self.success(_("Suunatud {n} sooritajat").format(n=cnt))

        return self._redirect('index')

    def _delete(self, item):
        on_sooritusi = False
        for sooritus in item.sooritused:
            if sooritus.staatus == const.S_STAATUS_VABASTATUD:
                sooritus.testiruum_id = None
                sooritus.testikoht_id = None
            else:
                on_sooritusi = True
                break
        if on_sooritusi:
            self.error(_("Sooritusruumis on sooritajaid ja seda ei saa eemaldada"))
        else:
            testikoht = item.testikoht
            ainus_ruum = len(testikoht.testiruumid) == 1
            if ainus_ruum:
                # kogu testikohtas ei või olla läbiviijaid
                labiviijad = list(testikoht.labiviijad)
            else:
                # selles testiruumis ei või olla läbiviijaid
                labiviijad = list(item.labiviijad)
                    
            for rcd in labiviijad:
                if rcd.kasutaja_id:
                    if rcd.testiruum_id:
                        self.error(_("Sooritusruumi on määratud läbiviijaid ja seda ei saa eemaldada"))
                    else:
                        self.error(_("Soorituskohta on määratud läbiviijaid ja seda ei saa eemaldada"))                        
                    model.Session.rollback()
                    return
                rcd.delete()
            item.delete()
            if ainus_ruum:
                # selles kohas rohkem testiruume ei olegi
                testikoht.delete()
            else:
                algused = [tr.algus for tr in testikoht.testiruumid if tr != item and tr.algus]
                testikoht.alates = algused and min(algused) or None
            self.success(_("Andmed on kustutatud"))
            model.Session.commit()

    def _after_delete(self, parent_id=None):
        """Kuhu peale läbiviija kirje kustutamist minna
        """
        return self._redirect('index')

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test
        
    def _perm_params(self):
        return {'obj':self.c.test}

        
def genereeri_oppurite_kohad(handler, toimumisaeg):
    """Soorituskohata sooritajate suunamine oma kooli. 
    Kui kool ei ole soorituskoht, siis lisatakse soorituskoht ja suunatakse ikkagi.
    """
    toimumisaeg_id = toimumisaeg.id
    
    def childfunc(protsess):
        q = (model.Session.query(model.Sooritus.id)
             .filter(model.Sooritus.toimumisaeg_id==toimumisaeg_id)
             .filter(model.Sooritus.testikoht_id==None)
             .filter(model.Sooritus.staatus==const.S_STAATUS_REGATUD)
             .join(model.Sooritus.sooritaja)
             .order_by(model.Sooritaja.perenimi, model.Sooritaja.eesnimi)
             )

        cnt_koolita = 0
        cnt = 0 

        testiruumid = set()
        sooritused_id = [s_id for s_id, in q.all()]
        total = len(sooritused_id)
        toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        testiosa = toimumisaeg.testiosa

        for ind, s_id in enumerate(sooritused_id):
            rcd = model.Sooritus.get(s_id)
            sooritaja = rcd.sooritaja
            kool_koht = sooritaja.kool_koht
            if not kool_koht:
                cnt_koolita += 1
                continue
            testikoht = model.Testikoht.query.\
                filter_by(koht_id=kool_koht.id).\
                filter_by(toimumisaeg_id=toimumisaeg.id).\
                first()
            if not testikoht:
                testikoht = model.Testikoht(koht_id=kool_koht.id,
                                            testiosa=testiosa,
                                            toimumisaeg=toimumisaeg,
                                            staatus=const.B_STAATUS_KEHTIV,
                                            sooritused_seq=0)
                testikoht.gen_tahis()
                # luuakse testiruumid ja läbiviijad
                tr = testikoht.give_testiruum(None, toimumispaev_id=rcd.reg_toimumispaev_id)
                tr.give_labiviijad()

            # leiame testiruumi
            found = False
            for testiruum in testikoht.testiruumid:
                vabukohti = testiruum.vabukohti
                if vabukohti is None or vabukohti > 0:
                    found = True
                    break
            if not found:
                testiruum = testikoht.give_testiruum(None, toimumispaev_id=rcd.reg_toimumispaev_id)

            # suuname
            testiruumid.add(testiruum)
            if rcd.testiruum:
                testiruumid.add(testiruum)

            cnt += 1
            rcd.suuna(testikoht, testiruum)

            if protsess:
                protsent = round(ind * 100 / total, -1)
                if protsess.lopp:
                    raise ProcessCanceled()
                if protsent > protsess.edenemisprotsent:
                    protsess.edenemisprotsent = protsent
                    protsess.viga = _("Suunatud {n} sooritajat").format(n=ind+1)
                    model.Session.commit()

        msg = ''
        if cnt:
            for testiruum in testiruumid:
                testiruum.set_sooritajate_arv()

            model.Session.commit()
            if cnt == 1:
                msg = _("Suunatud 1 sooritaja")
            else:
                msg = _("Suunatud {n} sooritajat").format(n=cnt)
        if cnt_koolita:
            if msg:
                msg += ', '
            msg += _("{n} sooritajal pole õppeasutust").format(n=cnt_koolita)

        if protsess:
            protsess.viga = msg
        return msg

    buf = _("Soorituskohtade genereerimine")
    ta_id = toimumisaeg.id
    tk = toimumisaeg.testimiskord
    params = {'testimiskord': tk,
              'test': tk.test,
              'liik': model.Arvutusprotsess.LIIK_VALIM,
              'kirjeldus': buf,
              }
    model.Arvutusprotsess.start(handler, params, childfunc)
    handler.success(_("Soorituskohtade genereerimise protsess on käivitatud"))

def jaota_sooritajad(self):
    """Soorituskohata sooritajad jaotatakse automaatselt eelistatud piirkonna järgi.
    Sooritaja õppimise kooli ei arvestata.

    Iga testisoorituskohaga sidumata ja registreeritud olekus oleva 
    testiosasoorituse kohta süsteem loob seose 
    registreerimise käigus määratud piirkonna eelistuse alusel 
    (leiab sooritaja poolt eelistatud piirkonda kuuluva testisoorituskoha, 
    kus on vabu kohti; 
    mitme sobiva hulgast valitakse mitmekeelse testi korral eelistatult koht, 
    kus on juba olema sama soorituskeelega testisooritajaid, 
    mitme samaväärse testisoorituskoha vahel valitakse juhuslikult).

    self = handler
    """
    # suunatavate arv
    suunatavate_arv = self.request.params.get('arv')
    if suunatavate_arv:
        suunatavate_arv = int(suunatavate_arv)

    # piirkond, milles jaotamine toimub
    piirkond_id = self.request.params.get('piirkond_id')
    cnt_piirkonnas = None

    # sooritajate hulk, kelle seast võetakse suunatavad
    q = model.Sooritus.query.\
        filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id).\
        filter(model.Sooritus.testikoht_id==None).\
        filter(model.Sooritus.staatus==const.S_STAATUS_REGATUD).\
        join(model.Sooritus.sooritaja)
    cnt_piirkonnata = q.filter(model.Sooritaja.piirkond_id==None).count();
    if piirkond_id:
        piirkond = model.Piirkond.get(piirkond_id)
        q = q.filter(model.Sooritaja.piirkond_id.in_(piirkond.get_alamad_id()))
        cnt_piirkonnas = q.count()
    else:
        q = q.filter(model.Sooritaja.piirkond_id!=None)
    q = q.order_by(model.Sooritaja.perenimi, model.Sooritaja.eesnimi)
    cnt_eisobi = 0
    cnt_maaratud = 0 

    testiruumid = set()

    # mitmekeelse testi korral püütakse samakeelsed kokku panna
    eelista_samakeelseid = len(self.c.toimumisaeg.testimiskord.get_keeled()) > 1

    # tsykkel yle kohata soorituste
    for rcd in q.all():
        sooritaja = rcd.sooritaja

        # otsime soorituskohti, mis on soovitud piirkonnas
        piirkonnad = sooritaja.piirkond.get_alamad_id()
        q1 = model.Testiruum.query.\
            join(model.Testiruum.testikoht).\
            filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id).\
            join(model.Testikoht.koht).\
            filter(model.Koht.piirkond_id.in_(piirkonnad))
            
        # filtreerime need kohad, kus on vabu kohti
        q1 = q1.filter(sa.or_(model.Testiruum.kohti==None,
                              model.Testiruum.kohti-model.Testiruum.sooritajate_arv>0))

        if eelista_samakeelseid:
            # filtreerime need kohad, kus juba on samakeelseid sooritajaid
            q2 = q1.join(model.Testikoht.testipaketid).\
                filter(model.Testipakett.lang==sooritaja.lang)
        
            # filtreerime need ruumid, kus juba on samakeelseid sooritajaid
            q3 = q2.filter(model.Testiruum.testiprotokollid.any(\
                    model.Testiprotokoll.testipakett_id==model.Testipakett.id))
            paringud = (q3, q2, q1)
        else:
            paringud = (q1,)

        # otsime sobiva testiruumi
        testiruum = None
        # päringud tingimuste leebumise järjekorras

        for qi in paringud:
            li = qi.all()
            len_qi = len(li)
            if len_qi > 1:
                # sobivaid ruume on mitu, valime neist juhuslikult yhe
                testiruum = li[random.randrange(len_qi)]
                break
            elif len_qi == 1:
                # sobivaid ruume on yks
                testiruum = li[0]
                break

        if testiruum:
           # leiti sobiv ruum 
            rcd.suuna(testiruum.testikoht, testiruum)
            testiruum.sooritajate_arv += 1
            testiruum.flush()
            cnt_maaratud += 1
            if suunatavate_arv and cnt_maaratud >= suunatavate_arv:
                # soovitud arv sooritajaid on suunatud
                break
        else:
            cnt_eisobi += 1

    buf = ''
    if cnt_piirkonnas == 0:
        buf += _("Valitud piirkonda ei ole ükski sooritaja registreeritud. ")
    if cnt_piirkonnata:
        buf += _("{n} sooritaja piirkond on valimata. ").format(n=cnt_piirkonnata)
    if cnt_eisobi:
        buf += _("{n} sooritaja jaoks pole sobivat kohta. ").format(n=cnt_eisobi)
    if cnt_maaratud:
        if cnt_maaratud == 1:
            buf += _("1 sooritaja on kohale määratud. ")
        else:
            buf += _("{n} sooritajat on kohtadesse jaotatud. ").format(n=cnt_maaratud)
        model.Session.commit()
    self.notice(buf)

def start_muusk(handler, toimumisaeg):
    """Muu soorituskoha teadete saatmise protsessi alustamine
    """
    toimumisaeg_id = toimumisaeg.id
    
    def childfunc(protsess):
        q = (model.Session.query(model.Sooritaja.kool_koht_id).distinct()
             .join(model.Sooritaja.sooritused)
             .filter(model.Sooritus.toimumisaeg_id==toimumisaeg_id)
             .filter(model.Sooritus.staatus.in_((const.S_STAATUS_REGATUD,
                                                 const.S_STAATUS_ALUSTAMATA)))
             .join(model.Sooritus.testikoht)
             .filter(model.Testikoht.koht_id!=model.Sooritaja.kool_koht_id)
             )
        kohad_id = [koht_id for koht_id, in q.all()]
        total = len(kohad_id)
        cnt = 0
        for ind, koht_id in enumerate(kohad_id):
            if send_muusk_kool(handler, toimumisaeg_id, koht_id):
                cnt += 1
            if protsess:
                protsent = round((ind + 1) * 100 / total, -1)
                if protsess.lopp:
                    raise ProcessCanceled()
                protsess.edenemisprotsent = protsent
                protsess.viga = _("Saadetud {n} teadet").format(n=cnt)
                model.Session.commit()

    buf = _("Muu soorituskoha teadete saatmine")
    ta_id = toimumisaeg.id
    tk = toimumisaeg.testimiskord
    params = {'testimiskord': tk,
              'test': tk.test,
              'liik': model.Arvutusprotsess.LIIK_MUUSK,
              'kirjeldus': buf,
              }
    model.Arvutusprotsess.start(handler, params, childfunc)
    handler.success(_("Muu soorituskoha teadete saatmine on käivitatud"))

def send_muusk_kool(handler, toimumisaeg_id, kool_koht_id):
    "Koolile muu soorituskoha teadete saatmine"
    q = (model.Session.query(model.Sooritaja.eesnimi,
                             model.Sooritaja.perenimi,
                             model.Sooritus.kavaaeg,
                             model.Koht.nimi,
                             model.Aadress.tais_aadress)
         .join(model.Sooritaja.sooritused)
         .filter(model.Sooritus.toimumisaeg_id==toimumisaeg_id)
         .filter(model.Sooritus.staatus.in_((const.S_STAATUS_REGATUD,
                                             const.S_STAATUS_ALUSTAMATA)))
         .join(model.Sooritus.testikoht)
         .filter(model.Testikoht.koht_id!=model.Sooritaja.kool_koht_id)
         .join(model.Testikoht.koht)
         .outerjoin(model.Koht.aadress)
         .filter(model.Sooritaja.kool_koht_id==kool_koht_id)
         .order_by(model.Sooritaja.eesnimi,
                   model.Sooritaja.perenimi)
         )
    suunamised = []
    for eesnimi, perenimi, aeg, koht_nimi, aadress in q.all():
        if aeg and handler.h.is_null_time(aeg):
            s_aeg = handler.h.str_from_date(aeg)
        elif aeg:
            s_aeg = handler.h.str_from_datetime(aeg)
        else:
            s_aeg = ''
        nimi = f'{eesnimi} {perenimi}'
        suunamised.append((nimi, s_aeg, koht_nimi, aadress))

    if suunamised:
        # antud kooli ja toimumisaja kõigi mujal sooritajate kohta teate saatmine
        kool_koht = model.Koht.get(kool_koht_id)
        ta = model.Toimumisaeg.get(toimumisaeg_id)
        tahised = ta.tahised
        test = ta.testiosa.test

        template = 'mail/muusk.mako'
        subject, body = handler.render_mail(template, 
                                            {'kool_nimi': kool_koht.nimi, 
                                             'test_nimi': test.nimi,
                                             'tahised': tahised,
                                             'suunamised': suunamised,
                                            })
        
        emails = []
        kasutajad = []
        for kasutaja in kool_koht.get_admin():
            epost = kasutaja.epost
            if epost:
                emails.append(epost)
                kasutajad.append(kasutaja)

        if not emails:
            log.error("Kooli {s} aadresse pole".format(s=kool_koht.nimi))
            return

        saajad = ', '.join(emails)
        err = Mailer(handler).send(emails, subject, body, out_err=False)
        if not err:
            log.info(f'{tahised} teade saadetud {kool_koht.nimi}: {saajad}')
            kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUUSK,
                              teema=subject,
                              sisu=body,
                              teatekanal=const.TEATEKANAL_EPOST)
            for k in kasutajad:
                ks = model.Kirjasaaja(kasutaja_id=k.id,
                                      epost=k.epost,
                                      koht_id=kool_koht_id,
                                      toimumisaeg_id=toimumisaeg_id)
                kiri.kirjasaajad.append(ks)
            model.Session.commit()
            return True
