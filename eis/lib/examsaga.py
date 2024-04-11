import random
from simplejson import dumps
from datetime import datetime
import logging
import eiscore.const as const
import eiscore.i18n as i18n
_ = i18n._
import eis.model as model
from eis.lib.block import BlockController
from eis.lib.blockresponse import BlockResponse
from eiscore.examwrapper import RecordWrapper, MemYlesandevastus, MemKV, MemKS
from eis.lib.blockcalc import BlockCalc
from eis.lib.npcalc import Npcalc
from eis.lib.examclient import ExamClient
from eis.lib.helpers import fstr
import eis.lib.utils as utils
log = logging.getLogger(__name__)

class ExamSaga:
    def __init__(self, handler):
        self.handler = handler

    def init_klaster(self, sooritus, sooritaja):
        """Kontrollitakse, kas klaster on määratud.
        Kui pole, siis viiakse andmed klastrisse.
        """
        oli_id = sooritaja.klaster_id
        klaster_id, exapi_host = model.Klaster.give_klaster(sooritaja)
        if oli_id != klaster_id or not sooritus.klastrist_toomata:
            # saadame sooritaja kirje klastrisse
            # kas on erialatesti lisaaeg
            q = (model.SessionR.query(model.Erialatest.komplekt_id,
                                      model.Erialatest.alatest_id,
                                      model.Erialatest.lisaaeg)
                 .filter(model.Erialatest.komplekt_id==model.Erikomplekt.komplekt_id)
                 .filter(model.Erikomplekt.sooritus_id==model.Sooritus.id)
                 .filter(model.Sooritus.sooritaja_id==sooritaja.id))
            erikomplektid = {r[1]: {'komplekt_id': r[0],
                                    'alatest_id': r[1],
                                    'lisaaeg': r[2]} for r in q.all()}
            ExamClient(self.handler, exapi_host).create_sooritaja(sooritus, sooritaja, erikomplektid)
            sooritus.klastrist_toomata = True
            model.Session.commit()
        return exapi_host
        
    def from_examdb(self, exapi_host, sooritus, sooritaja1, test, testiosa, toimumisaeg, lang, hiljem=None):
        "Eksamiklastrist tuuakse kirjed, vajadusel arvutatakse tulemused ja kustutatakse klastrist"
        def _arvutada_hiljem():
            """Kas arvutada tulemused kohe peale sooritamist
            või teha seda jõudluse parandamiseks hiljem"""
            if not test.diagnoosiv:
                if toimumisaeg and toimumisaeg.testimiskord.arvutada_hiljem:
                    return True
            return False
        if hiljem is None:
            hiljem = _arvutada_hiljem()
        log.debug(f'hiljem: {hiljem}')
        
        # tõmbame vastused
        error, dtos = ExamClient(self.handler, exapi_host).get_sooritus(sooritus.id, hiljem)
        if error:
            self.handler.error(error)
        else:
            # arvutame arvutihinnatavate yksikylesannete pallid kokku

            # nende listide elementidest tehakse eraldi klasside objektid,
            # muudest elementidest tehakse RecordWrapper
            clsmap = {'ylesandevastused': MemYlesandevastus,
                      'kysimusevastused': MemKV,
                      'kvsisud': MemKS,
                      }
            tos = RecordWrapper.create_from_dict(dtos, clsmap)
            if hiljem:
                # salvestame ainult testiosasoorituse kirje
                self._save_in_center(tos, True)
            elif tos.staatus == const.S_STAATUS_TEHTUD:
                # arvutame ylesannete tulemused
                self._calculate(tos, testiosa, lang)
                # salvestame punktid klastris               
                cl = ExamClient(self.handler, exapi_host)
                rc = cl.set_sooritus_p(tos)
                if rc:
                    # salvestame vastused ja hinded keskserveris
                    tos, sooritaja = self._save_in_center(tos, False)
                    # märgime klastris, et enam klastris ei muudeta
                    cl.teisaldatud_sooritus(tos.id)
                    # arvutame tulemuse kokku
                    # vajame päris testi kirjet
                    test = model.Test.get(test.id)
                    self._calculate_total(sooritus, sooritaja, test, testiosa, hiljem)
            else:
                # test pole veel tehtud, aga salvestame kõik klastris olevad andmed keskserveris
                self._save_in_center(tos, False)
            model.Session.commit()

    def yv_from_examdb(self, exapi_host, sooritus, testiosa, ryv, lang, ty, vy, ylesanne):
        "Jagatud töö ülesande kinnitamisel tuuakse kirjed eksamiserverist"

        sooritus_id = sooritus.id
        ty_id = ryv.testiylesanne_id
        
        # varasemad kinnitatud vastused märgitakse vanaks
        for yv2 in sooritus.get_ylesandevastused(ty_id, kehtiv=True, loplik=None):
            yv2.kehtiv = None

        # arvutame tulemuse
        self.calculate_yv(ryv, ylesanne, vy, ty, testiosa, lang)
            
        # salvestame kinnitatud vastuse
        yv = self._save_in_center_yv(sooritus_id, ryv)
        yv.kehtiv = True
        yv.muudetav = False
        return yv
        
    def _save_in_center(self, tos, hiljem):
        # salvestame kirjed keskserveris
        sooritus = model.Sooritus.unpack_item(tos, True)
        sooritaja = sooritus.sooritaja
        if not sooritaja.algus:
            sooritaja.algus = sooritus.algus
        if hiljem:
            # rohkem praegu keskserverit ei koorma
            sooritus.klastrist_toomata = True
            return sooritus, sooritaja
        for r in tos.alatestisooritused:
            # alatestisooritus võidi luua ka vahepeal keskserveris
            atos = sooritus.get_alatestisooritus(r.alatest_id)
            if atos:
                # siis kirjutame olemasoleva kirje yle, mitte ei loo uut
                r.id = atos.id
            model.Alatestisooritus.unpack_item(r, True)
        for r in tos.ylesandevastused:
            self._save_in_center_yv(sooritus.id, r)
        for r in tos.npvastused:
            nv = model.Npvastus.unpack_item(r)
            nv.sooritus_id = sooritus.id
        for r in tos.soorituskomplektid:
            model.Soorituskomplekt.unpack_item(r)
        for r in tos.soorituslogid:
            model.Soorituslogi.unpack_item(r)
        sooritus.klastrist_seisuga = datetime.now()
        sooritus.klastrist_toomata = False
        sooritus.give_hindamisolekud()
        sooritaja.update_staatus()
        model.Session.commit()
        log.debug(f'saved_in_center {sooritus.id} st={sooritus.staatus} hst={sooritus.hindamine_staatus}')
        return sooritus, sooritaja

    def _save_in_center_yv(self, sooritus_id, r):
        # ylesandevastuse salvestamine keskserveris
        yv = model.Ylesandevastus.unpack_item(r)
        yv.sooritus_id = sooritus_id
        for r1 in r.kysimusevastused:
            kv = model.Kysimusevastus.unpack_item(r1)
            kv.ylesandevastus = yv
            li_ks_id = []
            for r2 in r1.kvsisud:
                ks = model.Kvsisu.unpack_item(r2)
                ks.kysimusevastus = kv
                li_ks_id.append(ks.id)
            for ks in kv.kvsisud:
                if ks.id not in li_ks_id:
                    ks.delete()
        for r1 in r.loendurid:
            lr = model.Loendur.unpack_item(r1)
            lr.ylesandevastus = yv
        return yv
    
    def _calculate(self, tos, testiosa, lang):
        # uuendame testiosade ja alatestide sooritamise staatust
        for yv in tos.ylesandevastused:
            # arvutatakse iga ylesande punktid
            vy_id = yv.valitudylesanne_id
            vy = model.Valitudylesanne.get(vy_id)
            if not vy:
                log.error(f'vy {vy_id} on kustutatud')
                continue
            ty = vy.testiylesanne
            ylesanne = vy.ylesanne
            self.calculate_yv(yv, ylesanne, vy, ty, testiosa, lang)
            log.debug(f'CALC VY {vy_id} yv {yv.id} p={yv.pallid}')

    def _calculate_total(self, sooritus, sooritaja, test, testiosa, hiljem, on_jagatudtoo=False):
        # uuendame testiosade ja alatestide sooritamise staatust
        from eis.lib.resultentry import ResultEntry

        sooritaja.update_staatus()
        if not hiljem:
            model.Session.flush()
            sooritus.give_hindamisolekud()
            resultentry = ResultEntry(self.handler, const.SISESTUSVIIS_VASTUS, test, testiosa, on_jagatudtoo)
            for holek in sooritus.hindamisolekud:
                resultentry.update_hindamisolek(sooritaja, sooritus, holek, is_update_sooritus=False)
            resultentry.update_sooritus(sooritaja, sooritus)
        lv = sooritus.intervjuu_labiviija
        if lv:
            lv.calc_toode_arv()

    def calculate_yv(self, yv, ylesanne, vy, ty, testiosa, lang):
        "Ühe ülesande hindamine"
        blockcalc = BlockCalc(self.handler)

        # vastused on kysimustekaupa kysimusevastuste kirjetes
        responses = {kv.kood: kv for kv in yv.kysimusevastused}

        # arvutatakse hindepallid
        koef = vy.koefitsient or 0
        toorpunktid, arvuti, kasitsi, max_toorpunktid, buf, on_arvuti, on_kasitsi, f_locals = \
                     blockcalc.calculate(ylesanne, responses, lang, yv, koefitsient=koef, testiosa=testiosa)

        # kui ylesanne on yleni arvutihinnatav, siis salvestatakse 
        # kohe ylesande lõplik tulemus
        if toorpunktid is None:
            # ei saa automaatselt hinnata
            arvutihinnatav = False
            yv.pallid = yv.toorpunktid = None
        else:
            # arvutame pallid kokku
            arvutihinnatav = not on_kasitsi
            yv.toorpunktid = toorpunktid
            yv.pallid = toorpunktid * koef

        if arvuti is not None:
            arvuti *= koef
        yv.pallid_arvuti = arvuti

        if kasitsi is not None:
            kasitsi *= koef
        yv.pallid_kasitsi = kasitsi

        if arvutihinnatav:
            yv.staatus = const.B_STAATUS_KEHTIV
        else:
            yv.staatus = const.B_STAATUS_KEHTETU

        # ylesande max pallid
        if ty.max_pallid is not None:
            yv.max_pallid = ty.max_pallid
        else:
            yv.max_pallid = ylesanne.max_pallid
            
        return yv, f_locals

    def delete_sooritaja(self, sooritaja):
        "Sooritaja kustutamine, kasutatakse testi eelvaate eemaldamisel"
        klaster_id = sooritaja.klaster_id
        if klaster_id:
            klaster_id, host = model.Klaster.get_klaster(klaster_id)
            if host:
                error = ExamClient(self.handler, host).delete_sooritaja(sooritaja.id)
        for tos in sooritaja.sooritused:
            sooritus_id = tos.id
            q = (model.Session.query(model.Soorituskomplekt)
                 .filter_by(sooritus_id=sooritus_id))
            for r in q.all():
                r.delete()
            q = (model.Session.query(model.Ylesandevastus)
                 .filter_by(sooritus_id=sooritus_id))
            for r in q.all():
                r.delete()
            q = (model.Session.query(model.Npvastus)
                 .filter_by(sooritus_id=sooritus_id))
            for r in q.all():
                r.delete()
        model.Session.flush()
        sooritaja.delete()
        
    def sooritus_ylesandevastused(self, sooritus, testiylesanne_id=None, komplekt_id=None, muudetav=None, kehtiv=True, ylesanne_id=None, vy=None):
        "Sooritusega seotud ylesandevastuste kirjed"
        li = []
        q = (model.Session.query(model.Ylesandevastus)
             .filter_by(sooritus_id=sooritus.id)
             )
        if testiylesanne_id:
            q = q.filter_by(testiylesanne_id=testiylesanne_id)
        if kehtiv:
            q = q.filter(model.Ylesandevastus.kehtiv==True)
        if muudetav:
            q = q.filter(model.Ylesandevastus.muudetav==True)
        if ylesanne_id:
            q = q.join((model.Valitudylesanne, model.Valitudylesanne.ylesanne_id==ylesanne_id))
        for rcd in q.all():
            if komplekt_id:
                # otsitakse antud komplekti kuuluva ylesande vastust
                vy2 = model.Valitudylesanne.get(rcd.valitudylesanne_id)
                if vy2 and vy2.komplekt_id == komplekt_id:
                    if (not vy or vy.id == vy2.id):
                        li.append(rcd)
            elif rcd.loplik:
                # otsitakse lõplikult valitud ylesande vastust
                li.append(rcd)
        return li

    def sooritus_get_ylesandevastus(self, sooritus, testiylesanne_id, komplekt_id=None, vy=None, muudetav=None, kehtiv=True, ylesanne_id=None):
        yv = None
        for rcd in self.sooritus_ylesandevastused(sooritus, testiylesanne_id,
                                                  komplekt_id=komplekt_id,
                                                  muudetav=muudetav, kehtiv=kehtiv,
                                                  vy=vy, ylesanne_id=ylesanne_id):
            yv = rcd
            if yv.loplik:
                break
            # vaatame edasi, kas leidub ka lõplik (valikylesandes)
            continue
        return yv

    def give_soorituskomplekt(self, sooritus_id, komplektivalik_id):
        q = (model.Session.query(model.Soorituskomplekt)
             .filter_by(sooritus_id=sooritus_id)
             .filter_by(komplektivalik_id=komplektivalik_id))
        rcd = q.first()
        if not rcd:
            rcd = model.Soorituskomplekt(sooritus_id=sooritus_id,
                                         komplektivalik_id=komplektivalik_id)
            model.Session.flush()
        return rcd
        
        
