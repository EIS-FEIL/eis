from simplejson import dumps
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.xtee import ehis

log = logging.getLogger(__name__)

KLASS_RYHMAD = 'r'

class EhisoppuridController(BaseResourceController):
    _permission = 'eksaminandid'
    _ITEM_FORM = forms.admin.EhisoppuridForm
    _INDEX_TEMPLATE = 'admin/ehisoppurid.mako'
    _actions = 'index,create'

    def _query(self):
        self._get_protsessid()
        self.set_debug()

        self.c.opt_kool = self._get_opt_kool()
        # ES-2739
        is_ES2739 = not self.is_live
        if is_ES2739:
            self.c.opt_klass = [('', _("Kõik klassid")), (KLASS_RYHMAD, _("Lasteaiarühmad"))] + const.EHIS_KLASS
        else:
            self.c.opt_klass = [('', _("Kõik klassid")),] + const.EHIS_KLASS

    def _get_opt_kool(self):
        oppetasemed = (const.E_OPPETASE_ALUS,
                       const.E_OPPETASE_YLD,
                       const.E_OPPETASE_GYMN)
        q = (model.SessionR.query(model.Koht.kool_id, model.Koht.nimi)
             .filter(model.Koht.koolioppekavad.any(
                 model.Koolioppekava.kavatase_kood.in_(oppetasemed)
                 ))
             .filter(model.Koht.kool_id>0)
             .filter(model.Koht.staatus==const.B_STAATUS_KEHTIV)
             .order_by(model.Koht.nimi)
             )
        return [('0', _("Kõik koolid"))] + [(k_id, k_nimi) for (k_id, k_nimi) in q.all()]
        
    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        if c.sessioon_id:
            c.bytest = True
            if not c.testiliik:
                sessioon = model.Testsessioon.get(c.sessioon_id)
                c.testiliik = sessioon and sessioon.testiliik_kood or None
            
    def _search_protsessid(self, q):
        q = q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_OPPURID)
        return q

    def _error_create(self):
        extra_info = self._index_d()
        html = self.form.render(self._INDEX_TEMPLATE, extra_info=extra_info)
        return Response(html)

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            self.success()
        return self._redirect('index')

    def _create(self):
        """Arvutusprotsessi käivitamine
        """
        if self.request.params.get('uuenda2'):
            return self._create_test()
        else:
            return self._create_kool()

    def _create_kool(self):
        "Kooli kaupa päring"
        kool_id = self.form.data['kool_id']
        klass = self.form.data['klass']
        if not kool_id and not klass:
            self.error(_("Palun vali kool või klass või mõlemad"))
            return

        desc = 'Õppurite uuendamine EHISest'
        if kool_id:
            q = (model.SessionR.query(model.Koht.nimi)
                 .filter(model.Koht.kool_id==kool_id))
            for k_nimi, in q.all():
                desc += ', ' + k_nimi
        if kool_id and klass == KLASS_RYHMAD:
            # lasteaialaste päring
            # kontrollime, et on lasteaaed
            q = (model.SessionR.query(model.Koht.id)
                 .filter_by(kool_id=kool_id)
                 .join(model.Koht.koolioppekavad)
                 .filter(model.Koolioppekava.kavatase_kood==const.E_OPPETASE_ALUS))
            if q.count() == 0:
                self.error(_("{nimi} pole lasteaed").format(nimi=k_nimi))
                return
            klassid = [None]
        elif klass:
            # kindla klassi päring
            klass_nimi = klass
            for kood, nimi in const.EHIS_KLASS:
                if kood == klass:
                    klass_nimi = nimi
                    break
            desc += ', ' + klass_nimi
            klassid = [klass]
        else:
            # kooli kõigi klasside päring
            klassid = [kood for (kood, nimi) in const.EHIS_KLASS]
            
        params = {'liik': model.Arvutusprotsess.LIIK_OPPURID,
                  'kirjeldus': desc,
                  }
        childfunc = lambda rcd: self._uuenda_kool(rcd, klassid, kool_id)
        model.Arvutusprotsess.start(self, params, childfunc)
        self.success('Protsess on käivitatud')
        debug = self.request.params.get('debug')
        return self._redirect('index', klass=klass, kool_id=kool_id, debug=debug)

    def _uuenda_kool(self, protsess, klassid, kool_id=None):
        "Andmete uuendamise läbiviimine"
        
        # ES-2739
        is_ES2739 = not self.is_live
        if is_ES2739:
            oppetasemed = (const.E_OPPETASE_ALUS,
                           const.E_OPPETASE_YLD,
                           const.E_OPPETASE_GYMN)
        else:
            oppetasemed = (const.E_OPPETASE_YLD,
                           const.E_OPPETASE_GYMN)
        q = (model.Session.query(model.Koht.kool_id)
             .filter(model.Koht.koolioppekavad.any(
                 model.Koolioppekava.kavatase_kood.in_(oppetasemed)
                 ))
             .filter(model.Koht.kool_id>0)
             )
        if kool_id:
            # pärime etteantud kooli kohta
            q = q.filter(model.Koht.kool_id==kool_id)
        else:
            # pärime kõigi kehtivate koolide kohta
            q = q.filter(model.Koht.staatus==const.B_STAATUS_KEHTIV)
        q = q.order_by(model.Koht.kool_id)
        koolid_id = [k_id for k_id, in q.all()]
        uuendada_id = koolid_id

        oppurite_arv = 0
        # uuendame koolide kaupa
        total_kool = len(uuendada_id)
        total_klass = len(klassid)
        total = total_kool * total_klass
        buf = f'Kokku {total_kool} kooli'
        model.Arvutusprotsess.trace(buf)
        reg = ehis.Ehis(handler=self)
        cnt = 0
        for cnt1, kool_id in enumerate(uuendada_id):
            for cnt2, klass in enumerate(klassid):
                cnt += 1
                model.Arvutusprotsess.trace('%d/%d oppurid_kool(%s,%s)...' % (cnt, total, kool_id, klass))
                message, oppimised = reg.oppurid_kool(kool_id, klass)
                if message:
                    if message.startswith('Kutsekoolil puudub klass'):
                        # pole tehniline viga
                        # "Kutsekoolil puudub klass: G12"
                        continue
                    # kui on tehniline viga, siis protsess katkeb
                    raise Exception(message)
                else:
                    ftrace = model.Arvutusprotsess.trace
                    cnt_kl = model.Opilane.update_klass(oppimised, kool_id, klass, None, ftrace)
                    oppurite_arv += cnt_kl
                    if protsess:
                        protsess.edenemisprotsent = cnt * 100. / total
                    model.Session.commit()

                if protsess and protsess.lopp:
                    # protsess on katkestatud, edasi ei arvuta
                    raise ProcessCanceled()
            buf = 'Saadud {n} õppuri andmed'.format(n=oppurite_arv)
            if protsess:
                protsess.set_viga(buf)
            else:
                log.debug(buf)
                
    def _create_test(self):
        "Testi kaupa päring"
        c = self.c
        testiliik = self.form.data['testiliik']
        sessioon_id = self.form.data['sessioon_id']
        test_id = self.form.data['test_id']

        if not sessioon_id or not test_id:
            self.error(_("Palun vali testiliik, testsessioon ja test"))
            return

        sessioon = model.Testsessioon.get(sessioon_id)
        test = model.Test.get(test_id)
        desc = f'Sooritajate õppimisandmete uuendamine EHISest, {sessioon.nimi}, {test.nimi}'
        staatused = (const.S_STAATUS_REGATUD,
                     const.S_STAATUS_ALUSTAMATA)
        q = (model.Session.query(sa.func.count(model.Sooritaja.id))
             .join(model.Sooritaja.testimiskord)
             .filter(model.Testimiskord.testsessioon_id==sessioon_id)
             .filter(model.Testimiskord.test_id==test_id)
             )
        q1 = q.filter(model.Sooritaja.staatus > const.S_STAATUS_ALUSTAMATA)
        q2 = q.filter(model.Sooritaja.staatus.in_(staatused))
        if q2.scalar() == 0:
            if q1.scalar() > 0:
                self.error(_("Andmeid ei uuendata, sest kõik sooritajad on juba sooritamist alustanud"))
            else:
                self.error(_("Andmeid ei uuendata, sest testil pole ühtki registreeritud sooritajat"))
        else:
            params = {'liik': model.Arvutusprotsess.LIIK_OPPURID,
                      'kirjeldus': desc,
                      }
            childfunc = lambda rcd: self._uuenda_test(rcd, sessioon_id, test_id)
            model.Arvutusprotsess.start(self, params, childfunc)
            self.success('Protsess on käivitatud')
        debug = self.request.params.get('debug')
        return self._redirect('index', testiliik=testiliik, sessioon_id=sessioon_id, test_id=test_id, debug=debug)

    def _uuenda_test(self, protsess, sessioon_id, test_id):
        "Andmete uuendamise läbiviimine"
        staatused = (const.S_STAATUS_REGATUD,
                     const.S_STAATUS_ALUSTAMATA)
        q = (model.Session.query(model.Kasutaja.isikukood)
             .join(model.Kasutaja.sooritajad)
             .join(model.Sooritaja.testimiskord)
             .filter(model.Testimiskord.testsessioon_id==sessioon_id)
             .filter(model.Testimiskord.test_id==test_id)
             .filter(model.Sooritaja.staatus.in_(staatused))
             .filter(model.Kasutaja.isikukood!=None)
             )
        isikukoodid = [ik for ik, in q.all()]
        total = len(isikukoodid)
        
        reg = ehis.Ehis(handler=self)
        err = ehis.uuenda_opilased(self,
                                   isikukoodid,
                                   protsess=protsess,
                                   progress_end=90,
                                   force=True)
        if err:
            if protsess:
                protsess.viga = err
            else:
                self.error(err)
            return

        model.Session.commit()
        
        # uuendame sooritajate õppimise andmed registreeringus
        staatused = (const.S_STAATUS_REGATUD,
                     const.S_STAATUS_ALUSTAMATA)
        q = (model.Session.query(model.Sooritaja,
                                 model.Testimiskord.kool_testikohaks)
             .join(model.Sooritaja.testimiskord)
             .filter(model.Testimiskord.testsessioon_id==sessioon_id)
             .filter(model.Testimiskord.test_id==test_id)
             .filter(model.Sooritaja.staatus.in_(staatused))
             )
        changed = 0
        for cnt1, (sooritaja, kool_testikohaks) in enumerate(q.all()):
            vana_koht_id = sooritaja.kool_koht_id
            sooritaja.set_ehis_data()
            uus_koht_id = sooritaja.kool_koht_id
            if uus_koht_id != vana_koht_id:
                model.Arvutusprotsess.trace('sooritaja %d vana kool %s uus kool %s' % (sooritaja.id, vana_koht_id, uus_koht_id))
                changed += 1
                if uus_koht_id and kool_testikohaks:
                    # suuname teise testikohta
                    staatus = sooritaja.staatus
                    sooritaja.give_sooritused(staatus)

        if protsess:
            protsess.viga = 'Uuendatud {n} õppuri andmed, muudetud {n2} sooritaja õppimiskoht'.format(n=total, n2=changed)
