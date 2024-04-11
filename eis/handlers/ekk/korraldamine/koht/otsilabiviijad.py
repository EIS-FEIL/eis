from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class OtsilabiviijadController(BaseResourceController):
    """Läbiviijate otsimine dialoogiaknas.
    """
    _permission = 'korraldamine'
    _MODEL = model.Kasutaja
    _INDEX_TEMPLATE = 'ekk/korraldamine/koht.otsilabiviijad.mako'
    _DEFAULT_SORT = 'kasutaja.perenimi,kasutaja.eesnimi' # vaikimisi sortimine
    _no_paginate = True
    _get_is_readonly = False # labiviijaprofiil.mako
    
    def _search(self, q1):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        self.c.grupp_id = int(self.c.grupp_id)

        # kui kool või EKK määrab suulise osa hindajaid, siis need ei pea olema eelnevalt käskkirja kantud,
        # kuna käskkirja kantakse nad alles peale määramist (EH-300)
        testiosa = self.c.toimumisaeg.testiosa
        if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
            on_kaskkiri = False
        else:
            on_kaskkiri = True
            
        # get_valik_q() tuleb kutsuda siit, mitte _query() seest, 
        # kuna seal ei ole veel self.c.* seatud
        q = self.c.testikoht.get_valik_q(self.c.grupp_id, on_piirkond=False, lang=self.c.lang, on_kaskkiri=on_kaskkiri)

        if self.c.isikukood:
            q = q.filter(eis.forms.validators.IsikukoodP(self.c.isikukood)
                         .filter(model.Kasutaja))
        if self.c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(self.c.eesnimi))
        if self.c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(self.c.perenimi))

        if self.c.piirkond_id:
            piirkond = model.Piirkond.get(self.c.piirkond_id)
            piirkonnad_id = piirkond.get_ylemad_id()
            q = q.filter(model.Kasutaja.kasutajapiirkonnad.any(\
                    model.Kasutajapiirkond.piirkond_id.in_(piirkonnad_id)))
            
        if self.c.nous_kord or self.c.nous_sess or self.c.nous:
            grupp_id = self.c.grupp_id
            if grupp_id in (const.GRUPP_HINDAJA_S, 
                            const.GRUPP_HINDAJA_S2, 
                            const.GRUPP_HINDAJA_K): 
                field = model.Nousolek.on_hindaja
            elif grupp_id == const.GRUPP_INTERVJUU:
                field = model.Nousolek.on_intervjueerija
            elif grupp_id == const.GRUPP_VAATLEJA:
                field = model.Nousolek.on_vaatleja
            else:
                # komisjoniliige, esimees vms
                field = None

            if self.c.nous:
                # on andnud nõusoleku sellel toimumisajal osalema
                if field:
                    nous_f = sa.and_(model.Nousolek.toimumisaeg_id==self.c.toimumisaeg.id, 
                                     field==True)
                    q = q.filter(model.Kasutaja.nousolekud.any(nous_f))
                else:
                    q = q.filter(model.Kasutaja.nousolekud.any(
                            model.Nousolek.toimumisaeg_id==self.c.toimumisaeg.id))

            elif self.c.nous_kord:
                # on andnud nõusoleku sellel testimiskorral osalema
                nous_f = model.Nousolek.toimumisaeg.has(\
                    model.Toimumisaeg.testimiskord_id==self.c.toimumisaeg.testimiskord_id)
                if field:
                    nous_f = sa.and_(nous_f, field==True)
                q = q.filter(model.Kasutaja.nousolekud.any(nous_f))

            elif self.c.nous_sess:
                # on andnud nõusoleku mõnel sellesse testsessiooni kuuluval
                # toimumiskorral osalema
                nous_f = model.Nousolek.toimumisaeg.has(\
                    model.Toimumisaeg.testimiskord.has(\
                        model.Testimiskord.testsessioon_id==\
                            self.c.toimumisaeg.testimiskord.testsessioon_id))
                if field:
                    nous_f = sa.and_(nous_f, field==True)
                q = q.filter(model.Kasutaja.nousolekud.any(nous_f))

        if q.count() == 0:
            if self.c.isikukood:
                self._selgita_sobimatust(on_piirkond=False, on_kaskkiri=on_kaskkiri)
            else:
                self.error(_("Otsingu tingimustele vastavaid isikuid ei leitud"))
        return q

    def _selgita_sobimatust(self, on_piirkond=True, on_kaskkiri=True):
        """Anname teada, miks antud isikukoodiga isik ei sobi läbiviijaks.
        """
        c = self.c
        kasutaja = model.Kasutaja.get_by_ik(c.isikukood)
        koht = c.testikoht.koht
        grupp_id = c.grupp_id
        
        viga_profiilis, errors = selgita_lv_sobimatust(self,
                                                       kasutaja,
                                                       c.toimumisaeg,
                                                       koht,
                                                       grupp_id,
                                                       on_kaskkiri=on_kaskkiri)

        if kasutaja:
            err = selgita_lv_piirkond(self, kasutaja, c.toimumisaeg, koht, grupp_id)
            if err:
                errors.append(err)
                c.kasutaja = kasutaja
                c.seo_kohaga = True    

            err = selgita_lv_nous(self, kasutaja, c.toimumisaeg, grupp_id, c.nous_kord, c.nous_sess, c.nous)
            if err:
                errors.append(err)
            
        if not errors and kasutaja:
            err = _("{s} ei vasta seatud tingimustele!").format(s=kasutaja.nimi)
        else:
            err = ' '.join(errors)
        self.error(err)
        if viga_profiilis:
            c.kasutaja = kasutaja
            c.muuda_profiil = True

    def _search_default(self, q):
        self.c.lang = self.c.toimumisaeg.testimiskord.get_keeled()

    def _paginate(self, q):
        return q.limit(150).all()

    def __before__(self):
        c = self.c
        c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        c.testikoht = model.Testikoht.get(self.request.matchdict.get('testikoht_id'))
        labiviija_id = self.request.params.get('labiviija_id')
        if labiviija_id:
            c.labiviija = model.Labiviija.get(labiviija_id)
            c.labiviija_id = c.labiviija.id
            c.grupp_id = c.labiviija.kasutajagrupp_id
        else:
            c.grupp_id = int(self.request.params.get('grupp_id'))

    def _perm_params(self):
        return {'obj':self.c.testikoht}

def selgita_lv_sobimatust(handler, kasutaja, toimumisaeg, koht, grupp_id, lang=None, on_kaskkiri=True, on_koolitus=True):
    """Anname teada, miks antud isikukoodiga isik ei sobi läbiviijaks.
    """
    test = toimumisaeg.testiosa.test
    profiil = kasutaja and kasutaja.profiil or None
    errors = []
    viga_profiilis = False
    if not kasutaja:
        err = _("Isik ei kuulu testi läbiviijate sekka. ")
        errors.append(err)
    else:
        if not kasutaja.on_labiviija and (grupp_id not in (const.GRUPP_KOMISJON, const.GRUPP_KOMISJON_ESIMEES) or test.on_tseis):
            # kui pole TE ega SE liiki test, siis ei ole komisjoni liikmel vaja profiili
            # muidu peab olema läbiviija profiil        
            err = _("Isik ei kuulu testi läbiviijate sekka. ")
            errors.append(err)
            viga_profiilis = True

        # keeled, mis peavad profiilis olema
        if lang and isinstance(lang, list):
            # keeled on ette antud
            keeled = lang
        elif lang:
            # keel on ette antud
            keeled = [lang]
        else:
            # kontrollitakse kõiki testimiskorra keeli
            keeled = []

        if grupp_id == const.GRUPP_HINDAJA_S2:
            grupp_id = const.GRUPP_HINDAJA_S

        ta = toimumisaeg
        if grupp_id == const.GRUPP_VAATLEJA:
            if not profiil or not profiil.on_vaatleja:
                err = _("Isiku profiil ei näe ette vaatlejana tegutsemist.")
                errors.append(err)
                viga_profiilis = True
            else:
                for lang in keeled:
                    if not profiil or lang not in (profiil.v_skeeled or ''):
                        lang_nimi = model.Klrida.get_lang_nimi(lang)
                        err = _("{keel} ei ole isiku vaatlemiskeelte seas.").format(keel=lang_nimi)
                        viga_profiilis = True
                        errors.append(err)
                if ta.vaatleja_koolituskp:
                    if not profiil or not profiil.v_koolitusaeg or \
                       ta.vaatleja_koolituskp > profiil.v_koolitusaeg:
                        err = _("Isik pole läbinud vaatlejakoolitust {s2} või hiljem.").format(s2=ta.vaatleja_koolituskp.strftime('%d.%m.%Y'))
                        errors.append(err)
                        if handler.c.app_ekk:
                            viga_profiilis = True
                if len([p for p in kasutaja.pedagoogid if p.koht_id==koht.id]):
                    err = _("Isik töötab samas kohas ja seetõttu ei saa seal vaatleja olla.")
                    errors.append(err)

                if on_kaskkiri and ta.hindaja_kaskkirikpv:
                    if not profiil or not profiil.v_kaskkirikpv or \
                       ta.hindaja_kaskkirikpv > profiil.v_kaskkirikpv:
                        err = _("Isik pole lisatud käskkirja {s2} või hiljem").format(s2=ta.hindaja_kaskkirikpv.strftime('%d.%m.%Y'))
                        errors.append(err)
                        if handler.c.app_ekk:
                            viga_profiilis = True
                            
        elif grupp_id == const.GRUPP_T_ADMIN:
            if not profiil or not profiil.on_testiadmin:
                err = _("Isiku profiil ei näe ette testi administraatorina tegutsemist.")
                errors.append(err)
                viga_profiilis = True
        elif grupp_id in (const.GRUPP_KOMISJON, const.GRUPP_KOMISJON_ESIMEES) and not test.on_tseis:
            # komisjoniliikmel ei pea profiili olema, va TE ja SE liiki testides
            pass
        else:
            if grupp_id == const.GRUPP_HINDAJA_K:
                # kui on hindaja või intervjueerija, siis kontrollime,
                # et suudab antud keeles hinnata ja intervjueerida
                for lang in keeled:
                    if not profiil or lang not in (profiil.k_skeeled or ''):
                        lang_nimi = model.Klrida.get_lang_nimi(lang)                        
                        err = _("{keel} ei ole isiku kirjaliku hindamise keelte seas.").format(keel=lang_nimi)                        
                        errors.append(err)
                        viga_profiilis = True
            elif grupp_id in (const.GRUPP_HINDAJA_S, const.GRUPP_INTERVJUU):
                # kui on hindaja või intervjueerija, siis kontrollime,
                # et suudab antud keeles hinnata ja intervjueerida
                for lang in keeled:
                    if not profiil or lang not in (profiil.s_skeeled or ''):
                        lang_nimi = model.Klrida.get_lang_nimi(lang)                        
                        err = _("{keel} ei ole isiku suulise hindamise keelte seas.").format(keel=lang_nimi)                        
                        errors.append(err)
                        viga_profiilis = True

            aine_kood = test.aine_kood
            q = (model.Aineprofiil.query
                 .filter_by(kasutaja_id=kasutaja.id)
                 .filter_by(aine_kood=aine_kood)
                 .filter_by(kasutajagrupp_id=grupp_id))
            keeletase_kood = test.keeletase_kood
            if keeletase_kood:
                q = q.filter(model.Aineprofiil.keeletase_kood==keeletase_kood)
            q = q.order_by(sa.desc(model.Aineprofiil.koolitusaeg))
            aineprofiil = q.first()
            if not aineprofiil:
                if grupp_id == const.GRUPP_HINDAJA_K:
                    if keeletase_kood:
                        err = _("Isiku profiilis ei ole ette nähtud osalemist antud aines ({s2}) kirjaliku hindajana keeleoskuse tasemel {s4}.").format(s2=test.aine_nimi, s4=test.keeletase_nimi)
                    else:
                        err = _("Isiku profiilis ei ole ette nähtud osalemist antud aines ({s2}) kirjaliku hindajana. ").format(s2=test.aine_nimi)
                else:
                    grupp = model.Kasutajagrupp.get(grupp_id)
                    if keeletase_kood:
                        err = _("Isiku profiilis ei ole ette nähtud osalemist antud aines ({s2}) ja rollis ({s3}) keeleoskuse tasemel {s4}.").format(
                            s2=test.aine_nimi, s3=grupp.nimi, s4=test.keeletase_nimi)
                    else:
                        err = _("Isiku profiilis ei ole ette nähtud osalemist antud aines ({s2}) ja rollis ({s3}).").format(
                            s2=test.aine_nimi, s3=grupp.nimi)
                errors.append(err)
                viga_profiilis = True
            else:
                if on_koolitus:
                    if grupp_id == const.GRUPP_INTERVJUU:
                        koolituskpv = toimumisaeg.intervjueerija_koolituskp
                    elif grupp_id == const.GRUPP_KONSULTANT:
                        koolituskpv = toimumisaeg.konsultant_koolituskp
                    elif grupp_id == const.GRUPP_KOMISJON:
                        koolituskpv = toimumisaeg.komisjoniliige_koolituskp
                    elif grupp_id == const.GRUPP_KOMISJON_ESIMEES:
                        koolituskpv = toimumisaeg.esimees_koolituskp
                    else:
                        koolituskpv = toimumisaeg.hindaja_koolituskp
                    if koolituskpv:
                        q1 = q.filter(model.Aineprofiil.koolitusaeg>=koolituskpv)
                        if not q1.count():
                            aine_nimi = model.Klrida.get_str('AINE', aine_kood)
                            err = _('Isik pole läbinud õppeaine "{aine}" koolitust {kpv} või hiljem.').format(
                                aine=aine_nimi,
                                kpv=handler.h.str_from_date(koolituskpv))
                            errors.append(err)

                if on_kaskkiri:
                    kaskkirikpv = None
                    if grupp_id == const.GRUPP_INTERVJUU:
                        if toimumisaeg.intervjueerija_kaskkirikpv:
                            kaskkirikpv = toimumisaeg.intervjueerija_kaskkirikpv
                    else:
                        if toimumisaeg.hindaja_kaskkirikpv:
                            kaskkirikpv = toimumisaeg.hindaja_kaskkirikpv
                    if kaskkirikpv:
                        q1 = q.filter(model.Aineprofiil.kaskkirikpv>=kaskkirikpv)                
                        if not q1.count():
                            aine_nimi = model.Klrida.get_str('AINE', aine_kood)
                            err = _('Isik pole kantud õppeaines "{aine}" käskkirja {kpv} või hiljem.').format(
                                aine=aine_nimi,
                                kpv=handler.h.str_from_date(kaskkirikpv))
                            errors.append(err)
    return viga_profiilis, errors

def selgita_lv_piirkond(handler, kasutaja, toimumisaeg, koht, grupp_id):
    q1 = (model.Kasutajakoht.query
          .filter(model.Kasutajakoht.kasutaja_id==kasutaja.id)
          .filter(model.Kasutajakoht.koht_id==koht.id))
    piirkond = koht.piirkond
    if not q1.count() and piirkond:
        # kui koht ei sobi, siis kontrollime, et antud piirkond sobib 
        piirkonnad_id = piirkond.get_ylemad_id()
        q1 = (model.Kasutajapiirkond.query
              .filter(model.Kasutajapiirkond.kasutaja_id==kasutaja.id)
              .filter(model.Kasutajapiirkond.piirkond_id.in_(piirkonnad_id)))
    if not q1.count():
        if handler.c.app_ekk and piirkond:
            err = _("Isik ei ole selles piirkonnas ({s2}).").format(s2=piirkond.nimi)
        else:
            err = _("Isik pole seotud soorituskohaga {s2}.").format(s2=koht.nimi)
        return err

def selgita_lv_nous(handler, kasutaja, toimumisaeg, grupp_id, nous_kord, nous_sess, nous):
    if nous_kord or nous_sess or nous:
        if grupp_id in (const.GRUPP_HINDAJA_S, 
                        const.GRUPP_HINDAJA_S2, 
                        const.GRUPP_HINDAJA_K): 
            field = model.Nousolek.on_hindaja
        elif grupp_id == const.GRUPP_INTERVJUU:
            field = model.Nousolek.on_intervjueerija
        elif grupp_id == const.GRUPP_VAATLEJA:
            field = model.Nousolek.on_vaatleja
        else:
            # komisjoniliige, esimees vms
            field = None

        q = model.Nousolek.query.filter(model.Nousolek.kasutaja_id==kasutaja.id)
        if field:
            q = q.filter(field==True)

        if nous:
            # on andnud nõusoleku sellel toimumisajal osalema
            q = q.filter(model.Nousolek.toimumisaeg_id==toimumisaeg.id)
        elif nous_kord:
            # on andnud nõusoleku sellel testimiskorral osalema
            q = q.join(model.Nousolek.toimumisaeg).\
                filter(model.Toimumisaeg.testimiskord_id==toimumisaeg.testimiskord_id)
        elif nous_sess:
            # on andnud nõusoleku mõnel sellesse testsessiooni kuuluval
            # toimumiskorral osalema
            q = q.join(model.Nousolek.toimumisaeg).\
                join(model.Toimumisaeg.testimiskord).\
                filter(model.Testimiskord.testsessioon_id==toimumisaeg.testimiskord.testsessioon_id)
        if not q.first():
            err = _("Isik ei ole avaldanud osalemise soovi.")
            return err

def paranda_lv_sobimatust(handler, kasutaja, toimumisaeg, koht, grupp_id, lang=None):
    """Isiku profiil muudetakse sobivaks läbiviija rollis olemiseks
    """
    def _add_lang(skeeled, fix_lang):
        "Uute keelte lisamine profiili keelte loetellu"
        s_new = ' '.join(fix_lang)
        if skeeled:
            return skeeled + ' ' + s_new
        else:
            return s_new
        
    test = toimumisaeg.testiosa.test
    profiil = kasutaja.profiil
    if not profiil:
        profiil = kasutaja.give_profiil()

    if not kasutaja.on_labiviija and \
           (grupp_id not in (const.GRUPP_KOMISJON, const.GRUPP_KOMISJON_ESIMEES) or test.on_tseis):
        # kui pole TE ega SE liiki test, siis ei ole komisjoni liikmel vaja profiili
        # muidu peab olema läbiviija profiil        
        kasutaja.on_labiviija = True

    # keeled, mis peavad profiilis olema
    if lang and isinstance(lang, list):
        # keeled on ette antud
        keeled = lang
    elif lang:
        # keel on ette antud
        keeled = [lang]
    else:
        # kontrollitakse kõiki testimiskorra keeli
        #keeled = testimiskord.get_keeled()
        keeled = []

    if grupp_id == const.GRUPP_HINDAJA_S2:
        grupp_id = const.GRUPP_HINDAJA_S

    ta = toimumisaeg
    if grupp_id == const.GRUPP_VAATLEJA:
        if not profiil.on_vaatleja:
            profiil.on_vaatleja = True

        fix_lang = []
        for lang in keeled:
            if lang not in (profiil.v_skeeled or ''):
                fix_lang.append(lang)
        profiil.v_skeeled = _add_lang(profiil.v_skeeled, fix_lang)
        
    elif grupp_id == const.GRUPP_T_ADMIN:
        if not profiil.on_testiadmin:
            profiil.on_testiadmin = True

    elif grupp_id in (const.GRUPP_KOMISJON, const.GRUPP_KOMISJON_ESIMEES) and not test.on_tseis:
        # komisjoniliikmel ei pea profiili olema, va TE ja SE liiki testides
        pass
    else:
        if grupp_id == const.GRUPP_HINDAJA_K:
            # kui on hindaja või intervjueerija, siis kontrollime,
            # et suudab antud keeles hinnata ja intervjueerida
            fix_lang = []
            for lang in keeled:
                if lang not in (profiil.k_skeeled or ''):
                    fix_lang.append(lang)
            profiil.k_skeeled = _add_lang(profiil.k_skeeled, fix_lang)

        elif grupp_id in (const.GRUPP_HINDAJA_S, const.GRUPP_INTERVJUU):
            # kui on hindaja või intervjueerija, siis kontrollime,
            # et suudab antud keeles hinnata ja intervjueerida
            fix_lang = []
            for lang in keeled:
                if lang not in (profiil.s_skeeled or ''):
                    fix_lang.append(lang)
            profiil.s_skeeled = _add_lang(profiil.s_skeeled, fix_lang)

        aine_kood = test.aine_kood
        q = (model.Aineprofiil.query
             .filter_by(kasutaja_id=kasutaja.id)
             .filter_by(aine_kood=aine_kood)
             .filter_by(kasutajagrupp_id=grupp_id))
        keeletase_kood = test.keeletase_kood
        if keeletase_kood:
            q = q.filter(model.Aineprofiil.keeletase_kood==keeletase_kood)
        q = q.order_by(sa.desc(model.Aineprofiil.koolitusaeg))
        aineprofiil = q.first()
        if not aineprofiil:
            ap = model.Aineprofiil(kasutaja_id=kasutaja.id,
                                   aine_kood=aine_kood,
                                   kasutajagrupp_id=grupp_id)
            if keeletase_kood:
                ap.keeletase_kood = keeletase_kood

