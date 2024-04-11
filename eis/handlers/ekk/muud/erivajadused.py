from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
import eis.lib.pdf as pdf
_ = i18n._
log = logging.getLogger(__name__)

class ErivajadusedController(BaseResourceController):
    """Erivajaduste loetelu ja andmed    
    """
    _permission = 'erivajadused'
    _MODEL = model.Sooritus
    _INDEX_TEMPLATE = 'ekk/muud/erivajadused.otsing.mako'
    _LIST_TEMPLATE = 'ekk/muud/erivajadused.otsing_list.mako'
    _EDIT_TEMPLATE = 'ekk/muud/erivajadus.mako'
    _ITEM_FORM = forms.ekk.regamine.ErivajadusedForm
    _SEARCH_FORM = forms.ekk.regamine.ErivajadusedOtsingForm
    _DEFAULT_SORT = 'sooritus.id' # vaikimisi sortimine
    _ignore_default_params = ['xls','mail']
    _get_is_readonly = False
    
    def _query(self):
        self.c.opt_sessioon = self.c.opt.testsessioon
        Kool_koht = sa.orm.aliased(model.Koht, name='kool_koht')
        q = (model.SessionR.query(model.Sooritus, 
                                 model.Sooritaja.lang, 
                                 model.Kasutaja.isikukood,
                                 model.Kasutaja.synnikpv,
                                 model.Sooritaja.eesnimi,
                                 model.Sooritaja.perenimi,
                                 model.Test.nimi,
                                 model.Test.aine_kood,
                                 model.Testiosa.nimi,
                                 model.Koht.nimi,
                                 model.Ruum.tahis,
                                 Kool_koht.nimi,
                                 model.Komplekt.tahis)
             .filter(model.Sooritus.on_erivajadused==True)
             .join(model.Sooritus.sooritaja)
             .join(model.Sooritaja.testimiskord)
             .join(model.Sooritaja.test)
             .join(model.Sooritaja.kasutaja)
             .join(model.Sooritus.testiosa)
             .join(model.Sooritus.toimumisaeg)
             .outerjoin(model.Sooritus.testikoht)
             .outerjoin(model.Testikoht.koht)
             .outerjoin(model.Sooritus.testiruum)
             .outerjoin(model.Testiruum.ruum)
             .outerjoin(model.Sooritus.erikomplektid)
             .outerjoin(model.Erikomplekt.komplekt)
             .outerjoin((Kool_koht, Kool_koht.id==model.Sooritaja.kool_koht_id))
             )
        
        if not self.c.sessioon_id and len(self.c.opt_sessioon):
            self.c.sessioon_id = self.c.opt_sessioon[0][0]

        # leiame kasutajale lubatud piirkondade loetelu
        piirkonnad_id = self.c.user.get_kasutaja().get_piirkonnad_id('erivajadused', const.BT_SHOW)
        # kas pole õigust kõigi piirkondade korraldamiseks?
        if None not in piirkonnad_id:
            # piirkondlik korraldaja ei või kõiki piirkondi vaadata, 
            q = q.filter(sa.or_(model.Sooritaja.piirkond_id.in_(piirkonnad_id),
                                model.Koht.piirkond_id.in_(piirkonnad_id)))

        return q

    def _search_default(self, q):
        return None

    def _search(self, q):
        c = self.c
        if c.toimumisaeg_id or c.tahis:
            # korraldamise materjalide väljastamise lehelt linkides on olemas toimumisaeg_id
            if c.toimumisaeg_id:
                ta = model.Toimumisaeg.get(c.toimumisaeg_id)
            else:
                ta = model.Toimumisaeg.query.filter_by(tahised=c.tahis).first()

            if ta:
                c.sessioon_id = ta.testimiskord.testsessioon_id
                c.tahis = ta.tahised
                c.toimumisaeg_id = ta.id
                q = q.filter(model.Sooritus.toimumisaeg_id==c.toimumisaeg_id)
        else:
            q = q.filter(model.Testimiskord.testsessioon_id==int(c.sessioon_id))

        if c.test_id:
            q = q.filter(model.Test.id==c.test_id)
        if c.aine_kood:
            q = q.filter(model.Test.aine_kood==c.aine_kood)
        if c.kinnitatud:
            q = q.filter(model.Sooritus.on_erivajadused_kinnitatud==True)
        if c.kinnitamata:
            q = q.filter(model.Sooritus.on_erivajadused_kinnitatud==False)
        if c.vaadatud:
            q = q.filter(model.Sooritus.on_erivajadused_vaadatud==True)
        if c.vaatamata:
            q = q.filter(model.Sooritus.on_erivajadused_vaadatud==False)                        
        if c.maakond_kood:
            # koos tasemega, nt 1.37, eemaldame taseme
            kood1 = c.maakond_kood.split('.')[-1]
            q = q.join(model.Koht.aadress).filter(model.Aadress.kood1==kood1)
        if c.soorituskoht_id:
            q = q.filter(model.Testikoht.koht_id==c.soorituskoht_id)
        if c.oppimiskoht_id:
            q = q.filter(model.Sooritaja.kool_koht_id==c.oppimiskoht_id)
        for erivajadus in c.erivajadus:
            if erivajadus == 'vabastatud':
                q = q.filter(
                    sa.or_(model.Sooritus.staatus==const.S_STAATUS_VABASTATUD,
                           model.Sooritaja.vabastet_kirjalikust==True,
                           sa.exists().where(sa.and_(
                               model.Sooritus.id==model.Alatestisooritus.sooritus_id,
                               model.Alatestisooritus.staatus==const.S_STAATUS_VABASTATUD))
                           )
                    )
            elif c.kinnitatud:
                q = q.filter(model.Sooritus.erivajadused.any(
                    sa.and_(model.Erivajadus.erivajadus_kood==erivajadus,
                            model.Erivajadus.kinnitus==True)))
            else:
                q = q.filter(model.Sooritus.erivajadused.any(
                    model.Erivajadus.erivajadus_kood==erivajadus))

        c.hide_reviewed = False
        if c.sessioon_id:
            sessioon = model.Testsessioon.get(c.sessioon_id)
            if sessioon and sessioon.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
                c.hide_reviewed = True

        if c.xls:
            return self._index_xls(q)
        if c.mail:
            if not c.kordus:
                # saadame ainult neile, kellele veel pole saatnud
                q = q.filter(model.Sooritus.erivajadused_teavitatud==None)
            self._send_mail(q)

        return q

    def _send_mail(self, q):

        def _send_kontakt(sooritused, saajad):
            to = [r for r in saajad if r]
            if not to or not sooritused:
                return 0

            test_id = sooritused[0].sooritaja.test_id
            data = {'sooritused': sooritused,
                    'test': model.Test.get(test_id),
                    }
            subject, body = self.render_mail('mail/erivajaduseteade.mako', data)
            body = Mailer.replace_newline(body)
            if not Mailer(self).send(to, subject, body):
                log.debug('Saadetud kiri "%s" aadressidele %s' % (subject, to))
                now = datetime.now()
                for tos in sooritused:
                    tos.erivajadused_teavitatud = now
                return len(sooritused)

        def _send_sooritajale(sooritused, saaja_k):
            to = saaja_k.epost
            if not to or not sooritused:
                return 0
            test_id = sooritused[0].sooritaja.test_id
            data = {'sooritused': sooritused,
                    'test': model.Test.get(test_id),
                    }
            subject, body = self.render_mail('mail/erivajaduseteade.mako', data)
            body = Mailer.replace_newline(body)
            if not Mailer(self).send(to, subject, body):
                log.debug('Saadetud kiri "%s" aadressidele %s' % (subject, to))
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                model.Kirjasaaja(kiri=kiri, kasutaja_id=saaja_k.id, epost=to)
                return len(sooritused)

        cnt = 0
        q = q.join(model.Sooritus.testiosa)
        q = q.order_by(model.Sooritaja.kool_koht_id,
                       model.Sooritaja.test_id,
                       model.Sooritaja.kasutaja_id,
                       model.Testiosa.seq)
        prev_koht_id = None
        prev_test_id = None
        prev_sooritaja_id = None
        sooritused = list()
        saajad = set()
        sooritused2 = list()
        saaja_k = None
        for rcd in q.all():
            tos = rcd[0]
            if tos.on_erivajadused_kinnitatud:
                sooritaja = tos.sooritaja
                test_id = sooritaja.test_id
                koht_id = sooritaja.kool_koht_id

                # kiri sooritajale endale sooritaja enda andmetega
                if sooritaja.id != prev_sooritaja_id:
                    _send_sooritajale(sooritused2, saaja_k)
                    sooritused2 = list()
                    saaja_k = None
                    prev_sooritaja_id = sooritaja.id
                sooritused2.append(tos)
                saaja_k = sooritaja.kasutaja
                         
                # kiri kooli sooritajate kontaktisikutele kooli kõigi õppurite andmetega
                if test_id != prev_test_id or not koht_id or koht_id != prev_koht_id:
                    cnt += _send_kontakt(sooritused, saajad)
                    sooritused = list()
                    saajad = set()
                    prev_test_id = test_id
                    prev_koht_id = koht_id

                sooritused.append(tos)
                saajad.add(sooritaja.kontakt_epost)
                if sooritaja.esitaja_koht:
                    saajad.add(sooritaja.esitaja_koht.epost)

        _send_sooritajale(sooritused2, saaja_k)
        cnt += _send_kontakt(sooritused, saajad)
                
        buf = ''
        if cnt > 0:
            buf += _("Saadetud teated {n} erivajadustega soorituse kohta. ").format(n=cnt)
        else:
            buf = _("Pole teateid, mida saata.")
        
        self.notice(buf)
        model.Session.commit()
        
    def _prepare_items(self, q):
        c = self.c

        # tabeli päis
        header = [_("Isikukood"),
                  _("Eesnimi"),
                  _("Perekonnanimi"),
                  _("Soorituse tähis"),
                  _("Soorituskeel"),
                  _("Aine"),
                  _("Test"),
                  _("Toimumisaeg"),
                  _("Soorituskoht"),
                  _("Ruum"),
                  _("Õppimiskoht"),
                  ]
        if not c.xls:
            header.append(_("Erivajadused"))
        header.append(_("Kinnitatud"))
        if not c.hide_reviewed:
            header.append(_("Üle vaadatud"))
        header.append(_("Ül komplekt"))
        if c.xls:
            header.append(_("Vabastatud"))

        eri_koodid = set()

        # tabeli sisu
        items = []
        for rcd in q.all():
            row = self._prepare_row(rcd)
            items.append(row)

            if c.xls:
                # leiame sooritusele märgitud erivajadused ja paneme dicti
                tos = rcd[0]
                if tos.testiosa.test.testiliik_kood == const.TESTILIIK_POHIKOOL:
                    # bugzilla 170: põhikooli osas näidata kõiki taotletud eritingimusi
                    q = (model.SessionR.query(model.Erivajadus.erivajadus_kood,
                                             model.Erivajadus.taotlus_markus)
                         .filter_by(sooritus_id=tos.id)
                         .filter_by(taotlus=True))
                elif tos.on_erivajadused_kinnitatud:
                    q = (model.SessionR.query(model.Erivajadus.erivajadus_kood,
                                             model.Erivajadus.kinnitus_markus)
                         .filter_by(sooritus_id=tos.id)
                         .filter_by(kinnitus=True))
                else:
                    q = (model.SessionR.query(model.Erivajadus.erivajadus_kood,
                                             model.Erivajadus.taotlus_markus)
                         .filter_by(sooritus_id=tos.id)
                         .filter_by(taotlus=True))
                d_eri = dict()
                for kood, markus in q.all():
                    d_eri[kood] = markus or ''
                    eri_koodid.add(kood)
                row.append(d_eri)

        if c.xls:
            # leiame kõik erivajadused, mis on loetelus kasutusel
            # teeme igaühele eraldi olemasolu veeru ja märkuse veeru
            q = (model.SessionR.query(model.Klrida)
                 .filter(model.Klrida.klassifikaator_kood=='ERIVAJADUS')
                 .filter(model.Klrida.kood.in_(eri_koodid))
                 .order_by(model.Klrida.bitimask, model.Klrida.jrk))
            eri_koodid_sorted = list()
            for krcd in q.all():
                eri_koodid_sorted.append(krcd.kood)
                header.append(krcd.ctran.nimi)
                header.append(_("Märkused"))

            header.append(_("Üldised märkused"))

            for row in items:
                d_eri = row.pop(-1)
                for kood in eri_koodid_sorted:
                    markus = d_eri.get(kood)
                    row.append(markus is not None and _("Jah") or '')
                    row.append(markus or '')
                markus = d_eri.get(None)
                row.append(markus or '')
            
        return header, items

    def _prepare_row(self, rcd):
        "Tabeli ühe rea väljade kokkupanek"
        c = self.c
        h = self.h

        tos, lang, isikukood, synnikpv, eesnimi, perenimi, test_nimi, aine_kood, testiosa_nimi, koht_nimi, ruum_tahis, kool_koht_nimi, komplekt_tahis = rcd
        row = [isikukood or h.str_from_date(synnikpv),
               eesnimi,
               perenimi,
               tos.tahised,
               model.Klrida.get_lang_nimi(lang),
               model.Klrida.get_str('AINE', aine_kood),
               test_nimi,
               tos.toimumisaeg and tos.toimumisaeg.tahised or '',
               koht_nimi,
               ruum_tahis,
               kool_koht_nimi,
               ]
        if not c.xls:
            row.append(tos.get_str_erivajadused('<br/>'))
        row.append(h.sbool(tos.on_erivajadused_kinnitatud))
        if not c.hide_reviewed:
            row.append(h.sbool(tos.on_erivajadused_vaadatud))        
        row.append(komplekt_tahis)
        if c.xls:
            li = []
            if tos.staatus == const.S_STAATUS_VABASTATUD:
                li.append(tos.testiosa.nimi)
            for atos in tos.alatestisooritused:
                if atos.staatus == const.S_STAATUS_VABASTATUD:
                    li.append(atos.alatest.nimi)
            row.append(', '.join(li) or '')
        return row

    def _update(self, item):
        collection = []
        vabastatud_alatestid_id = self.form.data.get('vaba_alatest_id')
        oli_vabastatud = item.staatus == const.S_STAATUS_VABASTATUD
        on_vaadatud = self.form.data.get('on_erivajadused_vaadatud')
        on_tagasilykatud = self.form.data.get('decline')
        
        # testiosa vabastus
        if self.form.data.get('vaba_osa'):
            # kogu testiosast vabastatud
            item.staatus = const.S_STAATUS_VABASTATUD
            for alatest in item.alatestid:
                atos = item.give_alatestisooritus(alatest.id)
                atos.staatus = const.S_STAATUS_VABASTATUD
        else:          
            # alatestide vabastus
            for alatest in item.alatestid:
                on_vabastatud = alatest.id in vabastatud_alatestid_id
                atos = item.get_alatestisooritus(alatest.id)
                if atos and atos.staatus == const.S_STAATUS_VABASTATUD and not on_vabastatud:
                    # eemaldame vabastuse
                    atos.staatus = item.staatus
                elif on_vabastatud:
                    if not atos:
                        atos = item.give_alatestisooritus(alatest.id)
                    if atos.staatus != const.S_STAATUS_VABASTATUD:
                        atos.staatus = const.S_STAATUS_VABASTATUD

            if item.staatus == const.S_STAATUS_VABASTATUD:
                # võtame testiosa vabastuse maha
                item.staatus = item.sooritaja.staatus

            for rcd in self.form.data.get('ev'):
                if not rcd.get('erivajadus_kood'):
                    # üldine märkuste kirje
                    rcd['erivajadus_kood'] = None
                    rcd['taotlus'] = bool(rcd.get('taotlus_markus'))
                    rcd['kinnitus'] = bool(rcd.get('kinnitus_markus'))
                if on_tagasilykatud:
                    rcd['kinnitus'] = False
                if rcd.get('taotlus') or rcd.get('kinnitus'):
                    collection.append(rcd)

            BaseGridController(item.erivajadused, model.Erivajadus).save(collection)

        item.sooritaja.from_form(self.form.data, 'r_')
        model.Session.flush()
        item.set_erivajadused(None)

        if on_tagasilykatud:
            item.on_erivajadused_tagasilykatud = True
            item.on_erivajadused_vaadatud = item.on_erivajadused_kinnitatud = False
        else:
            item.on_erivajadused_tagasilykatud = False
            if on_vaadatud:
                item.on_erivajadused_vaadatud = True
            else:
                item.on_erivajadused_kinnitatud = True
                   
        if oli_vabastatud != item.staatus == const.S_STAATUS_VABASTATUD:
            testiruum = item.testiruum
            if testiruum:
                testiruum.set_sooritajate_arv()
