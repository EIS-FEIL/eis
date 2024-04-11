import pickle
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.sarnasedvastused import SarnasedvastusedDoc
log = logging.getLogger(__name__)

class SarnasedvastusedController(BaseResourceController):
    """Aruanne vastustest, mil ühes grupis sooritajatel on suur osa valevastustest ühesugused
    """
    _permission = 'hindamisanalyys'
    _INDEX_TEMPLATE = 'ekk/hindamine/sarnasedvastused.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/sarnasedvastused_list.mako'
    _DEFAULT_SORT = 'sooritaja.kasutaja_id,sooritaja.id'
    _ignore_default_params = ['pdf','csv']
    _SEARCH_FORM = forms.ekk.hindamine.SarnasedvastusedForm # valideerimisvorm otsinguvormile
    _MODEL = model.Sooritus

    def _query(self):
        pass

    def _search(self, q1):
        if self.c.komplektivalik_id:
            self.c.komplektivalik = model.Komplektivalik.get(self.c.komplektivalik_id)

        if not self.c.komplekt_id:
            # ilma komplektita ei saa võrrelda
            if self.c.komplektivalik and len(self.c.komplektivalik.komplektid) == 1:
                self.c.komplekt_id = self.c.komplektivalik.komplektid[0].id
            else:
                self.error(_("Palun valida alatestid"))
                return
        if not self.c.samuvigu:
            self.c.samuvigu = 60

        if not self.c.otsi and not self.c.pdf and not self.c.csv:
            # kasutaja ei vajutanud otsimise nupule
            return

        # leiame kysimuste koguarvu ja iga kysimuse järjekorranumbri
        self.c.di_index, self.c.alatest_index, self.c.max_index = self._find_ksv_index(self.c.komplekt_id)

        # leiame kõik testiruumid 
        q = (model.SessionR.query(model.Testiruum.id, model.Koht.nimi, model.Ruum.tahis)
             .join(model.Testiruum.testikoht)
             .filter(model.Testikoht.staatus==const.B_STAATUS_KEHTIV)
             .filter(model.Testiruum.sooritajate_arv>0)
             .join(model.Testikoht.koht)
             .outerjoin(model.Testiruum.ruum))
        if self.c.testiruum_id:
            q = q.filter(model.Testiruum.id==self.c.testiruum_id)
        elif self.c.testikoht_id:
            q = q.filter(model.Testiruum.testikoht_id==self.c.testikoht_id)
        else:
            q = q.filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id)
        q = q.order_by(model.Koht.nimi, model.Ruum.tahis)

        # c.items on testiruumide andmete loetelu
        self.c.items = []
        for r in q.all():
            testiruum_id, koht_nimi, r_tahis = r
            # leiame iga testiruumi iga sooritaja vastused
            sooritused = self._get_data(testiruum_id, self.c.komplekt_id, self.c.di_index, self.c.alatest_index)
            # võrdleme sooritusi yksteisega ja leiame selle ruumi spikerdajad
            li_sarnased = self._compare(sooritused, self.c.samuvigu)
            if li_sarnased:
                self.c.items.append((koht_nimi, r_tahis, li_sarnased))

        if len(self.c.items) == 0:
            self.notice(_("Sarnaseid vastuseid ei leitud"))
        elif self.c.pdf:
            return self._index_pdf(q)
        elif self.c.csv:
            return self._index_csv(q)        

    def _index_pdf(self, q):
        doc = SarnasedvastusedDoc(self.c.toimumisaeg,
                                  self.c.items,
                                  self.c.max_index,
                                  self.c.alatest_index)
        data = doc.generate()
        if doc.error:
            filename = 'viga.txt'
            mimetype = const.CONTENT_TYPE_TXT
            data = doc.error
        else:
            filename = 'sarnasedvastused.pdf'
            mimetype = const.CONTENT_TYPE_PDF
        return utils.download(data, filename, mimetype)
                   
    def _find_ksv_index(self, komplekt_id):
        "Leiame iga kysimuse vastuse järjekorra komplektis, et saaks vastuseid kohakuti kuvada"

        q = model.SessionR.query(model.Kysimus, model.Valitudylesanne, model.Testiylesanne).\
            join(model.Kysimus.sisuplokk).\
            join((model.Valitudylesanne, model.Valitudylesanne.ylesanne_id==model.Sisuplokk.ylesanne_id)).\
            join(model.Valitudylesanne.testiylesanne).\
            filter(model.Valitudylesanne.komplekt_id==komplekt_id).\
            order_by(model.Testiylesanne.alatest_seq,
                     model.Testiylesanne.seq,
                     model.Kysimus.seq)

        n_index = 0
        di_index = {}
        alatest_index = [] # alatestide vahetuste asukohad
        prev_alatest_seq = -1
        for r in q.all():
            k, vy, ty = r
            if ty.alatest_seq != prev_alatest_seq:
                # alatest, mida varem pole nähtud
                if prev_alatest_seq != -1:
                    # alatest vahetus
                    alatest_index.append(n_index)
                    n_index += 1
                prev_alatest_seq = ty.alatest_seq
            if vy.id not in di_index:
                di_index[vy.id] = {}
            di_index[vy.id][k.id] = n_index
            #n_index += k.max_vastus or 1
            n_index += 1

        return di_index, alatest_index, n_index
        
    def _get_data(self, testiruum_id, komplekt_id, di_index, alatest_index):
        "Ühe testiruumi soorituste päring"

        sooritused = {}
        q = (model.SessionR.query(model.Sooritus.id,
                                 model.Ylesandevastus.valitudylesanne_id,
                                 model.Kysimus.id,
                                 model.Kvsisu.seq,
                                 model.Kysimus.max_vastus,
                                 model.Kvsisu.kood1,
                                 model.Kvsisu.kood2,
                                 model.Kvsisu.oige)
             .join((model.Valitudylesanne,
                    model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
             .filter(model.Valitudylesanne.komplekt_id==komplekt_id)
             .join((model.Sooritus,
                    model.Sooritus.id==model.Ylesandevastus.sooritus_id))
             .filter(model.Sooritus.testiruum_id==testiruum_id)
             .join(model.Ylesandevastus.kysimusevastused)
             .filter(model.Kysimusevastus.sisestus==1)
             .join(model.Kysimusevastus.kvsisud)
             .join((model.Testiylesanne,
                    model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id))
             .join((model.Kysimus,
                    model.Kysimus.id==model.Kysimusevastus.kysimus_id))
             .join(model.Sooritus.sooritaja)
             )
        cnt_oige = 0
        for r in q.all():
            sooritus_id, vy_id, k_id, kvs_seq, k_max_vastus, kood1, kood2, oige = r
            n_index = di_index[vy_id][k_id]

            value = '-'
            if oige == const.C_OIGE:
                value = '.'
                cnt_oige += 1
            elif oige == const.C_VALE:
                if kood1 and kood2:
                    value = '(%s,%s)' % (kood1, kood2)
                elif kood1:
                    value = kood1

            if sooritus_id not in sooritused:
                sooritused[sooritus_id] = dict()
                # alatestide vahetuse kohad märgime tärniga
                for r in alatest_index:
                    sooritused[sooritus_id][r] = ['*']

            data = sooritused[sooritus_id]
            if n_index in data:
                data[n_index].append(value)
            else:
                data[n_index] = [value]

        return sooritused

    def _compare(self, sooritused, samuvigu):
        "Ühe testiruumi soorituste võrdlemine, et leida sarnased valevastused"

        # sarnaste valevastuste paaride jada
        li = []

        # leiame iga sooritaja õigete vastuste arvu
        oigedvastused = {}
        for sooritus_id in sooritused:
            oige = 0
            for values in list(sooritused[sooritus_id].values()):
                oige += len([r for r in values if r=='.'])
            oigedvastused[sooritus_id] = oige

        # võrdleme kõiki sooritusi
        for sooritus1_id in sooritused:
            # yhe sooritaja vastused
            data1 = sooritused[sooritus1_id]
            for sooritus2_id in sooritused:
                if sooritus1_id < sooritus2_id:
                    # mittesarnased valevastused
                    msv = 0
                    # sarnased valevastused
                    svv = 0
                    # teise sooritaja vastused
                    data2 = sooritused[sooritus2_id]
                    # tsykkel yle kysimuste
                    for key in data1:
                        # esimese sooritaja valevastused antud kysimusele
                        valed1 = [r for r in data1[key] if r not in '-*.']
                        # teise sooritaja valevastused antud kysimusele
                        valed2 = [r for r in data2.get(key) or [] if r not in '-*.']
                        # sarnaste valevastuste arv
                        svv += len([r for r in valed1 if r in valed2])
                        # mittesarnaste valevastuste arv on nende kysimusevastuste arv,
                        # millele vähemalt yks vastas valesti, aga erinevalt teisest
                        li_msv1 = [r for r in valed1 if r not in valed2]
                        li_msv2 = [r for r in valed2 if r not in valed1]
                        # võimalike vastuste arv
                        max_cnt = max(len(data1[key]), len(data2.get(key) or []))
                        msv += min(len(li_msv1) + len(li_msv2), max_cnt)

                    if svv > 0:
                        svv_protsent = round(svv * 100 / (svv + msv))
                        if svv_protsent >= samuvigu:
                            # nendel kahel sooritusel on piisavalt palju yhesuguseid valevastuseid
                            rcd = self._prepare_row(svv, msv,
                                                    sooritus1_id, data1, oigedvastused[sooritus1_id],
                                                    sooritus2_id, data2, oigedvastused[sooritus2_id])
                            li.append(rcd)
                        
        return li

    def _prepare_row(self, svv, msv,
                     sooritus1_id, data1, oige1,
                     sooritus2_id, data2, oige2):
        "Kahe sarnaste vastustega sooritaja andmete saamise funktsioon"
        
        q = model.SessionR.query(model.Sooritus.tahised,
                                model.Kasutaja.isikukood,
                                model.Sooritus.pallid)
        q = q.join(model.Sooritus.sooritaja).\
            join(model.Sooritaja.kasutaja)

        tahised1, ik1, pallid1 = q.filter(model.Sooritus.id==sooritus1_id).first()
        tahised2, ik2, pallid2 = q.filter(model.Sooritus.id==sooritus2_id).first()

        hh = msv and float(svv) / msv or None

        return [[ik1, tahised1, pallid1, data1, oige1], 
                [ik2, tahised2, pallid2, data2, oige2],
                hh, svv, msv,
                ]

    def _prepare_header(self):
        c = self.c
        h = self.h
        header = [_("Isikukood"),
                  _("Töökood"),
                  _("Vastused"),
                  ]
        for n in range(c.max_index - 1):
            header.append('')
        header.extend([_("Tulemus"),
                       'ÕV',
                       'H-H',
                       'SVV',
                       'MSV',
                       ])
        return header

    def _prepare_items(self, q):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        c = self.c
        h = self.h
        header = self._prepare_header()
        items = []
        for n, rcd in enumerate(c.items):
            koht_nimi, ruum_tahis, li_sarnased = rcd
            item = ['%s ruum %s' % (koht_nimi, ruum_tahis or '')]
            items.append(item)

            for rcd in li_sarnased:
                li1, li2, hh, svv, msv = rcd

                # esimene isik
                [ik1, tahised1, pallid1, data1, oige1] = li1
                item = [ik1 or '',
                        tahised1 or '',
                        ]
                for n in range(c.max_index):
                    value = ''
                    if n in c.alatest_index:
                        value = '*'
                    elif n in data1:
                        value = ' '.join(data1.get(n))
                    item.append(value)
                item.append(h.fstr(pallid1) or '')
                item.append(oige1 or '')
                
                item.append(h.fstr(hh) or '')
                item.append(svv or '')
                item.append(msv or '')
                items.append(item)

                # teine isik
                [ik1, tahised1, pallid1, data1, oige1] = li2
                item = [ik1 or '',
                        tahised1 or '',
                        ]
                for n in range(c.max_index):
                    value = ''
                    if n in c.alatest_index:
                        value = '*'
                    elif n in data1:
                        value = ' '.join(data1.get(n))
                    item.append(value)
                item.append(h.fstr(pallid1) or '')
                item.append(oige1 or '')
                items.append(item or '')

        return header, items

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.test = self.c.toimumisaeg.testiosa.test
        
    def _perm_params(self):
        return {'obj': self.c.test}
