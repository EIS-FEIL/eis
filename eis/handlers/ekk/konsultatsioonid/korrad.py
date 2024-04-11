# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
from eis.lib.basegrid import *
import eis.handlers.ekk.testid.korrad as korrad
log = logging.getLogger(__name__)
_ = i18n._

class KorradController(korrad.KorradController):
    """Konsultatsiooni testimiskorrad
    """
    _permission = 'konsultatsioonid'

    _MODEL = model.Testimiskord
    _EDIT_TEMPLATE = 'ekk/konsultatsioonid/kord.mako'
    _INDEX_TEMPLATE = 'ekk/konsultatsioonid/kord.mako'
    _ITEM_FORM = forms.ekk.konsultatsioonid.KordForm 
    _get_is_readonly = False

    def _index_d(self):
        res = BaseResourceController._index_d(self)
        return res

    def new(self, format='html'):
        mall_id = self.request.params.get('mall_id')
        if mall_id:
            return self._new_malliga(mall_id)
        
        copy_id = self.request.params.get('id')
        if copy_id:
            # tehakse koopia olemasolevast testimiskorrast
            item = model.Testimiskord.get(copy_id)
            self.c.item = item.copy()
            model.Session.commit()
            self.success(_('Testimiskord on kopeeritud!'))
            return self.render_to_response(self._EDIT_TEMPLATE)
        else:
            return BaseResourceController.new(self)

    def _new_malliga(self, mall_id):
        # mallist võtta uue toimumiskorra andmed

        def cp_testikohad(ta, m_ta):
            # TE/SE korral soorituskohtade ja läbiviijate kopeerimine
            testikohad_seq = 0
            for m_testikoht in m_ta.testikohad:
                testikohad_seq = max(testikohad_seq, int(m_testikoht.tahis))

                # lisame testikoha
                uus_testikoht = ta.give_testikoht(m_testikoht.koht_id)
                uus_testikoht.tahis = m_testikoht.tahis
                uus_testikoht.set_tahised()

                # lisame testiruumid
                map_testiruum = {}
                for m_testiruum in m_testikoht.testiruumid:
                    uus_testiruum = uus_testikoht.give_testiruum(m_testiruum.ruum_id, m_testiruum.tahis)
                    uus_testiruum.toimumispaev_id = None
                    uus_testiruum.nimekiri_id = None                    
                    map_testiruum[m_testiruum.id] = uus_testiruum

                # lisame läbiviijad
                for m_lv in m_testikoht.labiviijad:
                    if m_lv.kasutajagrupp_id == const.GRUPP_KONSULTANT:
                        m_testiruum_id = m_lv.testiruum_id
                        if m_testiruum_id:
                            uus_testiruum = map_testiruum[m_testiruum_id]
                            lv = uus_testiruum.create_labiviija(m_lv.kasutajagrupp_id)
                        else:
                            lv = uus_testikoht.create_labiviija(m_lv.kasutajagrupp_id)

                        lv.liik = m_lv.liik
                        lv.lang = m_lv.lang
                        lv.planeeritud_toode_arv = m_lv.planeeritud_toode_arv
                        lv.testikoht = uus_testikoht
                        lv.testiruum = uus_testiruum
                        lv.aktiivne = m_lv.aktiivne
                        kasutaja = m_lv.kasutaja
                        if kasutaja:
                            lv.set_kasutaja(kasutaja)

            ta.testikohad_seq = testikohad_seq

        mall = model.Testimiskord.get(mall_id)
        cp_tkord = model.EntityHelper.copy(mall)
        cp_tkord.test = self.c.test
        cp_tkord.tahis = '--autouniq' # et flushi ajal oleks unikaalne
        cp_tkord.tahis = cp_tkord.gen_tahis_new()
        cp_tkord.on_mall = False
        cp_tkord.valim_testimiskord_id = None

        testiosa = self.c.test.give_testiosa()
        for r in mall.piirkonnad:
            cp_tkord.piirkonnad.append(r)

        m_ta = mall.toimumisajad[0]
        cp_ta = model.EntityHelper.copy(m_ta)
        cp_ta.testiosa = testiosa
        cp_ta.testimiskord = cp_tkord
        cp_ta.set_tahised()
        cp_ta.testikohad_seq = 0
        cp_ta.alates = None
        cp_ta.kuni = None
        if self.c.test.on_tseis:
            # TE/SE korral lisada ka soorituskohad ja läbiviijad
            cp_testikohad(cp_ta, m_ta)

        model.Session.commit()
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _update(self, item, lang=None):
        self._bind_parent(item)
        vana_tahis = item.tahis
        item.from_form(self.form.data, self._PREFIX, lang=lang)
        item.tahis = item.tahis and item.tahis.upper() or None
        if vana_tahis and item.tahis != vana_tahis:
            for ta in item.toimumisajad:
                ta.set_tahised()
        self._update_lang(item)
        test = item.test or model.Test.get(item.test_id)
        if item.on_mall and not item.nimi:
            item.nimi = '%s %s' % (self.c.test.nimi, item.tahis)

        testiosa = test.give_testiosa()
        item.give_toimumisaeg(testiosa)
        self.c.toimumisaeg = toimumisaeg = item.toimumisajad[0]
        # konsultatsiooni toimumisajal ei toimu koguste arvutamist
        self.c.toimumisaeg.on_kogused = 1
        self.c.toimumisaeg.on_hindamisprotokollid = 1

        self.c.toimumisaeg.from_form(self.form.data, 'ta_', lang=lang)

        gctrl = BaseGridController(toimumisaeg.toimumispaevad,
                                   model.Toimumispaev,
                                   parent_controller=self)
        gctrl.save(self.form.data.get('tpv'))
        li_aeg = []
        for tpv in toimumisaeg.toimumispaevad:
            if not tpv in gctrl.deleted:
                if tpv.kell:
                    tpv.aeg = datetime.combine(tpv.kuupaev, time(tpv.kell[0], tpv.kell[1]))
                else:
                    tpv.aeg = datetime.combine(tpv.kuupaev, time(0, 0))
                li_aeg.append(tpv.aeg.date())

        for tpv in toimumisaeg.toimumispaevad:
            if not tpv in gctrl.deleted:        
                for tr in tpv.testiruumid:
                    if not tr.algus or tr.algus.date() != tpv.kuupaev:
                        tr.algus = tpv.aeg

        if not len(li_aeg):
            errors = {'tpv-0.kuupaev': _('Väärtus puudub')}
            raise ValidationError(self, errors)
        
        toimumisaeg.alates = min(li_aeg)
        toimumisaeg.kuni = max(li_aeg)

        # # kui rollide nõutavust on muudetud,
        # # aga testikohad on juba määratud, siis tuleb vajadusel teha testikohtadele
        # # läbiviijate kirjeid juurde
        # for tk in toimumisaeg.testikohad:
        #     for tr in tk.testiruumid:
        #         tr.give_labiviijad()

        toimumisaeg.flush()
        item.alates = toimumisaeg.alates
        item.kuni = toimumisaeg.kuni
        if item.alates:
            item.aasta = item.alates.year

        toimumisaeg.update_aeg()
        model.Testileping.give_for(item)
        
    def _update_lang(self, item):
        pass
    
    def _edit_eksam(self, id):
        self.c.item = model.Testimiskord.get(id)
        self.c.eksamid_id = [r.eksam_testimiskord_id for r in self.c.item.eksamikorrad]
        q = model.Session.query(model.Testimiskord.id, 
                                model.Test.id, 
                                model.Testimiskord.tahis, 
                                model.Test.nimi)
        q = q.filter(model.Testimiskord.testsessioon_id==self.c.item.testsessioon_id).\
            join(model.Testimiskord.test).\
            filter(model.Test.aine_kood==self.c.item.test.aine_kood).\
            filter(model.Test.testityyp==const.TESTITYYP_EKK)
        keeletase_kood = self.c.item.test.keeletase_kood
        if keeletase_kood:
            q = q.filter(model.Test.testitasemed.any(model.Testitase.keeletase_kood==keeletase_kood))

        self.c.items = q.all()
        self.c.on_kons = True
        return self.render_to_response('ekk/konsultatsioonid/kons.eksamid.mako')

    def _update_eksam(self, id):
        item = model.Testimiskord.get(id)
        id_list = [r.eksam_testimiskord_id for r in item.eksamikorrad]

        posted_id_list = list(map(int, self.request.params.getall('kord_id')))
        for kord_id in posted_id_list:
            if kord_id in id_list:
                # juba olemas, andmebaasis ei muuda midagi
                id_list.remove(kord_id)
            else:
                # lisame
                rcd = model.Testikonsultatsioon(eksam_testimiskord_id=kord_id,
                                                kons_testimiskord_id=item.id)
                item.eksamikorrad.append(rcd)

        for kord_id in id_list:
            # eemaldame
            rcd = model.Testikonsultatsioon.query.\
                filter_by(eksam_testimiskord_id=kord_id).\
                filter_by(kons_testimiskord_id=item.id).\
                first()
            if rcd:
                rcd.delete()

        model.Session.commit()
        self.success()

        return self._redirect('edit', id)

