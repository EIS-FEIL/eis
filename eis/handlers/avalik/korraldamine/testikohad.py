import math
from eis.lib.baseresource import *
from eis.lib.helpers import is_null_time
_ = i18n._

log = logging.getLogger(__name__)

class TestikohadController(BaseResourceController):
    _permission = 'avalikadmin'
    _MODEL = model.Testikoht
    _SEARCH_FORM = forms.avalik.admin.KorraldamineForm
    _INDEX_TEMPLATE = 'avalik/korraldamine/otsing.mako'
    _LIST_TEMPLATE = 'avalik/korraldamine/otsing_list.mako'
    _DEFAULT_SORT = '-toimumisaeg.alates,toimumisaeg.tahised' # vaikimisi sortimine
    _perm_koht = True
    _actions = 'index,show,delete'
    
    def _query(self):
        q = (model.Session.query(model.Testikoht,
                                 model.Test.nimi,
                                 model.Toimumisaeg,
                                 model.Testiosa)
             .filter(model.Testikoht.koht_id==self.c.user.koht_id)
             .join(model.Testikoht.toimumisaeg)
             .join(model.Toimumisaeg.testiosa)
             .join(model.Toimumisaeg.testimiskord)
             .join(model.Testimiskord.test)
             .filter(model.Test.avaldamistase==const.AVALIK_EKSAM)
             .filter(model.Testimiskord.osalemise_naitamine==True))
        return q

    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.alates:
            q = q.filter(model.Toimumisaeg.kuni >= c.alates)
        if c.kuni:
            q = q.filter(model.Toimumisaeg.alates <= c.kuni)
        if c.aktiiv != 'f':
            q = q.filter(model.Toimumisaeg.kuni >= date.today())
        if c.testsessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==c.testsessioon_id)

        # debug
        if c.hindajad:
            q = q.filter(model.Toimumisaeg.hindaja1_maaraja.in_(const.MAARAJA_KOHAD))
        if c.test_id:
            q = q.filter(model.Testimiskord.test_id==c.test_id)

        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item        
        return q

    def _prepare_header(self):
        header = [('test.nimi', _("Testi nimetus")),
                  ('toimumisaeg.tahised', _("Tähis")),
                  ('toimumisaeg.alates', _("Kuupäev")),
                  ('testiosa.vastvorm_kood', _("Vastamise vorm")),
                  (None, _("Sooritajate arv")),
                  (None, _("Ruumid")),
                  (None, _("Läbiviijad")),
                  (None, _("Hindajad")),
                  ]
        return header
    
    def _prepare_item(self, rcd, n):
        testikoht, t_nimi, ta, osa = rcd

        on_ruumid = tkoht_on_ruumid(osa, ta, testikoht)       
        on_labiviijad = tkoht_on_labiviijad(osa, ta, testikoht)
        on_hindajad = tkoht_on_hindajad(osa, ta, testikoht)
        #log.debug(f'{testikoht.id},{ta.tahised} hindajad:{on_hindajad}')
        
        item = [t_nimi,
                ta.tahised,
                ta.millal,
                osa.vastvorm_nimi,
                testikoht.get_sooritajatearv(),
                on_ruumid,
                on_labiviijad,
                on_hindajad]
        return item

    def show(self):
        testikoht_id = self.request.matchdict.get('id')
        url = self.url('korraldamine_sooritajad', testikoht_id=testikoht_id)
        return HTTPFound(location=url)

    def _delete(self, item):
        err = None
        toimumisaeg = item.toimumisaeg
        if not self.c.user.has_permission('avalikadmin', const.BT_DELETE, item) or \
               self.c.user.koht_id != item.koht_id:
            err = _("Puudub õigus")
        elif toimumisaeg.kohad_kinnitatud:
            err = _("Soorituskohad on juba kinnitatud!")
        else:
            for truum in item.testiruumid:
                if truum.sooritajate_arv == 0:
                    truum.delete()
                else:
                    err = _("Soorituskohta ei saa enam eemaldada, sest leidub sooritajaid")
                    break
            for lv in item.labiviijad:
                if not lv.toode_arv:
                    lv.delete()
                else:
                    err = _("Soorituskohta ei saa enam eemaldada")
            if not err:
                item.delete()
                model.Session.commit()
        if err:
            self.error(err)
        else:
            self.success(_("Soorituskoht on eemaldatud!"))

    def __before__(self):
        id = self.request.matchdict.get('id')
        if id:
            self.c.testikoht = model.Testikoht.get(id)
        

def tkoht_on_ruumid(testiosa, ta, testikoht, for_mail=False):
    "Kas testikoht on ruumid määranud?"
    if not ta.ruumide_jaotus:
        # soorituskoht ei või ruume määrata
        return None
    on_ruumid = True
    today = date.today()
    now = datetime.combine(today, time(0))
    until_date = utils.add_working_days(today, 3)
    until_time = datetime.combine(until_date, time(0))
    for tr in testikoht.testiruumid:
        if for_mail and not (now <= tr.algus < until_time):
            # huvitavad ainult lähema 3 päeva testid
            continue
        if ta.ruum_noutud and tr.ruum_id is None:
            on_ruumid = False
            break
        if is_null_time(tr.algus):
            on_ruumid = False
            break
    return on_ruumid

def tkoht_on_labiviijad(testiosa, ta, testikoht, for_mail=False):
    "Kas testikoht on läbiviijad määranud?"
    rollid = []
    if ta.esimees_maaraja:
        rollid.append(const.GRUPP_KOMISJON_ESIMEES)
    if ta.komisjoniliige_maaraja:
        rollid.append(const.GRUPP_KOMISJON)

    if ta.on_ruumiprotokoll:
        rollid_r = rollid
        rollid_k = []
    else:
        rollid_r = []
        rollid_k = rollid
        
    if ta.admin_maaraja and ta.labiviijate_jaotus:
        rollid_r.append(const.GRUPP_T_ADMIN)

    maaramata = \
      _tkoht_on_labiviijad_testiruumis(testiosa, ta, testikoht, for_mail, rollid_r) + \
      _tkoht_on_labiviijad_testikohal(testiosa, ta,testikoht, for_mail, rollid_k)

    if for_mail:
        # rollid, mille läbiviijaid pole määratud
        return maaramata
    else:
        if maaramata:
            # ei ole määratud
            on_labiviijad = False
        elif rollid_r or rollid_k:
            # läbiviijaid saab määrata ja on määratud
            on_labiviijad = True
        else:
            # ei saa määrata
            on_labiviijad = None
        return on_labiviijad
    
def _tkoht_on_labiviijad_testiruumis(testiosa, ta, testikoht, for_mail, rollid_r):
    # ruumide läbiviijad
    if for_mail:
        # teavituste jaoks
        today = date.today()
        now = datetime.combine(today, time(0))
        until_date = utils.add_working_days(today, 3)
        until_time = datetime.combine(until_date, time(0))

    maaramata = []
    for grupp_id in rollid_r:
        flt_lv = sa.and_(model.Labiviija.testiruum_id==model.Testiruum.id,
                         model.Labiviija.kasutajagrupp_id==grupp_id,
                         model.Labiviija.kasutaja_id!=None)
        q = (model.Session.query(model.Testiruum.id)
             .filter(model.Testiruum.testikoht_id==testikoht.id)
             .outerjoin((model.Labiviija, flt_lv))
             .filter(model.Labiviija.id==None)
             )
        if for_mail:
            # huvitavad ainult eesolevad testid
            q = q.filter(model.Testiruum.algus >= now)
            if grupp_id in (const.GRUPP_KOMISJON, const.GRUPP_KOMISJON_ESIMEES) \
              and ta.komisjon_maaramise_tahtaeg:
                # teavitada siis, kui komisjoni määramise tähtajani on alla 3 päeva
                if ta.komisjon_maaramise_tahtaeg >= until_date:
                    # ei ole vaja teavitada
                    continue
            else:
                # teavitada siis, kui testi toimumiseni on alla 3 päeva
                q = q.filter(model.Testiruum.algus < until_time)

        if q.count() > 0:
            # leidub ruume, kus puudub antud rollis läbiviija
            maaramata.append((grupp_id, None))
    return maaramata

def _tkoht_on_labiviijad_testikohal(testiosa, ta, testikoht, for_mail, rollid_k):
    # testikoha läbiviijad
    if for_mail:
        # teavituste jaoks
        today = date.today()
        now = datetime.combine(today, time(0))
        until_date = utils.add_working_days(today, 2)
        until_time = datetime.combine(until_date, time(0))

    maaramata = []
    for grupp_id in rollid_k:
        if for_mail:
            if grupp_id in (const.GRUPP_KOMISJON, const.GRUPP_KOMISJON_ESIMEES) \
              and ta.komisjon_maaramise_tahtaeg:
                # teavitada siis, kui komisjoni määramise tähtajani on alla 3 päeva            
                if ta.komisjon_maaramise_tahtaeg >= until_date:
                    # ei ole vaja teavitada
                    continue
            else:
                if testikoht.alates >= until_time:
                    # ei ole vaja teavitada
                    continue
                    
        q = (model.Session.query(model.Labiviija.id)
             .filter(model.Labiviija.testikoht_id==testikoht.id)
             .filter(model.Labiviija.kasutajagrupp_id==grupp_id)
             .filter(model.Labiviija.kasutaja_id!=None)
             )
        cnt = q.count()
        if grupp_id == const.GRUPP_KOMISJON and testiosa.test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
            # Riigieksamikomisjonid määratakse arvestusega, et iga 20 eksaminandi kohta on
            # riigieksamikomisjonis üks liige ja koos esimehega kokku mitte vähem kui kolm liiget.
            if cnt <= 1 and not for_mail:
                # peab olema vähemalt esimees + 2 liiget
                maaramata.append((grupp_id, None))
            else:
                # arvutame vajaliku liikmete arvu eksaminandide arvu järgi
                q = (model.Session.query(sa.func.count(model.Sooritus.id))
                     .filter(model.Sooritus.testikoht_id==testikoht.id))
                n = q.scalar()
                min_cnt = max(3, math.ceil(n / 20)) - 1 # min liikmete arv ilma esimeheta
                if cnt < min_cnt:
                    maaramata.append((grupp_id, min_cnt))
        elif cnt == 0:
            # soorituskohas puudub antud rollis läbiviija
            maaramata.append((grupp_id, None))
    return maaramata

def tkoht_on_hindajad(testiosa, ta, testikoht, for_mail=False):
    "Kas soorituskoht on hindajad määranud?"
    tkord = ta.testimiskord
    if tkord.sisaldab_valimit:
        q = (model.Session.query(model.Sooritaja.id)
             .join(model.Sooritaja.sooritused)
             .filter(model.Sooritus.testikoht_id==testikoht.id))
        on_valim = q.filter(model.Sooritaja.valimis==True).first() is not None
        on_valimita = q.filter(model.Sooritaja.valimis==False).first() is not None
    else:
        on_valim = False
        on_valimita = True

    liigid = []
    # kirjalike hindajatega testiosade vastamisvormid
    vastvorm_kh = (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I)
    if on_valimita:
        if ta.hindaja1_maaraja in const.MAARAJA_KOHAD:
            liigid.append((False, const.HINDAJA1))
        if testiosa.vastvorm_kood in vastvorm_kh and \
           ta.hindaja2_maaraja in const.MAARAJA_KOHAD:
            liigid.append((False, const.HINDAJA2))
    if on_valim:
        if ta.hindaja1_maaraja_valim in const.MAARAJA_KOHAD:
            liigid.append((True, const.HINDAJA1))
        if testiosa.vastvorm_kood in vastvorm_kh and \
           ta.hindaja2_maaraja_valim in const.MAARAJA_KOHAD:
            liigid.append((True, const.HINDAJA2))
    if not liigid:
        # soorituskoht ei määra hindajaid
        return None

    if testiosa.vastvorm_kood in (const.VASTVORM_SP, const.VASTVORM_SH):
        # suulise testi hindajaid tuleb kontrollida kõigis ruumides
        return _tkoht_on_hindajad_s(testiosa, ta, testikoht, for_mail, tkord.sisaldab_valimit, liigid)
    else:
        # kirjalikud hindajad
        return _tkoht_on_hindajad_k(testiosa, ta, testikoht, for_mail, liigid)
    
def _tkoht_on_hindajad_k(testiosa, ta, testikoht, for_mail, liigid):
    "Kas etteantud liigiga kirjalikud hindajad on testikohas määratud?"
    maaramata = []
    testiosa_id = ta.testiosa_id

    q = (model.Session.query(model.Hindamiskogum.tahis)
         .filter(model.Hindamiskogum.testiosa_id==testiosa_id)
         .filter(model.Hindamiskogum.arvutihinnatav==False)
         .filter(model.Hindamiskogum.staatus==const.B_STAATUS_KEHTIV)
         )
    for valimis, liik in liigid:
        flt_lv = sa.and_(model.Labiviija.testikoht_id==testikoht.id,
                         model.Labiviija.kasutaja_id!=None,
                         model.Labiviija.valimis==valimis,
                         model.Labiviija.liik==liik)
            
        # kas leidub hindamiskogum, millele selles soorituskohas pole hindajat?
        q1 = q.filter(~ model.Hindamiskogum.labiviijad.any(flt_lv))
        for hk_tahis, in q1.all():
            if not for_mail:
                return False
            maaramata.append((hk_tahis, liik, valimis))

    if not for_mail:
        # hindajad on määratud
        return True       
    return maaramata

def _tkoht_on_hindajad_s(testiosa, ta, testikoht, for_mail, sisaldab_valimit, liigid):
    "Kas etteantud liigiga suulised hindajad on testikoha kõigis ruumides määratud?"
    
    if for_mail:
        # teavituste jaoks
        today = date.today()
        now = datetime.combine(today, time(0))
        until_date = utils.add_working_days(today, 3)
        until_time = datetime.combine(until_date, time(0))

    maaramata = []

    # ruumide läbiviijad
    for valimis, liik in liigid:
        if liik == const.HINDAJA1:
            grupp_id = const.GRUPP_HINDAJA_S
        elif liik == const.HINDAJA2:
            grupp_id = const.GRUPP_HINDAJA_S2

        flt_lv = sa.and_(model.Labiviija.testiruum_id==model.Testiruum.id,
                         model.Labiviija.kasutajagrupp_id==grupp_id,
                         model.Labiviija.kasutaja_id!=None,
                         model.Labiviija.valimis==valimis)
            
        q = (model.Session.query(model.Testiruum.id)
             .filter(model.Testiruum.testikoht_id==testikoht.id)
             .outerjoin((model.Labiviija, flt_lv))
             .filter(model.Labiviija.id==None)
             )
        if sisaldab_valimit:
            # kontrollime, kas valimiga või valimita sooritajaid selles ruumis on
            q = q.filter(sa.exists().where(
                sa.and_(
                    model.Sooritus.testiruum_id==model.Testiruum.id,
                    model.Sooritus.sooritaja_id==model.Sooritaja.id,
                    model.Sooritaja.valimis==valimis)
                ))

        if for_mail:
            # huvitavad ainult lähima 3 tööpäeva toimumised
            q = (q.filter(model.Testiruum.algus >= now)
                 .filter(model.Testiruum.algus < until_time))

        if q.count() > 0:
            # leidub ruume, kus puudub antud rollis läbiviija
            maaramata.append((None, liik, valimis))

    if for_mail:
        # rollid, mille läbiviijaid pole määratud
        return maaramata
    else:
        if maaramata:
            # ei ole määratud
            on_labiviijad = False
        elif liigid:
            # läbiviijaid saab määrata ja on määratud
            on_labiviijad = True
        else:
            # ei saa määrata
            on_labiviijad = None
        return on_labiviijad
