from simplejson import dumps
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from eis.lib.resultentry import ResultEntry
from .ekspertvaatamised import EkspertvaatamisedController
from .hindajavaade_hkhindamine import get_tab_urls
import logging
log = logging.getLogger(__name__)

class EksperthindamisedController(EkspertvaatamisedController):
    """Eksperthindaja hindab või vaatab lahendaja kirjalikku lahendust.
    """
    _permission = 'eksperthindamine'
    _MODEL = model.Testiylesanne
    _INDEX_TEMPLATE = 'ekk/hindamine/ekspert.hindamine.mako'
    _EDIT_TEMPLATE = 'ekk/hindamine/ekspert.hindamine.ylesanne.mako'    
    _ITEM_FORM = forms.avalik.hindamine.KHindamineForm
    _get_is_readonly = False
    _actions = 'index,show,edit,create,update,download'

    def _ty_edit(self, ty_id):
        c = self.c

        if c.hindamiskogum:
            # kui toimub hindamine, leiame hindamise kirje
            if c.olen_ekspert or c.ettepanek or c.olen_hindaja6:
                # kui olen ekspert, siis broneeritakse see töö minu hindamiseks
                # või kui olen vaide korral hindamisel ettepaneku sisestaja
                self._give_hindamine()
                # salvestame hindamise kirje
                model.Session.commit()
            elif c.ekspert_labiviija:
                # kui olen ekspert, siis leitakse hindamise kirje, mida ma hakkan sisestama
                self._give_hindamine()

        super()._ty_edit(ty_id)

    def _get_tab_urls(self):
        # vasakul poolel ylesande avamise (GET) või hindamise salvestamise (POST) URL
        c = self.c
        h = self.h

        def f_submit_url(ty_id):
            if ty_id:
                # ylesande hindamine
                return h.url(f'hindamine_ekspert_hindamine', sooritus_id=c.sooritus.id, 
                             toimumisaeg_id=c.toimumisaeg.id, hindamiskogum_id=c.hindamiskogum_id, id=ty_id)
            else:
                # hindamiskogumi hindamiskriteeriumite hindamine
                return h.url(f'hindamine_ekspert_hindamised', sooritus_id=c.sooritus.id, 
                             toimumisaeg_id=c.toimumisaeg.id, hindamiskogum_id=c.hindaja_id)

        c.f_submit_url = f_submit_url

        get_tab_urls(self, self.c)

    def _update_mcomments(self, id):
        "Tekstis märgitud vigade ja kommentaaride automaatne salvestamine"
        c = self.c
        params = self.request.json_body
        yv = model.Ylesandevastus.get(params['yv_id'])
        assert yv.sooritus_id == c.sooritus.id, 'Vale sooritus'
        vy = yv.valitudylesanne
        k_id = int(params['k_id'])
        ksseq = int(params['ksseq'])
        kysimus = model.Kysimus.get(k_id)
        kv = yv.get_kysimusevastus(k_id)
        hindamine = self._give_hindamine()
        if kv and hindamine:
            yhinne = hindamine.give_ylesandehinne(yv, vy)
            ksm = yhinne.give_ksmarkus(kv, ksseq)
            ksm.markus = dumps(params['items'])
            model.Session.commit()
            res = {'result':'OK'}
        else:
            res = {'result':'NOK'}
        return Response(json_body=res)

    def _update(self, item):
        c = self.c
        params = self.request.params
        op = params.get('op')
        # lopeta - kinnita hindamine, tagasi nimistusse
        # (suulise hindamise korral parameeter lopeta, kirjaliku korral op)
        lopeta = op == 'lopeta' or self.request.params.get('lopeta')
        peata = op == 'peata' # peata
        labi = op == 'labi' # märgi läbivaadatuks

        if not c.ekspert_labiviija and not c.olen_ekspert and not c.olen_hindaja6:
            self.error(_("Kasutaja pole ekspert"))
            return self._redirect('show')

        hindamine = self._give_hindamine()
        if not hindamine:
            self.error(_("Tööd ei saa enam hinnata"))
            return self._redirect('show')

        self._save_hindamine(hindamine, lopeta, labi)
        return self._after_update(op)

    def _after_update(self, op):
        next_ty_id = self._get_next_id(op)
        if next_ty_id:
            url = self.url_current('edit', id=next_ty_id)
            return HTTPFound(location=url)
        return self._redirect_to_index(True)

    def _create(self, **kw):
        # hindamiskriteeriumitega hindamiskogumi hindamise salvestamine        
        return self._update(None)

    def _save_hindamine(self, hindamine, lopeta, labi):
        c = self.c
        holek = hindamine.hindamisolek
            
        sisestus = 1
        hindamine.komplekt = komplekt = holek.komplekt
        
        hindamine.hindaja_kasutaja_id = self.c.user.id
        hindamine.ksm_naeb_hindaja = self.form.data['ksm_naeb_hindaja']
        hindamine.ksm_naeb_sooritaja = self.form.data['ksm_naeb_sooritaja']

        resultentry = ResultEntry(self, const.SISESTUSVIIS_PALLID, c.testiosa.test, c.testiosa)
        sooritaja = c.sooritus.sooritaja
        if c.ekspert_labiviija:
            # toimub märkuste lisamine ainult
            resultentry.ekspert_labivaatus = True
        elif c.ettepanek:
            # vaide korral hindamise ettepaneku sisestamine
            # tyhjad väljad saavad väärtuseks kehtiva tulemuse
            resultentry.ekspert_ettepanek = True

        prefix = ''
        if c.testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
            resultentry.save_hindamine(sooritaja, self.form.data, lopeta, prefix, c.sooritus, holek, c.testiosa, hindamine, None, False)
        else:
            resultentry.save_ty_hindamine(sooritaja, self.form.data, lopeta, prefix, c.sooritus, holek, c.testiosa, hindamine, None, False)

        if c.ekspert_labiviija:
            labivaatus = hindamine.give_labivaatus(c.ekspert_labiviija.id)
            if labi:
                # ekspert kinnitab, et on läbi vaadanud
                labivaatus.staatus = const.B_STAATUS_KEHTIV

        if resultentry.errors:
            raise ValidationError(self, resultentry.errors)

        model.Session.commit()
        if lopeta and resultentry.error_lopeta:
            self.error(resultentry.error_lopeta)
            
        if hindamine.labiviija:
            hindamine.labiviija.calc_toode_arv()
            model.Session.commit()

    def _give_hindamine(self):           
        c = self.c
        if c.hindamiskogum.kursus_kood and c.hindamiskogum.kursus_kood != c.sooritaja.kursus_kood:
            log.error('Vale kursus (sooritaja %d kursus %s, hindamiskogum %d kursus %s)' % \
                      (c.sooritaja.id,
                       c.sooritaja.kursus_kood,
                       c.hindamiskogum.id,
                       c.hindamiskogum.kursus_kood))
            return
        holek = c.sooritus.give_hindamisolek(c.hindamiskogum)
        if c.olen_ekspert:
            # IV hindamine
            liik = const.HINDAJA4
            c.hindamine = holek.give_hindamine(liik,
                                                    hindaja_kasutaja_id=c.user.id)
            lv = model.Labiviija.give_hindaja(c.toimumisaeg.id, 
                                              c.user.id,
                                              liik, 
                                              c.testiosa, 
                                              c.hindamiskogum_id)
            c.hindamine.labiviija = lv
        #elif c.toimumisaeg.testimiskord.tulemus_kinnitatud and c.sooritus.sooritaja.vaie
        elif c.ekspert_labiviija or (c.olen_hindamisjuht and c.ettepanek):
            # vaide korral hindamine
            liik = const.HINDAJA5
            
            #if holek.hindamistase != const.HINDAJA5:
            #    # ei ole vaide korral hindamiseks mõeldud
            #    return
            c.hindamine = holek.give_hindamine(liik)
        elif c.olen_hindaja6:
            liik = const.HINDAJA6
            c.hindamine = holek.give_hindamine(liik,
                                                    hindaja_kasutaja_id=c.user.id)            
            lv = model.Labiviija.give_hindaja(c.toimumisaeg.id, 
                                              c.user.id,
                                              liik, 
                                              c.testiosa, 
                                              c.hindamiskogum_id)
            c.hindamine.labiviija = lv
        else:
            # ei saa midagi hinnata
            return

        holek.hindamistase = liik
        c.hindamine.komplekt = holek.komplekt
        model.Session.flush()
        return c.hindamine

    def __before__(self):
        super().__before__()

        c = self.c
        hindamiskogum_id = self.request.matchdict.get('hindamiskogum_id')
        if hindamiskogum_id:
            c.hindamiskogum = model.Hindamiskogum.get(hindamiskogum_id)
        if c.action != 'download':
            self._kas_ekspert()

    def _kas_ekspert(self):
        c = self.c
        c.sooritaja = c.sooritus.sooritaja

        testimiskord = c.toimumisaeg.testimiskord
        test = c.test

        if testimiskord.tulemus_kinnitatud and test.testiliik_kood != const.TESTILIIK_RV:
            # kui tulemused on kinnitatud, siis on võimalik V ja VI hindamine
            if c.sooritaja.vaie and \
                   c.sooritaja.vaie.staatus in (const.V_STAATUS_MENETLEMISEL, const.V_STAATUS_ETTEPANDUD):
                # töö kohta käib vaidemenetlus
                # kas olen vaide ekspert
                q = (model.Labiviija.query
                     .filter(model.Labiviija.kasutaja_id==c.user.id)
                     .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT)
                     .filter(model.Labiviija.toimumisaeg_id==c.toimumisaeg.id)
                     )
                c.ekspert_labiviija = q.first()
            elif c.user.has_permission('ekk-hindamine6', const.BT_UPDATE, obj=test):
                holek = c.sooritus.get_hindamisolek(c.hindamiskogum)
                if holek and holek.hindamistase == const.HINDAJA6:
                   c.olen_hindaja6 = True 

        elif not c.toimumisaeg.tulemus_kinnitatud or test.testiliik_kood == const.TESTILIIK_RV:
            # kas olen IV hindaja
            # EH-289: rahvusvahelise eksami korral toimub IV hindamine ka peale kinnitamist,
            # kuna vaidlustamine ei käi EISi kaudu
            c.olen_ekspert = c.user.has_group(const.GRUPP_HINDAMISEKSPERT, aine_kood=c.test.aine_kood)

