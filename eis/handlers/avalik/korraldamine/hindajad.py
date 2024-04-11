from eis.lib.baseresource import *
from eis.handlers.admin.ehisopetajad import opt_koolipedagoogid
from eis.handlers.ekk.korraldamine.koht.otsilabiviijad import (
    selgita_lv_sobimatust,
    paranda_lv_sobimatust
    )
from eis.handlers.ekk.otsingud.labiviijateated import send_labiviija_maaramine
_ = i18n._
log = logging.getLogger(__name__)

class HindajadController(BaseResourceController):
    _permission = 'avalikadmin'
    _MODEL = model.Labiviija
    _INDEX_TEMPLATE = '/avalik/korraldamine/hindajad.mako'
    _LIST_TEMPLATE = '/avalik/korraldamine/hindajad_list.mako'     
    _EDIT_TEMPLATE = '/avalik/korraldamine/hindaja.edit.mako'
    _DEFAULT_SORT = 'hindamiskogum.id'
    _UNIQUE_SORT = 'labiviija_1.id'
    _get_is_readonly = False
    _no_paginate = True

    def _query(self):
        testiosa_id = self.c.toimumisaeg.testiosa_id
        q = (model.Session.query(model.Hindamiskogum.id,
                                 model.Hindamiskogum.tahis)
             .filter(model.Hindamiskogum.testiosa_id==testiosa_id)
             .filter(model.Hindamiskogum.arvutihinnatav==False)
             )
        return q
    
    def _search_default(self, q):
        return self._search(q)

    def _query_hindajad(self, q):
        # tab1 päring, hindajate kaupa
        c = self.c

        self.Labiviija1 = sa.orm.aliased(model.Labiviija, name='labiviija1') # hindaja_1
        f_hindaja1 = sa.and_(self.Labiviija1.hindamiskogum_id==model.Hindamiskogum.id,
                             sa.or_(self.Labiviija1.liik==const.HINDAJA1,
                                    sa.and_(self.Labiviija1.liik==const.HINDAJA2,
                                            self.Labiviija1.hindaja1_id==None)),
                             self.Labiviija1.toimumisaeg_id==c.toimumisaeg.id,
                             self.Labiviija1.testikoht_id==c.testikoht.id)

        self.Labiviija2 = sa.orm.aliased(model.Labiviija, name='labiviija2') # hindaja_2
        f_hindaja2p = sa.and_(self.Labiviija2.hindamiskogum_id==model.Hindamiskogum.id,
                             self.Labiviija2.liik==const.HINDAJA2,
                             self.Labiviija2.toimumisaeg_id==c.toimumisaeg.id,
                             self.Labiviija2.testikoht_id==c.testikoht.id,
                             self.Labiviija2.hindaja1_id==self.Labiviija1.id)

        q = (q.with_entities(model.Hindamiskogum,
                             self.Labiviija1,
                             self.Labiviija2)
             .outerjoin((self.Labiviija1, f_hindaja1))
             .outerjoin((self.Labiviija2, f_hindaja2p))
             )

        # kuvame määramata hindajaga ridu ainult juhul, kui kool peab ise hindaja määrama
        if not self._koolis_maaratav(False) and not self._koolis_maaratav(True):
            # kool ei peaks saama määrata ei valimi ega mittevalimi sooritajaid
            # kuvame ainult neid ridu, kus läbiviija on juba olemas
            q = q.filter(sa.or_(self.Labiviija1.id!=None,
                                self.Labiviija2.id!=None))
        
        return q

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        testiosa = c.toimumisaeg.testiosa
        hkogumid = [r for r in testiosa.hindamiskogumid if r.staatus]
        c.paarishindamine = bool([r for r in hkogumid if r.paarishindamine])
        c.hindamiskogumid_opt = [(r.id, r.tahis) for r in hkogumid \
                                 if not r.arvutihinnatav]
        if c.tab2 != 'tab2':
            # hindajate kaupa
            q = self._query_hindajad(q)
            
        hindamiskogum_id = None
        if c.hindamiskogum_id:
            hindamiskogum_id = int(c.hindamiskogum_id)
            q = q.filter(model.Hindamiskogum.id==hindamiskogum_id)

        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item
        c.prepare_item_hk = self._prepare_item_hk

        return q

    def _paginate(self, q):
        c = self.c
        if c.tab2 != 'tab2':
            # hindajate kaupa
            return q.all()
        else:
            # hindamiskogumite kaupa
            items = []
            sisaldab_valimit = c.testimiskord.sisaldab_valimit
            kmdata = {}
            for rcd in q.all():
                for valimis in (sisaldab_valimit and (False, True) or (False,)):
                    try:
                        rc = kmdata[valimis]
                    except KeyError:
                        # pole veel kontrollitud
                        rc = kmdata[valimis] = self._koolis_maaratav(valimis)
                    if rc:
                        item = self._prepare_item_hk(rcd, True, valimis)
                        items.append(item)
            return items

    def _koolis_maaratav(self, valimis):
        "Kas kool määrab hindajaid"
        c = self.c
        if c.toimumisaeg.koolis_hindamine(valimis):
            # kool määrab oma õpilaste hindajaid
            # kas õpilasi on?
            q = (model.Session.query(model.Sooritaja.id)
                 .join(model.Sooritaja.sooritused)
                 .filter(model.Sooritus.testikoht_id==c.testikoht.id)
                 .filter(model.Sooritaja.valimis==valimis)
                 )
            if q.first():
                return True
        if c.toimumisaeg.muu_koha_hindamine(valimis):
            # kool määrab muude koolide õpilaste hindajaid
            return True
        return False 

    def _order_field(self, q, is_desc, field):
        return BaseResourceController._order_field(self, q, is_desc, 'anon1_' + field)

    def _prepare_header(self):
        c = self.c
        if c.tab2 == 'tab2':
            # hindamiskogumite kaupa
            return self._prepare_header_hk()

        # hindajate kaupa
        header = [('kasutaja1.isikukood', _("Hindaja"), 'isikukood'),
                  ('labiviija1.hinnatud_toode_arv', _("Lõpetatud hindamisi"), 'hinnatud'),
                  (None, _("Peatatud hindamisi"), 'pooleli'),
                  ]
        if c.paarishindamine:
            header.extend([('kasutaja2.isikukood', _("Paariline"), 'paariline'),
                           ('labiviija2.hinnatud_toode_arv', _("Lõpetatud hindamisi"), 'hinnatud2'),
                           (None, _("Peatatud hindamisi"), 'pooleli2'),
                           ])
        header.extend([(None, _("Keel"), 'keel'),
                       (None, _("Klass"), 'klass'),
                       (None, _("Max tööde arv"), 'maxtoodearv'),
                       (None, _("Olek"), 'olek'),
                       ('hindamiskogum.nimi', _("Hindamiskogum"), 'hindamiskogum'),                       
                       ])
        if c.testimiskord.sisaldab_valimit:
            header.append((None, _("Valim"), 'valim'))
        return header

    def _prepare_header_hk(self):
        # hindajate kaupa
        header = [(None, _("Hindamiskogum"), 'hindamiskogum'),
                  (None, _("Hindajate arv"), 'hindajatearv'),
                  (None, _("Arvutihinnatud"), 'arvutihinnatud'),
                  ]
        if self.c.paarishindamine:
            header.extend([(None, _("Hindamine alustamata"), 'alustamata'),
                           (None, _("Hindamine pooleli"), 'pooleli'),
                           (None, _("Hinnatud käsitsi"), 'hinnatud'),
                           (None, _("2. hindamine alustamata"), 'alustamata2'),
                           (None, _("2. hindamine pooleli"), 'pooleli2'),
                           (None, _("2. hinnatud käsitsi"), 'hinnatud2'),
                           ])
        else:
            header.extend([(None, _("Hindamine alustamata"), 'alustamata'),
                           (None, _("Hindamine pooleli"), 'pooleli'),
                           (None, _("Hinnatud käsitsi"), 'hinnatud'),
                           ])
        if self.c.testimiskord.sisaldab_valimit:
            header.append((None, _("Valim"), 'valim'))
            
        return header

    def _prepare_item(self, rcd, on_html=False):
        c = self.c
        hk, hindaja1, hindaja2 = rcd
        hkasutaja1 = hindaja1 and hindaja1.kasutaja
        hkasutaja2 = hindaja2 and hindaja2.kasutaja
        hindaja = hindaja1 or hindaja2

        if hkasutaja1:
            h1_nimi = hkasutaja1.nimi
        else:
            h1_nimi = _("Määramata")
        if hindaja1:
            h1_hinnatud = hindaja1.hinnatud_toode_arv or 0
            h1_peatatud = (hindaja1.toode_arv or 0) - (hindaja1.hinnatud_toode_arv or 0)
            #h1_nimi += ' (%s)' % hindaja1.kasutajagrupp_nimi
        else:
            h1_hinnatud = h1_peatatud = ''
        item = [h1_nimi,
                h1_hinnatud,
                h1_peatatud]

        if self.c.paarishindamine:
            valimis = hindaja and hindaja.valimis
            if hkasutaja2:
                h2_nimi = hkasutaja2.nimi
            elif not hk.paarishindamine:
                h2_nimi = ''
            elif valimis and not hk.kahekordne_hindamine_valim:
                h2_nimi = ''
            elif not valimis and not hk.kahekordne_hindamine:
                h2_nimi = ''
            else:
                h2_nimi = _("Määramata")
            if hindaja2:
                h2_hinnatud = hindaja2.hinnatud_toode_arv or 0
                h2_peatatud = (hindaja2.toode_arv or 0) - (hindaja2.hinnatud_toode_arv or 0)
            else:
                h2_hinnatud = h2_peatatud = ''
            item.extend([h2_nimi,
                         h2_hinnatud,
                         h2_peatatud])

        klassid = ''
        if hindaja:
            li_kl = []
            for r in hindaja.labiviijaklassid:
                if r.klass:
                    buf = f"{r.klass}{r.paralleel or ''}"
                else:
                    buf = _("määramata")
                li_kl.append(buf)
            if li_kl:
                klassid = ', '.join(li_kl)
            
        item.extend([hindaja and model.Klrida.get_lang_nimi(hindaja.lang) or '',
                     klassid,
                     hindaja and hindaja.planeeritud_toode_arv or '',
                     hindaja and hindaja.staatus_nimi or '',
                     hk.tahis])
        if c.testimiskord.sisaldab_valimit:
            item.append(hindaja and hindaja.valimis and _("Valim") or '')
        return item

    def _prepare_item_hk(self, rcd, on_html, valimis):
        c = self.c
        hk_id, hk_tahis = rcd

        # määratud hindajate arv
        q = (model.Session.query(sa.func.count(model.Labiviija.id))
             .filter(model.Labiviija.testikoht_id==c.testikoht.id)
             .filter(model.Labiviija.hindamiskogum_id==hk_id)
             .filter(model.Labiviija.valimis==valimis)
             )
        hindajate_arv = q.scalar()

        # tööde arvud
        q = (model.Session.query(sa.func.count(model.Hindamisolek.id))
             .filter(model.Hindamisolek.hindamiskogum_id==hk_id)
             .join(model.Hindamisolek.sooritus)
             .filter(model.Sooritus.toimumisaeg_id==c.toimumisaeg.id)
             .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritaja.valimis==valimis)
             )
        if not c.toimumisaeg.muu_koha_hindamine(valimis):
            q1 = q.filter(model.Sooritus.testikoht_id==c.testikoht.id)
        else:
            q1 = q.filter(model.Sooritus.testikoht_id!=c.testikoht.id)

        # arvutihinnatud tööde arv
        q2 = (q1.filter(model.Hindamisolek.hindamistase==const.HTASE_ARVUTI)
              .filter(model.Hindamisolek.mittekasitsi==True)
              .filter(model.Hindamisolek.staatus==const.H_STAATUS_HINNATUD))
        arvuti = q2.scalar()


        item = [hk_tahis,
                hindajate_arv,
                arvuti]

        # I ja II hindamine
        f_h = sa.and_(model.Hindamisolek.id==model.Hindamine.hindamisolek_id,
                      model.Hindamine.labiviija_id==model.Labiviija.id,
                      model.Hindamine.staatus!=const.H_STAATUS_LYKATUD,
                      model.Labiviija.valimis==valimis,
                      model.Labiviija.testikoht_id==c.testikoht.id)

        for liik in (const.HINDAJA1, const.HINDAJA2):
            # alustamata hindamiste arv
            q2 = (q1.filter(model.Hindamisolek.mittekasitsi==False)
                  .filter(model.Hindamisolek.staatus != const.H_STAATUS_HINNATUD)
                  .filter(~ sa.exists()
                          .where(f_h)
                          .where(model.Hindamine.liik==liik)
                          .where(model.Hindamine.staatus.in_((const.H_STAATUS_POOLELI,
                                                              const.H_STAATUS_HINNATUD))
                                 ))
                  )
            alustamata = q2.scalar()

            # hindamine pooleli
            q2 = (q1.filter(model.Hindamisolek.mittekasitsi==False)
                  .filter(sa.exists()
                          .where(f_h)                          
                          .where(model.Hindamine.liik==liik)
                          .where(model.Hindamine.staatus==const.H_STAATUS_POOLELI)
                          ))
            pooleli = q2.scalar()
            #if hk_tahis == '5.2':  model.log_query(q2)
            # hinnatud
            q2 = (q1.filter(model.Hindamisolek.mittekasitsi==False)
                  .filter(sa.exists()
                          .where(f_h)                          
                          .where(model.Hindamine.liik==liik)
                          .where(model.Hindamine.staatus==const.H_STAATUS_HINNATUD)
                          ))
            hinnatud = q2.scalar()
            item.extend([alustamata,
                         pooleli,
                         hinnatud])
            if c.testimiskord.sisaldab_valimit:
                item.append(valimis and _("Valim") or '')
            if not c.paarishindamine:
                break
        
        return item

    def new(self, format='html'):
        """Dialoogiakna avamine uue hindaja lisamise alustamiseks: valitakse hindamiskogum
        """
        if self.request.params.get('sub') == 'kontroll':
            return self._new_kontroll()
        self.c.valimis = self.request.params.get('valimis') and True or False
        return self.render_to_response('/avalik/korraldamine/hindajad.otsikogum.mako')

    def _index_otsihindaja(self, sobita=None):
        """Hindamiskogum on valitud, kuvame hindaja otsimise vormi, kuvame hindajad
        """
        c = self.c
        params = self.request.params
        reuse = params.get('reuse')
        # profiili sobitamise päringus on meetod POST, tavalises otsingus GET
        method = sobita and 'POST' or 'GET'
        self._sub_params_into_c(sub='otsihindaja', reuse=reuse, method=method)

        c.hk_id = params.getall('hk_id')
        hindamiskogumid_id = params.get('hindamiskogumid_id')
        if not c.hk_id and hindamiskogumid_id:
            c.hk_id = hindamiskogumid_id.split(',')
        c.valimis = self.request.params.get('valimis') and True or False
        if not c.lang:
            # kui tuldi määramata isikuga hindaja realt ja keelt veel pole
            opt_k = c.toimumisaeg.testimiskord.opt_keeled
            if not c.toimumisaeg.muu_koha_hindamine(c.valimis):
                # leiame minu soorituskohas kasutusel olevad keeled
                dik = c.toimumisaeg.get_sooritajatearvud(c.testikoht.id, valimis=c.valimis)
                opt_k = [r for r in opt_k if dik.get(r[0])]
            if len(opt_k) == 1:
                # ainult 1 keel ongi
                c.lang = opt_k[0][0]
            if not c.lang:
                # suuname keelt valima
                return self._redirect('new', hk_id=c.hk_id)
           
        for hindamiskogum_id in c.hk_id:
            hindamiskogum = model.Hindamiskogum.get(hindamiskogum_id)

            # kas kool saab valida mõlemat hindajat ja need pole paaris
            if c.valimis:
                c.paarishindamine = hindamiskogum.kahekordne_hindamine_valim and \
                                    hindamiskogum.paarishindamine
                c.vali1v2 = hindamiskogum.kahekordne_hindamine_valim and \
                            not hindamiskogum.paarishindamine and \
                            c.toimumisaeg.hindaja1_maaraja_valim in const.MAARAJA_KOHAD and \
                            c.toimumisaeg.hindaja2_maaraja_valim in const.MAARAJA_KOHAD
            else:
                c.paarishindamine = hindamiskogum.kahekordne_hindamine and \
                                    hindamiskogum.paarishindamine
                c.vali1v2 = hindamiskogum.kahekordne_hindamine and \
                            not hindamiskogum.paarishindamine and \
                            c.toimumisaeg.hindaja1_maaraja in const.MAARAJA_KOHAD and \
                            c.toimumisaeg.hindaja2_maaraja in const.MAARAJA_KOHAD
            break

        testiosa = self.c.toimumisaeg.testiosa
        if testiosa.vastvorm_kood in (const.VASTVORM_SP, const.VASTVORM_SH):
            grupp_id = const.GRUPP_HINDAJA_S
        else:
            grupp_id = const.GRUPP_HINDAJA_K

        c.opt_kasutaja = c.testikoht.get_labiviijad_opt(grupp_id, on_kasutamata=False, lang=c.lang)
        c.opt_opetaja = opt_koolipedagoogid(self, c.user.koht_id)

        c.klassid, c.sooritajate_arv = self._get_klassid(c.lang, c.hk_id, c.valimis)

        c.kasutaja1, c.error1, c.muuda_profiil1 = self._find_hindaja(c.isikukood1, c.hkasutaja1_id, c.opetaja1_id)
    
        if c.paarishindamine:
            c.kasutaja2, c.error2, c.muuda_profiil2 = self._find_hindaja(c.isikukood2, c.hkasutaja2_id, c.opetaja2_id)
            if c.kasutaja2 and c.kasutaja2 == c.kasutaja1:
                c.kasutaja2 = None
                c.error2 = _("Sama isik ei või samas paaris olla I ja II hindaja korraga.")
        return self.render_to_response('/avalik/korraldamine/hindajad.otsihindaja.mako')

    def _find_hindaja(self, isikukood, kasutaja_id, pedagoog_id):
        error = kasutaja = None
        if kasutaja_id:
            kasutaja = model.Kasutaja.get(kasutaja_id)
            if not kasutaja:
                error = _("Kasutajat ei leitud")
        elif pedagoog_id:
            pedagoog = model.Pedagoog.get(pedagoog_id)
            kasutaja = model.Kasutaja.get_by_ik(pedagoog.isikukood)
            if not kasutaja:
                kasutaja = model.Kasutaja.add_kasutaja(pedagoog.isikukood,
                                                       pedagoog.eesnimi,
                                                       pedagoog.perenimi)
                model.Session.commit()
        elif isikukood:
            kasutaja = eis.forms.validators.IsikukoodP(isikukood).get(model.Kasutaja)
            if not kasutaja:
                error = _("Sellise isikukoodiga kasutajat ei leitud")

        if kasutaja:
            koht = self.c.testikoht.koht
            testiosa = self.c.toimumisaeg.testiosa
            if testiosa.vastvorm_kood in (const.VASTVORM_SP, const.VASTVORM_SH):
                grupp_id = const.GRUPP_HINDAJA_S
            else:
                grupp_id = const.GRUPP_HINDAJA_K
            viga_profiilis, errors = \
                selgita_lv_sobimatust(self,
                                      kasutaja,
                                      self.c.toimumisaeg,
                                      koht,
                                      grupp_id,
                                      lang=self.c.lang)
            if errors:
                if grupp_id == const.GRUPP_HINDAJA_S:
                    error = _("{s} profiil ei luba tal olla selle testi suuline hindaja.").format(s=kasutaja.nimi)
                else:
                    error = _("{s} profiil ei luba tal olla selle testi kirjalik hindaja.").format(s=kasutaja.nimi)
                errors.insert(0, error)
                msg = ' '.join(errors)
                return kasutaja, msg, True
            else:
                return kasutaja, None, None
        return None, error, None

    def _new_kontroll(self):
        "Kontrollitakse, kas kõigile klassidele on hindaja määratud"
        c = self.c
        errors = []
        sisaldab_valimit = c.testimiskord.sisaldab_valimit
        v_values = sisaldab_valimit and [False, True] or [False]
        for valimis in v_values:
            if c.toimumisaeg.koolis_hindamine(valimis):
                for hk in c.toimumisaeg.testiosa.hindamiskogumid:
                    # vaatame läbi kõik kehtivad hindamiskogumid
                    if hk.staatus != const.B_STAATUS_KEHTIV or hk.arvutihinnatav:
                        continue
                    # leiame hindamiskogumi sooritajate arvu klasside ja keelte lõikes
                    q = (model.Session.query(model.Sooritaja.klass,
                                             model.Sooritaja.paralleel,
                                             model.Sooritaja.lang,
                                             sa.func.count(model.Sooritus.id))
                         .join(model.Sooritaja.sooritused)
                         .filter(model.Sooritus.testikoht_id==c.testikoht.id)
                         .outerjoin((model.Hindamisolek,
                                     sa.and_(model.Hindamisolek.sooritus_id==model.Sooritus.id,
                                             model.Hindamisolek.hindamiskogum_id==hk.id)
                                     ))
                         .filter(sa.or_(model.Hindamisolek.mittekasitsi==False,
                                        model.Hindamisolek.id==None))
                         .filter(model.Sooritaja.valimis==valimis)
                         .group_by(model.Sooritaja.klass,
                                   model.Sooritaja.paralleel,
                                   model.Sooritaja.lang)
                         .order_by(model.Sooritaja.klass,
                                   model.Sooritaja.paralleel,
                                   model.Sooritaja.lang)
                         )
                    # planeeritud tööde arvu päring
                    qp = (model.Session.query(model.Labiviija.planeeritud_toode_arv)
                          .filter(model.Labiviija.testikoht_id==c.testikoht.id)
                          .filter(model.Labiviija.hindamiskogum_id==hk.id)
                          .filter(model.Labiviija.valimis==valimis)
                          .filter(model.Labiviija.kasutaja_id!=None)
                          )
                    on_moni_sooritaja = on_moni_piisav = False
                    pole_maaratud = []
                    vahe_maaratud = []
                    keeled = {}
                    hk_pl_arv = hk_toode_arv = 0
                    for klass, paralleel, lang, cnt in q.all():
                        #log.debug(f'{hk.id} valimis={valimis} sooritajad: {klass}{paralleel} {lang} - {cnt} tk')
                        if lang in keeled:
                            keeled[lang] += cnt
                        else:
                            keeled[lang] = cnt

                        hk_toode_arv += cnt
                        # kas selle klassi jaoks on piisavalt hindajaid?
                        q1 = (qp.filter(model.Labiviija.lang==lang)
                              .filter(sa.or_(
                                  ~ model.Labiviija.labiviijaklassid.any(),
                                  model.Labiviija.labiviijaklassid.any(
                                      sa.and_(model.Labiviijaklass.klass==klass,
                                              model.Labiviijaklass.paralleel==paralleel)
                                      )
                                  ))
                              )
                        klass_pl_arv = 0
                        for t_arv, in q1.all():
                            #log.debug(f'  lv {t_arv}')
                            if t_arv is not None:
                                klass_pl_arv += t_arv
                            else:
                                hk_pl_arv = klass_pl_arv = None
                                break
                        if hk_pl_arv is not None and klass_pl_arv is not None:
                            hk_pl_arv += klass_pl_arv
                        if klass_pl_arv is None or klass_pl_arv >= cnt:
                            # on piisavalt määratud
                            on_moni_piisav = True
                        elif klass_pl_arv == 0:
                            # ei ole määratud
                            pole_maaratud.append((klass, paralleel, lang))
                        else:
                            # ei ole piisavalt palju määratud
                            vahe_maaratud.append((klass, paralleel, lang))

                    if hk_toode_arv:
                        #log.debug(f'{hk.id} valimis={valimis} lang={lang} arv={hk_toode_arv} plan={hk_pl_arv}')

                        # leidub sooritajaid
                        if pole_maaratud:
                            if not on_moni_piisav and not vahe_maaratud:
                                # pole yheski klassis määratud
                                if not sisaldab_valimit:
                                    error = _("Hindamiskogumi {s1} hindajaid pole määratud.").format(s1=hk.tahis)
                                elif valimis:
                                    error = _("Hindamiskogumi {s1} valimi hindajaid pole määratud.").format(s1=hk.tahis)
                                else:
                                    error = _("Hindamiskogumi {s1} mitte-valimi hindajaid pole määratud.").format(s1=hk.tahis)
                            else:
                                li = []
                                for klass, paralleel, lang in pole_maaratud:
                                    if not klass:
                                        buf = '"%s"' % _("määramata")
                                    else:
                                        buf = '%s%s' % (klass, paralleel or '')
                                    if len(keeled) > 1:
                                        buf += ' (%s)' % model.Klrida.get_lang_nimi(lang)
                                    li.append(buf)
                                if not sisaldab_valimit:
                                    error = _("Hindamiskogumi {s1} hindajaid pole määratud klassile {s2}.").format(s1=hk.tahis, s2=', '.join(li))
                                elif valimis:
                                    error = _("Hindamiskogumi {s1} valimi hindajaid pole määratud klassile {s2}.").format(s1=hk.tahis, s2=', '.join(li))
                                else:
                                    error = _("Hindamiskogumi {s1} hindajaid pole määratud klassile {s2}.").format(s1=hk.tahis, s2=', '.join(li))
                            errors.append(error)

                        if vahe_maaratud:
                            if not on_moni_piisav and not pole_maaratud:
                                # pole yheski klassis määratud
                                if not sisaldab_valimit:
                                    error = _("Hindamiskogumi {s1} hindajatele planeeritud tööde arv pole piisav.").format(s1=hk.tahis)
                                elif valimis:
                                    error = _("Hindamiskogumi {s1} valimi hindajatele planeeritud tööde arv pole piisav.").format(s1=hk.tahis)
                                else:
                                    error = _("Hindamiskogumi {s1} mitte-valimi hindajatele planeeritud tööde arv pole piisav.").format(s1=hk.tahis)
                            else:
                                li = []
                                for klass, paralleel, lang in vahe_maaratud:
                                    if not klass:
                                        buf = '"%s"' % _("määramata")
                                    else:
                                        buf = '%s%s' % (klass, paralleel or '')
                                    if len(keeled) > 1:
                                        buf += ' (%s)' % model.Klrida.get_lang_nimi(lang)
                                    li.append(buf)
                                if not sisaldab_valimit:
                                    error = _("Hindamiskogumi {s1} hindajate planeeritud tööde arv pole piisav klassi {s2} hindamiseks.").format(s1=hk.tahis, s2=', '.join(li))
                                elif valimis:
                                    error = _("Hindamiskogumi {s1} valimi hindajate planeeritud tööde arv pole piisav klassi {s2} hindamiseks.").format(s1=hk.tahis, s2=', '.join(li))
                                else:
                                    error = _("Hindamiskogumi {s1} mitte-valimi hindajate planeeritud tööde arv pole piisav klassi {s2} hindamiseks.").format(s1=hk.tahis, s2=', '.join(li))
                            errors.append(error)

                        if not pole_maaratud:
                            for lang, lang_cnt in keeled.items():
                                pl_arv = 0
                                q2 = qp.filter(model.Labiviija.lang==lang)
                                for t_arv, in q2.all():
                                    if t_arv is not None:
                                        pl_arv += t_arv
                                    else:
                                        pl_arv = None
                                        break
                                if pl_arv is not None and pl_arv < lang_cnt:
                                    s1 = hk.tahis
                                    if len(keeled) > 1:
                                        s1 += " ({lang})".format(lang=model.Klrida.get_lang_nimi(lang))
                                    if not sisaldab_valimit:
                                        error = _("Hindamiskogumi {s1} hindajatele on planeeritud liiga vähe töid (planeeritud on {n1}, sooritajaid on {n2}).")
                                    elif valimis:
                                        error = _("Hindamiskogumi {s1} valimi hindajatele on planeeritud liiga vähe töid (planeeritud on {n1}, sooritajaid on {n2}).")
                                    else:
                                        error = _("Hindamiskogumi {s1} mitte-valimi hindajatele on planeeritud liiga vähe töid (planeeritud on {n1}, sooritajaid on {n2}).")
                                    error = error.format(s1=s1, n1=pl_arv, n2=lang_cnt)
                                    errors.append(error)
                                    
                        # avastamata jäävad need juhtumid,
                        # kus mitme klassi peale kokku on planeeritud liiga vähe töid,
                        # näiteks kui sooritajaid on 10A - 3 tk, 10B - 3 tk, 10C - 3 tk
                        # planeeritud hindaja X 10A+10B - 3 tööd, hindaja Y 10C - 6 tööd
                        # või
                        # planeeritud hindaja X 10A+10B - 5 tööd, hindaja Y 10B+10C - 5 tööd
                        # ja X hindab ära kõik 10 B klassis olevad 3 tööd,
                        # mistõttu 10 A planeeritud liiga vähe,
                        # aga 10C planeeritud liiga palju

        buf = ''
        for error in errors:
            buf += f'<p>{error}</p>'
        if not errors:
            buf = _("Esmapilgul paistab, et kõik hindajad on määratud!")
        return Response(buf)

    def _get_klassid(self, lang, li_hk_id, valimis):
        # leitakse sooritajate arvud klasside kaupa
        c = self.c
        klassid = []
        sooritajate_arv = 0
        if not c.toimumisaeg.muu_koha_hindamine(valimis):
            # hinnatakse oma kooli sooritajaid
            q = (model.Session.query(model.Sooritaja.klass, model.Sooritaja.paralleel, sa.func.count(model.Sooritus.id))
                 .join(model.Sooritaja.sooritused)
                 .filter(model.Sooritus.testikoht_id==c.testikoht.id)
                 .filter(model.Sooritus.staatus<=const.S_STAATUS_TEHTUD)
                 .filter(model.Sooritaja.lang==lang)
                 .filter(model.Sooritaja.valimis==valimis)
                 .outerjoin((model.Hindamisolek,
                             sa.and_(model.Hindamisolek.sooritus_id==model.Sooritus.id,
                                     model.Hindamisolek.hindamiskogum_id.in_(li_hk_id))))
                 .filter(sa.or_(model.Hindamisolek.mittekasitsi==False,
                                model.Hindamisolek.id==None))
                 .group_by(model.Sooritaja.klass, model.Sooritaja.paralleel)
                 .order_by(model.Sooritaja.klass, model.Sooritaja.paralleel)
                 )
            #model.log_query(q)
            log.debug(q.count())
            for klass, paralleel, cnt in q.all():
                klassid.append((klass or '', paralleel or '', cnt))
                sooritajate_arv += cnt
        return klassid, sooritajate_arv

    def _get_param_klassid(self):
        # postitatud andmetest leitakse klasside jada
        klass = self.request.params.getall('klass')
        klassid_arv =  int(self.request.params.get('klassid_arv') or 0)
        klassid = []
        not_all = len(klass) < klassid_arv
        if not_all:
            for _klass in klass:
                k, p = _klass.split('-', 1)
                klassid.append((k or None, p or None))

        try:
            planeeritud_toode_arv = int(self.request.params.get('planeeritud_toode_arv'))
        except:
            planeeritud_toode_arv = None
        return klassid, planeeritud_toode_arv      

    def _create_otsihindaja(self):
        """Labiviija on valitud, salvestame uue hindaja
        """
        c = self.c
        params = self.request.params
        if params.get('sobita'):
            # isiku profiil tehakse sobivaks ja siis uuesti otsingusse
            return self._create_sobita()
        
        hk_id = params.getall('hk_id')
        valimis = params.get('valimis') and True or False
        lang = self.params_lang()
        vali2 = params.get('vali2')
        kasutaja1_id = params.get('kasutaja1_id') 
        kasutaja2_id = params.get('kasutaja2_id') 
        ta = self.c.toimumisaeg
        
        # mis klassi hindab
        klassid, planeeritud_toode_arv = self._get_param_klassid()        
        # läbiviijate kirjed hiljem sõnumite saatmiseks
        m_labiviijad = []

        testiosa = c.toimumisaeg.testiosa
        on_suuline = testiosa.vastvorm_kood in (const.VASTVORM_SP, const.VASTVORM_SH)

        if kasutaja1_id:
            kasutaja1 = model.Kasutaja.get(kasutaja1_id)
            if not kasutaja1:
                self.error(_("Hindaja valimata"))
                return self._redirect('index')
            kasutaja2 = kasutaja2_id and model.Kasutaja.get(kasutaja2_id) or None

            for hindamiskogum_id in hk_id:
                hindamiskogum = model.Hindamiskogum.get(hindamiskogum_id)
                if valimis:
                    voib2 = ta.hindaja1_maaraja_valim not in const.MAARAJA_KOHAD and \
                            ta.hindaja2_maaraja_valim in const.MAARAJA_KOHAD
                    voib1 = ta.hindaja1_maaraja_valim in const.MAARAJA_KOHAD
                else:
                    voib2 = ta.hindaja1_maaraja not in const.MAARAJA_KOHAD and \
                            ta.hindaja2_maaraja in const.MAARAJA_KOHAD
                    voib1 = ta.hindaja1_maaraja in const.MAARAJA_KOHAD

                # enamasti lisatakse I hindajat
                # II hindajat saab lisada siis, kui kohal on II hindaja määramise õigus,
                # aga pole I hindaja määramise õigust
                if valimis:
                    kkh = hindamiskogum.kahekordne_hindamine_valim
                else:
                    kkh = hindamiskogum.kahekordne_hindamine
                if kkh and not hindamiskogum.paarishindamine and voib2:
                    liik = const.HINDAJA2
                elif vali2:
                    liik = const.HINDAJA2
                elif voib1:
                    liik = const.HINDAJA1
                else:
                    self.error(_("Toimumisaja seaded ei luba koolil I hindajat määrata"))
                    break
                mkh = ta.muu_koha_hindamine(valimis, liik)
                
                if not (kkh and hindamiskogum.paarishindamine):
                    q = (model.Labiviija.query
                         .filter_by(toimumisaeg_id=self.c.toimumisaeg.id)
                         .filter_by(hindamiskogum_id=hindamiskogum_id)
                         .filter_by(lang=lang)
                         .filter_by(liik=liik)
                         .filter_by(valimis=valimis)
                         .filter_by(testikoht_id=self.c.testikoht.id)
                         .filter_by(kasutaja_id=kasutaja1.id)
                         )
                    if q.count() > 0:
                        self.error('Isik on juba hindajaks lisatud')
                        continue

                if not on_suuline:
                    grupp_id = const.GRUPP_HINDAJA_K
                elif liik == const.HINDAJA2:
                    grupp_id = const.GRUPP_HINDAJA_S2
                else:
                    grupp_id = const.GRUPP_HINDAJA_S
                rcd1 = model.Labiviija(toimumisaeg=self.c.toimumisaeg,
                                       hindamiskogum_id=hindamiskogum_id,
                                       lang=lang,
                                       kasutajagrupp_id=grupp_id,
                                       liik=liik,
                                       testikoht_id=self.c.testikoht.id,
                                       planeeritud_toode_arv=None,
                                       toode_arv=0,
                                       valimis=valimis,
                                       muu_koha_hindamine=mkh,
                                       hinnatud_toode_arv=0,
                                       tasu_toode_arv=0)                            
                                       
                rcd1.set_kasutaja(kasutaja1, ta)
                rcd1.planeeritud_toode_arv = planeeritud_toode_arv
                rcd1.set_klassid(klassid)

                rcd2 = None
                if kkh and hindamiskogum.paarishindamine:
                    # kahekordne hindamine paaris (ainult kirjalikus testis)
                    if kasutaja2_id == kasutaja1_id:
                        self.error(_("Hindajad peavad erinema"))
                        return self._redirect('index')

                    if not kasutaja2:
                        self.error(_("Teine hindaja valimata"))
                        return self._redirect('index')

                    rcd2 = model.Labiviija(toimumisaeg=self.c.toimumisaeg,
                                           hindamiskogum_id=hindamiskogum_id,
                                           lang=lang,
                                           kasutajagrupp_id=grupp_id,
                                           hindaja1=rcd1,
                                           liik=const.HINDAJA2,
                                           testikoht_id=self.c.testikoht.id,
                                           planeeritud_toode_arv=None,
                                           toode_arv=0,
                                           valimis=valimis,
                                           muu_koha_hindamine=mkh,
                                           hinnatud_toode_arv=0,
                                           tasu_toode_arv=0)                            
                    
                    rcd2.set_kasutaja(kasutaja2, ta)
                    rcd2.planeeritud_toode_arv = planeeritud_toode_arv
                    rcd2.set_klassid(klassid)

                m_labiviijad.append((hindamiskogum.tahis, rcd1, rcd2))

            # mõlemale hindajale saadetakse määramise teated
            tahised1 = []
            tahised2 = []
            for tahis, r1, r2 in m_labiviijad:
                if r1:
                    rcd1 = r1
                    tahised1.append(tahis)
                if r2:
                    rcd2 = r2
                    tahised2.append(tahis)
            if tahised1:
                send_labiviija_maaramine(self, rcd1, kasutaja1, ta, tahised1)
            if tahised2:
                send_labiviija_maaramine(self, rcd2, kasutaja2, ta, tahised2)
                    
        model.Session.commit()
        return self._redirect('index')

    def _create_sobita(self):
        "Isiku profiil tehakse sobivaks, et teda määrata hindajaks"
        c = self.c
        kasutaja_id = int(self.request.params.get('sobita'))
        kasutaja = model.Kasutaja.get(kasutaja_id)
        koht = c.testikoht.koht
        lang = self.request.params.get('lang')
        testiosa = self.c.toimumisaeg.testiosa
        if testiosa.vastvorm_kood in (const.VASTVORM_SP, const.VASTVORM_SH):
            grupp_id = const.GRUPP_HINDAJA_S
        else:
            grupp_id = const.GRUPP_HINDAJA_K

        paranda_lv_sobimatust(self,
                              kasutaja,
                              c.toimumisaeg,
                              koht,
                              grupp_id,
                              lang=lang)
        model.Session.commit()
        return self._index_otsihindaja(True)

    def _edit(self, item):
        li_hk_id = [item.hindamiskogum_id]
        valimis = item.valimis
        self.c.klassid, self.c.sooritajate_arv = self._get_klassid(item.lang, li_hk_id, valimis)

    def _update(self, item, lang=None):
        klassid, item.planeeritud_toode_arv = self._get_param_klassid()
        item.set_klassid(klassid)

        item2 = item.get_hindaja2()
        if item2:
            item2.planeeritud_toode_arv = item.planeeritud_toode_arv
            item2.set_klassid(klassid)
        model.Session.commit()
        return self._redirect('index')
    
    def _delete(self, item):
        rc = True
        if len(item.hindamised):
            self.error(_("Ei saa kustutada, sest hindaja {s} on juba alustanud hindamist").format(s=item.kasutaja.nimi))
            rc = False
        else:
            for rcd in item.paarishindajad:
                if len(rcd.hindamised):
                    self.error(_("Ei saa kustutada, sest hindaja {s} on juba alustanud hindamist").format(s=rcd.kasutaja.nimi))
                    rc = False
                    break
                rcd.delete()
            if rc:
                item.delete()
                model.Session.commit()
                self.success(_("Andmed on kustutatud"))

    def __before__(self):
        c = self.c
        c.testikoht = model.Testikoht.get(self.request.matchdict.get('testikoht_id'))
        c.toimumisaeg = c.testikoht.toimumisaeg
        c.testimiskord = c.toimumisaeg.testimiskord
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testiosa.test
        koht_maarab = c.toimumisaeg.hindaja1_maaraja in const.MAARAJA_KOHAD or \
                      c.toimumisaeg.hindaja2_maaraja in const.MAARAJA_KOHAD or \
                      c.toimumisaeg.hindaja1_maaraja_valim in const.MAARAJA_KOHAD or \
                      c.toimumisaeg.hindaja2_maaraja_valim in const.MAARAJA_KOHAD
        assert koht_maarab, _("Vale määraja")

    def _perm_params(self):
        if self.c.testikoht.koht_id != self.c.user.koht_id:
            return False
