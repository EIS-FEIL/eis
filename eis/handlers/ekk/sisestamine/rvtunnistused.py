# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController

log = logging.getLogger(__name__)
_ = i18n._

class RvtunnistusedController(BaseResourceController):
    """Rahvusvaheliste eksamite soorituste sisestamine
    """
    _permission = 'sisestamine'
    _MODEL = model.Rvsooritaja
    _INDEX_TEMPLATE = 'ekk/sisestamine/rvtunnistused.mako'
    _EDIT_TEMPLATE = 'ekk/sisestamine/rvtunnistus.mako'
    #_DEFAULT_SORT = 'sooritus.tahised'
    _SEARCH_FORM = forms.ekk.sisestamine.RvtunnistusedForm
    _ITEM_FORM = forms.ekk.sisestamine.RvtunnistusForm
    _get_is_readonly = False
    _ignore_default_params = ['otsi', 'otsinimi', 'kasutaja_id', 'uus', 'failiga']
    
    def index(self):
        if self.request.params.get('failiga'):
            rveksam_id = self.request.params.get('rveksam_id')
            if rveksam_id:
                return HTTPFound(location=self.url('sisestamine_rvtunnistused_new_fail', rveksam_id=rveksam_id))
        return BaseResourceController.index(self)
    
    def _search_default(self, q):
        pass

    def _search(self, q1):
        c = self.c
        
        if not c.otsi and not c.otsinimi and not c.uus and not c.kasutaja_id:
            # kui ei vajutatud sisestamise nupule
            return

        if not c.rveksam_id:
            self.error(_('Palun valida eksam'))
            return
        
        kasutaja = None
        if c.kasutaja_id:
            # isik on valitud loetelust
            kasutaja = model.Kasutaja.get(c.kasutaja_id)

        elif c.otsi:
            if not c.isikukood:
                self.error(_('Palun sisestada isikukood'))
                return
            else:
                # sisestati isikukood
                kasutaja = model.Kasutaja.get_by_ik(c.isikukood)
                if not kasutaja:
                    # kui kasutajat EISis pole, siis otsime RRist
                    kasutaja = xtee.set_rr_pohiandmed(self, None, c.isikukood)            
                    if not kasutaja:
                        # kui kasutajat ei ole EISis ega ka RRis, siis pole midagi teha
                        return
                    # salvestame loodud kasutaja
                    model.Session.commit()

        elif c.otsinimi:
            if not (c.synnikpv and c.eesnimi and c.perenimi):
                self.error(_('Palun sisestada sünnikuupäev, eesnimi ja perekonnanimi'))
                return
            else:
                # sisestati nimi, kuvame valiku
                q = (model.Kasutaja.query
                     .filter(model.Kasutaja.synnikpv==c.synnikpv)
                     .filter(model.Kasutaja.eesnimi==c.eesnimi)
                     .filter(model.Kasutaja.perenimi==c.perenimi)
                     )
                return q

        elif c.uus:
            if c.synnikpv and c.eesnimi and c.perenimi:
                # lisada uus isik
                kasutaja = model.Kasutaja.add_kasutaja(None,
                                                       c.eesnimi,
                                                       c.perenimi,
                                                       c.synnikpv)
                model.Session.commit()
            
        if not kasutaja:
            self.error(_('Palun sisestada isikukood või sünniaeg ja nimi'))
            return

        rcd = model.Rvsooritaja.query.\
              filter(model.Rvsooritaja.rveksam_id==c.rveksam_id).\
              join(model.Rvsooritaja.tunnistus).\
              filter(model.Tunnistus.kasutaja_id==kasutaja.id).\
              first()
        if rcd:
            # tunnistus on juba olemas
            return self._redirect('edit', id=rcd.id)
        else:
            return self._redirect('new', kasutaja_id=kasutaja.id, rveksam_id=c.rveksam_id)
       
    def _new(self, item):
        self.c.tunnistus = self.c.new_item()
        item.arvest_lopetamisel = True

        k_id = self.request.params.get('kasutaja_id')
        if k_id:
            self.c.kasutaja = model.Kasutaja.get(k_id)
        if not self.c.kasutaja:
            self.error(_('Sooritaja on valimata'))
            raise self._redirect('index')
        else:
            self.c.tunnistus.eesnimi = self.c.kasutaja.eesnimi
            self.c.tunnistus.perenimi = self.c.kasutaja.perenimi
            
        rv_id = self.request.params.get('rveksam_id')
        if rv_id:
            self.c.rveksam = model.Rveksam.get(rv_id)
        if not self.c.rveksam:
            self.error(_('Eksam on valimata'))
            raise self._redirect('index')            

        self.c.sooritajad = self._get_sooritajad(self.c.kasutaja.id, self.c.rveksam.id)

    def _edit(self, item):
        if item.tunnistus:
            self.c.tunnistus = item.tunnistus
            self.c.kasutaja = item.tunnistus.kasutaja
        if item.rveksam:
            self.c.rveksam = item.rveksam

        self.c.sooritajad = self._get_sooritajad(self.c.kasutaja.id, self.c.rveksam.id)

    def _get_sooritajad(self, kasutaja_id, rveksam_id):
        # leiame testisooritused, kust võtta punktid tunnistusele
        q = (model.Sooritaja.query
             .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
             .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
             .join(model.Sooritaja.test)
             .filter(model.Test.rveksam_id==rveksam_id)
             .order_by(model.sa.desc(model.Sooritaja.algus))
             )
        return q.all()
            
    def _create(self, **kw):
        rveksam_id = self.form.data['rveksam_id']
        kasutaja_id = self.form.data['kasutaja_id']
        
        item = model.Rvsooritaja(rveksam_id=rveksam_id)
        item.tunnistus = model.Tunnistus(kasutaja_id=kasutaja_id,
                                         seq=0)

        # # kanname õpilase kooli rvsooritaja kirjesse, statistika jaoks
        # kasutaja = model.Kasutaja.get(kasutaja_id)
        # opilane = kasutaja.opilane
        # if opilane and not opilane.on_lopetanud:
        #     item.kool_koht_id = opilane.koht_id
            
        self._update(item)
        return item

    def _update(self, item):
        # omistame vormilt saadud andmed
        item.from_form(self.form.data, 'f_')
        tunnistus = item.tunnistus
        tunnistus.from_form(self.form.data, 't_')
        #if tunnistus.valjastamisaeg:
        #    tunnistus.oppeaasta = tunnistus.valjastamisaeg.year
        # bugzilla-140 2017-10-06: rv tunnistuste õppeaastana tuleb arvestada tunnistuse sisestamise aega
        created = tunnistus.created or date.today()
        tunnistus.oppeaasta = created.month > 8 and created.year + 1 or created.year
        # määrame saadud keeleoskuse taseme
        rveksam = model.Rveksam.get(item.rveksam_id)
        if rveksam.keeletase_kood:
            item.keeletase_kood = rveksam.keeletase_kood
        elif item.rveksamitulemus_id:
            tulemus = model.Rveksamitulemus.get(item.rveksamitulemus_id)
            item.keeletase_kood = tulemus.keeletase_kood
        item.sooritaja_id = self.form.data.get('sooritaja_id') or None
        if item.sooritaja_id:
            sooritaja = model.Sooritaja.get(item.sooritaja_id)
            test = sooritaja.test
            if not (len(test.testitasemed) and test.testitasemed[0].pallid is not None):
                # kui EIS ei anna testi eest taset, siis omistame tunnistuse taseme testisooritusele ka
                sooritaja.keeletase_kood = item.keeletase_kood

        #j = item.sooritaja
        #jtase = j.keeletase_kood
        
        BaseGridController(item.rvsooritused,
                           model.Rvsooritus,
                           pkey='rvosaoskus_id').\
                           save(self.form.data.get('osa'))
        
