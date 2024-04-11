from itertools import groupby
from eis.lib.baseresource import *
from eis.handlers.ekk.otsingud.tulemusteteavitused import send_epost_sooritaja, send_epost_avaldet
import eis.lib.pdf as pdf
_ = i18n._
log = logging.getLogger(__name__)

class TulemusedController(BaseResourceController):
    """Tulemuste avaldamine
    """
    _permission = 'tulemusteavaldamine'
    _MODEL = model.Testimiskord
    _INDEX_TEMPLATE = 'ekk/muud/tulemused.mako'
    _LIST_TEMPLATE = 'ekk/muud/tulemused_list.mako'
    _DEFAULT_SORT = '-testimiskord.id' # vaikimisi sortimine
    _EDIT_TEMPLATE = 'ekk/muud/tulemus.avaldamine.mako'

    _index_after_create = True

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        # makos kasutamiseks
        c.get_count = self.get_count
        q = (q.join(model.Testimiskord.test)
             .filter(model.Test.testityyp==const.TESTITYYP_EKK)
             )

        c.opt_sessioon = c.opt.testsessioon
        if not c.sessioon_id and len(c.opt_sessioon):
            c.sessioon_id = c.opt_sessioon[0][0]

        if c.sessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==int(c.sessioon_id))
            self._get_protsessid()
        else:
            q = None
        return q

    def _get_korrad(self, korrad_id):
        li = []
        for kord_id in korrad_id:
            kord = model.Testimiskord.get(kord_id)
            li.append(kord)
        return li

    def _new_d(self):
        """Avaldamise muudatuste vormi avamine"""
        c = self.c
        params = self.request.params
        korrad_id = list(map(int, params.getall('kord_id')))
        c.korrad = self._get_korrad(korrad_id)
        c.sessioon_id = params.get('sessioon_id')
        c.list_url = params.get('list_url')
        c.koondtulemus_avaldet = all([k.koondtulemus_avaldet for k in c.korrad])
        c.alatestitulemused_avaldet = all([k.alatestitulemused_avaldet for k in c.korrad])
        c.ylesandetulemused_avaldet = all([k.ylesandetulemused_avaldet for k in c.korrad])
        c.aspektitulemused_avaldet = all([k.aspektitulemused_avaldet for k in c.korrad])                
        c.ylesanded_avaldet = all([k.ylesanded_avaldet for k in c.korrad])
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _create_avaldamine(self):
        """Avaldamise muudatuste vormil salvestamine"""
        params = self.request.params
        korrad_id = list(map(int, params.getall('kord_id')))
        korrad = self._get_korrad(korrad_id)
        mail_tahised = []
        for kord in korrad:
            midagi_avaldet = False
            for key in ('koondtulemus_avaldet',
                        'alatestitulemused_avaldet',
                        'ylesandetulemused_avaldet',
                        'aspektitulemused_avaldet',
                        'ylesanded_avaldet'):
                avaldet = bool(params.get(key))
                oli_avaldet = kord.__getattr__(key)
                if oli_avaldet != avaldet:
                    kord.__setattr__(key, avaldet)
                    if avaldet:
                        # sel testimiskorral midagi avaldati
                        midagi_avaldet = True
            if midagi_avaldet:
                # kas on selline testimiskord, millel avaldamise kohta on vaja teavitus saata? (ES-31)
                test = kord.test
                if test.testiliik_kood in (const.TESTILIIK_POHIKOOL,
                                           const.TESTILIIK_RIIGIEKSAM,
                                           const.TESTILIIK_RV,
                                           const.TESTILIIK_TASE):
                    if test.testiliik_kood != const.TESTILIIK_TASE or test.testiklass_kood == const.TESTIKLASS_3:
                        # tasemetööde korral saata teavitus ainult siis, kui on 3.klass
                        mail_tahised.append(kord.tahised)
                
        model.Session.commit()
        if mail_tahised:
            sessioon = model.Testsessioon.get(self.request.params.get('sessioon_id'))
            testiliik = sessioon.testiliik_kood
            send_epost_avaldet(self, mail_tahised, testiliik)
            
        self.success()
        return self._after_update(None)

    def _create(self):
        params = self.request.params
        op = params.get('op')
        if params.get('avaldamine'):
            return self._create_avaldamine()
        elif params.get('testkiri'):
            return self._send(const.TEATEKANAL_EPOST, True)
        elif op == 'epost':
            # sooritajate teavitamine
            return self._send(const.TEATEKANAL_EPOST)
        elif op == 'kool':
            # koolide teavitamine
            return self._send(const.TEATEKANAL_EPOST, kool=True)        
        
    def _send(self, teatekanal, testkiri=False, unknown=False, kool=False):
        """Teadete saatmine"""

        sessioon = model.Testsessioon.get(self.request.params.get('sessioon_id'))
        testiliik = sessioon.testiliik_kood

        korrad_id = list(map(int, self.request.params.getall('kord_id')))
        q = (model.Session.query(model.Testimiskord)
             .filter(model.Testimiskord.id.in_(korrad_id)))
        tahised = ', '.join([r.tahised for r in q.all()])
        kordus = self.request.params.get('kordusk') or False

        skanal = self.c.opt.TEATEKANAL.get(teatekanal)
        if kool:
            desc = _("Tulemuste teavituste saatmine koolidele {s}, {s2}").format(s=tahised, s2=skanal)
        else:
            desc = _("Tulemuste teavituste saatmine {s}, {s2}").format(s=tahised, s2=skanal)

        testaadress = None
        if testkiri:
            desc += ' (%s)' %  _("testkiri")
            testaadress = self.request.params.get('testaadress') 
            if not testaadress:
                self.error(_("Puudub testkirja aadress"))
                return self._after_update(None)
            
        params = {'liik': model.Arvutusprotsess.LIIK_M_TULEMUS,
                  'kirjeldus': desc,
                  'testimiskord_id': len(korrad_id) == 1 and korrad_id[0] or None,
                  'testsessioon_id': sessioon.id,
                  }
        childfunc = lambda protsess: self._send_childfunc(protsess, testiliik, teatekanal, kool, korrad_id, kordus, unknown, testaadress)
        model.Arvutusprotsess.start(self, params, childfunc)
        self.success(_("Saatmise protsess käivitatud"))
        return self._after_update(None)

    def _search_protsessid(self, q):
        sessioon_id = self.c.sessioon_id or self.request.params.get('sessioon_id')
        q = (q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_M_TULEMUS)
             .filter(model.Arvutusprotsess.testsessioon_id==sessioon_id)
             )
        return q
        
    def _send_childfunc(self, protsess, testiliik, teatekanal, kool, korrad_id, kordus, unknown, testaadress):
        error = None
        
        # andmete kogumine
        if kool:
            # koolide teated
            q = self._query_data_koolid(korrad_id, kordus)
            total = len(q)
        else:
            # sooritajate teated
            q = self._query_data(korrad_id, teatekanal, kordus, unknown)
            q = q.order_by(model.Sooritaja.kasutaja_id)
            total = q.count()
        
        if not total:
            if kool:
                error = _("Pole kedagi teavitada, kellel oleks õigus tulemusi vaadata")
            else:
                error = _("Pole sooritajaid, kellele kirju saata")
        if error:
            if protsess:
                protsess.set_viga(error)
            else:
                self.error(error)
            return
        if protsess:
            protsess.edenemisprotsent = 10
            model.Session.commit()
        
        # kirjade saatmine
        on_tseis = testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)
        if kool:
            items = q
            total = len(items)
        elif on_tseis:
            total = q.count()
            items = q.all()
        else:
            total = q.count()
            items = groupby(list(q.all()), lambda r: r[0])

        def itemfunc(r):
            if kool:
                # koolile teadete saatmine
                rc = send_epost_kool(self, r, testaadress)
                return rc
            
            if on_tseis:
                # on_tseis, teated sooritaja kaupa
                kasutaja_id, sooritaja_id = r
                sooritaja = model.Sooritaja.get(sooritaja_id)
                kasutaja = sooritaja.kasutaja
                sooritajad = None
            else:
                # riigieksamite tulemused, teated kasutaja kaupa
                (kasutaja_id), sooritajad_id = r
                sooritajad = [model.Sooritaja.get(r[1]) for r in sooritajad_id]
                kasutaja = model.Kasutaja.get(kasutaja_id)
                sooritaja = None

            if teatekanal == const.TEATEKANAL_EPOST:
                rc = send_epost_sooritaja(self,
                                          kasutaja,
                                          testaadress=testaadress,
                                          sooritaja=sooritaja,
                                          sooritajad=sooritajad)
            return rc
                                       
        if not protsess:
            for r in items:
                itemfunc(r)
                if testaadress:
                    break
        else:
            model.Arvutusprotsess.iter_mail(protsess, self, total, items, itemfunc)

    def _after_update(self, id):
        """Peale salvestamist tuuakse ette otsingu sama lehekülg, mis enne oli.
        """
        kw = {}
        list_url = self.request.params.get('list_url')
        if list_url:
            t = self.h.update_params(list_url, _debug=True, **kw)
            kw = t[1]

        kw['kord_id'] = self.request.params.getall('kord_id')
        return self._redirect('index', **kw)   

    def get_count(self, kord):
        """Mako kutsub seda välja, et arvutada iga testimiskorra kohta teavituse arvud
        """
        cnt_epost = self._query_data([kord.id], const.TEATEKANAL_EPOST).count()
        on_vaided = (model.Vaie.query
                     .join(model.Vaie.sooritaja)
                     .filter(model.Sooritaja.testimiskord_id==kord.id)
                     .count())
        return cnt_epost, on_vaided

    def _query_data(self, korrad_id, teatekanal, kordus=False, unknown=False):
        q = (model.Session.query(model.Sooritaja.kasutaja_id, model.Sooritaja.id)
             .filter(model.Sooritaja.hindamine_staatus == const.H_STAATUS_HINNATUD)
             .filter(model.Sooritaja.pallid != None)
             .join(model.Sooritaja.testimiskord)
             .filter(model.Testimiskord.koondtulemus_avaldet==True)
             .join(model.Sooritaja.kasutaja))
        if len(korrad_id) == 1:
            q = q.filter(model.Sooritaja.testimiskord_id==korrad_id[0])
        else:
            q = q.filter(model.Sooritaja.testimiskord_id.in_(korrad_id))

        if teatekanal == const.TEATEKANAL_EPOST:
            q = (q.filter(model.Sooritaja.teavitatud_epost==None)
                 .filter(model.Kasutaja.epost != None)
                 .filter(model.Kasutaja.epost != ''))

        return q

    def _query_data_koolid(self, korrad_id, kordus=False):
        "Koolide teate saajate päring"

        data = []
        for kord_id in korrad_id:
            tkord = model.Testimiskord.get(kord_id)
            if not tkord.koondtulemus_avaldet:
                continue
            test = tkord.test
            # leiame soorituskohad
            q = (model.SessionR.query(model.Testikoht.koht_id, model.Testikoht.id)
                 .distinct()
                 .join(model.Testikoht.toimumisaeg)
                 .filter(model.Toimumisaeg.testimiskord_id==kord_id)
                 .filter(model.Testikoht.sooritused.any(
                     model.Sooritus.staatus==const.S_STAATUS_TEHTUD))
                 .order_by(model.Testikoht.koht_id)
                 )

            tkohad = {}
            for koht_id, testikoht_id in q.all():
                if koht_id not in tkohad:
                    tkohad[koht_id] = []
                tkohad[koht_id].append(testikoht_id)
                
            for koht_id, koht_tkohad_id in tkohad.items():
                koht = model.Koht.get(koht_id)
                k_data = []
                if tkord.tulemus_koolile:
                    # leiame soorituskohtade adminid
                    for k in koht.get_admin():
                        if k.epost:
                            k_data.append((k.epost, k.id, None))
                if tkord.tulemus_admin:
                    # leiame testiadminid
                    q = (model.SessionR.query(model.Labiviija.id,
                                             model.Kasutaja)
                         .join(model.Labiviija.kasutaja)
                         .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN)
                         .filter(model.Labiviija.testikoht_id.in_(koht_tkohad_id))
                         )
                    if not kordus:
                        # saadame ainult neile, kes pole varem kirja saanud
                        q = q.filter(~ sa.exists().where(
                            sa.and_(model.Labiviijakiri.labiviija_id==model.Labiviija.id,
                                    model.Labiviijakiri.kiri_id==model.Kiri.id,
                                    model.Kiri.tyyp==model.Kiri.TYYP_KOOL_TULEMUS,
                                    model.Kiri.teatekanal==const.TEATEKANAL_EPOST)))
                    for lv_id, k in q.all():
                        if k.epost:
                            k_data.append((k.epost, k.id, lv_id))
                if k_data:
                    # on keegi, kellele saata
                    # vaatame, kui paljudel pole töö hinnatud
                    q = (model.SessionR.query(sa.func.count(model.Sooritaja.id))
                         .filter(model.Sooritaja.hindamine_staatus!=const.H_STAATUS_HINNATUD)
                         .filter(model.Sooritaja.testimiskord_id==kord_id)
                         .filter(model.Sooritaja.sooritused.any(
                             sa.and_(model.Sooritus.testikoht_id.in_(koht_tkohad_id),
                                     model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                                    ))
                         )
                    hindamata = q.scalar()
                    data.append((test.nimi, kord_id, koht.id, k_data, hindamata))
        return data

def send_epost_kool(handler, rcd, testaadress=None):
    "Koolile teadete saatmine"
    test_nimi, kord_id, koht_id, k_data, hindamata = rcd
    tkord = model.Testimiskord.get(kord_id)
    koht = model.Koht.get(koht_id)
    teatekanal = const.TEATEKANAL_EPOST
    pw_host = handler.request.registry.settings.get('eis.pw.url')
    url = '%s/eis/ktulemused/%s' % (pw_host, tkord.test_id)
    data = {'test_nimi': test_nimi,
            'koht_nimi': koht.nimi,
            'hindamata': hindamata,
            'tulemus_koolile': tkord.tulemus_koolile,
            'tulemus_admin': tkord.tulemus_admin,
            'tulemused_url': url,
            }
    mako = 'mail/tulemus_kool.mako'
    subject, body = handler.render_mail(mako, data)

    # saajate aadressid
    to = list(set([r[0] for r in k_data]))
    
    log.debug('Saadan kirja koolile %s aadressile %s' % (koht.nimi, ', '.join(to)))

    # saadame e-kirja
    err = Mailer(handler).send(to, subject, body, out_err=False)
    if err:
        buf = '%s (%s %s)' % (err, k.nimi, to)
        model.Arvutusprotsess.trace(buf)
        return False, err
    else:
        log.debug(_("Saadetud kiri aadressile {s}").format(s=to))

    if not testaadress:
        kiri = model.Kiri(saatja_kasutaja_id=handler.c.user.id,
                          tyyp=model.Kiri.TYYP_KOOL_TULEMUS,
                          sisu=body,
                          teema=subject,
                          teatekanal=teatekanal,
                          sisu_url=url)
        for epost, k_id, lv_id in k_data:
            if lv_id:
                model.Labiviijakiri(labiviija_id=lv_id, kiri=kiri)
            model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost, koht_id=koht.id)
        model.Session.commit()
    return True, None
