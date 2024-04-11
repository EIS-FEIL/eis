import base64
from simplejson import dumps
from eis.lib.baseresource import *
from eis.lib.pdf.avalikmaterjal import AvalikMaterjalDoc
import eis.lib.ddocs as ddocs
from eis.lib.inmemoryzip import InMemoryZip
import eis.lib.html_export as html_export
import pickle
_ = i18n._
log = logging.getLogger(__name__)

FN_VASTUSED = 'vastused.dat' # failinimi konteineris, milles on vastused

class KinnitamineController(BaseResourceController):
    """Protokolli kinnitamine
    """
    _permission = 'toimumisprotokoll'
    _INDEX_TEMPLATE = 'avalik/protokollid/kinnitamine.mako'

    def index(self):
        return self.render_to_response(self._INDEX_TEMPLATE)

    def create(self):
        """Protokolli kinnitamine
        """
        sub = self._get_sub()
        if sub:
            return eval('self._create_%s' % sub)()

        f = self.request.params.get('protokoll_dok')

        err = self._osalemine_margitud()
        if err:
            self.error(err)

        elif self.request.params.get('genereeri'):
            # genereeritakse uus protokoll
            if self.c.toimumisprotokoll.staatus in (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD):
                self.error(_("Protokoll on juba kinnitatud"))
            else:
                return self._create_gen()

        elif self.request.params.get('preview'):
            return self._create_gen(True)
        
        elif f != b'':
            file_data = f.value
            filename = f.filename
            ext = filename.rsplit('.', 1)[-1].lower()
            if ext not in (const.ASICE, const.BDOC):
                self.error(_('Faili ei salvestata, kuna see pole ASIC-E ega BDOC'))
            else:
                self.c.toimumisprotokoll.filename = _fn_local(filename)
                self.c.toimumisprotokoll.filedata = file_data
                self.c.toimumisprotokoll.staatus = const.B_STAATUS_KINNITATUD
                self.c.toimumisprotokoll.kehtivuskinnituseta = False
                model.Session.commit()
                self.success(_('Protokoll on kinnitatud'))
        else:
            self.error(_('Palun laadi fail üles'))
        return self._after_create(None)
            
    def _after_create(self, id):
        return self._redirect('index', toimumisprotokoll_id=self.c.toimumisprotokoll.id)        

    def _create_prepare_signature(self):
        """Allkirjastamise alustamine: brauserilt on saadud sert,
        selle kohta arvutatakse allkirjastatav räsi.
        """
        error = None
        mpr = self.c.toimumisprotokoll        
        filedata = mpr.filedata
        ext = mpr.fileext
        if not filedata:
            error = _('Protokolli pole koostatud')

        filename = 'protokoll.%s' % ext
        filedata, res = ddocs.DdocS.prepare_signature(self, filedata, filename, error)
        if filedata:
            dformat = const.ASICE
            mpr.filename = f'protokoll.{dformat}'
            mpr.filedata = filedata
            model.Session.commit()

        return res
    
    def _create_finalize_signature(self):
        """Allkirjastamise lõpetamine: brauserilt on saadud allkiri,
        see lisatakse pooleli oleva konteineri sisse.
        """
        mpr = self.c.toimumisprotokoll
        filedata, signers, dformat = ddocs.DdocS.finalize_signature(self, mpr.filedata)
        if filedata:
            mpr.filename = f'protokoll.{dformat}'
            mpr.filedata = filedata
            mpr.staatus = const.B_STAATUS_KINNITATUD
            model.Session.commit()
            self.success()

        return self._redirect('index')

    def _download(self, id, format):
        """Näita faili"""

        filedata = self.c.toimumisprotokoll.filedata
        filename = 'protokoll.%s' % (self.c.toimumisprotokoll.fileext)

        if not filedata:
            raise NotFound(_('Dokumenti ei leitud'))   

        return utils.download(filedata, filename)

    def _gen_pdf(self, is_preview=False):
        """Väljatrükid
        """
        doc = AvalikMaterjalDoc(self.c.toimumisprotokoll)
        if is_preview:
            doc.preview = True
        return doc.generate(), doc.error

    def _gen_vastused(self, testikohad_id):
        """Koondvastuse moodustamine, EISi formaadis
        """
        q = model.Sooritus.query.\
            filter(model.Sooritus.testikoht_id.in_(testikohad_id)).\
            join(model.Sooritus.sooritaja).\
            filter(model.Sooritaja.lang==self.c.toimumisprotokoll.lang)
        sooritused = q.all()
        p = Pack(None)
        li = p.pack_sooritused(sooritused)
        data = pickle.dumps(li, pickle.HIGHEST_PROTOCOL)
        data = base64.b64encode(data)
        return data

    def _gen_kutse_komplektid(self, testikohad_id):
        """Komplektid õige vastusega HTMLis, kutseeksami jaoks
        """
        # leiame kasutatud komplektid
        q = (model.Session.query(model.Sooritaja.lang, model.Komplekt.id)
             .distinct()
             .join(model.Sooritaja.sooritused)
             .join(model.Sooritus.hindamisolekud)
             .join(model.Hindamisolek.komplekt)
             )
        if self.c.testiruum:
            q = q.filter(model.Sooritus.testiruum_id==self.c.testiruum.id)
        else:
            q = q.filter(model.Sooritus.testikoht_id.in_(testikohad_id))
        q = q.order_by(model.Sooritaja.lang,
                       model.Komplekt.komplektivalik_id,
                       model.Komplekt.tahis)

        lang_k = [(lang, k_id) for (lang, k_id) in q.all()]

        # leiame komplektides kasutatud piltide mahu
        total = 0
        for lang, k_id in lang_k:
            q = (model.Session.query(sa.func.sum(
                sa.func.coalesce(model.T_Sisuobjekt.filesize, model.Sisuobjekt.filesize)))
                 .select_from(model.Sisuobjekt)
                 .outerjoin((model.T_Sisuobjekt,
                            sa.and_(model.T_Sisuobjekt.orig_id==model.Sisuobjekt.id,
                                    model.T_Sisuobjekt.ylesandeversioon_id==None,
                                    model.T_Sisuobjekt.lang==lang)))
                 .join(model.Sisuobjekt.sisuplokk)
                 .join((model.Valitudylesanne,
                       model.Valitudylesanne.ylesanne_id==model.Sisuplokk.ylesanne_id))
                 .filter(model.Valitudylesanne.komplekt_id==k_id))
            k_total = q.scalar()
            total += k_total or 0
        # testi 104 piltide maht on 189 MB ja see on liiga suur ES-3452
        # testi 103 piltide maht on 13 MB
        MAX_BYTES = 25000000 # 25 MB
        if total:
            log.info('Testi {id} komplektide failide maht on {n} B'.format(id=self.c.test.id, n=total))
        
        li = []
        self.c.block_correct = True # märkida õiged valikud
        if total > MAX_BYTES:
            log.debug('Komplektide faili protokolli ei lisa')
        else:
            # lisatakse komplektide failid
            for lang, k_id in lang_k:
                komplekt = model.Komplekt.get(k_id)

                filedata = html_export.export_test_pdf(komplekt, lang, self)
                fn = 'komplekt%s %s.pdf' % (komplekt.id, komplekt.tahis.replace('/', '_'))            
                li.append((fn, filedata))

        return li

    def _gen_kutse_kvastused(self, testikohad_id):
        """Kysimuste vastused Excelis, kutseeksami jaoks
        """
        testikoht = self.c.toimumisprotokoll.testikoht
        test = self.c.test
        testiosa = testikoht.testiosa
        if testiosa.lotv:
            # lõdva struktuuri korral ei saa andmeid yhes tabelis kuvada
            return []

        def _get_items(tycnt):
            items = []
            # leiame sooritajate tulemused
            q = (model.Session.query(model.Sooritus,
                                     model.Sooritaja.eesnimi,
                                     model.Sooritaja.perenimi,
                                     model.Sooritaja.lang,
                                     model.Kasutaja.isikukood)
                 .join(model.Sooritus.sooritaja)
                 .join(model.Sooritaja.kasutaja)
                 .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                 )
            if self.c.testiruum:
                q = q.filter(model.Sooritus.testiruum_id==self.c.testiruum.id)
            else:
                q = q.filter(model.Sooritus.testikoht_id.in_(testikohad_id))
            q = q.order_by(model.Sooritaja.perenimi,
                           model.Sooritaja.eesnimi)
            sptyybid = (const.INTER_CHOICE,
                        const.INTER_SLIDER,
                        const.INTER_EXT_TEXT,
                        const.INTER_INL_TEXT)
            for sooritus, eesnimi, perenimi, lang, ik in q.all():
                # valikvastusega küsimuse sisuplokkide vastused
                qs = (model.Session.query(model.Ylesandevastus.testiylesanne_id,
                                          model.Valitudylesanne.komplekt_id,
                                          model.Testiylesanne.alatest_id,
                                          model.Sisuplokk.ylesanne_id,
                                          model.Kysimus.kood,
                                          model.Sisuplokk.nimi,
                                          model.Kvsisu.kood1,
                                          model.Kvsisu.sisu,
                                          model.Kvsisu.oige,
                                          model.Valik.nimi)
                      .filter(model.Ylesandevastus.sooritus_id==sooritus.id)
                      .filter(model.Ylesandevastus.loplik==True)
                      .join((model.Testiylesanne,
                             model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id))
                      .join((model.Valitudylesanne,
                             model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
                      .join(model.Ylesandevastus.kysimusevastused)
                      .join(model.Kysimusevastus.kvsisud)
                      .join((model.Kysimus,
                             model.Kysimus.id==model.Kysimusevastus.kysimus_id))
                      .join(model.Kysimus.sisuplokk)
                      .filter(model.Sisuplokk.tyyp.in_(sptyybid))
                      .outerjoin((model.Valik,
                                  sa.and_(model.Valik.kysimus_id==model.Kysimus.id,
                                          model.Valik.kood==model.Kvsisu.kood1)))
                      .order_by(model.Testiylesanne.seq,
                                model.Sisuplokk.seq,
                                model.Kysimus.seq,
                                model.Kvsisu.seq)
                       )
                
                sdata = {} # sooritaja tulemused ty kaupa
                kdata = [] # komplektid
                for ty_id, km_id, a_id, y_id, k_kood, sp_nimi, v_kood, ks_sisu, v_oige, v_nimi in qs.all():
                    if ty_id not in sdata:
                        sdata[ty_id] = []
                    sdata[ty_id].append((km_id, ty_id, y_id, sp_nimi, v_kood, ks_sisu, v_nimi, v_oige))
                    cnt = len(sdata[ty_id])
                    if cnt > tycnt[ty_id]:
                        tycnt[ty_id] = cnt
                    if km_id not in kdata:
                        kdata.append(km_id)
                        
                item = (ik,
                        eesnimi,
                        perenimi,
                        lang,
                        self.h.str_from_date(sooritus.algus),
                        sdata,
                        kdata)
                items.append(item)
            return items

        def _get_cols(tycnt):
            # paneme paika veerud
            prev_kv_id = None
            cols = []
            header = [_('Test'),
                      _('Isikukood'),
                      _('Eesnimi'),
                      _('Perekonnanimi'),
                      _('Keel'),
                      _('Kuupäev'),
                      ]
            for alatest in list(testiosa.alatestid) or [None]:
                if alatest:
                    testiylesanded = list(alatest.testiylesanded)
                    kv_id = alatest.komplektivalik_id
                    a_title = '%s_%s_' % (alatest.seq, alatest.nimi) 
                else:
                    testiylesanded = list(testiosa.testiylesanded)
                    for kv in testiosa.komplektivalikud:
                        kv_id = True
                    a_title = ''
                if prev_kv_id != kv_id:
                    prev_kv_id = kv_id
                    cols.append(('KV', kv_id))
                    header.append(_('Komplekt'))
                for ty in testiylesanded:
                    title = '%s%02d' % (a_title, ty.seq)
                    v_cnt = tycnt[ty.id]
                    for seq in range(v_cnt):
                        cols.append((ty.id, seq))
                        suffix = v_cnt > 1 and f'_{seq+1}' or ''
                        header.append(f'{title}_kysimus{suffix}')
                        header.append(f'{title}_vastus{suffix}')
                        header.append(f'{title}_oige{suffix}')
            return cols, header
                
        tycnt = {} # testiylesande kysimuste max võimalik arv
        for ty in testiosa.testiylesanded:
            tycnt[ty.id] = 0
            
        # leiame soorituste andmed
        items = _get_items(tycnt)
        # paneme paika veerud
        cols, header = _get_cols(tycnt)

        # leiame komplektivalikud
        kvalikud = {}
        ktahised = {}
        for kv in testiosa.komplektivalikud:
            for k in kv.komplektid:
                kvalikud[k.id] = kv.id
                ktahised[k.id] = k.tahis

        rows = []
        # paneme andmete tabeli kokku
        for ik, eesnimi, perenimi, lang, algus, sdata, kdata in items:
            kdict = {kvalikud[k_id]: k_id for k_id in kdata}
            row = [test.nimi,
                   ik,
                   eesnimi,
                   perenimi,
                   lang,
                   algus]
            for col in cols:
                if col[0] == 'KV':
                    # komplekti veerg
                    kv_id = col[1]
                    km_id = kdict.get(kv_id)
                    row.append(ktahised.get(km_id))
                else:
                    # ylesande veerud
                    ty_id = col[0]
                    kseq = col[1]
                    r = sdata.get(ty_id)
                    if r and len(r) > kseq:
                        km_id, ty_id, y_id, sp_nimi, v_kood, ks_sisu, v_nimi, v_oige = r[kseq]
                        row.append('%d - %s' % (y_id, sp_nimi)) # kysimus
                        if v_kood:
                            sresp = '%s - %s' % (v_kood, v_nimi)
                        else:
                            sresp = ks_sisu
                        row.append(sresp) # vastus
                        row.append(v_oige) # oige
                    else:
                        row.append('')
                        row.append('')
                        row.append('')
            rows.append(row)

        filedata = utils.xls_data(header, rows)        
        return filedata

    def _gen_kutse_tulemused(self, testikohad_id):
        """Kysimuste vastused Excelis, kutseeksami jaoks
        """
        testikoht = self.c.toimumisprotokoll.testikoht
        test = self.c.test
        testiosa = testikoht.testiosa

        def _get_cols():
            # paneme paika veerud
            prev_kv_id = None
            cols = []
            header = [_('Sooritaja'),
                      _('Kuupäev'),
                      ]
            for alatest in list(testiosa.alatestid) or [None]:
                if alatest:
                    testiylesanded = list(alatest.testiylesanded)
                    kv_id = alatest.komplektivalik_id
                    a_title = '%s %s' % (alatest.nimi, _('kokku'))
                else:
                    testiylesanded = list(testiosa.testiylesanded)
                    for kv in testiosa.komplektivalikud:
                        kv_id = True
                    a_title = None
                testiylesanded = [ty for ty in testiylesanded if ty.liik == const.TY_LIIK_Y]
                if testiylesanded:
                    # alatestis leidub mõni tavaline ylesanne
                    if prev_kv_id != kv_id:
                        prev_kv_id = kv_id
                        cols.append(('KV', kv_id))
                        header.append(_('Komplekt'))
                    for ty in testiylesanded:
                        cols.append(('TY', ty.id))
                        header.append(ty.tahis or '')
                    if alatest:
                        cols.append(('A', alatest.id))
                        header.append('%s %s' % (alatest.nimi, _('kokku')))

            header.append(_('Kokku'))
            header.append(_('Ajakulu'))
            return cols, header

        def _get_items(cols):
            items = []
            # leiame sooritajate tulemused
            q = (model.Session.query(model.Sooritus, model.Sooritaja)
                 .join(model.Sooritus.sooritaja)
                 .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                 )
            if self.c.testiruum:
                q = q.filter(model.Sooritus.testiruum_id==self.c.testiruum.id)
            else:
                q = q.filter(model.Sooritus.testikoht_id.in_(testikohad_id))
            q = q.order_by(model.Sooritus.tahised,
                           model.Sooritaja.perenimi,
                           model.Sooritaja.eesnimi)
            for sooritus, sooritaja in q.all():
                # ylesannete tulemused
                qs = (model.Session.query(model.Ylesandevastus.pallid,
                                          model.Ylesandevastus.testiylesanne_id)
                      .filter(model.Ylesandevastus.sooritus_id==sooritus.id)
                      .filter(model.Ylesandevastus.loplik==True)
                      )
                sdata = {}
                for pallid, ty_id in qs.all():
                    sdata[ty_id] = self.h.fstr(pallid)

                # alatestide tulemused
                qa = (model.Session.query(model.Alatestisooritus.pallid,
                                          model.Alatestisooritus.alatest_id)
                      .filter(model.Alatestisooritus.sooritus_id==sooritus.id)
                      )
                adata = {a_id: self.h.fstr(pallid) for (pallid, a_id) in qa.all()}

                # sooritatud komplektid
                qk = (model.Session.query(model.Hindamisolek.komplekt_id,
                                          model.Komplekt.komplektivalik_id,
                                          model.Komplekt.tahis)
                      .filter(model.Hindamisolek.sooritus_id==sooritus.id)
                      .join(model.Hindamisolek.komplekt)
                      )
                kdata = {}
                for km_id, kv_id, k_tahis in qk.all():
                    kdata[kv_id] = k_tahis

                # rea kokkupanek
                if sooritus.tahised:
                    nimi = '%s %s' % (sooritus.tahised, sooritaja.nimi)
                else:
                    nimi = sooritaja.nimi
                item = [nimi,
                        self.h.str_from_date(sooritus.algus),
                        ]
                for col in cols:
                    if col[0] == 'KV':
                        kv_id = col[1]
                        item.append(kdata.get(kv_id))
                    elif col[0] == 'TY':
                        ty_id = col[1]
                        item.append(sdata.get(ty_id))
                    elif col[0] == 'A':
                        a_id = col[1]
                        item.append(adata.get(a_id))
                item.append(sooritaja.get_tulemus())
                item.append(self.h.str_from_time_sec(sooritus.ajakulu))
                items.append(item)
            return items

        cols, header = _get_cols()
        rows = _get_items(cols)

        filedata = utils.xls_data(header, rows)        
        return filedata

    def _create_gen(self, is_preview=False):
        vastvorm_e = (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_SH)
        e_testikohad_id = [r.id for r in self.c.testikohad \
                           if r.testiosa.vastvorm_kood in vastvorm_e]

        # genereerime failid
        data_pdf, error = self._gen_pdf(is_preview)

        if not error:
            test = self.c.test
            if test.testiliik_kood == const.TESTILIIK_KUTSE:
                zipf = InMemoryZip().append('protokoll.pdf', data_pdf)
                # e-testi korral lisame konteinerisse sooritajate antud vastused
                if len(e_testikohad_id) or self.c.testiruum:
                    for fn_v, data_v in self._gen_kutse_komplektid(e_testikohad_id):
                        zipf.append(fn_v, data_v)

                    data_v = self._gen_kutse_kvastused(e_testikohad_id)
                    if data_v:
                        zipf.append('vastused.xlsx', data_v)                    
                    data_v = self._gen_kutse_tulemused(e_testikohad_id)
                    if data_v:
                        zipf.append('tulemused.xlsx', data_v)
                        
                filedata = zipf.close().read()
                fileext = const.ZIP
            else:
                filedata = data_pdf
                fileext = const.PDF
        if error:
            self.error(error)
        elif is_preview:
            filename = 'protokoll.%s' % (fileext)
            return utils.download(filedata, filename)
            
        else:
            # salvestame konteineri andmebaasis
            mpr = self.c.toimumisprotokoll
            mpr.filename = f'protokoll.{fileext}'
            mpr.filedata = filedata
            mpr.staatus = const.B_STAATUS_KINNITATUD
            mpr.kehtivuskinnituseta = False
            mpr.edastatud = None
            model.Session.commit()
            self.success(_('Protokoll on koostatud'))

        return self._after_create(None)

    def _osalemine_margitud(self):
        """Kas kõigi osaliste osaline on märgitud?
        Kui pole, siis ei tohi saada protokolli kinnitada.
        """
        prot_tulemusega = self.c.testimiskord and self.c.testimiskord.prot_tulemusega
        testiruum_id = self.c.testiruum and self.c.testiruum.id or None
        testikohad_id = not testiruum_id and [tk.id for tk in self.c.testikohad] or None

        q = (model.Session.query(sa.func.count(model.Sooritus.id))
             .filter(model.Sooritus.staatus.in_((const.S_STAATUS_REGATUD,
                                                 const.S_STAATUS_ALUSTAMATA,
                                                 const.S_STAATUS_POOLELI)))
             )
        if testiruum_id:
            q = q.filter(model.Sooritus.testiruum_id==testiruum_id)
        else:
            q = q.filter(model.Sooritus.testikoht_id.in_(testikohad_id))
        if q.scalar() > 0:
            model.log_query(q)
            return _('Protokolli ei saa kinnitada, kuna kõigi osalejate olekud pole märgitud')

        if prot_tulemusega:
            q = (model.Session.query(sa.func.count(model.Sooritus.id))
                 .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                 .filter(model.Sooritus.pallid==None))
            if testiruum_id:
                q = q.filter(model.Sooritus.testiruum_id==testiruum_id)
            else:
                q = q.filter(model.Sooritus.testikoht_id.in_(testikohad_id))
            if q.scalar() > 0:
                return _('Protokolli ei saa kinnitada, kuna kõigi osalejate tulemused pole sisestatud')

        else:
            lvgrupid_id = (const.GRUPP_T_ADMIN,
                           const.GRUPP_VAATLEJA,
                           const.GRUPP_HINDAJA_S,
                           const.GRUPP_HINDAJA_S2,
                           const.GRUPP_INTERVJUU,
                           const.GRUPP_HIND_INT,
                           const.GRUPP_KOMISJON,
                           const.GRUPP_KOMISJON_ESIMEES,
                           const.GRUPP_KONSULTANT)
            q = (model.Session.query(sa.func.count(model.Labiviija.id))
                 .filter(model.Labiviija.kasutajagrupp_id.in_(lvgrupid_id))
                 .filter(model.Labiviija.staatus==const.L_STAATUS_MAARATUD))
            if testiruum_id:
                q = q.filter(model.Labiviija.testiruum_id==testiruum_id)
            else:
                q = q.filter(model.Labiviija.testikoht_id.in_(testikohad_id))
            if q.scalar() > 0:
                return _('Protokolli ei saa kinnitada, kuna kõigi läbiviijate olekud pole märgitud')

    def __before__(self):
        c = self.c
        toimumisprotokoll_id = self.request.matchdict.get('toimumisprotokoll_id')
        c.toimumisprotokoll = model.Toimumisprotokoll.get(toimumisprotokoll_id)
        c.testiruum = c.toimumisprotokoll.testiruum
        c.testimiskord = c.toimumisprotokoll.testimiskord
        c.test = c.testimiskord.test
        c.testikohad = list(c.toimumisprotokoll.testikohad)
        for testikoht in c.testikohad:
            toimumisaeg = testikoht.toimumisaeg
            if not c.toimumisaeg1:
                c.toimumisaeg1 = toimumisaeg
            if not toimumisaeg.on_hindamisprotokollid:
                c.is_edit = False

        c.can_edit = c.user.has_permission('toimumisprotokoll', const.BT_UPDATE, c.toimumisprotokoll)
        if not c.can_edit:
            c.is_edit = False

    def _perm_params(self):
        return {'obj': self.c.toimumisprotokoll}

    def _has_permission(self):
        # kontrollitakse, et hindamiskirjed on loodud
        for testikoht in self.c.testikohad:
            if not testikoht.toimumisaeg.on_hindamisprotokollid and self._is_modify():
                return False
        return BaseController._has_permission(self)

def _fn_local(fnPath):
    """
    Rajast eraldatakse failinimi.
    """
    pos = max(fnPath.rfind('\\'), fnPath.rfind('/'))
    if pos > -1:
        return fnPath[pos + 1:]
    else:
        return fnPath

