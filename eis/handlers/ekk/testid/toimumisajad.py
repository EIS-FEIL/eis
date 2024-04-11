from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
import eis.lib.sebconfig as sebconfig
_ = i18n._

log = logging.getLogger(__name__)

class ToimumisajadController(BaseResourceController):

    _permission = 'testimiskorrad'
    _MODEL = model.Toimumisaeg
    _EDIT_TEMPLATE = 'ekk/testid/korrad.toimumisaeg.mako'
    _ITEM_FORM = forms.ekk.testid.ToimumisaegForm 

    def _show(self, item):
        if self.c.test.on_kutse:
            # kutseeksami toimumisaja vorm on mujal
            raise HTTPFound(location=self.url('test_kutse_kord', test_id=self.c.test.id, id=item.testimiskord_id))
        return self._edit(item)
            
    def _edit(self, item):
        q = (model.Session.query(model.Hindamiskogum.id, model.Hindamiskogum.nimi)
             .filter(model.Hindamiskogum.testiosa_id==item.testiosa_id)
             .filter(model.Hindamiskogum.staatus==const.B_STAATUS_KEHTIV)
             .order_by(model.Hindamiskogum.nimi))
        self.c.opt_hindamiskogum = [(r_id, r_nimi) for (r_id, r_nimi) in q.all()]
        self.c.opt_veriff = self._opt_veriff_integration()

    def _opt_veriff_integration(self):
        settings = self.request.registry.settings
        li = []
        ids = settings.get('veriff.integrations')
        if ids:
            for int_id in ids.split():
                int_id = int_id.strip()
                if int_id:
                    name = settings.get(f'veriff.{int_id}.name')
                    li.append((int_id, name))
        return li
    
    def _update(self, item, lang=None):
        errors = {}
        self._bind_parent(item)
        oli_seb = item.verif_seb
        item.from_form(self.form.data, self._PREFIX, lang=lang)

        # hindamise alguse aeg
        h_algus_kp = self.form.data['hindamise_algus_kp']
        h_algus_kell = self.form.data['hindamise_algus_kell']
        if h_algus_kp:
            if h_algus_kell:
                tm = time(h_algus_kell[0], h_algus_kell[1])
            else:
                tm = time(0,0)
            item.hindamise_algus  = datetime.combine(h_algus_kp, tm)
        else:
            item.hindamise_algus = None
            
        item.prot_admin = self.form.data['prot_admin2'] or self.form.data['prot_admin1'] or const.PROT_NULL
        if item.on_veriff:
            item.verif_param = self.form.data.get('veriff_int_id')
        if item.verif_seb and not oli_seb and not item.seb_konf:
            # märgiti SEB, genereerime vaikimisi SEB konfi
            item.seb_konf = sebconfig.generate()
        elif not item.verif_seb and oli_seb:
            # eemaldati SEB, eemaldame konfi
            item.seb_konf = None
            
        item.ruum_noutud = not self.form.data.get('ruum_maaramata')
        testiosa = item.testiosa
        # testi admin on nõutav parajasti siis, kui on kirjalik e-test
        item.admin_maaraja = testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE)
            
        if testiosa.vastvorm_kood not in (const.VASTVORM_KE, const.VASTVORM_SE):
            # kui pole kirjalik e-test, siis ei ole arvutite regamise nõue asjakohane
            item.on_arvuti_reg = None

        self.c.item = item
        gctrl = BaseGridController(item.toimumispaevad,
                                   model.Toimumispaev,
                                   parent_controller=self)
        tpvdata = self.form.data.get('tpv')
        gctrl.save(tpvdata)
        on_valim = len([r for r in tpvdata if r['valim']]) > 0
        toimumispaevad = list(item.toimumispaevad)
        
        li_aeg = []
        for ind, tpv in enumerate(toimumispaevad):
            if not tpv in gctrl.deleted:
                if not tpv.valim:
                    # kui pole valimi sooritajate aeg
                    if on_valim:
                        # valimi sooritajatele keelatud
                        tpv.valim = False
                    else:
                        # valimi piiranguid pole
                        tpv.valim = None
                if tpv.kell:
                    tpv.aeg = datetime.combine(tpv.kuupaev, time(tpv.kell[0], tpv.kell[1]))
                else:
                    # kell 00.00 tähendab, et kellaaeg on määramata
                    tpv.aeg = datetime.combine(tpv.kuupaev, time(0, 0))

                if tpv.d_lopp or tpv.t_lopp:
                    if not tpv.d_lopp:
                        tpv.d_lopp = tpv.kuupaev
                    if not tpv.t_lopp:
                        tpv.t_lopp = (23,59)
                    tpv.lopp = datetime.combine(tpv.d_lopp, time(tpv.t_lopp[0], tpv.t_lopp[1]))                    
                    if tpv.lopp < tpv.aeg:
                        errors = {f'tpv-{ind}.d_lopp': _("Lõpp ei saa olla enne algust")}
                    li_aeg.append(tpv.lopp.date())
                else:
                    tpv.lopp = None
                li_aeg.append(tpv.aeg.date())

            
        # järjestame aja järgi ja määrame jrk nr ehk seansi
        toimumispaevad.sort(key=lambda tpv: (tpv.aeg, tpv.seq, tpv.id))
        for ind, tpv in enumerate(toimumispaevad):
            tpv.seq = ind + 1
                
        vaikimisi_tpv = None
        for tpv in toimumispaevad:
            if not tpv in gctrl.deleted:        
                if vaikimisi_tpv is None:
                    vaikimisi_tpv = tpv
                for tr in tpv.testiruumid:
                    # toimumisaja seadetes kellaaja muutmisel muudetakse algus ja lõpp
                    # nendes sama toimumispäeva ruumides, kus on teine kuupäev
                    # või on seadistatud, et soorituskoha kellaaega ei saa vabalt sisestada ja ruumis on teine kellaaeg
                    # või on ruumis lõpu aeg ja toimumisaja seadetes ei ole lõpu aega
                    if not tr.algus \
                           or tr.algus.date() != tpv.kuupaev \
                           or item.kell_valik and (tr.algus != tpv.aeg or tr.lopp != tpv.lopp) \
                           or not tr.lopp and tpv.lopp:
                        tr.muuda_algus(tpv.aeg)
                        tr.lopp = tpv.lopp
                        model.Sooritus.set_piiraeg_muutus(testiosa.id, testiruum_id=tr.id)
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
                tr.lopp = vaikimisi_tpv.lopp

        if not len(li_aeg):
            errors['tpv-0.kuupaev'] = _("Väärtus puudub")

        if item.hindaja2_maaraja or item.hindaja2_maaraja_valim:
            # kas leidub mõni kahekordse hindamisega hindamiskogum?
            li = [hk for hk in testiosa.hindamiskogumid if hk.kahekordne_hindamine or hk.kahekordne_hindamine_valim]
            if not li:
                if item.hindaja2_maaraja:
                    errors['f_hindaja2_maaraja'] = _("Testiosas pole ühtki kahekordse hindamisega hindamiskogumit!")
                elif item.hindaja2_maaraja_valim:
                    errors['f_hindaja2_maaraja_valim'] = _("Testiosas pole ühtki kahekordse hindamisega hindamiskogumit!")                    
            
        if errors:
            raise ValidationError(self, errors)
        
        item.alates = min(li_aeg)
        item.kuni = max(li_aeg)

        YmbrikuliikGridController(item.valjastusymbrikuliigid,
                                  model.Valjastusymbrikuliik,
                                  parent_controller=self).\
            save(self.form.data.get('vb'))

        if item.valjastuskoti_maht:
            for r in item.valjastusymbrikuliigid:
                if r.maht and r.maht > item.valjastuskoti_maht:
                    errors = {'f_valjastuskoti_maht': _("Turvakott peab iga ümbrikuliigi korral mahutama vähemalt ühe ümbrikutäie töid")}
                    raise ValidationError(self, errors)   

        TagastusymbrikuliikGridController(item.tagastusymbrikuliigid,
                                          model.Tagastusymbrikuliik,
                                          parent_controller=self)\
            .save(self.form.data.get('tb'))

        if item.tagastuskoti_maht:
            for r in item.tagastusymbrikuliigid:
                if r.maht and r.maht > item.tagastuskoti_maht:
                    errors = {'f_tagastuskoti_maht': _("Turvakott peab iga ümbrikuliigi korral mahutama vähemalt ühe ümbrikutäie töid")}
                    raise ValidationError(self, errors)   
                 
        komplektid_id = self.form.data.get('komplekt_id')
        # komplekt ei saa olla kohustuslik, sest vbl ülesandeid veel koostatakse
        item.update_komplektid(komplektid_id)

        # kui vaatlejate/hindajate/intervjueerijate nõutavust on muudetud,
        # aga testikohad on juba määratud, siis tuleb vajadusel teha testikohtadele
        # läbiviijate kirjeid juurde
        for tk in item.testikohad:
            for tr in tk.testiruumid:
                tr.give_labiviijad(tk)
                if item.on_arvuti_reg == False and tr.arvuti_reg != const.ARVUTI_REG_POLE:
                    # kui arvutite regamine pole nõutud, siis eemaldame regamise kõigilt ruumidelt
                    tr.arvuti_reg = const.ARVUTI_REG_POLE
            
        item.flush()
        testimiskord = item.testimiskord
        testimiskord.alates = min([ta.alates for ta in testimiskord.toimumisajad if ta.alates])
        testimiskord.kuni = max([ta.kuni for ta in testimiskord.toimumisajad if ta.kuni])
        if testimiskord.alates and not testimiskord.aasta:
            testimiskord.aasta = testimiskord.alates.year
        item.update_aeg()

    def _show_proctorio(self, id):
        c = self.c
        c.item = model.Toimumisaeg.get(id)
        template = '/ekk/testid/verif.proctorio.mako'
        return self.render_to_response(template)

    def _edit_proctorio(self, id):
        return self._show_proctorio(id)

    def _update_proctorio(self, id):
        item = model.Toimumisaeg.get(id)
        verif_params = self.request.params.getall('verif_param') or []
        if not verif_params:
            self.error(_("Palun vali, milleks Proctoriot kasutatakse"))
            return self._edit_proctorio(id)
        item.verif_param = ','.join(verif_params)
        model.Session.commit()
        html = '<script>close_dialog();</script>'
        return Response(html)

    def _show_seb(self, id):
        "SEB seadete akna kuvamine"
        c = self.c
        c.item = model.Toimumisaeg.get(id)
        if not c.item.seb_konf:
            # kui konfi ei ole, siis luuakse
            c.item.seb_konf = sebconfig.generate()
            model.Session.commit()
        template = '/ekk/testid/verif.seb.mako'
        return self.render_to_response(template)

    def _edit_seb(self, id):
        return self._show_seb(id)

    def _update_seb(self, id):
        "SEB seadete salvestamine"
        item = model.Toimumisaeg.get(id)
        value = self.request.params.get('seb_konf')
        if self.request.params.get('genereeri'):
            # uue kirjelduse genereerimine
            item.seb_konf = sebconfig.generate()
            model.Session.commit()
            self.success(_("Genereeriti uus fail"))
        elif value == b'':
            self.error(_("Fail puudub"))
        else:
            # SEB Configuration Tool tehtud faili laadimine
            filedata = value.value
            if sebconfig.check_plist(filedata):
                item.seb_konf = filedata
                model.Session.commit()
                self.success(_("Fail on salvestatud!"))
            else:
                self.error(_("Seda faili ei saanud lugeda (palun kasutada krüptimata faili)"))
                
        return self._edit_seb(id)

    def _download(self, id, format=None):
        "SEB konfi allalaadimine"
        item = model.Toimumisaeg.get(id)
        filedata = item and item.seb_konf
        if not filedata:
            raise NotFound('Kirjet %s ei leitud' % id)
        #filedata = sebconfig.compress_plain(filedata)
        mimetype = 'application/octet-stream'
        filename = 'SEB-%s.seb' % (item.tahised)
        return utils.download(filedata, filename, mimetype)
    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(test_id)
        
        BaseResourceController.__before__(self)

    def _perm_params(self):
        return {'obj':self.c.test}


class YmbrikuliikGridController(BaseGridController):
    def create_subitem(self, rcd, lang=None):
        subitem = self._MODEL(toimumisaeg=self.parent_controller.c.item)
        subitem.gen_tahis()
        subitem.from_form(rcd, lang=lang)
        self.seq += 1
        subitem.seq = self.seq
        self._COLLECTION.append(subitem)
        if self.parent and self.parent.id:
            subitem.parent_id = self.parent.id
        return subitem

class TagastusymbrikuliikGridController(YmbrikuliikGridController):
    def create_subitem(self, rcd, lang=None):
        subitem = YmbrikuliikGridController.create_subitem(self, rcd, lang)
        self._save_hk(subitem, rcd)
        return subitem

    def update_subitem(self, subitem, rcd, lang=None):
        subitem = YmbrikuliikGridController.update_subitem(self, subitem, rcd, lang)
        self._save_hk(subitem, rcd)
        return subitem
    
    def _save_hk(self, subitem, rcd):
        hindamiskogumid_id = rcd['hindamiskogum_id']
        for hk in list(subitem.hindamiskogumid):
            try:
                hindamiskogumid_id.remove(hk.id)
            except ValueError:
                subitem.hindamiskogumid.remove(hk)
        for hk_id in hindamiskogumid_id:
            hk = model.Hindamiskogum.get(hk_id)
            subitem.hindamiskogumid.append(hk)
