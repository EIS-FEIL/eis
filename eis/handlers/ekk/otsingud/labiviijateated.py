from smtplib import SMTPRecipientsRefused

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.labiviijateade import LabiviijateadeDoc
from eis.lib.pdf.vaatlejateade import VaatlejateadeDoc

log = logging.getLogger(__name__)

class LabiviijateatedController(BaseResourceController):
    """Läbiviijateadete ja meeldetuletuste saatmine
    """
    _permission = 'aruanded-labiviijateated'
    _MODEL = model.Kiri
    _INDEX_TEMPLATE = 'ekk/otsingud/labiviijateated.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/labiviijateated_list.mako'
    _SEARCH_FORM = forms.ekk.otsingud.LabiviijateatedForm
    _DEFAULT_SORT = 'kasutaja.perenimi,kasutaja.eesnimi'
    _ignore_default_params = ['csv','xls','op']
    
    def _query(self):
        return None

    def _search_default(self, q):
        return None

    def _order_able(self, q, field):
        """Kontrollitakse, kas antud välja järgi on võimalik sortida
        """
        if field.startswith('kiri.') and self.c.ltyyp == model.Kiri.TYYP_LABIVIIJA_LEPING:
            return False
        else:
            return BaseResourceController._order_able(self, q, field)

    def _search(self, q1):
        if not self.c.sessioon_id:
            if self.request.params.get('saatmata'):
                self.error(_("Palun valida testsessioon"))
            return

        self.c.on_tseis = on_tseis = self.c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)

        if self.c.ltyyp not in (model.Kiri.TYYP_LABIVIIJA_TEADE,
                                model.Kiri.TYYP_LABIVIIJA_MEELDE,
                                model.Kiri.TYYP_LABIVIIJA_LEPING):
            self.c.ltyyp = model.Kiri.TYYP_LABIVIIJA_MEELDE

        q = self._search_saatmata_labiviija_kasutajakaupa()

        if self.c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))

        if self.c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(self.c.eesnimi))
        if self.c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(self.c.perenimi))
        #model.log_query(q)
        self._get_protsessid()
        self.c.arv = q.count()
        return q

    def _search_saatmata_labiviija_kasutajakaupa(self):
        "Kõigi testiliikide teated läbiviijale"
        li_select = [model.Kasutaja.id, 
                     model.Kasutaja.isikukood,
                     model.Kasutaja.synnikpv,
                     model.Kasutaja.nimi, 
                     model.Kasutaja.epost,
                     ]
        self.c.headers = [(1, 'kasutaja.isikukood kasutaja.synnikpv', _("Isikukood või sünniaeg"), None),
                          (3, 'kasutaja.perenimi,kasutaja.eesnimi', _("Nimi"), None),
                          (4, 'kasutaja.epost', _("E-posti aadress"), None),
                          ]

        q = model.SessionR.query(*li_select)
        if self.c.ltyyp == model.Kiri.TYYP_LABIVIIJA_LEPING:
            if not self.c.grupp_id:
                raise ValidationError(self, {'grupp_id': _("Palun valida roll")})
            
            # otsitakse neid, kes profiili ja käskkirja poolest sobivad,
            # aga ei ole läbiviijaks määratud
            f, f_profiil, f_aineprofiil = self._filter_profiil(True)

            if self.c.grupp_id in (const.GRUPP_HINDAJA_S12, const.GRUPP_HINDAJA_S, const.GRUPP_HINDAJA_S2, const.GRUPP_INTERVJUU):
                # kui on suuline roll, siis peab olema läbiviijaks määratud
                # (kool on juba määranud enne lepingu sõlmimist)
                f_labiviija = self._filter_labiviija_kasutajakaupa(True)
                f = sa.and_(f,
                            f_labiviija,
                            model.Labiviija.kasutaja_id==model.Kasutaja.id)

            f1 = None
            if f_profiil is not None:
                f1 = (sa.exists()
                      .where(f_profiil)
                      .where(f)
                      .where(model.Profiil.kasutaja_id==model.Kasutaja.id))
            if f_aineprofiil is not None:
                f2 = (sa.exists()
                      .where(f_aineprofiil)
                      .where(f)
                      .where(model.Aineprofiil.kasutaja_id==model.Kasutaja.id))
                if f1 is None:
                    f1 = f2
                else:
                    f1 = sa.or_(f1, f2)
            if f1 is not None:
                q = q.filter(f1)
        else:
            # otsitakse läbiviijaks määratud isikuid
            f = self._filter_labiviija_kasutajakaupa(True)
            if len(f):
                q = q.filter(model.Kasutaja.labiviijad.any(f))
        #model.log_query(q)
        return q

    def _filter_labiviija_kasutajakaupa(self, saatmata):
        f = [model.Labiviija.toimumisaeg_id==model.Toimumisaeg.id,
             model.Toimumisaeg.testimiskord_id==model.Testimiskord.id]
        if self.c.grupp_id:
            if self.c.grupp_id == const.GRUPP_HINDAJA_S12:
                f.append(model.Labiviija.kasutajagrupp_id.in_((const.GRUPP_HINDAJA_S, const.GRUPP_HINDAJA_S2)))
            else:
                f.append(model.Labiviija.kasutajagrupp_id==self.c.grupp_id)
        if self.c.toimumisaeg_id:
            f.append(model.Labiviija.toimumisaeg_id==int(self.c.toimumisaeg_id))
        elif self.c.testimiskord_id:
            f.append(model.Toimumisaeg.testimiskord_id==self.c.testimiskord_id)
        elif self.c.sessioon_id:
            f.append(model.Testimiskord.testsessioon_id==int(self.c.sessioon_id))
            if self.c.test_id:
                f.append(model.Testimiskord.test_id==self.c.test_id)
                
        if self.c.koht_id:
            f.append(model.Labiviija.testikoht.has(\
                    model.Testikoht.koht_id==self.c.koht_id))

        elif self.c.piirkond_id:
            piirkond = model.Piirkond.get(self.c.piirkond_id)
            piirkonnad_id = piirkond.get_alamad_id()
            f.append(model.Labiviija.testikoht.has(\
                model.Testikoht.koht.has(\
                    model.Koht.piirkond_id.in_(piirkonnad_id))))

        if saatmata and not self.c.kordus:
            # otsime ainult need, kellele ei ole veel kirja saadetud
            if self.c.ltyyp == model.Kiri.TYYP_LABIVIIJA_MEELDE:
                f.append(model.Labiviija.meeldetuletusaeg==None)
            elif self.c.ltyyp == model.Kiri.TYYP_LABIVIIJA_TEADE:
                f.append(model.Labiviija.teateaeg==None)
            else:
                f.append(~ model.Labiviija.labiviijakirjad.any(\
                    model.Labiviijakiri.kiri.has(model.Kiri.tyyp==self.c.ltyyp)))

        return sa.and_(*f)

    def _filter_profiil(self, saatmata):
        
        f = [model.Toimumisaeg.testimiskord_id==model.Testimiskord.id,
             model.Testimiskord.test_id==model.Test.id]
        if self.c.toimumisaeg_id:
            f.append(model.Toimumisaeg.id==int(self.c.toimumisaeg_id))
        elif self.c.testimiskord_id:
            f.append(model.Toimumisaeg.testimiskord_id==self.c.testimiskord_id)
        elif self.c.sessioon_id:
            f.append(model.Testimiskord.testsessioon_id==int(self.c.sessioon_id))
            if self.c.test_id:
                f.append(model.Testimiskord.test_id==self.c.test_id)

        # koha ja piirkonna tingimusi ignoreeritakse, kuna läbiviijat pole kohale veel määratud

        # if saatmata and not self.c.kordus:
        #     # otsime ainult need, kellele ei ole veel kirja saadetud
        #     f.append(~ model.Labiviija.labiviijakirjad.any(\
        #         model.Labiviijakiri.kiri.has(model.Kiri.tyyp==self.c.ltyyp)))

        f_profiil = sa.and_(model.Toimumisaeg.vaatleja_maaraja==True,
                            model.Profiil.v_kaskkirikpv>=model.Toimumisaeg.hindaja_kaskkirikpv)

        if self.c.grupp_id == const.GRUPP_INTERVJUU:
            f_aineprofiil = sa.and_(model.Aineprofiil.aine_kood==model.Test.aine_kood,
                                    model.Test.id==model.Testimiskord.test_id,
                                    model.Aineprofiil.kaskkirikpv>=model.Toimumisaeg.intervjueerija_kaskkirikpv)
        else:
            f_aineprofiil = sa.and_(model.Aineprofiil.aine_kood==model.Test.aine_kood,
                                    model.Test.id==model.Testimiskord.test_id,
                                    model.Aineprofiil.kaskkirikpv>=model.Toimumisaeg.hindaja_kaskkirikpv)            

        if self.c.grupp_id == const.GRUPP_VAATLEJA:
            # otsitakse ainult vaatlejaid
            f_aineprofiil = None
        elif self.c.grupp_id:
            # otsitakse ainult hindajaid ja intervjueerijaid
            f_profiil = None
            if self.c.grupp_id in (const.GRUPP_HINDAJA_S12, const.GRUPP_HINDAJA_S, const.GRUPP_HINDAJA_S2):
                f_aineprofiil = sa.and_(f_aineprofiil,
                                        model.Aineprofiil.kasutajagrupp_id==const.GRUPP_HINDAJA_S)
            else:
                f_aineprofiil = sa.and_(f_aineprofiil,
                                        model.Aineprofiil.kasutajagrupp_id==self.c.grupp_id)

        return sa.and_(*f), f_profiil, f_aineprofiil

    def create(self):
        "Kirjade saatmine"
        self.form = Form(self.request, schema=self._SEARCH_FORM)
        if self.form.validate():
            self._copy_search_params(self.form.data, save=True)
            q = self._search(None)
            if q:
                op = self.request.params.get('op')
                if op == 'epost':
                    cnt = q.count()
                    if self.c.toimumisaeg_id:
                        ta = model.Toimumisaeg.get(self.c.toimumisaeg_id)
                        tahised = ta.tahised
                    elif self.c.testimiskord_id:
                        tk = model.Testimiskord.get(self.c.testimiskord_id)
                        tahised = tk.tahised
                    elif self.c.test_id:
                        tahised = self.c.test_id
                    else:
                        tahised = ''
                    desc = 'Läbiviijate teadete saatmine %s (%d kirja)' % (tahised, cnt)
                    params = {'liik': model.Arvutusprotsess.LIIK_M_LABIVIIJA,
                              'kirjeldus': desc,
                              'test_id': self.c.test_id or None,
                              'testimiskord_id': self.c.testimiskord_id or None,
                              'toimumisaeg_id': self.c.toimumisaeg_id or None,
                              'testsessioon_id': self.c.sessioon_id or None,
                              }
                    childfunc = lambda protsess: self._send_eposts(protsess, q)
                    model.Arvutusprotsess.start(self, params, childfunc)
                    self.success('Saatmise protsess käivitatud')

                elif op == 'tpost':
                    q = self._order(q)
                    return self._send_tpost(q)

        return self._redirect('index', getargs=True)

    def _search_protsessid(self, q):
        sessioon_id = self.c.sessioon_id or self.request.params.get('sessioon_id')
        q = (q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_M_LABIVIIJA)
             .filter(model.Arvutusprotsess.testsessioon_id==sessioon_id)
             )
        return q

    def _get_saatmata_profiilid(self, item):
        kasutaja_id = item[0]

        # leiame testid, mida isik võiks potentsiaalselt läbi viia
        f, f_profiil, f_aineprofiil = self._filter_profiil(True)
        q1 = q2 = None
        if f_profiil is not None:
            q1 = (model.SessionR.query(model.Profiil.v_kaskkirikpv.label('kaskkirikpv'),
                                      model.Test.testiliik_kood,
                                      model.Test.aine_kood,
                                      sa.sql.expression.literal_column(str(const.GRUPP_VAATLEJA)).label('kasutajagrupp_id'))
                  .distinct()
                  .filter(f_profiil)
                  .filter(f)
                  .filter(model.Profiil.kasutaja_id==kasutaja_id))
        if f_aineprofiil is not None:
            q2 = (model.SessionR.query(model.Aineprofiil.kaskkirikpv,
                                      model.Test.testiliik_kood,
                                      model.Aineprofiil.aine_kood,
                                      model.Aineprofiil.kasutajagrupp_id)
                  .distinct()
                  .filter(f_aineprofiil)
                  .filter(f)
                  .filter(model.Aineprofiil.kasutaja_id==kasutaja_id))
        if q1 and q2:
            q = q1.union(q2)
        else:
            q = q1 or q2
        return q.all()

    def _get_saatmata_labiviijad(self, item):
        kasutaja_id = item[0]

        # leiame testid, kus isik on läbiviijaks määratud
        f = self._filter_labiviija_kasutajakaupa(True)
        q = (model.Labiviija.query
             .filter(model.Labiviija.kasutaja_id==kasutaja_id)
             .filter(f)
             .outerjoin(model.Labiviija.testiruum)
             .order_by(model.Testiruum.algus)
             )
        return q.all()

    def _send_eposts(self, protsess, q):
        c = self.c
        total = q.count()

        def itemfunc(rcd):
            k_id, k_ik, k_synnikpv, k_nimi, k_epost = rcd[:5]
            if not k_epost:
                return False, k_nimi
            else:
                k = model.Kasutaja.get(k_id)           
                if c.ltyyp == model.Kiri.TYYP_LABIVIIJA_LEPING:
                    labiviijad = list(self._get_saatmata_profiilid(rcd))
                else:
                    labiviijad = list(self._get_saatmata_labiviijad(rcd))
                if send_epost_labiviija(self, c.ltyyp, k, c.grupp_id, labiviijad, c.testiliik, c.taiendavinfo):
                    return True, None
                else:
                    return False, k_epost
                
        model.Arvutusprotsess.iter_mail(protsess, self, total, q.all(), itemfunc)
    
    def _send_tpost(self, q):

        # igat liiki testide jaoks, vahet teeb läbiviijate leidmise funktsioon
        if self.c.ltyyp == model.Kiri.TYYP_LABIVIIJA_LEPING:
            self.error(_("Lepingu sõlmimise teavitusi paberil ei saadeta"))
            return self._redirect('index', getargs=True)
            
        elif self.c.grupp_id == const.GRUPP_VAATLEJA:
            doc = VaatlejateadeDoc(self, self.c.ltyyp)
        else:
            doc = LabiviijateadeDoc(self, self.c.ltyyp, self.c.testiliik)            

        data = doc.generate(items=q.all(), get_labiviijad=self._get_saatmata_labiviijad)

        # salvestame teate aja läbiviija kirjes
        model.Session.commit()
        filename = '%s.pdf' % (self.c.ltyyp)
        mimetype = const.CONTENT_TYPE_PDF
        return utils.download(data, filename, mimetype)

def send_epost_labiviija(handler, tyyp, k, grupp_id, labiviijad, testiliik, taiendavinfo=None):
    tyybid = (model.Kiri.TYYP_LABIVIIJA_TEADE,
              model.Kiri.TYYP_LABIVIIJA_MEELDE,
              model.Kiri.TYYP_LABIVIIJA_LEPING)
    assert tyyp in tyybid, 'vale tyyp %s' % tyyp
    
    to = k.epost
    if not to:
        return False
    data = {'isik_nimi': k.nimi,
            'labiviijad': labiviijad,
            'user_nimi': handler.c.user.fullname,
            'taiendavinfo': taiendavinfo,
            }
    mako = None
    if tyyp == model.Kiri.TYYP_LABIVIIJA_LEPING:
        mako = 'mail/labiviijaleping.teavitus.mako'
        rollid = []
        for kaskkirikpv, testiliik_kood, aine_kood, grupp_id in labiviijad:
            grupp_nimi = model.Kasutajagrupp.get(grupp_id).nimi.lower()
            if not kaskkirikpv:
                handler.error(_("{s1} ei ole käskkirja kantud ({s2}, {s3})").format(s1=k.nimi, s2=grupp_nimi, s3=aine_kood))
            else:
                roll = (handler.h.str_from_date(kaskkirikpv),
                        model.Klrida.get_str('TESTILIIK', testiliik_kood),
                        model.Klrida.get_str('AINE', aine_kood).lower(),                        
                        grupp_nimi)
                rollid.append(roll)
        if len(rollid) == 0:
            return False

        if grupp_id == const.GRUPP_VAATLEJA:
            data['kaskija'] = 'Haridus- ja Noorteameti peadirektori'
            # vaatlejal ei kuva aineid, EH-339
            roll = rollid[0]
            roll = (roll[0], roll[1], '', roll[3])
            rollid = [roll]
        elif testiliik == const.TESTILIIK_RV:
            # prantsuse keele hindaja leping
            data['kaskija'] = 'Haridus- ja Noorteameti peadirektori'            
        else:
            data['kaskija'] = 'haridus- ja teadusministri'

        data['rollid'] = rollid

    elif grupp_id == const.GRUPP_VAATLEJA:
        mako = 'mail/%s.vaatleja.mako' % tyyp
    elif tyyp == model.Kiri.TYYP_LABIVIIJA_TEADE:
        if testiliik in (const.TESTILIIK_RIIGIEKSAM,
                         const.TESTILIIK_POHIKOOL,
                         const.TESTILIIK_TASE,
                         const.TESTILIIK_SEADUS):
            mako = 'mail/%s_%s.mako' % (tyyp, testiliik)
    elif tyyp == model.Kiri.TYYP_LABIVIIJA_MEELDE:
        if testiliik in (const.TESTILIIK_RIIGIEKSAM,
                         const.TESTILIIK_POHIKOOL,
                         const.TESTILIIK_TASE,
                         const.TESTILIIK_SEADUS):
            mako = 'mail/%s_%s.mako' % (tyyp, testiliik)

    if not mako:
        handler.error(_("Neid teateid selle testiliigi korral ei saadeta"))
        return False
                
    subject, body = handler.render_mail(mako, data)
    err = Mailer(handler).send(to, subject, body, out_err=False)
    if err:
        buf = '%s (%s %s)' % (err, k.nimi, to)
        model.Arvutusprotsess.trace(buf)        
        return False
    else:
        kiri = model.Kiri(saatja_kasutaja_id=handler.c.user.id,
                          tyyp=tyyp,
                          sisu=body,
                          teema=subject,
                          teatekanal=const.TEATEKANAL_EPOST)
        for lv in labiviijad:
            if tyyp == model.Kiri.TYYP_LABIVIIJA_TEADE:
                lv.teateaeg = datetime.now()
                model.Labiviijakiri(labiviija=lv, kiri=kiri)                
            elif tyyp == model.Kiri.TYYP_LABIVIIJA_MEELDE:
                lv.meeldetuletusaeg = datetime.now()
                model.Labiviijakiri(labiviija=lv, kiri=kiri)
                                                                    
        model.Kirjasaaja(kiri=kiri, kasutaja_id=k.id, epost=k.epost)
        model.Session.commit()
        log.debug(_("Saadetud kiri aadressile {s}").format(s=to))
        return True

def send_labiviija_maaramine(handler, lv, k, ta, li_hk_tahised=[]):
    "Testi admini või hindaja määramisel saadetakse määratud läbiviijale teade"
    grupp_id = lv.kasutajagrupp_id
    algus = tahtaeg = hk_tahis = hk_tahised = None
    if grupp_id == const.GRUPP_T_ADMIN and ta.admin_teade:
        # saadetakse testi adminiks määramise teade
        mako = 'mail/labiviijamaaramine.admin.mako'
    elif grupp_id == const.GRUPP_KOMISJON and ta.admin_teade:
        # saadetakse komisjoni liikmeks määramise teade
        mako = 'mail/labiviijamaaramine.komisjon.mako'        
    elif handler.c.app_eis and \
             grupp_id in (const.GRUPP_HINDAJA_K,
                          const.GRUPP_HINDAJA_S,
                          const.GRUPP_HINDAJA_S2,
                          const.GRUPP_HIND_INT):
        # saadetakse hindajaks määramise teade
        # (ainult avalikus vaates määramise korral ES-2806)
        mako = 'mail/labiviijamaaramine.hindaja.mako'
        algus = handler.h.str_from_datetime(ta.hindamise_algus, hour0=False)
        tahtaeg = handler.h.str_from_date(ta.hindamise_tahtaeg)
        if len(li_hk_tahised) > 1:
            # võimalus anda mitu hindamiskogumit
            hk_tahised = ', '.join(li_hk_tahised)
        else:
            hk = lv.hindamiskogum
            hk_tahis = hk and hk.tahis or None
    else:
        # määrati selline roll, mille korral teadet ei saadeta
        return

    # andmed malli jaoks
    test = ta.testiosa.test
    if grupp_id == const.GRUPP_HINDAJA_K:
        testiruum = None
        testialgus = None
    else:
        testiruum = lv.testiruum
        testialgus = testiruum and testiruum.algus
        
    if testialgus:
        millal = handler.h.str_from_datetime(testialgus, hour0=False)
    else:
        millal = ta.millal

    ruum = testiruum and testiruum.ruum 
    ruum_tahis = ruum and ruum.tahis or None 
    testikoht = lv.testikoht 
    koht = testikoht and testikoht.koht 
    koht_nimi = koht and koht.nimi or ''
    if koht_nimi and ruum_tahis:
        koht_nimi = f'{koht_nimi}, ruum {ruum_tahis}'

    data = {'isik_nimi': k.nimi,
            'test_nimi': test.nimi,
            'millal': millal,
            'koht_nimi': koht_nimi,
            'tahtaeg': tahtaeg,
            'algus': algus,
            'hk_tahised': hk_tahised,
            'hk_tahis': hk_tahis,
            }

    # kui on e-posti aadress, siis saadetakse e-post
    teatekanal = const.TEATEKANAL_EIS
    subject, body = handler.render_mail(mako, data)
    to = k.epost
    if to:
        err = Mailer(handler).send(to, subject, body)
        if err:
            buf = '%s (%s %s)' % (err, k.nimi, to)
            log.error(buf)
        else:
            # õnnestus saata
            teatekanal = const.TEATEKANAL_EPOST
            log.debug(_("Saadetud kiri aadressile {s}").format(s=to))
            
    kiri = model.Kiri(saatja_kasutaja_id=handler.c.user.id,
                      tyyp=model.Kiri.TYYP_LABIVIIJA_MAARAMINE,
                      sisu=body,
                      teema=subject,
                      teatekanal=teatekanal)
    model.Labiviijakiri(labiviija=lv, kiri=kiri)
    model.Kirjasaaja(kiri=kiri, kasutaja_id=k.id, epost=to)
    log.debug(f'lv määramise teade {k.nimi}')
    # tuleb teha commit
    return True
