from simplejson import dumps
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from eis.lib.resultentry import ResultEntry
from eis.lib.pdf.vaideettepanek import VaideettepanekDoc
import eis.lib.ddocs as ddocs

import logging
log = logging.getLogger(__name__)

class EttepanekudController(BaseResourceController):
    """Eksperthindaja hindab lahendaja kirjalikku lahendust.
    """
    _permission = 'eksperthindamine'
    _MODEL = model.Sooritus
    _EDIT_TEMPLATE = 'ekk/hindamine/ekspert.ettepanek.mako'
    _ITEM_FORM = forms.avalik.hindamine.EttepanekForm
    _get_is_readonly = False

    def _view(self, item):
        self.c.show_tulemus = True
        if item.staatus != const.S_STAATUS_TEHTUD:
            self.notice(_("Sooritamise olek: {s}").format(s=item.staatus_nimi))

    def _edit(self, item):
        self._view(item)

        vaie = self.c.sooritaja.vaie
        if vaie.staatus == const.V_STAATUS_MENETLEMISEL or vaie.staatus == const.V_STAATUS_ETTEPANDUD:
            self._calc_pallid(vaie, False)
            model.Session.commit()
            if not vaie.ettepanek_pohjendus:
                if vaie.pallid_parast == vaie.pallid_enne:
                    if self.c.test.aine_kood == const.AINE_RK:
                        # tasemeeksam
                        pohjendus = _("eksamitöö on hinnatud vastavalt hindamisjuhendile.")
                    else:
                        pohjendus = _("põhjendusel, et eksamitöö on hinnatud vastavalt hindamisjuhendile.")
                else:
                    if self.c.test.aine_kood == const.AINE_RK:
                        pohjendus = ''
                    else:
                        pohjendus = _("põhjendusel, et ")
                vaie.ettepanek_pohjendus = pohjendus

    def _update(self, item):
        # vajutati nupule "Genereeri dokument"
        vaie = self.c.sooritaja.vaie

        # arvutatakse vaidejärgsed pallid
        self._calc_pallid(vaie, True)

        # kasutaja võis sisestada põhjenduse
        pohjendus = self.form.data.get('f_ettepanek_pohjendus')
        if pohjendus != vaie.ettepanek_pohjendus:
            if vaie.ettepanek_dok:
                # ettepanek on juba olemas
                self.notice(_("Senine ettepaneku dokument tühistati, kuna selle sisu on muudetud"))
                vaie.ettepanek_dok = None
                vaie.ettepanek_pdok = None
            vaie.ettepanek_pohjendus = pohjendus          

        if not vaie.ettepanek_pohjendus:
            raise ValidationError(self, {'f_ettepanek_pohjendus': _("Palun sisestada põhjendus")})

        for ta in self.c.sooritaja.testimiskord.toimumisajad:
            on_ekspertryhm = model.SessionR.query(sa.func.count(model.Labiviija.id)).\
                             filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT).\
                             filter(model.Labiviija.toimumisaeg_id==ta.id).\
                             scalar()
            if not on_ekspertryhm:
                self.error(_("Toimumisaja {s} jaoks ei ole ekspertrühma moodustatud").format(s=ta.tahised))
                return self._redirect('edit')                    
            
        self._gen_ettepanek_dok(self.c.sooritaja.vaie)

        # arvutame ekspertide tasu
        for tos in self.c.sooritaja.sooritused:
            q = model.SessionR.query(model.Labiviija).\
                filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT).\
                filter(model.Labiviija.toimumisaeg_id==tos.toimumisaeg_id)
            for lv in q.all():
                lv.calc_toode_arv()
                lv.tasu = lv.get_tasu()            
            
        model.Session.commit()
        return self._redirect('edit')

    def _calc_pallid(self, vaie, kinnita):
        "Arvutatakse vaidejärgne tulemus ja luuakse puuduvad hindamiskirjed"

        osapallid = 0
        for sooritus in self.c.sooritaja.sooritused:
            # loome hindamise kirjed kõigile ylesannetele, millele ekspert pole hinnet andnud
            # ja arvutame hindamised kokku
            osapallid += self._calc_pallid_sooritus(sooritus, kinnita) or 0

        max_pallid = self.c.sooritaja.max_pallid
        max_osapallid = self.c.sooritaja.max_osapallid
        sooritaja_pallid = osapallid * max_pallid / max_osapallid
        if self.c.sooritaja.test.ymardamine:
            sooritaja_pallid = round(sooritaja_pallid + 1e-12)        
        if (sooritaja_pallid or 0) != vaie.pallid_parast:
            # midagi on muudetud
            if vaie.ettepanek_dok:
                # ettepanek on juba olemas
                self.notice(_("Senine ettepaneku dokument tühistati, kuna selle sisu on muudetud"))
                vaie.ettepanek_ext = None
                vaie.ettepanek_dok = None
                vaie.ettepanek_pdok = None
            vaie.pallid_parast = sooritaja_pallid or 0
            vaie.muutus = vaie.pallid_parast - vaie.pallid_enne
            vaie.ettepanek_pohjendus = None
            

    def _calc_pallid_sooritus(self, sooritus, kinnita):
        """Arvutatakse vaidejärgne tulemus ja luuakse puuduvad hindamiskirjed
        (ettepaneku koostamise ajal, enne vaideotsuse koostamist)
        """
        log.debug('ETTEPANEKU ARVUTUS %s / %s' % (sooritus.id, sooritus.tahised))
        if sooritus.staatus != const.S_STAATUS_TEHTUD:
            sooritus.pallid_peale_vaiet = 0
            return 0

        if sooritus.ylesanneteta_tulemus:
            # ei kirjuta yle, sest ylesannete kaupa tulemusi ei ole
            # on ainult kogutulemus, mis sisestatakse otse dialoogiaknas
            return sooritus.pallid_peale_vaiet

        testiosa = sooritus.testiosa
        test = testiosa.test
        resultentry = ResultEntry(self, const.SISESTUSVIIS_PALLID, test, testiosa)
        sooritaja = sooritus.sooritaja
        resultentry.ekspert_ettepanek = True
        on_tulemustega = False
        alatestipallid = {}
        testiosa = sooritus.testiosa
        for holek in sooritus.hindamisolekud:
            hindamine = holek.give_hindamine(const.HINDAJA5)
            hindamine.komplekt_id = holek.komplekt_id
            holek.hindamistase = const.HINDAJA5
            hk_pallid = 0
            hkogum = holek.hindamiskogum
            arvutus = hkogum.arvutus_kood
            for ty in hkogum.testiylesanded:
                yv = sooritus.get_ylesandevastus(ty.id)
                if yv:
                    yhinne = hindamine.get_ylesandehinne(yv)
                    if not yhinne:
                        # loome hindamise kirje kehtivate tulemustega
                        yhinne = hindamine.give_ylesandehinne(yv, None)
                        yhinne.toorpunktid_kasitsi = yv.toorpunktid_kasitsi or 0
                        yhinne.toorpunktid = yv.toorpunktid or 0
                        yhinne.pallid_kasitsi = yv.pallid_kasitsi or 0
                        log.debug('set pk1=%s' % yv.pallid_kasitsi)
                        yhinne.pallid = yv.pallid or 0
                        if arvutus == const.ARVUTUS_SUMMA:
                            yhinne.toorpunktid_kasitsi /= 2.
                            yhinne.pallid_kasitsi /= 2.
                            yhinne.toorpunktid /= 2.
                            yhinne.pallid /= 2.

                    vy = yv.valitudylesanne
                    if ty.sisestusviis == const.SISESTUSVIIS_VASTUS and vy.ylesanne.arvutihinnatav:
                        oige = None
                    elif ty.sisestusviis == const.SISESTUSVIIS_OIGE:
                        oige = True
                    else:
                        oige = False

                    # arvutame arvutihinnatavad kysimused (siin ei arvesta aspekte)
                    y_pallid, y_toorpunktid, pallid_arvuti, pallid_kasitsi, tp_arvuti, tp_kasitsi = \
                              resultentry._calc_ty_kysimused(sooritaja, sooritus, yv, ty, vy, oige, yhinne=yhinne)

                    if len(yv.vastusaspektid) == 0:
                        yhinne.pallid_kasitsi = pallid_kasitsi
                        log.debug('set pk2=%s' % pallid_kasitsi)
                        yhinne.toorpunktid_kasitsi = tp_kasitsi
                        yhinne.pallid = y_pallid
                        yhinne.toorpunktid = y_toorpunktid
                    else:
                        yhinne.pallid = (yhinne.pallid_kasitsi or 0) + (pallid_arvuti or 0)
                        yhinne.toorpunktid = (yhinne.toorpunktid_kasitsi or 0) + (tp_arvuti or 0)

                    y_pallid = yhinne.pallid or 0
                    hk_pallid += y_pallid
                    if ty.alatest_id not in alatestipallid:
                        alatestipallid[ty.alatest_id] = 0
                    if arvutus == const.ARVUTUS_SUMMA:
                        y_pallid *= 2
                    alatestipallid[ty.alatest_id] += y_pallid
                    log.debug('%s yhinne.id=%s kasitsi=%s, kokku %s' % (ty.tahis, yhinne.id, self.h.fstr(yhinne.pallid_kasitsi), self.h.fstr(y_pallid)))

            #hindamine.pallid = hk_pallid
            if kinnita:
                hindamine.staatus = const.H_STAATUS_HINNATUD
                resultentry.update_hindamisolek(sooritaja, sooritus, holek, True, False)
            else:
                resultentry._calc_hindamine(sooritaja, sooritus, hindamine, hkogum, testiosa)
            log.debug('Hindamiskogumi %s pallid=%s (hindamine=%s, holek %s)\n' % (hkogum.tahis, self.h.fstr(hk_pallid), hindamine.id, holek.id))

        log.debug('alatestipallid: %s' % str(alatestipallid))
        if testiosa.test.on_tseis:
            # tasemeeksamite korral alatestide pallid ymardatakse
            for alatest_id in alatestipallid:
                alatestipallid[alatest_id] = round(alatestipallid[alatest_id] + 1e-12)
        #sooritus_pallid = round(sum(alatestipallid.values()) + 1e-12)
        sooritus_pallid = sum(alatestipallid.values())
        sooritus.pallid_peale_vaiet = sooritus_pallid or 0
        return sooritus_pallid

    def _gen_ettepanek_diff(self):
        vaie = self.c.sooritaja.vaie
        diff = {}
        for tos in self.c.sooritaja.sooritused:
            testiosa_tahis = tos.testiosa.tahis
            for holek in tos.hindamisolekud:
                hindamine = holek.get_hindamine(const.HINDAJA5)
                if hindamine:
                    for hinne in hindamine.ylesandehinded:
                        vastus = hinne.ylesandevastus
                        if hinne.pallid is not None and vastus.pallid != hinne.pallid:
                            ty = vastus.valitudylesanne.testiylesanne
                            diff[(testiosa_tahis, ty.alatest_seq, ty.seq)] = \
                                                  hinne.pallid - (vastus.pallid or 0)
        return diff


    def _gen_ettepanek_pdf(self, item):
        diff = self._gen_ettepanek_diff()
        doc = VaideettepanekDoc(self, item, diff)
        data = doc.generate()
        if doc.error:
            self.error(doc.error)
            return
        #item.ettepanek_txt = doc.txt
        return data

    def _gen_ettepanek_dok(self, item):
        # loome PDFi
        data_pdf = self._gen_ettepanek_pdf(item)
        if data_pdf:
            item.ettepanek_ext = const.PDF
            item.ettepanek_pdok = None
            item.ettepanek_dok = data_pdf
            model.Session.commit()
            
    def _update_prepare_signature(self, id):
        """Allkirjastamise alustamine: brauserilt on saadud sert,
        selle kohta arvutatakse allkirjastatav räsi.
        """
        sooritus = model.Sooritus.get(id)
        vaie = sooritus.sooritaja.vaie
        error = None
        if vaie.staatus != const.V_STAATUS_MENETLEMISEL and vaie.staatus != const.V_STAATUS_ETTEPANDUD:
            error =  _("Vaie on juba olekus {s}").format(s=vaie.staatus_nimi)

        elif vaie.ettepanek_dok is None:
            error = _("Ettepanekut pole koostatud")

        elif vaie.ettepanek_pdok is not None and vaie.modified > datetime.now() - timedelta(minutes=10):
            error = _("Allkirjastamine on juba pooleli")

        filename = 'ettepanek.%s' % vaie.ettepanek_ext
        filedata, res = ddocs.DdocS.prepare_signature(self, vaie.ettepanek_dok, filename, error)
        if filedata:
            # pistame faili andmebaasi
            vaie.ettepanek_pdok = filedata
            model.Session.commit()

        return res
    
    def _update_finalize_signature(self, id):
        """Allkirjastamise lõpetamine: brauserilt on saadud allkiri,
        see lisatakse pooleli oleva DDOC-faili sisse.
        """
        sooritus = model.Sooritus.get(id)
        vaie = sooritus.sooritaja.vaie

        if vaie.staatus != const.V_STAATUS_MENETLEMISEL and vaie.staatus != const.V_STAATUS_ETTEPANDUD:
            self.error(_("Vaie on juba olekus {s}").format(s=vaie.staatus_nimi))
        else:
            filedata, signers, dformat = ddocs.DdocS.finalize_signature(self, vaie.ettepanek_pdok)
            if filedata:
                # salvestame allkirjastatud faili
                vaie.ettepanek_dok = filedata
                vaie.ettepanek_ext = dformat
                # pooleli allkirjastamise andmed teeme tühjaks
                vaie.otsus_pdok = None
                model.Session.commit()

        return self._after_update(id)

    def _update_ddoc(self, id):
        sooritus = model.Sooritus.get(id)
        vaie = sooritus.sooritaja.vaie

        if self.request.params.get('edasta'):
            # edasta vaie 
            self._update_edasta(vaie)
        else:
            # faili üles laadimine
            self._update_upload(vaie)
        return self._redirect('edit')      

    def _update_upload(self, vaie):
        """Käsitsi antud allkirjaga DDOCi üles laadimine
        """
        f = self.request.params.get('ettepanek_dok')
        if f != b'':
            vaie.ettepanek_dok = f.value
            model.Session.commit()
            self.success(_("Fail on laaditud"))
        else:
            self.error(_("Palun laadi fail üles"))

    def __before__(self):
        c = self.c
        c.sooritus = model.Sooritus.get(self.request.matchdict.get('id'))        
        c.sooritaja = c.sooritus.sooritaja
        c.test = c.sooritaja.test
        c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))

        if c.sooritaja.vaie and not c.sooritaja.vaie.otsus_dok and \
                c.sooritaja.vaie.staatus in (const.V_STAATUS_MENETLEMISEL, const.V_STAATUS_ETTEPANDUD):
            c.olen_hindamisjuht = c.user.has_group(const.GRUPP_T_HINDAMISJUHT, c.test) \
                or c.user.has_group(const.GRUPP_HINDAMISJUHT, aine_kood=c.test.aine_kood)

        if not c.olen_hindamisjuht:
            c.is_edit = False

    def _perm_params(self):
        test = self.c.test
        return {'aine': test.aine_kood,
                'testiliik': test.testiliik_kood,
                }

    def _update_edasta(self, item):
        if item.staatus != const.V_STAATUS_MENETLEMISEL and item.staatus != const.V_STAATUS_ETTEPANDUD:
            self.error(_("Vaie on juba olekus {s}").format(s=item.staatus_nimi))
            return 
        if item.ettepanek_dok is None:
            self.error(_("Ettepanekut pole koostatud"))
            return

        kasutaja = self.c.sooritaja.kasutaja
        test = self.c.sooritaja.test
        item.staatus = const.V_STAATUS_ETTEPANDUD
        
        # kui on olemas vaidekomisjoni sekretär, siis saadetakse talle teade
        q = (model.Session.query(model.Kasutaja.id, model.Kasutaja.epost)
             .filter(model.Kasutaja.kasutajarollid.any(
                 sa.and_(model.Kasutajaroll.kasutajagrupp_id==const.GRUPP_VAIDEKOM_SEKRETAR,
                         model.Kasutajaroll.testiliik_kood==test.testiliik_kood,
                         model.Kasutajaroll.kehtib_alates<=datetime.now(),
                         model.Kasutajaroll.kehtib_kuni>=datetime.now())))
             )
        kasutajad = [(k_id, epost) for (k_id, epost) in q.all() if epost]
        if not kasutajad:
            # kui pole, siis saadetakse teade kõigile vaidekomisjoni liikmetele
            q = (model.Session.query(model.Kasutaja.id, model.Kasutaja.epost)
                 .filter(model.Kasutaja.kasutajarollid.any(
                     sa.and_(model.Kasutajaroll.kasutajagrupp_id==const.GRUPP_VAIDEKOM,
                             model.Kasutajaroll.testiliik_kood==test.testiliik_kood,
                             model.Kasutajaroll.kehtib_alates<=datetime.now(),
                             model.Kasutajaroll.kehtib_kuni>=datetime.now())))
                 )
            kasutajad = [(k_id, epost) for (k_id, epost) in q.all() if epost]
        li_epost = [r[1] for r in kasutajad]
        if len(li_epost):
            to = li_epost
            data = {'isik_nimi': kasutaja.nimi,
                    'test_nimi': test.nimi,
                    'user_nimi': self.c.user.fullname,
                    }
            subject, body = self.render_mail('mail/vaideettepanek.komisjonile.mako', data)
            body = Mailer.replace_newline(body)
            if not Mailer(self).send(to, subject, body):
                log.debug(_("Kiri saadetud vaidekomisjonile"))
                self.success(_("Kiri saadetud vaidekomisjonile aadressil {s}").format(s=', '.join(to)))
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                model.Sooritajakiri(sooritaja=self.c.sooritaja, kiri=kiri)
                for k_id, epost in kasutajad:
                    model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
        else:
            self.error(_("Vaidekomisjonile ei saa kirja saata, sest EIS ei tea vaidekomisjoni liikmeid või nende aadresse"))

        model.Session.commit()
        
    def _download(self, id, format):
        """Näita faili"""
        item = self._MODEL.get(id)
        vaie = item and item.sooritaja.vaie
        if not vaie:
            raise NotFound('Ei leitud')

        if format == 'pdf' and self.request.params.get('trykk'):
            # prinditav ettepaneku põhi (punktiirjoontega, käsitsi täitmiseks)
            doc = VaideettepanekDoc(self, vaie, None, True)
            filedata = doc.generate()
            if doc.error:
                self.error(doc.error)
                return self.index()
            filename = 'ettepanek.pdf'
        else:
            # digiallkirjastatav ettepanek (salvestatud fail - PDF või DDOC või BDOC)
            filedata = vaie.ettepanek_dok
            filename = 'ettepanek.%s' % (vaie.ettepanek_ext)

        if not filedata:
            raise NotFound('Dokumenti ei leitud')

        return utils.download(filedata, filename)

