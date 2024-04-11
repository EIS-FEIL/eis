from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
import eis.lib.pdf as pdf
log = logging.getLogger(__name__)
_ = i18n._

class ErivajadusedController(BaseResourceController):
    """Erivajaduste loetelu ja andmed    
    """
    _permission = 'avalikadmin'
    _MODEL = model.Sooritus
    _INDEX_TEMPLATE = 'avalik/erivajadused/erivajadused.otsing.mako'
    _LIST_TEMPLATE = 'avalik/erivajadused/erivajadused.otsing_list.mako'
    _EDIT_TEMPLATE = 'avalik/erivajadused/erivajadus.mako'
    _SEARCH_FORM = forms.avalik.regamine.ErivajadusedOtsingForm
    _ITEM_FORM = forms.avalik.regamine.ErivajadusedForm
    _DEFAULT_SORT = 'sooritus.id' # vaikimisi sortimine

    def _query(self):
        self.c.opt_sessioon = self.c.opt.testsessioon
        Kool_koht = sa.orm.aliased(model.Koht, name='kool_koht')
        q = model.SessionR.query(model.Sooritus, 
                                model.Sooritaja.lang, 
                                model.Kasutaja.isikukood,
                                model.Kasutaja.synnikpv,
                                model.Sooritaja.eesnimi,
                                model.Sooritaja.perenimi,
                                model.Test.nimi,
                                model.Test.aine_kood,
                                model.Testiosa.nimi,
                                model.Koht.nimi,
                                Kool_koht.nimi,
                                model.Komplekt.tahis)
        q = q.filter(model.Sooritus.on_erivajadused==True).\
            join(model.Sooritus.sooritaja).\
            filter(model.Sooritaja.kool_koht_id==self.c.user.koht_id).\
            join(model.Sooritaja.testimiskord).\
            join(model.Sooritaja.test).\
            join(model.Sooritaja.kasutaja).\
            join(model.Sooritus.testiosa).\
            join(model.Sooritus.toimumisaeg).\
            outerjoin(model.Sooritus.testikoht).\
            outerjoin(model.Testikoht.koht).\
            outerjoin(model.Sooritus.erikomplektid).\
            outerjoin(model.Erikomplekt.komplekt).\
            outerjoin((Kool_koht, Kool_koht.id==model.Sooritaja.kool_koht_id))
        
        if not self.c.sessioon_id and len(self.c.opt_sessioon):
            self.c.sessioon_id = self.c.opt_sessioon[0][0]

        return q

    def _search_default(self, q):
        return None

    def _search(self, q):
        c = self.c
        if c.test_id:
            q_test = q = q.filter(model.Test.id==c.test_id)
        if c.sessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==int(c.sessioon_id))
        if c.aine_kood:
            q = q.filter(model.Test.aine_kood==c.aine_kood)
        if c.kinnitatud:
            q = q.filter(model.Sooritus.on_erivajadused_kinnitatud==True)
        if c.kinnitamata:
            q = q.filter(model.Sooritus.on_erivajadused_kinnitatud==False)            
        if c.csv:
            return self._index_csv(q)
        if c.mail:
            self._send_mail(q)
        if c.test_id and q.count() == 0:
            # kui testi ID on antud, aga tulemusi pole, siis selgitatakse,
            # miks see test ei vasta tingimustele
            other_result = q_test.count() > 0
            self._explain_test(other_result)
            # kuvatakse tulemused ainult testi ID järgi, muid otsingutingimusi arvestamata
            q = q_test            
        return q


    def _explain_test(self, other_result):
        c = self.c
        errors = []

        def join_ja(li):
            if len(li) > 1:
                return ', '.join(li[:-1]) + _(" ja ") + li[-1]
            elif len(li) == 1:
                return li[-1]
            else:
                return ''

        def check_filter(q):
            # otsingutingimuste kontroll
            ferrors = []
            if c.sessioon_id:
                q1 = q.filter(model.Testimiskord.testsessioon_id==c.sessioon_id)
                if q1.count() == 0:
                    ferrors.append(_("testsessioon"))

            if c.aine_kood and test.aine_kood != c.aine_kood:
                ferrors.append(_("õppeaine"))
            if ferrors:
                return _("Testil on erinev {omadused}.").format(omadused=join_ja(ferrors))
            
        q = model.SessionR.query(model.Test).filter_by(id=c.test_id)
        test = q.first()
        if test:
            # test on olemas
            q = q.join(model.Test.testimiskorrad)
            if q.count() == 0:
                errors.append(_("Testi ei ole tsentraalselt korraldatud."))
            else:
                q = q.filter(model.Testimiskord.sooritajad.any(
                     model.Sooritaja.kool_koht_id==c.user.koht_id))
                if q.count() == 0:
                    errors.append(_("Testimiskorral ei ole meie kooli õpilasi."))
                elif other_result:
                    # test on kättesaadav, aga ei vasta otsingutingimustele
                    err = check_filter(q)
                    if err:
                        errors.append(err)
                    
            if errors:
                if other_result:
                    err = _("Kuvatakse test {id}, aga see ei vasta otsingutingimustele.").format(id=test.id)
                else:
                    err = _("Test {id} ei vasta otsingutingimustele.").format(id=test.id)
                msg = err + ' ' + ' '.join(errors)
                self.warning(msg)

    
    def _prepare_items(self, q):
        c = self.c

        # tabeli päis
        header = [_('Isikukood'),
                  _('Eesnimi'),
                  _('Perekonnanimi'),
                  _('Soorituse tähis'),
                  _('Soorituskeel'),
                  _('Aine'),
                  _('Test'),
                  _('Toimumisaeg'),
                  _('Soorituskoht'),
                  _('Õppimiskoht'),                 
                  _('Eritingimused'),
                  _('Kinnitatud'),
                  _('Ül komplekt'),
                  ]

        # tabeli sisu
        items = []
        for rcd in q.all():
            row = self._prepare_row(rcd)
            items.append(row)

        return header, items

    def _prepare_row(self, rcd):
        "Tabeli ühe rea väljade kokkupanek"
        c = self.c
        h = self.h

        tos, lang, isikukood, synnikpv, eesnimi, perenimi, test_nimi, aine_kood, testiosa_nimi, koht_nimi, kool_koht_nimi, komplekt_tahis = rcd
        row = [isikukood or h.str_from_date(synnikpv),
               eesnimi,
               perenimi,
               tos.tahised,
               model.Klrida.get_lang_nimi(lang),
               model.Klrida.get_str('AINE', aine_kood),
               test_nimi,
               tos.toimumisaeg and tos.toimumisaeg.tahised or '',
               koht_nimi,
               kool_koht_nimi,
               tos.get_str_erivajadused('\n'),
               h.sbool(tos.on_erivajadused_kinnitatud),
               komplekt_tahis
               ]

        return row

    def _update(self, item):
        if self.c.is_edit_p:
            # salvestatakse ainult neid eritingimusi, mida Innove ei kinnita
            self._update_p(item)
            return

        errors = {}
        on_erivajadused = False

        if item.tugiisik_kasutaja_id:
            on_erivajadused = True
        
        # salvestakse kõik eritingimused
        for tos in item.sooritaja.sooritused:
            if tos.staatus == const.S_STAATUS_VABASTATUD:
                on_erivajadused = True
                break
            else:
                for atos in tos.alatestisooritused:
                    if atos.staatus == const.S_STAATUS_VABASTATUD:
                        on_erivajadused = True
                        break

        collection = []
        for ind, rcd in enumerate(self.form.data.get('ev')):
            if not rcd.get('erivajadus_kood'):
                # üldine märkuste kirje
                rcd['erivajadus_kood'] = None
                rcd['taotlus'] = bool(rcd.get('taotlus_markus'))
            if rcd.get('taotlus'):
                if rcd.get('erivajadus_kood'):
                    on_erivajadused = True
                if not rcd['taotlus_markus']:
                    errors['ev-%d.taotlus_markus' % ind] = _('Palun sisestada põhjendus')
                collection.append(rcd)

        item.on_erivajadused_vaadatud = False
        if errors:
            raise ValidationError(self, errors)
        BaseGridController(item.erivajadused, model.Erivajadus).save(collection)
        item.sooritaja.from_form(self.form.data, 'r_')
        model.Session.flush()
        item.set_erivajadused(None)
        if not item.on_erivajadused:
            self.notice(_('Ühtki eritingimust pole valitud'))

    def _update_p(self, item):
        # salvestatakse ainult neid eritingimusi, mida Innove ei pea kinnitama
        errors = {}
        on_erivajadused = False
        collection = []
        for ind, rcd in enumerate(self.form.data.get('ev')):
            if not rcd.get('erivajadus_kood'):
                # üldine märkuste kirje
                rcd['erivajadus_kood'] = None
                rcd['taotlus'] = bool(rcd.get('taotlus_markus'))
            if rcd.get('taotlus'):
                if rcd.get('erivajadus_kood'):
                    on_erivajadused = True
                if not rcd['taotlus_markus']:
                    errors['ev-%d.taotlus_markus' % ind] = _('Palun sisestada põhjendus')
                collection.append(rcd)

        if not on_erivajadused:
            self.error(_('Ühtki eritingimust pole valitud'))
            raise ValidationError(self, errors)

        if errors:
            raise ValidationError(self, errors)
        test = item.testiosa.test
        erivajadused = [r for r in item.erivajadused if r.ei_vaja_kinnitust(test)]
        BaseGridController(erivajadused, model.Erivajadus, supercollection=item.erivajadused).save(collection)
        item.set_erivajadused(True)
        item.sooritaja.from_form(self.form.data, 'r_')
        
    def _delete(self, item):
        test = item.testiosa.test
        for r in list(item.erivajadused):
            if not self.c.is_edit_p or r.ei_vaja_kinnitust(test):
                r.delete()
        item.tugiisik_kasutaja_id = None
        model.Session.flush()
        item.set_erivajadused(None)
        model.Session.commit()
        self.success(_('Eritingimused on tühistatud'))

    def _perm_params(self):
        id = self.request.matchdict.get('id')
        if (self.c.is_edit or self.c.action=='delete') and id:
            item = model.Sooritus.get(id)
            tk = item.sooritaja.testimiskord
            if item.on_erivajadused_kinnitatud or tk and not self.c.user.has_permission('erivmark', const.BT_UPDATE, obj=tk):
                # erivajaduste märkimise aeg on läbi
                if tk and self.c.user.has_permission('erivmark_p', const.BT_UPDATE, obj=tk):
                    # saab muuta ainult neid eritingimusi, mida Innove ei kinnita
                    self.c.is_edit_p = True
                else:
                    # ei saa mingeid eritingimusi muuta
                    return False
