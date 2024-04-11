from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
_ = i18n._
from .korrad import KorradController
from eis.handlers.ekk.korraldamine.valjastus import create_toimumisprotokollid
log = logging.getLogger(__name__)

class KutsekorradController(KorradController):
    """Kutseeksami testimiskorrad
    """
    _permission = 'testimiskorrad'
    _MODEL = model.Testimiskord
    _EDIT_TEMPLATE = 'ekk/testid/korrad.kutsekord.mako'
    _INDEX_TEMPLATE = 'ekk/testid/korrad.kutsekord.mako'
    _get_is_readonly = False
    _ITEM_FORM = forms.ekk.testid.KutseTestimiskordForm

    def _new(self, item):
        item.prot_vorm = const.PROT_VORM_ALATULEMUS
        item.testsessioon_id = model.Testsessioon.get_default(self.c.test.testiliik_kood)
        t_keeled = self.c.test.keeled
        if len(t_keeled) == 1:
            item.skeeled = self.c.test.lang
        for osa in self.c.test.testiosad:
            ta = model.Toimumisaeg(testimiskord=item,
                                   testiosa=osa,
                                   on_arvuti_reg=False,
                                   jatk_voimalik=True,
                                   eelvaade_admin=True,
                                   admin_maaraja=True,
                                   prot_admin=2)

    def _update(self, item, lang=None):
        self._bind_parent(item)
        vana_tahis = item.tahis
        vana_prot_tulemusega = item.prot_tulemusega
        if item.id and item.tahis != self.form.data['f_tahis']:
            self._check_unique()
        item.from_form(self.form.data, self._PREFIX, lang=lang)
        if item.tahis:
            item.tahis = item.tahis.upper()
        if vana_tahis and item.tahis != vana_tahis:
            for ta in item.toimumisajad:
                ta.set_tahised()
        self._update_lang(item)
        if not item.skeeled:
            raise ValidationError(self, {'lang_err': _("puudub")})

        # kutseeksami fikseeritud seaded
        item.prot_vorm = const.PROT_VORM_ALATULEMUS        
        item.tulemus_koolile = False 
        item.tulemus_admin = True
        item.osalemise_naitamine = True
        item.analyys_eraldi = True
        item.reg_ekk = True
        item.reg_sooritaja = item.reg_xtee = item.reg_kool_ehis = item.reg_kool_eis = item.reg_kool_valitud = False
        item.give_toimumisajad()
        model.Session.flush()
        
        dta = {r['testiosa_id']: r for r in self.form.data['ta']}
        for ind, ta in enumerate(item.toimumisajad):
            osa = ta.testiosa
            rcd = dta.get(osa.id)
            if rcd:
                prefix = 'ta-%d' % ind
                self._update_toimumisaeg(ta, osa, item, rcd, prefix)
                ta.jatk_voimalik = True
                ta.eelvaade_admin = True
                
        model.Testileping.give_for(item)

    def _update_toimumisaeg(self, item, testiosa, testimiskord, data, prefix):
        errors = {}
        # kutseeksami toimumisaja fikseeritud seaded
        item.jatk_voimalik = True
        item.eelvaade_admin = True
        item.prot_admin = 2
        item.from_form(data)
        
        if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):
            item.admin_maaraja = True
        elif testiosa.vastvorm_kood == const.VASTVORM_I:
            item.admin_maaraja = False
        # p-testi korral valib kasutaja, kas admin on nõutav,
        # sest EISil pole p-testi adminiga midagi teha;
        # e-testi korral on admin nõutav parajasti siis, kui on kirjalik test

        if testiosa.vastvorm_kood not in (const.VASTVORM_KE, const.VASTVORM_SE):
            # kui pole kirjalik e-test, siis ei ole arvutite regamise nõue asjakohane
            item.on_arvuti_reg = None
            
        gctrl = BaseGridController(item.toimumispaevad,
                                   model.Toimumispaev,
                                   parent_controller=self)
        gctrl.save(data.get('tpv'))
        li_aeg = []
        for ind, tpv in enumerate(item.toimumispaevad):
            if not tpv in gctrl.deleted:
                if tpv.kell:
                    tpv.aeg = datetime.combine(tpv.kuupaev, time(tpv.kell[0], tpv.kell[1]))
                else:
                    tpv.aeg = datetime.combine(tpv.kuupaev, time(0, 0))
                if tpv.a_lopp:
                    tpv.alustamise_lopp = datetime.combine(tpv.kuupaev, time(tpv.a_lopp[0], tpv.a_lopp[1]))
                    if tpv.alustamise_lopp < tpv.aeg:
                        errors['%s.tpv-%d.a_lopp' % (prefix, ind)] = _("Lõpp ei saa olla enne algust") 
                elif item.aja_jargi_alustatav:
                    errors['%s.tpv-%d.a_lopp' % (prefix, ind)] = _("Väärtus puudub")
                else:
                    tpv.alustamise_lopp = None
                li_aeg.append(tpv.aeg.date())

        vaikimisi_tpv = None
        for tpv in item.toimumispaevad:
            if not tpv in gctrl.deleted:        
                if vaikimisi_tpv is None:
                    vaikimisi_tpv = tpv
                for tr in tpv.testiruumid:
                    if not tr.algus or tr.algus.date() != tpv.kuupaev:
                        tr.muuda_algus(tpv.aeg)

        if vaikimisi_tpv:
            # määrame toimumispäeva nendele ruumidele, millel veel ei ole toimumispäeva,
            # kuna need ruumid loodi enne toimumispäevade loomist
            q = (model.Testiruum.query
                 .join(model.Testiruum.testikoht)
                 .filter(model.Testikoht.toimumisaeg_id==item.id)
                 .filter(model.Testiruum.toimumispaev_id==None))
            for tr in q.all():
                tr.toimumispaev = vaikimisi_tpv
                tr.muuda_algus(vaikimisi_tpv.aeg)

        if not len(li_aeg):
            errors['%s.tpv-0.kuupaev' % prefix] = _("Väärtus puudub")
        else:
            item.alates = min(li_aeg)
            item.kuni = max(li_aeg)
                 
        komplektid_id = data.get('komplekt_id')
        # komplekt ei saa olla kohustuslik, sest vbl ülesandeid veel koostatakse
        item.update_komplektid(komplektid_id)

        # kui vaatlejate/hindajate/intervjueerijate nõutavust on muudetud,
        # aga testikohad on juba määratud, siis tuleb vajadusel teha testikohtadele
        # läbiviijate kirjeid juurde
        for tk in item.testikohad:
            for tr in tk.testiruumid:
                tr.give_labiviijad()

                if item.on_arvuti_reg == False and tr.arvuti_reg != const.ARVUTI_REG_POLE:
                    # kui arvutite regamine pole nõutud, siis eemaldame regamise kõigilt ruumidelt
                    tr.arvuti_reg = const.ARVUTI_REG_POLE
                elif item.on_arvuti_reg == True and tr.arvuti_reg == const.ARVUTI_REG_POLE:
                    # kui arvutite regamine on nõutud, siis nõuame regamist kõigis ruumides
                    tr.arvuti_reg = const.ARVUTI_REG_LUKUS 

        if errors:
            raise ValidationError(self, errors)
        
        model.Session.flush()
        testimiskord.alates = min([ta.alates for ta in testimiskord.toimumisajad if ta.alates])
        testimiskord.kuni = max([ta.kuni for ta in testimiskord.toimumisajad if ta.kuni])
        if testimiskord.alates:
            testimiskord.aasta = testimiskord.alates.year
        item.update_aeg()
        
