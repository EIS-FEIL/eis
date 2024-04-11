from eis.lib.baseresource import *
_ = i18n._
from eis.lib.xtee.rahvastikuregister import set_rr_pohiandmed
log = logging.getLogger(__name__)

class HindajadController(BaseResourceController):

    _permission = 'hindajamaaramine'
    _MODEL = model.Labiviija
    _INDEX_TEMPLATE = 'ekk/hindamine/maaramine.hindajad.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/maaramine.hindajad_list.mako'
    _DEFAULT_SORT = 'labiviija_1.tahis' # vaikimisi sortimine
    _UNIQUE_SORT = 'labiviija_1.id'
    _SEARCH_FORM = forms.ekk.hindamine.HindajadForm
    
    def _query(self):
        testiosa = self.c.toimumisaeg.testiosa
        self.c.hindamiskogumid_opt = [(r.id, r.tahis) for r in testiosa.hindamiskogumid \
                                          if r.staatus]
        if len(self.c.hindamiskogumid_opt) == 1:
            self.c.hindamiskogum_id = self.c.hindamiskogumid_opt[0][0]

        self.c.hindajad_opt = self._get_hindajad_opt()

        # kui kasutada ..table.alias(), siis filtri sees hindaja1.c.id=...
        # ja tulemuses on üksikud väljad, mitte objekt
        #self.Labiviija1 = model.Labiviija.table.alias('hindaja1')

        self.Kasutaja1 = None
        self.Kasutaja2 = None

        self.Labiviija1 = sa.orm.aliased(model.Labiviija) # hindaja_1
        f_hindaja1 = sa.and_(self.Labiviija1.hindamiskogum_id==model.Hindamiskogum.id,
                             self.Labiviija1.liik==const.HINDAJA1,
                             self.Labiviija1.toimumisaeg_id==self.c.toimumisaeg.id)

        self.Labiviija2 = sa.orm.aliased(model.Labiviija) # hindaja_2
        f_hindaja2p = sa.and_(self.Labiviija2.hindamiskogum_id==model.Hindamiskogum.id,
                             self.Labiviija2.liik==const.HINDAJA2,
                             self.Labiviija2.toimumisaeg_id==self.c.toimumisaeg.id,
                             self.Labiviija2.hindaja1_id==self.Labiviija1.id)

        f_hindaja2e = sa.and_(self.Labiviija2.hindamiskogum_id==model.Hindamiskogum.id,
                             self.Labiviija2.liik==const.HINDAJA2,
                             self.Labiviija2.toimumisaeg_id==self.c.toimumisaeg.id,
                             self.Labiviija2.hindaja1_id==None)

        # esimene päring, kus hindaja1 kirje on alati olemas
        q1 = (model.SessionR.query(model.Hindamiskogum, self.Labiviija1, self.Labiviija2)
              .join((self.Labiviija1, f_hindaja1))
              .outerjoin((self.Labiviija2, f_hindaja2p))
              .filter(sa.or_(self.Labiviija1.kasutaja_id!=None,
                             self.Labiviija2.kasutaja_id!=None))
              )
        # teine päring juhuks, kui on ainult hindaja2
        q2 = (model.SessionR.query(model.Hindamiskogum, self.Labiviija1, self.Labiviija2)
              .outerjoin((self.Labiviija1, sa.and_(self.Labiviija1.hindamiskogum_id==model.Hindamiskogum.id,
                                                   self.Labiviija1.id==None)))
              .join((self.Labiviija2, f_hindaja2e))
              .filter(sa.or_(self.Labiviija1.kasutaja_id!=None,
                             self.Labiviija2.kasutaja_id!=None))              
              )
        q = q1.union(q2)
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.hindamiskogum_id:
            hindamiskogum_id = int(c.hindamiskogum_id)
            q = q.filter(model.Hindamiskogum.id==hindamiskogum_id)
            c.hindamiskogum = model.Hindamiskogum.get(hindamiskogum_id)
        else:
            hindamiskogum_id = None

        self._get_arvud(hindamiskogum_id)
        
        if c.hindaja_id:
            hindaja_id = int(c.hindaja_id)
            #if c.kaks_hindajat:
            q = q.filter(sa.or_(self.Labiviija1.kasutaja_id==hindaja_id,
                                self.Labiviija2.kasutaja_id==hindaja_id))
        if c.csv:
            return self._index_csv(q)
        return q

    def _get_arvud(self, hindamiskogum_id):
        c = self.c
        
        c.sooritajatearvud = {}
        c.hinnataarvud = {}
        c.planeeritudarvud = {}

        v_values = c.testimiskord.sisaldab_valimit and [False, True] or [None]
        for valimis in v_values:
            if hindamiskogum_id:
                c.planeeritudarvud[valimis] = \
                    self._get_planeeritudarvud(hindamiskogum_id, valimis)

            c.sooritajatearvud[valimis] = \
                c.toimumisaeg.get_sooritajatearvud(valimis=valimis)
            c.hinnataarvud[valimis] = \
                c.toimumisaeg.get_sooritajatearvud(staatus=const.S_STAATUS_TEHTUD,
                                                   hindamiskogum_id=hindamiskogum_id,
                                                   valimis=valimis)        

    def _order_field(self, q, is_desc, field):
        # vormilt tulevad väljanimed nagu: labiviija_1.tahis
        # päring on tegelikult: anon_1.labiviija_1_tahis
        # välja arvatud kasutaja_1 ja kasutaja_2 (vt _order_join())
        if not field.startswith('kasutaja_'):
            field = field.replace('.', '_')
        return BaseResourceController._order_field(self, q, is_desc, field)
    
    def _order_join(self, q, tablename):
        """Otsingupäringu sortimisel lisatakse päringule join 
        tabeliga, mille välja järgi tuleb sortida
        """
        if tablename == 'kasutaja_1':
            if not self.Kasutaja1:
                self.Kasutaja1 = sa.orm.aliased(model.Kasutaja, name='kasutaja_1')
                q = q.join((self.Kasutaja1, self.Kasutaja1.id==self.Labiviija1.kasutaja_id))
        if tablename == 'kasutaja_2':
            if not self.Kasutaja2:
                self.Kasutaja2 = sa.orm.aliased(model.Kasutaja, name='kasutaja_2')
                q = q.outerjoin((self.Kasutaja2, self.Kasutaja2.id==self.Labiviija2.kasutaja_id))
        return q

    def _get_hindajad_opt(self):
        qh = (model.SessionR.query(model.Kasutaja.id, model.Kasutaja.nimi)
              .filter(model.Kasutaja.labiviijad.any(sa.and_(
                  model.Labiviija.toimumisaeg_id==self.c.toimumisaeg.id,
                  model.Labiviija.liik.in_((const.HINDAJA1, const.HINDAJA2)))))
              .order_by(model.Kasutaja.nimi)
              )
        return [(k[0],k[1]) for k in qh.all()] 

    def _get_planeeritudarvud(self, hindamiskogum_id, valimis):
        """Planeeritud tööde arvude statistika kogumine
        """
        q = model.SessionR.query(sa.func.sum(model.Labiviija.planeeritud_toode_arv), 
                                model.Labiviija.lang)
        q = (q.filter(model.Labiviija.toimumisaeg_id==self.c.toimumisaeg.id)
             .filter(model.Labiviija.liik==const.HINDAJA1)
             .filter(model.Labiviija.hindamiskogum_id==hindamiskogum_id)
             .filter(model.Labiviija.valimis==valimis)
             .group_by(model.Labiviija.lang)
             )

        di = {}
        total = 0
        for rcd in q.all():
            total += rcd[0] or 0
            di[rcd.lang] = rcd[0]
        di['total'] = total
        return di

    def _update(self, item):
        planeeritud_toode_arv = self.request.params.get('planeeritud_toode_arv')
        if planeeritud_toode_arv:
            planeeritud_toode_arv = int(planeeritud_toode_arv)
            maxvalue = self.c.toimumisaeg.get_sooritajatearv()
            if maxvalue < planeeritud_toode_arv:
                self.error(_("Planeeritud testisoorituste arv ei saa ületada {n}").format(n=maxvalue))
                return self._redirect('index')
        else:
            planeeritud_toode_arv = None
        item.planeeritud_toode_arv = planeeritud_toode_arv
        for rcd in item.paarishindajad:
            rcd.planeeritud_toode_arv = planeeritud_toode_arv

    def _after_update(self, id):
        return self._redirect('index')

    def new(self, format='html'):
        """Dialoogiakna avamine uue hindaja lisamise alustamiseks: valitakse hindamiskogum
        """
        self.c.valimis = self.request.params.get('valimis') and True or False
        return self.render_to_response('/ekk/hindamine/maaramine.otsikogum.mako')

    def _index_otsihindaja(self):
        """Hindamiskogum on valitud, kuvame hindaja otsimise vormi, kuvame hindajad
        """
        self.form = Form(self.request, schema=forms.ekk.hindamine.OtsihindajaForm, method='GET')
        if self.form.validate():
            arv = self.form.data.get('planeeritud_toode_arv')            
            if arv:
                arv = int(arv)
                maxvalue = self.c.toimumisaeg.get_sooritajatearv()
                if maxvalue < arv:
                    self.form.errors['planeeritud_toode_arv'] = \
                        _("Planeeritud testisoorituste arv ei saa ületada {n}").format(n=maxvalue)

        if self.form.errors:
            if 'planeeritud_toode_arv' in self.form.errors:
                template = '/ekk/hindamine/maaramine.otsikogum.mako'
            else:
                template = '/ekk/hindamine/maaramine.otsihindaja.mako'
            return Response(self.form.render(template, extra_info=self.response_dict))    
        self.c.planeeritud_toode_arv = self.form.data.get('planeeritud_toode_arv')
        self.c.lang = self.params_lang()
        self.c.hk_id = self.request.params.getall('hk_id')
        self.c.kasutaja1_id = self.request.params.get('kasutaja1_id')
        self.c.valimis = self.request.params.get('valimis') and True or False
        hindamiskogum1 = model.Hindamiskogum.get(self.c.hk_id[0])
        # kas on kokku vaja otsida 2 hindajat ja praegu otsitakse alles esimest?
        self.c.otsihindaja1_2st = hindamiskogum1.paarishindamine and not self.c.kasutaja1_id and not self.c.on_hindaja3
        ta = self.c.toimumisaeg
        # kas EKK saab valida mõlemat hindajat ja need pole paaris
        if self.c.valimis:
            voib = ta.hindaja1_maaraja_valim == const.MAARAJA_EKK and \
                   ta.hindaja2_maaraja_valim == const.MAARAJA_EKK
            self.c.vali1v2 = hindamiskogum1.kahekordne_hindamine_valim and \
                    not hindamiskogum1.paarishindamine and \
                    voib and not self.c.on_hindaja3
        else:
            voib = ta.hindaja1_maaraja == const.MAARAJA_EKK and \
                   ta.hindaja2_maaraja == const.MAARAJA_EKK
            self.c.vali1v2 = hindamiskogum1.kahekordne_hindamine and \
                    not hindamiskogum1.paarishindamine and \
                    voib and not self.c.on_hindaja3

        if self.c.test.testityyp == const.TESTITYYP_AVALIK:
            q = model.SessionR.query(model.Kasutaja)
            ik = self.form.data.get('isikukood')
            if ik:
                usp = validators.IsikukoodP(ik)
                q = q.filter(usp.filter(model.Kasutaja))

                # peab olma märgitud testide hindamisega seotud isikuks,
                # muidu pole hindajal tsentraalsete testide hindamist menyys
                q = q.filter(model.Kasutaja.on_labiviija==True)
                if q.count() == 0:
                    k = model.Kasutaja.get_by_ik(ik)
                    if not k or not k.on_labiviija:
                        self.error(_("Isik ei kuulu testide läbiviimisega seotud isikute hulka"))
                    # kui isik veel pole andmebaasis, siis otsime RRist
                    #k = set_rr_pohiandmed(self, None, isikukood=ik)
                    #if k:
                    #    model.Session.commit()
            else:
                q = None
        else:
            # EKK testi hindajal peab olema sobiv profiil
            q = (model.SessionR.query(model.Kasutaja)
                .distinct()
                .filter(model.Aineprofiil.kasutajagrupp_id==const.GRUPP_HINDAJA_K)
                .filter(model.Aineprofiil.aine_kood==self.c.toimumisaeg.testimiskord.test.aine_kood)
                .join(model.Aineprofiil.kasutaja))
            keeletase_kood = self.c.test.keeletase_kood
            if keeletase_kood:
                q = q.filter(model.Aineprofiil.keeletase_kood==keeletase_kood)
            
        if q:
            if self.c.kasutaja1_id:
                q = q.filter(model.Kasutaja.id!=int(self.c.kasutaja1_id))
            q = q.order_by(model.Kasutaja.nimi)
            self.c.items = q.all()
        return self.render_to_response('/ekk/hindamine/maaramine.otsihindaja.mako')

    def _create_otsihindajapaar(self):
        """Labiviija on valitud, salvestame uue hindaja
        """
        # kahekordne paarishindamine
        hk_id = self.request.params.getall('hk_id')
        #hindamiskogum_id = int(self.request.params.get('hindamiskogum_id'))
        valimis = self.request.params.get('valimis') == '1'        
        lang = self.params_lang()
        arv = self.request.params.get('planeeritud_toode_arv')
        planeeritud_toode_arv = arv and int(arv) or None

        kasutaja1_id = int(self.request.params.get('kasutaja1_id'))
        for key in self.request.params:
            prefix = 'kasutaja_'
            if key.startswith(prefix):
                kasutaja2_id = int(key[len(prefix):])
                break

        vastvorm_kood = self.c.toimumisaeg.testiosa.vastvorm_kood
        if vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I):
            kasutajagrupp_id = const.GRUPP_HINDAJA_K
        else:
            kasutajagrupp_id = const.GRUPP_HINDAJA_S
        liik = self.c.on_hindaja3 and const.HINDAJA3 or const.HINDAJA1
        testikoht_id = None

        for hindamiskogum_id in hk_id:
            rcd1 = model.Labiviija(toimumisaeg=self.c.toimumisaeg,
                                   hindamiskogum_id=hindamiskogum_id,
                                   lang=lang,
                                   liik=liik,
                                   on_paaris=True,
                                   kasutajagrupp_id=kasutajagrupp_id,
                                   testikoht_id=testikoht_id,
                                   planeeritud_toode_arv=planeeritud_toode_arv,
                                   valimis=valimis,
                                   toode_arv=0,
                                   hinnatud_toode_arv=0,
                                   tasu_toode_arv=0)
                                   
            rcd1.set_kasutaja(kasutaja1_id)
            model.Session.flush()

            rcd2 = model.Labiviija(toimumisaeg=self.c.toimumisaeg,
                                   hindamiskogum_id=hindamiskogum_id,
                                   lang=lang,
                                   hindaja1=rcd1,
                                   liik=const.HINDAJA2,
                                   on_paaris=True,
                                   kasutajagrupp_id=kasutajagrupp_id,
                                   testikoht_id=testikoht_id,
                                   planeeritud_toode_arv=planeeritud_toode_arv,
                                   valimis=valimis,
                                   toode_arv=0,
                                   hinnatud_toode_arv=0,
                                   tasu_toode_arv=0)
                                   
            rcd2.set_kasutaja(kasutaja2_id)
            model.Session.flush()
        model.Session.commit()
        return self._redirect('index', hindamiskogum_id=len(hk_id)==1 and hk_id[0] or None)

    def _create_otsihindaja(self):
        """Labiviija on valitud, salvestame uue hindaja
        """
        c = self.c
        hk_id = self.request.params.getall('hk_id')
        valimis = self.request.params.get('valimis') == '1'        
        lang = self.params_lang()
        arv = self.request.params.get('planeeritud_toode_arv')
        vali2 = self.request.params.get('vali2')
        planeeritud_toode_arv = arv and int(arv) or None
        ta = self.c.toimumisaeg
        vastvorm_kood = ta.testiosa.vastvorm_kood
        if vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I):
            kasutajagrupp_id = const.GRUPP_HINDAJA_K
        else:
            kasutajagrupp_id = const.GRUPP_HINDAJA_S
        testikoht_id = None

        for key in self.request.params:
            prefix = 'kasutaja_'
            if key.startswith(prefix):
                kasutaja_id = int(key[len(prefix):])
                for hindamiskogum_id in hk_id:
                    hindamiskogum = model.Hindamiskogum.get(hindamiskogum_id)

                    if valimis:
                        voib2 = ta.hindaja1_maaraja_valim != const.MAARAJA_EKK and \
                                ta.hindaja2_maaraja_valim == const.MAARAJA_EKK
                    else:
                        voib2 = ta.hindaja1_maaraja != const.MAARAJA_EKK and \
                                ta.hindaja2_maaraja == const.MAARAJA_EKK

                    if valimis:
                        kkh = hindamiskogum.kahekordne_hindamine_valim
                    else:
                        kkh = hindamiskogum.kahekordne_hindamine
                    if c.on_hindaja3:
                        liik = const.HINDAJA3
                    elif kkh and not hindamiskogum.paarishindamine and voib2:
                        liik = const.HINDAJA2
                    elif vali2:
                        liik = const.HINDAJA2
                    else:
                        liik = const.HINDAJA1

                    rcd1 = (model.Labiviija.query
                            .filter_by(toimumisaeg_id=self.c.toimumisaeg.id)
                            .filter_by(kasutaja_id=kasutaja_id)
                            .filter_by(kasutajagrupp_id=kasutajagrupp_id)
                            .filter_by(liik=liik)
                            .filter_by(lang=lang)
                            .filter_by(hindamiskogum_id=hindamiskogum_id)
                            .filter_by(valimis=valimis)
                            .first())
                    if rcd1:
                        kasutaja = model.Kasutaja.get(kasutaja_id)
                        self.error('%s on juba hindajaks määratud' % kasutaja.nimi)
                        continue

                    rcd1 = model.Labiviija(toimumisaeg=self.c.toimumisaeg,
                                           hindamiskogum_id=hindamiskogum_id,
                                           lang=lang,
                                           liik=liik,
                                           on_paaris=False,
                                           kasutajagrupp_id=kasutajagrupp_id,
                                           testikoht_id=testikoht_id,
                                           planeeritud_toode_arv=planeeritud_toode_arv,
                                           valimis=valimis,
                                           toode_arv=0,
                                           hinnatud_toode_arv=0,
                                           tasu_toode_arv=0)
                                           
                    rcd1.set_kasutaja(kasutaja_id)
                    model.Session.flush()

        model.Session.commit()
        return self._redirect('index', hindamiskogum_id=len(hk_id)==1 and hk_id[0] or None)

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

    def _after_delete(self, parent_id=None):
        return self._redirect('index')

    def _prepare_header(self):
        c = self.c
        if c.kaks_hindajat:
            header = [_("I hindaja"),
                      _("Tähis"),
                      _("II hindaja"),
                      _("Tähis"),
                      ]
        else:
            header = [_("Hindaja"),
                      _("Tähis"),
                      ]
        if c.toimumisaeg.hindaja1_maaraja in const.MAARAJA_KOHAD or \
           c.toimumisaeg.hindaja1_maaraja_valim in const.MAARAJA_KOHAD:
            header.append(_("Soorituskoht"))
        if c.testimiskord.sisaldab_valimit:
            header.append(_("Valim"))
        header.extend([_("Hindamiskogum"),
                       _("Keel"),
                       _("Olek"),
                       _("Planeeritud hinnata"),
                       _("Tegelikult hinnatud"),
                       ])
        return header
    
    def _prepare_item(self, rcd, n):
        c = self.c
        if c.kaks_hindajat:
            kogum, hindaja1, hindaja2 = rcd
        else:
            kogum, hindaja1 = rcd
            hindaja2 = None
        hindaja = hindaja1 or hindaja2
        kasutaja1 = hindaja1 and hindaja1.kasutaja
        kasutaja2 = hindaja2 and hindaja2.kasutaja
        item = [kasutaja1 and kasutaja1.nimi or '',
                hindaja1 and hindaja1.tahis or '',
                ]
        if c.kaks_hindajat:
            item.append(kasutaja2 and kasutaja2.nimi or '')
            item.append(hindaja2 and hindaja2.tahis)
        if c.toimumisaeg.hindaja1_maaraja in const.MAARAJA_KOHAD or \
           c.toimumisaeg.hindaja1_maaraja_valim in const.MAARAJA_KOHAD:
            testikoht = hindaja.testikoht
            item.append(testikoht and testikoht.koht.nimi or '')
        if c.testimiskord.sisaldab_valimit:
            item.append(hindaja.valimis and _("Valim") or '')
        item.append(kogum.tahis)
        item.append(model.Klrida.get_lang_nimi(hindaja.lang))
        item.append(hindaja.staatus_nimi)
        item.append(hindaja.planeeritud_toode_arv)
        buf = '%s' % (hindaja.hinnatud_toode_arv or 0)
        if hindaja1 and hindaja2:
            buf += ' / %s' % (hindaja2.hinnatud_toode_arv or 0)
        item.append(buf)
        return item

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.testimiskord = self.c.toimumisaeg.testimiskord
        self.c.test = self.c.testimiskord.test
        self.c.kaks_hindajat = True
        self.c.on_hindaja = True
            
    def _perm_params(self):
        return {'obj':self.c.test}
