from eis.lib.baseresource import *
from eis.lib.resultentry import ResultEntry
from eis.handlers.ekk.sisestamine.vastused import (
    sisestaja_soorituskoht,
    get_mittevalim_sooritus_id,
    cmp_mittevalim
    )
_ = i18n._
log = logging.getLogger(__name__)

class SuulisedhindamisedController(BaseResourceController):
    """Suuliste testide hinnete sisestamine paberil toodud hindamisprotokollilt
    """
    _permission = 'sisestamine'
    _MODEL = model.Hindamine
    _INDEX_TEMPLATE = 'ekk/sisestamine/suulised.hindamised.mako'
    _ITEM_FORM = forms.ekk.sisestamine.HindamisprotokollForm
    _DEFAULT_SORT = 'sooritus.tahised'
    _get_is_readonly = False
    _index_after_create = True

    def _query(self):
        self._set_opt_liik()

        if self.c.sisestus == 1:
            if not self.c.hindamisprotokoll.can_sis1(self.c.user.id):
                self.error(_('Sisestamine on kellelgi teisel juba pooleli'))
                raise self._back_to_index()
            elif self.c.hindamisprotokoll.sisestaja1_kasutaja_id != self.c.user.id:
                self.c.hindamisprotokoll.sisestaja1_kasutaja_id = self.c.user.id
                self.c.hindamisprotokoll.staatus1 = const.H_STAATUS_POOLELI
                model.Session.commit()

        elif self.c.sisestus == 2:
            if not self.c.hindamisprotokoll.can_sis2(self.c.user.id):
                self.error(_('Sisestamine on kellelgi teisel juba pooleli'))
                raise self._back_to_index()
            elif self.c.hindamisprotokoll.sisestaja2_kasutaja_id != self.c.user.id:
                self.c.hindamisprotokoll.sisestaja2_kasutaja_id = self.c.user.id
                self.c.hindamisprotokoll.staatus2 = const.H_STAATUS_POOLELI
                model.Session.commit()

        self.c.focus = self.request.params.get('focus')
        self.c.get_items = self._get_items

    def _get_items(self):
        # self.c.hindamiskogum_id seatakse makos

        if self.c.sisestus == 'p' and self.c.kahekordne_sisestamine:
            # on vaja näidata kahte sisestust korraga

            Hindamine1 = sa.orm.aliased(model.Hindamine)
            sisestus1 = 1

            Hindamine2 = sa.orm.aliased(model.Hindamine)
            sisestus2 = 2

            q = (model.Session.query(model.Sooritus, Hindamine1, Hindamine2)
                 .filter(model.Sooritus.testiprotokoll_id==self.c.hindamisprotokoll.testiprotokoll_id)
                 .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                 .join(model.Sooritus.sooritaja)
                 .join(model.Sooritus.hindamisolekud)
                 .filter(model.Hindamisolek.hindamiskogum_id==self.c.hindamiskogum_id)
                 .filter(model.Hindamisolek.puudus==False))

            q = q.outerjoin((Hindamine1,
                             sa.and_(Hindamine1.hindamisolek_id==model.Hindamisolek.id,
                                     Hindamine1.hindamisprotokoll_id==self.c.hindamisprotokoll.id,
                                     Hindamine1.tyhistatud==False,
                                     Hindamine1.sisestus==sisestus1)))
            q = q.outerjoin((Hindamine2,
                             sa.and_(Hindamine2.hindamisolek_id==model.Hindamisolek.id,
                                     Hindamine2.hindamisprotokoll_id==self.c.hindamisprotokoll.id,
                                     Hindamine2.tyhistatud==False,
                                     Hindamine2.sisestus==sisestus2)))

        else:
            sisestus = self.c.sisestus == 'p' and 1 or self.c.sisestus
            q = (model.Session.query(model.Sooritus, model.Hindamine)
                 .filter(model.Sooritus.testiprotokoll_id==self.c.hindamisprotokoll.testiprotokoll_id)
                 .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                 .join(model.Sooritus.sooritaja)
                 .join(model.Sooritus.hindamisolekud)
                 .filter(model.Hindamisolek.hindamiskogum_id==self.c.hindamiskogum_id)
                 .filter(model.Hindamisolek.puudus==False))
            q = q.outerjoin((model.Hindamine,
                             sa.and_(model.Hindamine.hindamisolek_id==model.Hindamisolek.id,
                                     model.Hindamine.hindamisprotokoll_id==self.c.hindamisprotokoll.id,
                                     model.Hindamine.tyhistatud==False,
                                     model.Hindamine.sisestus==sisestus)))

        if self.c.testiosa.on_alatestid:
            # leiame alatestid, mis sisaldavad selle hindamisprotokolli ülesandeid
            alatestid_id = set()
            for hk in self.c.hindamisprotokoll.sisestuskogum.hindamiskogumid:
                for ty in hk.testiylesanded:
                    alatestid_id.add(ty.alatest_id)

            # kui testiosal on alatestid, siis kontrollime, et sooritaja
            # poleks antud hindamisprotokolli alatestidest vabastatud
            q = q.filter(sa.and_(
                model.Sooritus.id==model.Alatestisooritus.sooritus_id,
                model.Alatestisooritus.alatest_id.in_(alatestid_id),
                model.Alatestisooritus.staatus==const.S_STAATUS_TEHTUD
            ))

        return q.order_by(model.Sooritus.tahised).all()

    def _create(self):
        """Hinnete salvestamine
        """
        hpr = self.c.hindamisprotokoll
        test = self.c.testiosa.test
        resultentry = ResultEntry(self, const.SISESTUSVIIS_PALLID, test, self.c.testiosa)
        lopeta = self.request.params.get('kinnita') or self.c.sisestus == 'p'
        sisestus1 = self.c.sisestus == 'p' and 1 or self.c.sisestus

        staatus1 = const.H_STAATUS_HINNATUD
        staatus2 = const.H_STAATUS_HINNATUD

        sisestuserinevus = False
        molemad = True
        # parandamise korral ei kontrolli esimese sisestuse vastavust teisele,
        # sest teine on esimese salvestamise ajal veel salvestamata
        compare2 = self.c.sisestus != 'p' and self.c.kahekordne_sisestamine

        hindajad_id = set()
        sooritused1 = {}
        sooritused2 = {}
        dt_now = datetime.now()
        
        n_last_hk = len(self.form.data.get('hk')) - 1
        for hk_n, hk in enumerate(self.form.data.get('hk')):
            # yhe hindamiskogumi hinnete salvestamine (kõik sooritused)
            hindamiskogum = model.Hindamiskogum.get(hk.get('hindamiskogum_id'))
            for n, rcd in enumerate(hk.get('hmine')):
                # rcd on yhe soorituse hindamisele vastav kirje
                sooritus_id = rcd['sooritus_id']
                tos = model.Sooritus.get(sooritus_id)
                sooritaja = tos.sooritaja
                # leitakse soorituse hindamisoleku kirje antud hindamiskogumi kohta
                holek = tos.give_hindamisolek(hindamiskogum)
                # leitakse hindamisolekule vastav hindamise kirje antud sisestuse kohta
                hindamine = holek.give_hindamine(hpr, sisestus1)

                # update_sooritus() pole esimese hindaja puhul vaja teha juhul,
                # kui salvestame kahekordse sisestamise parandamist
                # ja teise hindaja juures seda niikuinii teeme
                is_update_sooritus = self.c.sisestus != 'p' or not self.c.kahekordne_sisestamine
                komplekt_id = rcd['komplekt_id']
                komplekt = model.Komplekt.get(komplekt_id)
                if komplekt:
                    komplektivalik_id = komplekt.komplektivalik_id
                    sk = ExamSaga(self).give_soorituskomplekt(tos.id, komplektivalik_id)
                    sk.komplekt_id = komplekt.id
                    TestSaga(self).komplekt_set_lukus_tk(komplekt, self.c.testimiskord)
                else:
                    sk = None
                prefix = 'hk-%d.hmine-%d' % (hk_n, n)
                resultentry.save_sisestamine(sooritaja, rcd, lopeta, prefix, tos, holek, self.c.testiosa,
                                             hindamine, komplekt, sk, compare2, is_update_sooritus)

                hindajad_id.add(hindamine.labiviija_id)
                hindajad_id.add(hindamine.kontroll_labiviija_id)
                hindajad_id.add(hindamine.intervjuu_labiviija_id)
                if not hindamine.sisestaja_kasutaja_id:
                    hindamine.sisestaja_kasutaja_id = self.c.user.id

                if self.c.sisestus != 'p':
                    if hindamine.sisestuserinevus:
                        sisestuserinevus = True
                    if not hindamine.sisestatud:
                        molemad = False

                staatus1 = min(staatus1, hindamine.staatus)
                if tos.id not in sooritused1:
                    sooritused1[tos.id] = hindamine.sisestatud
                else:
                    sooritused1[tos.id] &= hindamine.sisestatud

                if self.c.sisestus == 1 and not self.c.kahekordne_sisestamine:
                    # valimi yhekordsel sisestamisel leiame mittevalimi soorituse ja mittevalimi protokolli vormi
                    mv_tos_id = get_mittevalim_sooritus_id(sooritaja, tos)
                    if mv_tos_id:
                        v_items = [(prefix, rcd)]
                        err = cmp_mittevalim(self, resultentry, v_items, tos, mv_tos_id)
                        if err:
                            # erineb mittevalimist
                            resultentry.warnings[prefix + '.sooritus_id'] = err

            if self.c.sisestus == 'p' and self.c.kahekordne_sisestamine:
                resultentry.sisestuserinevus = False # kas on erinevusi teise sisestusega
                resultentry.molemad = True # kas mõlemad sisestused on sisestatud
                sisestus2 = 2
                for n, rcd in enumerate(hk.get('hmine2')):
                    sooritus_id = rcd['sooritus_id']
                    tos = model.Sooritus.get(sooritus_id)
                    sooritaja = tos.sooritaja
                    # leitakse soorituse hindamisoleku kirje antud hindamiskogumi kohta
                    holek = tos.give_hindamisolek(hindamiskogum)
                    # leitakse hindamisolekule vastav hindamise kirje antud sisestuse kohta
                    hindamine2 = holek.give_hindamine(hpr, sisestus2)

                    komplekt_id = rcd['komplekt_id']
                    komplekt = model.Komplekt.get(komplekt_id)
                    if komplekt:
                        komplektivalik_id = komplekt.komplektivalik_id
                        sk = ExamSaga(self).give_soorituskomplekt(tos.id, komplektivalik_id)
                        sk.komplekt_id = komplekt.id
                        TestSaga(self).komplekt_set_lukus_tk(komplekt, self.c.testimiskord)
                    else:
                        sk = None
                    resultentry.save_sisestamine(sooritaja, rcd, lopeta, 'hk-%d.hmine2-%d' % (hk_n,n), tos, holek, self.c.testiosa, hindamine2, komplekt, sk, True)
                    staatus2 = min(staatus2, hindamine2.staatus)

                    if hindamine2.sisestuserinevus:
                        sisestuserinevus = True
                    if not hindamine2.sisestatud:
                        molemad = False

                    if tos.id not in sooritused2:
                        sooritused2[tos.id] = hindamine2.sisestatud
                    else:
                        sooritused2[tos.id] &= hindamine2.sisestatud

        log.debug('Sisestus {s1}: sisestuserinevus={s2}, molemad={s3}'.format(s1=self.c.sisestus, s2=sisestuserinevus, s3=molemad))
        if resultentry.errors:
            raise ValidationError(self, resultentry.errors)

        if self.c.sisestus != 'p':
            if not lopeta:
                # vajutati nupule "Loobu"
                staatus1 = const.H_STAATUS_LYKATUD
            if self.c.sisestus == 1:
                hpr.staatus1 = staatus1
            elif self.c.sisestus == 2:
                hpr.staatus2 = staatus1
        elif lopeta:
            if self.c.kahekordne_sisestamine:
                if not sisestuserinevus and molemad:
                    hpr.staatus1 = hpr.staatus2 = const.H_STAATUS_HINNATUD
            else:
                hpr.staatus1 = const.H_STAATUS_HINNATUD

        if hpr.staatus1 == const.H_STAATUS_HINNATUD and not self.c.kahekordne_sisestamine:
            hpr.staatus = const.H_STAATUS_HINNATUD
        elif hpr.staatus1 == const.H_STAATUS_HINNATUD and hpr.staatus2 == const.H_STAATUS_HINNATUD \
                and not sisestuserinevus:
            hpr.staatus = const.H_STAATUS_HINNATUD
        else:
            hpr.staatus = const.H_STAATUS_POOLELI

        # lisame sisestusolekute kirjed, et saaks sisestajate tööd
        # sisestuskogumite kaupa kokku arvestada
        sisestuskogum = self.c.hindamisprotokoll.sisestuskogum
        liik = self.c.hindamisprotokoll.liik
        for sooritus_id, sisestatud in sooritused1.items():
            tos = model.Sooritus.get(sooritus_id)
            solek = tos.give_sisestusolek(sisestuskogum, liik)
            staatus = sisestatud and const.H_STAATUS_HINNATUD or const.H_STAATUS_POOLELI
            if self.c.sisestus == 'p':
                solek.staatus1 = staatus
                if sooritus_id in sooritused2:
                    solek.staatus2 = sooritused2[sooritus_id] and const.H_STAATUS_HINNATUD or const.H_STAATUS_POOLELI
            elif self.c.sisestus == 1:
                solek.staatus1 = staatus
                if not solek.sisestaja1_algus:
                    solek.sisestaja1_algus = datetime.now()
                solek.sisestaja1_kasutaja_id = self.c.user.id
            elif self.c.sisestus == 2:
                solek.staatus2 = staatus
                if not solek.sisestaja2_algus:
                    solek.sisestaja2_algus = datetime.now()                
                solek.sisestaja2_kasutaja_id = self.c.user.id                
            solek.staatus = min(solek.staatus1, solek.staatus2)               

        model.Session.commit()
        
        # arvutame hindajate hinnatud tööde arvu kokku
        self.c.lisatud_labiviijad_id = list()
        for lv_id in hindajad_id:
            if lv_id:
                lv = model.Labiviija.get(lv_id)
                lv.calc_toode_arv()
                if lv in resultentry.neg_labiviijad:
                    # äsja siin lõime läbiviija kirje negatiivsest id-st
                    self.c.lisatud_labiviijad_id.append(lv.id)
        model.Session.commit()

        err = None
        if resultentry.warnings:
            err = _('Andmed on salvestatud, kuid ei lange kokku teise sisestamisega. Palun kontrolli märgitud andmeväljad üle.')
            if self.c.sisestus == 'p':
                # parandamise vormi kuvamisel otsitakse niikuinii erinevused alati üles
                # ja praegu leitud erinevusi pole vaja alles hoida
                lopeta = False
            else:
                # vormistame errori sellepärast, et saaks neid erinevusi kuvada
                raise ValidationError(self, resultentry.warnings, message=err)

        if lopeta and self.c.sisestus != 'p':
            if self.c.sisestus in (1,2) and staatus1 != const.H_STAATUS_HINNATUD:
                err = _('Ei saa kinnitada')

        if err:
            self.error(err)
        else:
            self.success()

        return hpr

    def _error_create(self):
        html = self.form.render(self._INDEX_TEMPLATE,
                                extra_info=self._index_d())            
        return Response(html)

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """   
        # lisame parameetri focus, et anda teada vajadusest viia fookus 
        # järgmise töö valimise tähise väljale lehekülje lõpus
        return self._redirect('index', focus='next')     

    def _set_opt_liik(self):
        self.c.opt_liik = [(const.HINDAJA1, 'I hindamine'),
                           (const.HINDAJA2, 'II hindamine'),
                           (const.HINDAJA3, 'III hindamine'),
                           ]

    def _back_to_index(self):
        return HTTPFound(location=self.url('sisestamine_suulised', sessioon_id=self.c.toimumisaeg.testimiskord.testsessioon_id, toimumisaeg_id=self.c.toimumisaeg.id))


    def __before__(self):
        self.c.sisestus = self.request.matchdict.get('sisestus') # mitmes sisestus (1,2 või p - parandamine)
        if self.c.sisestus in ('1','2'):
            self.c.sisestus = int(self.c.sisestus)

        hpr_id = self.request.matchdict.get('hindamisprotokoll_id')
        self.c.hindamisprotokoll = model.Hindamisprotokoll.get(hpr_id)
        self.c.toimumisaeg = self.c.hindamisprotokoll.testiprotokoll.testipakett.testikoht.toimumisaeg
        self.c.testimiskord = self.c.toimumisaeg.testimiskord
        self.c.kahekordne_sisestamine = self.c.toimumisaeg.kahekordne_sisestamine
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.hindamise_liik = self.c.hindamisprotokoll.liik_nimi

    def _perm_params(self):
        return {'testiliik': self.c.testiosa.test.testiliik_kood}

    def _has_permission(self):
        c = self.c
        if c.action == 'index':
            # kontrollitakse, kas sisestaja tohib antud hindamisprotokolli sisestada
            q = (model.Session.query(model.Testipakett.testikoht_id)
                 .join(model.Testipakett.testiprotokollid)
                 .join(model.Testiprotokoll.hindamisprotokollid)
                 .filter(model.Hindamisprotokoll.id==c.hindamisprotokoll.id)
                 )
            testikoht_id, = q.first()
            if sisestaja_soorituskoht(c.user.id, testikoht_id):
                self.error(_("Ümbriku kontroll. Palun edasta ümbrik korraldusspetsialistile."))
                return False
        return super()._has_permission()
    
