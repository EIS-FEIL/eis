from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister, ehis
from eis.forms import validators
log = logging.getLogger(__name__)

class KasutajadController(BaseResourceController):
    "Testide läbiviimisega seotud isikud"

    _MODEL = model.Kasutaja
    _SEARCH_FORM = forms.admin.KasutajadForm
    _ITEM_FORM = forms.admin.KasutajaForm
    _INDEX_TEMPLATE = '/admin/kasutajad.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = '/admin/kasutaja.mako' # muutmisvormi mall
    _LIST_TEMPLATE = '/admin/kasutajad_list.mako'
    _DEFAULT_SORT = 'perenimi'
    _ignore_default_params = ['ametikohad','csv']
    _permission = 'kasutajad'
    _get_is_readonly = False

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        c.header = self._prepare_header()
        c.prepare_row = self._prepare_row
        if c.kroll_id:
            q = model.SessionR.query(model.Kasutaja, model.Koht.nimi)
            today = date.today()
            f_kasutajaroll = model.Kasutaja.kasutajarollid.any(
                sa.and_(model.Kasutajaroll.kasutajagrupp_id==c.kroll_id,
                        model.Kasutajaroll.kehtib_alates<=today,
                        model.Kasutajaroll.kehtib_kuni>=today,
                        model.Kasutajaroll.koht_id==model.Koht.id)
                )
            if c.kroll_id in (const.GRUPP_K_ADMIN, const.GRUPP_K_JUHT):
                f_pedagoog = model.Kasutaja.pedagoogid.any(
                    sa.and_(model.Pedagoog.kasutajagrupp_id==c.kroll_id,
                            model.Pedagoog.koht_id==model.Koht.id))
                q = q.filter(sa.or_(f_kasutajaroll, f_pedagoog))
            else:
                q = q.filter(f_kasutajaroll)

        if c.kasped:
            today = date.today()
            q = q.filter(model.Kasutaja.pedagoogid.any(
                sa.and_(model.Pedagoog.on_ehisest==False,
                        sa.or_(model.Pedagoog.kehtib_kuni==None,
                               model.Pedagoog.kehtib_kuni>=today))
                ))
        if c.isikukood:
            q = q.filter(eis.forms.validators.IsikukoodP(c.isikukood).filter(model.Kasutaja))
            r = q.first()
            if r:
                kasutaja = c.kroll_id and r[0] or r
                if not kasutaja.on_labiviija:
                    self.error(_("See kasutaja ei ole seotud testide läbiviimisega"))
        else:
            q = q.filter(model.Kasutaja.on_labiviija==True)

        if c.epost:
            q = q.filter(model.Kasutaja.epost.ilike(c.epost))
        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))

        aineroll_id = c.roll_id not in (const.GRUPP_VAATLEJA, const.GRUPP_T_ADMIN) and c.roll_id
        if aineroll_id or c.aine:
            fli = []
            if aineroll_id:
                fli.append(model.Aineprofiil.kasutajagrupp_id==aineroll_id)
            if c.aine:
                fli.append(model.Aineprofiil.aine_kood==c.aine)
            q = q.filter(model.Kasutaja.aineprofiilid.any(sa.and_(*fli)))

        if c.tahis or c.roll_id in (const.GRUPP_VAATLEJA, const.GRUPP_T_ADMIN):
            q = q.join(model.Kasutaja.profiil)
            if c.roll_id == const.GRUPP_VAATLEJA:
                q = q.filter(model.Profiil.on_vaatleja==True)
            elif c.roll_id == const.GRUPP_T_ADMIN:
                q = q.filter(model.Profiil.on_testiadmin==True)                
            if c.tahis:
                fli = [model.Ainelabiviija.tahis==c.tahis]
                if c.aine:
                    fli.append(model.Ainelabiviija.aine_kood==c.aine)
                q = q.filter(model.Profiil.ainelabiviijad.any(sa.and_(*fli)))

        if c.testsessioon_id or c.test_id:
            if not c.nousolek and not c.maaratud:
                c.maaratud = True
            f = [model.Testimiskord.id==model.Toimumisaeg.testimiskord_id]
            if c.testsessioon_id:
                f.append(model.Testimiskord.testsessioon_id==c.testsessioon_id)
            if c.test_id:
                f.append(model.Testimiskord.test_id==c.test_id)

            if c.nousolek:
                f.append(model.Toimumisaeg.id==model.Nousolek.toimumisaeg_id)
                f.append(model.Nousolek.kasutaja_id==model.Kasutaja.id)
            if c.maaratud:
                f.append(model.Toimumisaeg.id==model.Labiviija.toimumisaeg_id)
                f.append(model.Labiviija.kasutaja_id==model.Kasutaja.id)
                if c.roll_id:
                    f.append(model.Labiviija.kasutajagrupp_id==c.roll_id)
            q = q.filter(sa.exists().where(sa.and_(*f)))

        k = c.user.get_kasutaja()
        piirkonnad_id = k.get_piirkonnad_id('kasutajad', const.BT_INDEX)
        if None not in piirkonnad_id:
            # kasutajal on antud õigus ainult teatud piirkonnis
            q = q.filter(model.Kasutaja.kasutajapiirkonnad.any(\
                    model.Kasutajapiirkond.piirkond_id.in_(piirkonnad_id)))

        if c.testsessioon_id and c.ametikohad:
            # värskendada ametikohtade andmed EHISest
            self._ehis_ametikohad(q)

        if c.csv:
            # väljastame CSV
            return self._index_csv(q)
        #model.log_query(q)
        return q

    def _search_default(self, q):
        """Otsingu tingimuste seadmine siis, kui otsing toimub 
        kohe otsinguvormi avamisel ja kasutaja pole veel saanud 
        otsingutingimusi valida.
        Kui soovitakse, et sellist vaikimisi otsingut ei tehtaks,
        siis tuleb tagastada None.
        """
        return None

    def _prepare_header(self):
        "Loetelu päis"
        li = [('isikukood', _("Isikukood")),
              ('eesnimi', _("Eesnimi")),
              ('perenimi', _("Perekonnanimi")),
              ('epost', _("E-post")),
              ]
        if self.c.kroll_id:
            li.append(('koht.nimi', _("Õppeasutus")))
        return li

    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        item, url = self._prepare_row(rcd, n)
        return item
    
    def _prepare_row(self, rcd, n=None):
        "Loetelu rida"
        if self.c.kroll_id:
            k, koht_nimi = rcd
            li = [k.isikukood,
                  k.eesnimi,
                  k.perenimi,
                  k.epost,
                  koht_nimi,
                  ]
        else:
            k = rcd
            li = [k.isikukood,
                  k.eesnimi,
                  k.perenimi,
                  k.epost]
        return li, self.url('admin_kasutaja', id=k.id)

    def _edit(self, item):
        self.c.can_set_pwd = self._can_set_pwd(item)
        if not item.id:
            # uue lisamine
            item.on_labiviija = True
        elif not item.on_labiviija:
            self.error(_("Kasutaja ei ole seotud testide läbiviimisega"))
            
    def _new(self, item):
        # kui uue isiku loomisel on isikukood ette antud, siis 
        # otsitakse selle isikukoodi järgi andmeid
        isikukood = self.request.params.get('isikukood')
        if isikukood:
            usp = eis.forms.validators.IsikukoodP(isikukood)
            if usp.isikukood:
                item2 = model.Kasutaja.get_by_ik(usp.isikukood)
                if item2:
                    self.c.item = item2
                elif self.request.is_ext() and usp.isikukood_ee:
                    # Eesti isikukood
                    self.c.item = item
                    xtee.set_rr_pohiandmed(self, item, usp.code)
                    model.Session.commit()
                    
    def _update(self, item):      
        is_new = not item.id
        item.from_form(self.form.data, 'k_')
        self._save_ik(item)
        item.kodakond_kood = self.form.data.get('kodakond_kood')
        parool = self.form.data.get('parool')
        if parool:
            if is_new or self._can_set_pwd(item):
                item.set_password(parool, True)
            else:
                self.error(_("Puudub õigus selle kasutaja parooli muutmiseks"))

        model.Aadress.adr_from_form(item, self.form.data, 'a_')
        item.give_profiil().from_form(self.form.data, 'p_')
        
    def _save_ik(self, item, voib_yh=False):
        c = self.c
        # synnikpv enne synnikpv või isikukoodi muutmist
        synnikpv = item.synnikpv

        ikkood = self.form.data.get('isikukood')
        riik = self.form.data.get('riik') or const.RIIK_EE
        # Eesti isikukood salvestatakse riigi prefiksita, muudel riikidel on prefiks ees
        if riik == const.RIIK_EE:
            ik = ikkood
        else:
            ik = f'{riik}{ikkood}'
        if ik and ik != item.isikukood:
            # isikukood muutus või lisati
            if c.user.on_admin or \
              (not item.isikukood and \
               (not item.id or c.user.has_permission('eksaminandid-ik', const.BT_UPDATE))):
                # kasutajal on õigus isikukoodi muuta
                # kontrollime isikukoodi reegleid
                usp = eis.forms.validators.IsikukoodP(ik)
                if not usp.isikukood:
                    raise ValidationError(self, {'isikukood': _("Vigases formaadis isikukood")})
                item2 = model.Kasutaja.get_by_ik(usp.isikukood)
                if item2 and item2.id != item.id:
                    # uue isikukoodiga isik on juba olemas
                    if item.isikukood and voib_yh:
                        # olemasoleva isikukoodi muutmine
                        # jätkub isikukirjete yhendamine (eksaminandid)
                        c.yhendaja_ik = ik
                        return self.edit()
                    # isikukoodita isikule isikukoodi andmine
                    model.Session.rollback()
                    self.error(_("Selle isikukoodiga kasutaja on juba olemas"))
                    raise HTTPFound(location=self.url('admin_kasutaja', id=item2.id))                
                        
                else:
                    # muudame isikukoodi
                    item.isikukood = usp.isikukood
                    
        # seatakse nimi, isikukood, synnikpv
        item.set_nimi()
        if self.request.is_ext():
            # kui synnikpv ja sugu on isikukoodiga seotud
            if synnikpv and synnikpv != item.synnikpv:
                raise ValidationError(self, {'k_synnikpv': _("Sünnikuupäev ei vasta isikukoodile")})
        
    def _can_set_pwd(self, kasutaja):
        # kparoolid-labiviija UPDATE - annab õiguse muuta parooli kasutajal, kes pole eksamikeskuse kasutaja
        # kparoolid UPDATE - annab õiguse muuta kõigi isikute paroole

        if self.c.user.has_permission('admin', const.BT_UPDATE):
            # admin saab kõigi kasutajate paroole muuta
            return True
        elif self.c.user.has_permission('kparoolid', const.BT_UPDATE):
            # ei saa muuta eksamikeskuse kasutajate paroole
            return not kasutaja.on_kehtiv_ametnik
        elif not kasutaja.id:
            # uue kasutaja loomisel saab talle parooli anda
            return True
        return False

    def _ehis_ametikohad(self, q):
        "Ametikohtade päring EHISest kõigi testsessiooni läbiviijate kohta"

        def _uuenda(isikukoodid):
            reg = ehis.Ehis(handler=self)
            message, ametikohad = reg.ametikohad(isikukoodid)
            if message:
                # tekkis viga
                return message
            else:
                d_isikud = dict()
                # jagame tulemused kasutajate kaupa
                for rcd in ametikohad:
                    ik = str(rcd.isikukood)
                    if ik not in d_isikud:
                        d_isikud[ik] = [rcd]
                    else:
                        d_isikud[ik].append(rcd)

                # uuendame iga kasutaja ametikohtade loetelu
                for isikukood in isikukoodid:
                    k = model.Kasutaja.get_by_ik(isikukood)
                    k_ametikohad = d_isikud.get(isikukood) or []
                    if k.update_pedagoogid(k_ametikohad):
                        xtee.uuenda_rr_pohiandmed(self, k)                    

                model.Session.commit()

        isikukoodid = []
        MAX_CNT = 500
        cnt = 0
        err = None
        for kasutaja in q.all():
            if kasutaja.isikukood:
                isikukoodid.append(kasutaja.isikukood)
            if len(isikukoodid) >= MAX_CNT:
                err = _uuenda(isikukoodid)
                isikukoodid = []
                if err:
                    break
                cnt += MAX_CNT

        if isikukoodid:
            err = _uuenda(isikukoodid)
            if not err:
                cnt += len(isikukoodid)

        if cnt or not err:
            self.success(_("Värskendatud {n} isiku andmed").format(n=cnt))
        if err:
            self.error(err)

    def _show_ehis(self, id):
        "Ametikohtade päring EHISest ühe isiku kohta"

        self.c.kasutaja = item = model.Kasutaja.get(id)
        reg = ehis.Ehis(handler=self)
        message, ametikohad = reg.ametikohad([item.isikukood])
    
        if message:
            self.error(message)
        else:
            if item.update_pedagoogid(ametikohad):
                xtee.uuenda_rr_pohiandmed(self, item)
            model.Session.commit()
        return self.render_to_response('/admin/kasutaja.ametikohad.mako')

    def _show_rr(self, id):
        "Isiku päring Rahvastikuregistrist"
        item = model.Kasutaja.get(id)
        err = None
        ik = item.isikukood
        if not ik:
            ik = self.request.params.get('isikukood')
            if not ik:
                err = _("Isikukood puudub")
        if not err:
            usp = validators.IsikukoodP(ik)
            if not usp.isikukood:
                err = _('Vigane isikukood "{s}"').format(s=ik)
            else:
                ik = usp.isikukood_ee
        if err:
            res = {'error': err}
        else:
            res = xtee.rr_pohiandmed_js(self, ik)
            kodakond = res.get('kodakond_kood')
            if kodakond and kodakond != item.kodakond_kood:
                item.kodakond_kood = kodakond
                model.Session.commit()
                res['kodakond_nimi'] = model.Klrida.get_str('KODAKOND', kodakond) or kodakond
        log.debug(res)
        return Response(json_body=res)

    def _empty_to_none(self, li):
        for rcd in li:
            for key, value in rcd.items():
                if value == '':
                    rcd[key] = None       

    def _create(self):
        item = model.Kasutaja()
        self._update(item)
        return item

