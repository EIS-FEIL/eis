# -*- coding: utf-8 -*- 
from cgi import FieldStorage
from eis.forms import validators, formencode
from eis.lib.baseresource import *
from eis.lib.resultentry import ResultEntry
from eis.lib.helpers import fstr
log = logging.getLogger(__name__)
_ = i18n._

RVS_MISSED = 0 # puudus
RVS_NOTREPORTED = 1 # osales, aga ei saanud taset ega tunnistust
RVS_OK = 2 # osales ja sai tunnistuse

class RvtunnistusedfailController(BaseResourceController):
    """Rahvusvaheliste eksamite soorituste sisestamine failiga
    """
    _permission = 'sisestamine'
    _EDIT_TEMPLATE = 'ekk/sisestamine/rvtunnistusedfail.mako'
    _actions = 'new,create'

    def _new_d(self):
        c = self.c
        c.fields, v1, osad = self._get_metadata(self.c.rveksam)
        c.opt_testid = self._get_opt_testid(self.c.rveksam)
        c.test_id = self.request.params.get('test_id')
        c.testimiskord_id = self.request.params.get('testimiskord_id')
        return self.response_dict

    def _get_opt_testid(self, rveksam):
        q = (model.SessionR.query(model.Test.nimi,
                                 model.Test.id)
             .filter(model.Test.testimiskorrad.any())
             .filter(model.Test.rveksam_id==rveksam.id)
             .order_by(sa.desc(model.Test.id)))
        li = []
        for t_nimi, t_id in q.all():
            li.append((t_id, t_nimi))
        return li
                     
    def _get_sooritajad(self, kasutaja_id, rveksam_id, test_id, testimiskord_id):
        # leiame testisooritused, kust võtta punktid tunnistusele
        # kuna toimumise protokolli ei täideta, siis ei pea staatus olema "tehtud"
        q = (model.Sooritaja.query
             .filter(model.Sooritaja.staatus.in_(
                 (const.S_STAATUS_REGATUD,
                  const.S_STAATUS_ALUSTAMATA,
                  const.S_STAATUS_PUUDUS,
                  const.S_STAATUS_TEHTUD)))
             .join(model.Sooritaja.test)
             .filter(model.Test.rveksam_id==rveksam_id)
             )
        if kasutaja_id:
            q = q.filter(model.Sooritaja.kasutaja_id==kasutaja_id)
        if testimiskord_id:
            q = q.filter(model.Sooritaja.testimiskord_id==testimiskord_id)
        elif test_id:
            q = q.filter(model.Sooritaja.test_id==test_id)
        q = q.order_by(model.sa.desc(model.Sooritaja.algus))
        return q.all()
            
    def create(self, **kw):
        c = self.c
        c.test_id = self.request.params.get('test_id')
        c.testimiskord_id = self.request.params.get('testimiskord_id')        
        kanna = self.request.params.get('kanna')
        self.form = Form(self.request, schema=self._ITEM_FORM, method='GET')        
        try:
            return self._load_file_contents(c.rveksam, c.test_id, c.testimiskord_id, kanna)
        except FileInputError as e:
            self.form.errors = {'fail': e.message}
            self._new_d()
            html = self.form.render(self._EDIT_TEMPLATE, extra_info=self.response_dict)            
            return Response(html)
        
    def _load_file_contents(self, rveksam, test_id, testimiskord_id, kanna):
        value = self.request.params.get('fail')
        if not isinstance(value, FieldStorage):
            raise FileInputError(_('Palun sisestada fail'))

        self.kantud_sooritajad_id = [] # sooritajate id, mille andmed on failist loetud
        self._trace_buf = ''
        
        # value on FieldStorage objekt
        filename = value.filename
        if filename.rsplit('.',1)[-1] in ('xlsx','xls'):
            raise FileInputError(_("Palun kasutada CSV vormingus faili"))

        value = value.value
        li, v1, osad = self._get_metadata(rveksam)
        fields_cnt = len(li) # mitu veergu peab failis olema

        # kontrollime faili sisu
        cnt_missed = cnt_notreported = cnt_ok = cnt_other = 0
        for ind, line in enumerate(value.splitlines()):
            try:
                line = utils.guess_decode(line).strip()
                if line:
                    row = [s.strip() for s in line.strip().split(';')]
                    if row:
                        rvstatus = self._load_row(row, rveksam, test_id, testimiskord_id, fields_cnt, v1, osad, ind, kanna)
                        if rvstatus == RVS_MISSED:
                            cnt_missed += 1
                        elif rvstatus == RVS_NOTREPORTED:
                            cnt_notreported += 1
                        elif rvstatus == RVS_OK:
                            cnt_ok += 1
            except FileInputError as e:
                raise FileInputError(e.message + ' (_(viga real {n}))'.format(n=ind+1))


        if kanna and rveksam.kantav_tulem:
            # need sooritajad, kelle andmeid failis polnud, märgitakse puudujaks
            sooritajad = self._get_sooritajad(None, rveksam.id, test_id, testimiskord_id)
            data = TunnistusData()
            data.rvstatus = RVS_MISSED
            data.tulemus = 0
            # for sooritaja in sooritajad:
            #     if sooritaja.id not in self.kantud_sooritajad_id:
            #         # sooritajat polnud failis, märgime puudujaks
            #         self._trace('puuduja %s' % (sooritaja.id))
            #         self._kanna_sooritusele(rveksam, sooritaja, data, True)
            #         cnt_other += 1
                    
        if cnt_ok or cnt_notreported or cnt_missed:
            model.Session.commit()
            msg = _("Failist laaditi {n1} tunnistuse, {n2} tunnistuseta soorituse ja {n3} testilt puudumise andmed. ").format(n1=cnt_ok, n2=cnt_notreported, n3=cnt_missed)
            if cnt_other:
                if testimiskord_id:
                    msg += _("{n} sooritaja andmeid polnud failis ning märgiti puudujaks").format(n=cnt_other)

            self.notice(msg)
            return self._redirect('new', test_id=test_id, testimiskord_id=testimiskord_id)

        else:
            raise FileInputError(_('Ei laaditud ühtki tunnistust'))

    def _load_row(self, row, rveksam, test_id, testimiskord_id, fields_cnt, v1, osad, ind, kanna):
        if len(row) != fields_cnt:
            raise FileInputError(_('Leitud {n1} veergu, aga igas reas peab olema {n2} veergu').format(n1=len(row), n2=fields_cnt))

        isikukood = row[0]
        if ind == 0 and isikukood.lower() == 'isikukood':
            # esimesel real võib olla veergude päis
            return 
        if not isikukood:
            raise FileInputError(_('Puudub isikukood'))
        try:
            validators.Isikukood().to_python(isikukood)
        except formencode.api.Invalid as ex:
            raise FileInputError(_('Vigane isikukood "{s}"').format(s=isikukood))

        self._trace('KASUTAJA %s' % (isikukood))
        # loeme failist info
        data = self._get_rowdata(row, rveksam, v1, osad)

        kasutaja = model.Kasutaja.get_by_ik(isikukood)
        if not kasutaja:
            # kui kasutajat EISis pole, siis otsime RRist
            kasutaja = xtee.set_rr_pohiandmed(self, None, isikukood)            
            if not kasutaja:
                # kui kasutajat ei ole EISis ega ka RRis, siis pole midagi teha
                raise FileInputError(_('Rahvastikuregistrist ei leitud isikukoodiga {s} isikut').format(s=isikukood))

        sooritaja = self._find_sooritaja(rveksam, test_id, testimiskord_id, kasutaja)
        item, tunnistus = self._find_tunnistus(data, rveksam, kasutaja, sooritaja)
        item, tunnistus = self._save_tunnistus(data, rveksam,
                                               test_id, testimiskord_id,
                                               kasutaja, v1, osad, kanna,
                                               item, tunnistus)

        if sooritaja:
            if item:
                item.sooritaja_id = sooritaja.id
                model.Session.flush()
                sooritaja.refresh()
            self._kanna_sooritusele(rveksam, sooritaja, data, kanna)
            
        return data.rvstatus

    def _find_tunnistus(self, data, rveksam, kasutaja, sooritaja):
        """Kui testi ja testimiskorra järgi on leitud sooritaja kirje
        ning sellega on seotud rvsooritaja kirje, siis kasutatakse seda;
        kui rvsooritaja kirjet ei ole, aga on antud tunnistuse nr,
        siis otsitakse kirje tunnistuse nr järgi
        """
        # kas EISi baasis on olemas rvsooritaja ja tunnistuse kirjed
        item = tunnistus = None
        if sooritaja:
            # kui sooritaja kirje on leitud, siis võetakse seotud rvsooritaja 
            for rvsooritaja in sooritaja.rvsooritajad:
                item = rvsooritaja
                tunnistus = rvsooritaja.tunnistus
                break
                
        if not item and data.tunnistusenr:
            # kui sooritaja kaudu rvsooritaja kirjet ei leita, aga on antud tunnistuse nr,
            # siis leitakse kirje tunnistuse nr järgi
            q = (model.Session.query(model.Rvsooritaja)
                 .join(model.Rvsooritaja.tunnistus)
                 .filter(model.Tunnistus.tunnistusenr==data.tunnistusenr)
                 .filter(model.Tunnistus.kasutaja_id==kasutaja.id)
                 .filter(model.Rvsooritaja.rveksam_id==rveksam.id)
                 .order_by(sa.desc(model.Rvsooritaja.id)))
            item = q.first()
            if item:
                tunnistus = item.tunnistus
        return item, tunnistus
    
    def _save_tunnistus(self, data, rveksam, test_id, testimiskord_id, kasutaja, v1, osad, kanna,
                        item, tunnistus):
        """Tunnistuse lisamine failist.
        Kui puudus või ei saanud tunnistust, siis märgitakse tunnistus kehtetuks
        ja rvsooritaja kirje kustutatakse.
        Kui osales ja sai tunnistuse, siis luuakse rvsooritaja kirje ja tunnistuse kirje.
        """
        
        if data.rvstatus == RVS_MISSED:
            # puudus
            if tunnistus:
                tunnistus.staatus = const.N_STAATUS_KEHTETU
                tunnistus.tyh_pohjendus = _('puudus eksamilt (andmed failist)')
            if item:
                item.delete()
        elif data.rvstatus == RVS_NOTREPORTED:
            # ei saavutanud taset
            if tunnistus:
                tunnistus.staatus = const.N_STAATUS_KEHTETU
                tunnistus.tyh_pohjendus = _('ei saanud tunnistust (andmed failist)')
            if item:
                item.delete()
        else:
            # sai tunnistuse
            if tunnistus is None:
                tunnistus = model.Tunnistus(kasutaja_id=kasutaja.id,
                                            eesnimi=kasutaja.eesnimi,
                                            perenimi=kasutaja.perenimi,
                                            seq=0)
            if item is None:
                item = model.Rvsooritaja(rveksam_id=rveksam.id)
            item.arvest_lopetamisel = True
            item.tunnistus = tunnistus
            created = date.today()
            tunnistus.oppeaasta = created.month > 8 and created.year + 1 or created.year
            tunnistus.tunnistusenr = data.tunnistusenr
            tunnistus.valjastamisaeg = data.valjastamisaeg
            tunnistus.kehtib_kuni = data.kehtib_kuni
            item.tulemus = data.tulemus
            item.rveksamitulemus_id = data.rveksamitulemus_id
            item.keeletase_kood = data.keeletase
            for (osa, vahemikud, on_autom_vahemikud) in osad:
                rvsooritus = item.give_rvsooritus(osa.id)
                osadata = data.osatulemused.get(osa.id)
                if osadata:
                    rvsooritus.tulemus = osadata.tulemus
                    rvsooritus.rvosatulemus_id = osadata.rvosatulemus_id
                    rvsooritus.on_labinud = osadata.on_labinud
                else:
                    rvsooritus.tulemus = None
                    rvsooritus.rvosatulemus_id = None
                    rvsooritus.on_labinud = None

        return item, tunnistus
    
    def _find_sooritaja(self, rveksam, test_id, testimiskord_id, kasutaja):
        # otsime sooritaja kirje
        sooritajad = list(self._get_sooritajad(kasutaja.id, rveksam.id, test_id, testimiskord_id))
        if sooritajad and len(sooritajad) == 1:
            sooritaja = sooritajad[0]
        elif sooritajad and len(sooritajad) > 1:
            raise FileInputError(_('Sooritajal {s} on võimalik tunnistusega siduda mitu eksamisooritust ja ei ole teada, milline neist siduda').format(s=kasutaja.isikukood))
        elif test_id or testimiskord_id:
            raise FileInputError(_('Isikul {s} ei ole valitud testil sellist sooritust, mida saaks tunnistusega siduda').format(s=kasutaja.isikukood))
        else:
            sooritaja = None
        return sooritaja

    def _get_rowdata(self, row, rveksam, v1, osad):
        inp = RowInput(self.request, row)
        data = TunnistusData()

        status = inp.get_str()
        if status == 'X':
            # puudus (osaoskuste tulemused peaksid olema X)
            data.rvstatus = RVS_MISSED
        elif status == 'Not Reported':
            # osales, aga ei saanud tunnistust (osaoskuste tulemused võivad olla olemas või märgitud NR)
            data.rvstatus = RVS_NOTREPORTED
        elif status == '':
            # osales ja sai tunnistuse (osaoskuste tulemused võivad olla olemas või märgitud NR)
            data.rvstatus = RVS_OK
        else:
            msg = _('Veerus {n} on vigane tunnistuseta jäämise põhjus "{s}" (lubatud on "X" või "Not Reported" või tühi)').format(n=inp.n+1, s=status)
            raise FileInputError(msg, status)
        
        if rveksam.on_tunnistusenr:
            data.tunnistusenr = inp.get_str(30)
        data.valjastamisaeg = inp.get_date()
        if rveksam.on_kehtivusaeg:
            data.kehtib_kuni = inp.get_date()
            
        if rveksam.on_arvtulemus:
            min_v = rveksam.alates
            if data.rvstatus == RVS_NOTREPORTED:
                min_v = 0
            try:
                data.tulemus = inp.get_float(min_v, rveksam.kuni)
            except FileInputError as ex:
                # arvulise kogutulemuse väljal võib arvu asemel olla:
                # X - märgib, et sooritaja puudus eksamilt - eeldab, et oleku veerus on ka X
                # NR - märgib, et isik osales, aga ei saanud taset
                value = ex.value
                if value == 'X':
                    if data.rvstatus != RVS_MISSED:
                        msg = _('Kogutulemuse veerus {n} on X, aga veerus 2 ei ole X').format(n=inp.n+1)
                        raise FileInputError(msg, value)
                elif value == 'NR':
                    if data.rvstatus != RVS_NOTREPORTED:
                        msg = _('Kogutulemuse veerus {n} on NR, aga veerus 2 ei ole "Not Reported"').format(n=inp.n+1)
                        raise FileInputError(msg, value)                    
                else:
                    raise
            if data.rvstatus == RVS_MISSED and data.tulemus:
                msg = _('Kogutulemus on veerus {n} antud, kuigi sooritaja puudus').format(n=inp.n+1)
                raise FileInputError(msg, data.tulemus)
                
        vahemikud, on_autom_vahemikud = v1
        data.rveksamitulemus_id = None
        len_v = len(vahemikud)
        if len_v:
            if on_autom_vahemikud:
                value = data.tulemus
            else:
                value = inp.get_str()
            v_id = None
            if value == 'X':
                # puudus
                if data.rvstatus != RVS_MISSED:
                    msg = _('Kogutulemuse veerus {n} on X, aga veerus 2 ei ole X').format(n=inp.n+1)
                    raise FileInputError(msg, value)
            elif value == 'NR':
                # ei saanud tunnistust
                if data.rvstatus != RVS_NOTREPORTED:
                    msg = _('Kogutulemuse veerus {n} on NR, aga veerus 2 ei ole "Not Reported"').format(n=inp.n+1)
                    raise FileInputError(msg, value)                    
            elif value is not None and value != '':
                for alates, kuni, rve_id, tahis in vahemikud:
                    if on_autom_vahemikud and value >= alates or \
                       not on_autom_vahemikud and value == tahis:
                        data.rveksamitulemus_id = rve_id
                        break
                if not data.rveksamitulemus_id and data.rvstatus == RVS_OK:
                    if on_autom_vahemikud:
                        msg = _('Veerus {n} tulemus "{s}" ei kuulu ühtegi vahemikku').format(n=inp.n+1, s=fstr(value))
                    else:
                        msg = _('Veerus {n} tulemuse tähist "{s}" ei ole kirjeldatud').format(n=inp.n+1, s=value)
                    raise FileInputError(msg, value)

        data.osatulemused = {} # pallid osaoskuste kaupa
        for (osa, vahemikud, on_autom_vahemikud) in osad:
            osadata = OsaData()
            len_v = len(vahemikud)
            if rveksam.on_arvtulemus:
                min_v = osa.alates
                if data.rvstatus == RVS_NOTREPORTED:
                    min_v = 0
                try:
                    osadata.tulemus = inp.get_float(min_v, osa.kuni)
                except FileInputError as ex:
                    # osaoskuse arvulise tulemuse väljal võib arvu asemel olla
                    # (sama, mis tyhi):
                    # NR - märgib, et isik osales, aga ei saanud osaoskuse lävest üle
                    # - - kasutatakse puudujate korral
                    value = ex.value
                    if value == 'X':
                        # puudus 
                        if data.rvstatus != RVS_MISSED:
                            msg = _('Veerus {n} on osatulemus X, aga veerus 2 ei ole X').format(n=inp.n+1)
                            raise FileInputError(msg, value)
                        else:
                            osadata.tulemus = None
                    elif value == 'NR' or value == '-':
                        # ei saanud osatulemust
                        osadata.tulemus = None
                    else:
                        raise
                    
            if len_v:
                if on_autom_vahemikud:
                    value = osadata.tulemus
                else:
                    value = inp.get_str()
                if value == 'X':
                    if data.rvstatus != RVS_MISSED:
                        msg = _('Veerus {n} on osatulemus X, aga veerus 2 ei ole X').format(n=inp.n+1)
                        raise FileInputError(msg, value)
                    else:
                        osadata.tulemus = None
                elif value is not None and value != '' and value not in ('NR', '-'):
                    for alates, kuni, rvosatulemus_id, tahis in vahemikud:
                        if on_autom_vahemikud and value >= alates or \
                               not on_autom_vahemikud and value == tahis:                    
                            osadata.rvosatulemus_id = rvosatulemus_id
                            break
                    if not osadata.rvosatulemus_id and data.rvstatus == RVS_OK:
                        if on_autom_vahemikud:
                            msg = _('Veerus {n} osatulemus "{s}" ei kuulu ühtegi vahemikku').format(n=inp.n+1, s=fstr(value))
                        else:
                            msg = _('Veerus {n} osatulemuse tähist "{s}" ei ole kirjeldatud').format(n=inp.n+1, s=value)
                        raise FileInputError(msg, value)

            if rveksam.on_osaoskused_jahei:
                osadata.on_labinud = inp.get_bool()
            data.osatulemused[osa.id] = osadata
            self._trace('rvosa %s tulemus %s' % (osa.id, fstr(osadata.tulemus)))
        keeletase = None
        if data.rvstatus == RVS_OK:
            if rveksam.keeletase_kood:
                keeletase = rveksam.keeletase_kood
            elif data.rveksamitulemus_id:
                rveksamitulemus = model.Rveksamitulemus.get(data.rveksamitulemus_id)
                keeletase = rveksamitulemus.keeletase_kood
        data.keeletase = keeletase
        return data

    def _kanna_sooritusele(self, rveksam, sooritaja, data, kanna):
        test = sooritaja.test
        if not (len(test.testitasemed) and test.testitasemed[0].pallid is not None):
            # kui EIS ei anna testi eest taset, siis omistame tunnistuse taseme testisooritusele ka
            sooritaja.keeletase_kood = data.keeletase
        self._trace('keeletase=%s' % sooritaja.keeletase_kood)
        if not (kanna and rveksam.kantav_tulem):
            # muude andmete ylekandmist ei valitud
            return

        self.kantud_sooritajad_id.append(sooritaja.id)

        rvpallid = {osa_id: r.tulemus for (osa_id, r) in data.osatulemused.items()}
        if data.rvstatus == RVS_MISSED:
            staatus = const.S_STAATUS_PUUDUS
        else:
            staatus = const.S_STAATUS_TEHTUD
            
        # kanname tunnistuselt tulemused ka sooritusele
        if sooritaja.pallid is None or sooritaja.mujalt_tulemus:
            # EISis hinnatud tulemust yle ei kirjutata
            sooritaja.staatus = staatus
            sooritaja.mujalt_tulemus = True
            resultentry = ResultEntry(self, None, test, None)
            total = 0
            self._trace('sooritaja {s1} staatus {s2} tase {s3}'.format(s1=sooritaja.id, s2=sooritaja.staatus, s3=sooritaja.keeletase_kood))
            for tos in sooritaja.sooritused:
                testiosa = tos.testiosa
                resultentry.testiosa = testiosa
                self._trace(' sooritus {s1} testiosa {s2}'.format(s1=tos.id, s2=testiosa.id))
                if tos.pallid is None or tos.ylesanneteta_tulemus:
                    # testiosa, kus veel tulemust pole või tulemus on tunnistuselt saadud
                    tos.ylesanneteta_tulemus = True
                    tos.staatus = staatus
                    tos_pallid = 0
                    for alatest in testiosa.alatestid:
                        atos = tos.give_alatestisooritus(alatest.id, sooritaja)
                        osa_id = alatest.rvosaoskus_id
                        if osa_id:
                            atos.staatus = staatus
                            atos.pallid = rvpallid.get(osa_id)
                            tos_pallid += atos.pallid or 0
                        self._trace('  atos {s1} alatest {s2} rvosa_id {s3} pallid {s4}'.format(s1=atos.id, s2=atos.alatest_id, s3=osa_id, s4=fstr(atos.pallid)))
                    osa_id = testiosa.rvosaoskus_id
                    if osa_id:
                        tos.pallid = rvpallid.get(osa_id)
                    else:
                        tos.pallid = tos_pallid
                    self._trace('    testiosa rvosa_id {s1} pallid {s2}'.format(s1=osa_id, s2=fstr(tos.pallid)))
                    tos.hindamine_staatus = const.H_STAATUS_HINNATUD
                    resultentry.update_sooritus(sooritaja, tos, False)
                total += tos.pallid or 0
            if rveksam.on_tulemus_tunnistusel:
                # kogutulemuse saab tunnistuselt
                sooritaja.pallid = data.tulemus
            else:
                # kogutulemuseks paneme soorituste summa
                sooritaja.pallid = total
            sooritaja.hindamine_staatus = const.H_STAATUS_HINNATUD
            resultentry.update_sooritaja(sooritaja)
            self._trace(' kokku sooritaja pallid={s1} tase={s2}'.format(s1=fstr(sooritaja.pallid), s2=sooritaja.keeletase_kood))
                
    def _get_metadata(self, rveksam):
        "Leitakse väljade nimed ja vahemikud"
        li = [_('Isikukood'),
              _('Tunnistuseta jäämise põhjus (/X/Not Reported)')]
        if rveksam.on_tunnistusenr:
            li.append(_('Tunnistuse nr'))
        li.append(_('Väljastamiskuupäev (pp.kk.aaaa)'))
        if rveksam.on_kehtivusaeg:
            li.append(_('Kehtib kuni (pp.kk.aaaa)'))

        on_vahemikud = len(rveksam.rveksamitulemused)
        on_autom_vahemikud = on_vahemikud

        vahemikud = []
        for r in rveksam.rveksamitulemused:
            vahemikud.append([r.alates, r.kuni, r.id, r.tahis or ''])
            if r.alates is None or r.kuni is None:
                on_autom_vahemikud = False
        if rveksam.on_arvtulemus:
            buf = _('Tulemus')
            if rveksam.alates is not None or rveksam.kuni is not None:
                buf1 = '%s-%s' % (fstr(rveksam.alates), fstr(rveksam.kuni))
            else:
                buf1 = _('arv')
            buf += ' (%s/X/NR)' % buf1
            li.append(buf)
        if on_vahemikud and not (rveksam.on_arvtulemus and on_autom_vahemikud):
            tahised = '/'.join([r[3] for r in vahemikud])
            li.append(_('Tulemus {s1})').format(s1=tahised))

        v1 = (vahemikud, on_autom_vahemikud)
        
        osad = []
        for osa in rveksam.rvosaoskused:
            on_autom_vahemikud = on_vahemikud = len(osa.rvosatulemused)

            vahemikud = []
            for r in osa.rvosatulemused:
                vahemikud.append([r.alates, r.kuni, r.id, r.tahis or ''])
                if r.alates is None or r.kuni is None:
                    on_autom_vahemikud = False

            if rveksam.on_arvtulemus:
                buf = osa.nimi
                if osa.alates is not None or osa.kuni is not None:
                    buf1 = '%s-%s' % (fstr(osa.alates), fstr(osa.kuni))
                else:
                    buf1 = _('arv')
                buf += ' (%s/X/NR/-)' % buf1
                li.append(buf)
            if on_vahemikud and not (rveksam.on_arvtulemus and on_autom_vahemikud):
                tahised = '/'.join([r[3] for r in vahemikud])
                li.append('%s (%s)' % (osa.nimi, tahised))
            if rveksam.on_osaoskused_jahei:
                li.append(_('Vastab tasemele (0/1)'))

            osad.append((osa, vahemikud, on_autom_vahemikud))

        return li, v1, osad
    
    def __before__(self):
        rveksam_id = self.request.matchdict.get('rveksam_id')
        self.c.rveksam = model.Rveksam.get(rveksam_id)

    def _trace(self, line):
        self._trace_buf += line + '\n'

class OsaData:
    tulemus = None
    rvosatulemus_id = None
    on_labinud = None
    
class TunnistusData:
    rvstatus = None
    tulemus = None
    rveksamitulemus_id = None
    keeletase = None
    osatulemused = {}
    tunnistusenr = None
    valjastamisaeg = None
    kehtib_kuni = None
    
class FileInputError(Exception):
    def __init__(self, message, value=None):
        self.message = message
        self.value = value

class RowInput:
    def __init__(self, request, row):
        self.n = 0
        self.row = row
        self.request = request
        
    def _next(self):
        self.n += 1
        return self.row[self.n]

    def get_str(self, length=None):
        value = self._next()
        if length and len(value) > length:
            raise FileInputError(_('Veerus {n} olev tekst ei või olla pikem kui {l} sümbolit').format(n=self.n+1, l=length), value)
        return value

    def get_date(self):
        value = self._next()                
        try:
            return forms.validators.EstDateConverter(if_missing=None).to_python(value)
        except formencode.api.Invalid as ex:
            raise FileInputError(_('Vigane kuupäev veerus {n}, peab olema pp.kk.aaaa').format(n=self.n+1), value)

    def get_float(self, min_v=None, max_v=None):
        value = self._next()                
        if value == '':
            return None
        try:
            value = float(value.replace(',','.'))
        except:
            raise FileInputError('Vigane arv veerus {n}'.format(n=self.n+1), value)
        if (max_v and max_v < value) or (min_v and min_v > value):
            raise FileInputError(_('Veerus {n} olev arv {value} peab olema vahemikus {min}-{max}').format(
                                         n=self.n+1,
                                         value=fstr(value),
                                         min=fstr(min_v),
                                         max=fstr(max_v)),
                                         value)
        return value

    def get_posint(self, min_v=None, max_v=None):
        value = self._next()
        if value == '':
            return None
        try:
            value = int(value)
        except:
            raise FileInputError(_('Vigane täisarv veerus {n}').format(n=self.n+1), value)
        if value <= 0:
            raise FileInputError(_('Veerus {n} olev arv {value} ei ole suurem kui 0').format(
                                        n=self.n+1,
                                        value=fstr(value)),
                                        value)
        if (max_v and max_v < value) or (min_v and min_v > value):
            raise FileInputError(_('Veerus {n} olev arv {value} ei ole vahemikus {min}-{max}').format(
                                         n=self.n+1,
                                         value=fstr(value),
                                         min=fstr(min_v),
                                         max=fstr(max_v)),
                                         value)
        return value

    def get_bool(self):
        value = self._next()
        if value == '':
            return None
        elif value == '1':
            return True
        elif value == '0':
            return False
        else:
            raise FileInputError(_('Veerus {n} võib olla 0 või 1').format(n=self.n+1), value)

