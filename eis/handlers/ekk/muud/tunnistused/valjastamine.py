from io import BytesIO
from pypdf import PdfWriter
from eis.lib.baseresource import *
from eis.lib.pdf import pages_loader
from eis.lib.pdf.tunnistus import TunnistusDoc
from eis.s3file import S3FileBuf
from eis.lib.digitempelclient import DigitempelClient
log = logging.getLogger(__name__)

# digitemplile allkirjastamiseks mõeldud kataloog MinIOs
DIGITEMPEL_PDF_DIR = 'digitempel/pdf'

class ValjastamineController(BaseResourceController):
    """Valitakse testsessioonid ja sooritajad, kellele koostatakse tunnistuste PDF-failid
    """
    _permission = 'tunnistused'
    _MODEL = model.Tunnistus
    _INDEX_TEMPLATE = 'ekk/muud/tunnistused.valjastamine.mako'
    _log_params_post = True
    _index_after_create = True

    def _index_d(self):
        self._copy_search_params()
        self._get_protsessid()        
        
        # if self.c.rekvisiit_id:
        #     self.c.rekvisiit = model.Rekvisiit.get(self.c.rekvisiit_id)
        if self.c.sooritaja_id:
            # suunatud vaiete loetelust
            sooritaja = model.Sooritaja.get(self.c.sooritaja_id)
            if sooritaja:
                self.c.testiliik = sooritaja.test.testiliik_kood
                self.c.sessioon_id = sooritaja.testimiskord.testsessioon_id
                self.c.isikukood = sooritaja.kasutaja.isikukood

                # valime tunnistuseliigiks uuendamist vajava tunnistuse liigi
                # kui seda ei ole, siis testiliigi
                q_liik = model.Session.query(model.Tunnistus.testiliik_kood).\
                    filter(model.Tunnistus.uuendada==True).\
                    join(model.Tunnistus.testitunnistused).\
                    filter(model.Testitunnistus.sooritaja_id==sooritaja.id)
                for liik, in q_liik.all():
                    self.c.tunnistuseliik = liik
                if not self.c.tunnistuseliik:
                    self.c.tunnistuseliik = self.c.testiliik
                
                if self.c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS):
                    self.c.testimiskord_id = sooritaja.testimiskord_id

                q, q_uued = self._valjasta_q(self.c.sessioon_id, True)
                self.c.kokku = q.count()
                if not self.c.kokku:
                    self.error('Väljastatavaid tunnistusi ei ole')
                else:  
                    self.c.uusi = q_uued.count()
                    self.c.asendatavaid = self.c.kokku - self.c.uusi

        if not self.c.testiliik:
            self.c.testiliik = const.TESTILIIK_RIIGIEKSAM

        # vastavus testi liigi ja selle põhjal väljastatava tunnistuse liigi vahel
        self.c.map_liigid = {
            const.TESTILIIK_RIIGIEKSAM: (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_TASE,),
            const.TESTILIIK_POHIKOOL: (const.TESTILIIK_TASE,),
            const.TESTILIIK_TASE: (const.TESTILIIK_TASE,),
            const.TESTILIIK_SEADUS: (const.TESTILIIK_SEADUS,),
            }
        
        lubatud_tunnistuseliigid = self.c.map_liigid[self.c.testiliik]
        if self.c.tunnistuseliik not in lubatud_tunnistuseliigid:
            self.c.tunnistuseliik = lubatud_tunnistuseliigid[0]

        self.c.opt_t_name = pages_loader.get_templates_opt('tunnistus_%s' % self.c.tunnistuseliik)        
        if not self.c.sessioon_id:
            opt_sessioon = model.Testsessioon.get_opt(self.c.testiliik)
            if len(opt_sessioon):
                self.c.sessioon_id = opt_sessioon[0][0]

        return self.response_dict

    def _index_kontroll(self):
        self.form = Form(self.request, schema=forms.ekk.muud.ValjastamineKontrollForm)
        if not self.form.validate():
            html = self.form.render(self._INDEX_TEMPLATE,
                                    extra_info=self._index_d())            
            return Response(html)

        self._copy_search_params(self.form.data)
        
        q, q_uued = self._valjasta_q(self.c.sessioon_id, True)
        #model.log_query(q_uued)
        
        if self.request.params.get('demo'):
            # kasutaja vajutas nupule "Proovi", et proovida PDF malli
            item = q.first()
            if item:
                sessioon = model.Testsessioon.get(self.c.sessioon_id)
                return self._valjasta_demo(self.c.tunnistuseliik, sessioon, self.c.t_name, item)
            else:
                self.error('Ühtki tunnistust ei leitud')

        self.c.kokku = q.count()
        if not self.c.kokku:
            self.error('Väljastatavaid tunnistusi ei ole')
        else:  
            self.c.uusi = q_uued.count()
            self.c.asendatavaid = self.c.kokku - self.c.uusi

        self.c.ainultuued = True
        self.c.nosub = True
        return self.index()

    def _create_valjasta(self):
        self._copy_search_params()
        sessioon = model.Testsessioon.get(self.c.sessioon_id)
        
        self.form = Form(self.request, schema=forms.ekk.muud.ValjastamineForm)
        self.form.validate()
        
        self._copy_search_params(self.form.data)
        
        for rcd in self._query_protsessid(True):
            rcd.lopp = datetime.now()
        
        ainultuued = self.form.data.get('ainultuued')
        pohjendus = self.form.data.get('pohjendus')
        t_name = self.form.data.get('t_name')
        
        if pohjendus and len(pohjendus) > 255:
            self.error('Põhjendus ei tohi olla pikem kui 255 sümbolit')
        else:
            childfunc = lambda protsess: self._valjasta(protsess, self.c.sessioon_id, t_name, ainultuued, pohjendus)
            params = {'liik': model.Arvutusprotsess.LIIK_VALJASTAMINE,
                      'kirjeldus': 'Tunnistuste väljastamine sessioonile %s' % sessioon.nimi,
                      'testsessioon_id': self.c.sessioon_id,
                      }
            model.Arvutusprotsess.start(self, params, childfunc)
            self.success('Tunnistuste väljastamine käivitatud')
            return self._redirect('index',
                                  tunnistuseliik=self.c.tunnistuseliik,
                                  testiliik=self.c.testiliik,
                                  sessioon_id=self.c.sessioon_id,
                                  testimiskord_id=self.c.testimiskord_id,
                                  t_name=self.c.t_name,
                                  isikukood=self.c.isikukood)
        self.c.nosub = True
        return self.index()
        
    def _valjasta_q(self, sessioon_id, ainultuued):
        "Päringu koostamine"

        tunnistuseliik = self.c.tunnistuseliik
        if tunnistuseliik == const.TESTILIIK_RIIGIEKSAM:
            f_tkord = sa.and_(model.Testimiskord.testsessioon_id==sessioon_id,
                              model.Testimiskord.test.has(model.Test.testiliik_kood==self.c.testiliik))
            if self.c.testimiskord_id:
                f_tkord = sa.and_(f_tkord, model.Testimiskord.id==self.c.testimiskord_id)

            q = model.Kasutaja.query.\
                filter(model.Kasutaja.sooritajad.any(\
                    sa.and_(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD,
                            model.Sooritaja.staatus==const.S_STAATUS_TEHTUD,
                            model.Sooritaja.testimiskord.has(f_tkord))))
            
            # ei tohi olla pooleli vaidemenetlusi
            # kontrollime, et antud kasutajal antud testsessioonis antud testiliigiga vaideid pooleli poleks
            Vaidesooritaja = sa.orm.aliased(model.Sooritaja)
            Vaidekord = sa.orm.aliased(model.Testimiskord)
            Vaidetest = sa.orm.aliased(model.Test)
            q = q.filter(~ sa.exists().where(sa.and_(model.Vaie.staatus.in_((const.V_STAATUS_MENETLEMISEL, const.V_STAATUS_ETTEPANDUD)),
                                                     model.Vaie.sooritaja_id==Vaidesooritaja.id,
                                                     Vaidesooritaja.kasutaja_id==model.Kasutaja.id,
                                                     Vaidesooritaja.testimiskord_id==Vaidekord.id,
                                                     Vaidekord.testsessioon_id==sessioon_id,
                                                     Vaidesooritaja.test_id==Vaidetest.id,
                                                     Vaidetest.testiliik_kood==self.c.testiliik)))
        else:
            # TASE, SEADUS
            # tunnistus väljastatakse, kui tulemus ei ole lävest väiksem
            q = model.Sooritaja.query.\
                join(model.Sooritaja.kasutaja).\
                join(model.Sooritaja.testimiskord).\
                join(model.Sooritaja.test).\
                filter(model.Testimiskord.testsessioon_id==sessioon_id).\
                filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD).\
                filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD).\
                filter(model.Sooritaja.tulemus_piisav==True).\
                filter(model.Test.testiliik_kood==self.c.testiliik)
            if self.c.testimiskord_id:
                q = q.filter(model.Testimiskord.id==self.c.testimiskord_id)

            if self.c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_POHIKOOL):
                # aine peab olema "eesti keel teise keelena"
                # ja keeletase peab olemas olema
                q = q.join(model.Sooritaja.test).\
                    filter(model.Test.aine_kood==const.AINE_ET2).\
                    filter(model.Sooritaja.keeletase_kood!=None)

            # ei tohi olla pooleli vaidemenetlusi
            q = q.filter(~ sa.exists().where(sa.and_(model.Vaie.staatus.in_((const.V_STAATUS_MENETLEMISEL, const.V_STAATUS_ETTEPANDUD)),
                                                     model.Vaie.sooritaja_id==model.Sooritaja.id)))
        if self.c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))            

        q1 = q
        if ainultuued:
            # jätame välja need õpilased, kellele on tunnistus juba tehtud (kui see ei vaja uuendamist)
            if tunnistuseliik == const.TESTILIIK_RIIGIEKSAM:
                q1 = q.filter(~ sa.exists().where(sa.and_(model.Tunnistus.kasutaja_id==model.Kasutaja.id,
                                                          model.Tunnistus.testsessioon_id==sessioon_id,
                                                          model.Tunnistus.staatus>=const.N_STAATUS_KEHTIV,
                                                          model.Tunnistus.testiliik_kood==const.TESTILIIK_RIIGIEKSAM,
                                                          model.Tunnistus.uuendada==False)))
            else:
                q1 = q.filter(~ sa.exists().where(sa.and_(model.Testitunnistus.sooritaja_id==model.Sooritaja.id,
                                                          model.Testitunnistus.tunnistus_id==model.Tunnistus.id,
                                                          model.Tunnistus.staatus>=const.N_STAATUS_KEHTIV,
                                                          model.Tunnistus.testiliik_kood==tunnistuseliik,
                                                          model.Tunnistus.uuendada==False)))
        return q, q1

    def _valjasta(self, protsess, sessioon_id, t_name, ainultuued, pohjendus):
        tunnistuseliik = self.c.tunnistuseliik
        sessioon = model.Testsessioon.get(sessioon_id)
        q_koik, q = self._valjasta_q(sessioon_id, ainultuued)
        doc = TunnistusDoc(tunnistuseliik, sessioon, t_name)
        total = q.count()
        cnt = 0
        sbuf = S3FileBuf()
        for item in q.all():
            # otsime senised tunnistused, et need kehtetuks märkida
            if tunnistuseliik == const.TESTILIIK_RIIGIEKSAM:
                kasutaja = item
                q_old = model.Tunnistus.query.\
                    filter(model.Tunnistus.kasutaja_id==kasutaja.id).\
                    filter(model.Tunnistus.testsessioon_id==sessioon.id).\
                    filter(model.Tunnistus.testiliik_kood==tunnistuseliik)
            else:
                sooritaja = item
                kasutaja = sooritaja.kasutaja
                q_old = model.Tunnistus.query.\
                    join(model.Tunnistus.testitunnistused).\
                    filter(model.Testitunnistus.sooritaja_id==sooritaja.id).\
                    filter(model.Tunnistus.testiliik_kood==tunnistuseliik)
                    
            seq = None # soorituse jrk nr (sessioonis või REISi tunnistuste korral koolis)
            t_numbrid = [] # sama tunnistuse varasemad numbrid
            numbrityvi = None # sama tunnistuse kõigi väljastuste yhine tyvi

            if ainultuued and q_old.filter(model.Tunnistus.uuendada==False).\
                   filter(model.Tunnistus.staatus>=const.N_STAATUS_KEHTIV).\
                   count() > 0:
                # on olemas vana kehtiv tunnistus, mis pole märgitud uuendamiseks,
                # aga praegu soovitakse ainult uute tunnistuste väljastamist
                # võibolla on paralleelselt käivitatud mitu väljastamist
                continue
            
            for t_old in q_old.all():
                # käime läbi vanad tunnistused (mille asemel uus tunnistus antakse)
                if t_old.uuendada:
                    t_old.uuendada = False
                if t_old.staatus >= const.N_STAATUS_KEHTIV:
                    t_old.staatus = const.N_STAATUS_KEHTETU
                    
                t_numbrid.append(t_old.tunnistusenr)
                # REISist antud tunnistuse tyvi on kujul 2AA-KKKSSS, kus AA - aasta, KKK - kool, SSS - sooritus (seq)
                # TSEISist antud tyvi on TAA-KKKKSSSSSSS, kus T - keeletase, KKKK - kool, SSSSSSS - sooritus, nt 412-12043201101-1
                numbrityvi = t_old.tunnistusenr.rsplit('-', 1)[0]
                seq = t_old.seq
            
            if numbrityvi is None:
                # varem pole tunnistust antud
                seq = model.Session.query(sa.func.max(model.Tunnistus.seq)).\
                    filter(model.Tunnistus.oppeaasta==sessioon.oppeaasta).\
                    filter(model.Tunnistus.testiliik_kood==tunnistuseliik).\
                    scalar()
                seq = (seq or 0) + 1
                if tunnistuseliik == const.TESTILIIK_RIIGIEKSAM:
                    esitaht = '2'
                elif tunnistuseliik == const.TESTILIIK_TASE:
                    tase_kood = sooritaja.keeletase_kood
                    if not tase_kood:
                        self.error('Sooritaja %s ei saanud testil %s keeleoskuse taset - ei saa genereerida tunnistusenumbrit' % \
                                   (sooritaja.kasutaja.nimi, sooritaja.test_id))
                        model.Session.rollback()
                        return cnt                        
                    tasemetunnused = {const.KEELETASE_A2: '4',
                                      const.KEELETASE_B1: '5',
                                      const.KEELETASE_B2: '6',
                                      const.KEELETASE_C1: '7',
                                      const.KEELETASE_ALG: 'A', # 1
                                      const.KEELETASE_KESK: 'A', # 2
                                      const.KEELETASE_KORG: 'A', # 3
                                      }
                    esitaht = tasemetunnused.get(tase_kood)
                    if not esitaht:
                        self.error('Sooritaja %s sai testil %s keeleoskuse taseme %s - ei saa genereerida tunnistusenumbrit' % \
                                   (sooritaja.kasutaja.nimi, sooritaja.test_id, tase_kood))                        
                        model.Session.rollback()
                        return cnt
                elif tunnistuseliik == const.TESTILIIK_SEADUS:
                    esitaht = '1'
                numbrityvi = '%s%02d-%06d' % (esitaht, sessioon.oppeaasta % 100, seq)
                
            # leiame uuele tunnistusele numbri
            for n_nr in range(1,10):
                tunnistusenr = '%s-%d' % (numbrityvi, n_nr)
                if tunnistusenr not in t_numbrid:
                    break
            opilane = kasutaja.any_opilane
            kool = opilane and opilane.koht or None
            tunnistus = model.Tunnistus(testsessioon=sessioon, 
                                        kasutaja_id=kasutaja.id,
                                        kool_koht=kool,
                                        oppeaasta=sessioon.oppeaasta,
                                        tunnistusenr=tunnistusenr,
                                        pohjendus=pohjendus,
                                        testiliik_kood=tunnistuseliik,
                                        seq=seq)

            tunnistus.valjastamisaeg = datetime.now()
            tunnistus.eesnimi = kasutaja.eesnimi
            tunnistus.perenimi = kasutaja.perenimi
            tunnistus.staatus = const.N_STAATUS_KEHTIV
            tunnistus.uuendada = False
            tunnistus.flush()

            sooritajad = list()
            # loome uuele tunnistusele seosed nende testisooritustega, 
            # mille tulemusi tunnistus tunnistab
            if tunnistuseliik == const.TESTILIIK_RIIGIEKSAM:
                q_sooritajad = model.Session.query(model.Sooritaja, model.Test).\
                   filter(model.Sooritaja.kasutaja_id==kasutaja.id).\
                   join(model.Sooritaja.testimiskord).\
                   filter(model.Testimiskord.testsessioon_id==sessioon.id).\
                   filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD).\
                   filter(model.Sooritaja.staatus.in_((const.S_STAATUS_TEHTUD, 
                                                       const.S_STAATUS_KATKESTATUD, 
                                                       const.S_STAATUS_KATKESPROT, 
                                                       const.S_STAATUS_EEMALDATUD))).\
                   join(model.Testimiskord.test).\
                   order_by(model.Test.nimi)

                for sooritaja, test in q_sooritajad.all():
                    testitunnistus = model.Testitunnistus(sooritaja_id=sooritaja.id,
                                                          tunnistus=tunnistus)
                    tunnistus.testitunnistused.append(testitunnistus)
                    sooritajad.append(sooritaja)

                doc.set_data(tunnistus.tunnistusenr, 
                             kasutaja.nimi,
                             tunnistus.valjastamisaeg,
                             tunnistus.oppeaasta, 
                             kasutaja,
                             q_sooritajad,
                             None)
            else:
                testitunnistus = model.Testitunnistus(sooritaja_id=sooritaja.id,
                                                      tunnistus=tunnistus)
                tunnistus.testitunnistused.append(testitunnistus)

                doc.set_data(tunnistus.tunnistusenr, 
                             kasutaja.nimi,
                             tunnistus.valjastamisaeg,
                             tunnistus.oppeaasta, 
                             kasutaja,
                             None,
                             sooritaja)
                sooritajad.append(sooritaja)
                    
            # võtame vaietelt maha uuendamise märked
            for testitunnistus in tunnistus.testitunnistused:
                for vaie in model.Vaie.query.filter_by(sooritaja_id=testitunnistus.sooritaja_id).all():
                    if vaie.tunnistada in (const.U_STAATUS_UUENDADA, const.U_STAATUS_VALJASTADA):
                        # kui pole teisi tunnistusi, mille uuendamist see vaie nõuab, 
                        # siis võtame uuendamise maha
                        q = model.Testitunnistus.query.\
                            filter(model.Testitunnistus.sooritaja_id==vaie.sooritaja_id).\
                            filter(model.Testitunnistus.tunnistus_id!=tunnistus.id).\
                            join(model.Testitunnistus.tunnistus).\
                            filter(model.Tunnistus.uuendada==True).\
                            filter(model.Tunnistus.staatus>=const.N_STAATUS_KEHTIV)
                        if q.count() == 0:
                            vaie.tunnistada = None

            filename = '%s.pdf' % tunnistus.tunnistusenr

            # genereerime tunnistuse PDFi
            data_pdf = doc.generate()
            data_pdf = self._add_metadata(data_pdf, kasutaja, sooritajad)
            tunnistus.set_filedata(data_pdf, filename)
            tunnistus.mallinimi = t_name

            sbuf.s3file_put(DIGITEMPEL_PDF_DIR, filename, data_pdf)
            model.Session.commit()
            cnt += 1
            if protsess:
                if protsess.lopp:
                    buf = 'Väljastamine katkestatud. Väljastati %d tunnistust.' % cnt
                    raise Exception(buf)
                protsess.edenemisprotsent = cnt / total * 100
                model.Session.commit()

        # äratame digitempli
        res = DigitempelClient(self).start()
        buf = 'Väljastati %d tunnistust.' % cnt
        model.Arvutusprotsess.trace(f'{buf}\nDigitempel.start: {str(res)}')
        protsess.viga = buf[:256]
        model.Session.commit()

    def _valjasta_demo(self, tunnistuseliik, sessioon, t_name, item):
        doc = TunnistusDoc(tunnistuseliik, sessioon, t_name)
        sooritajad = list()        
        if tunnistuseliik == const.TESTILIIK_RIIGIEKSAM:
            kasutaja = item
            q_sooritajad = (model.Session.query(model.Sooritaja, model.Test)
                            .filter(model.Sooritaja.kasutaja_id==kasutaja.id)
                            .join(model.Sooritaja.testimiskord)
                            .filter(model.Testimiskord.testsessioon_id==sessioon.id)
                            .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
                            .filter(model.Sooritaja.staatus.in_((const.S_STAATUS_TEHTUD, 
                                                                 const.S_STAATUS_KATKESTATUD, 
                                                                 const.S_STAATUS_KATKESPROT, 
                                                                 const.S_STAATUS_EEMALDATUD)))
                            .join(model.Testimiskord.test)
                            .order_by(model.Test.nimi)
                            )
            doc.set_data('000-000000-0',
                         kasutaja.nimi,
                         datetime.now(),
                         sessioon.oppeaasta,
                         kasutaja,
                         q_sooritajad,
                         None
                         )
            for sooritaja, test in q_sooritajad.all():
                sooritajad.append(sooritaja)
        else:
            sooritaja = item
            kasutaja = sooritaja.kasutaja
            doc.set_data('000-000000-0',
                         kasutaja.nimi,
                         datetime.now(),
                         sessioon.oppeaasta,
                         kasutaja,
                         None,
                         sooritaja
                         )
            sooritajad.append(sooritaja)
            
        filedata = doc.generate()
        filedata = self._add_metadata(filedata, kasutaja, sooritajad)
        return utils.download(filedata, 'tunnistus.pdf', const.CONTENT_TYPE_PDF)

    def _add_metadata(self, pdfdata, kasutaja, sooritajad):
        ever, edata = model.Tunnistusekontroll.encode_metadata(kasutaja, sooritajad)
        merger = PdfWriter()
        input = BytesIO(pdfdata)
        merger.append(input)
        metadata = {'/ExamDataVer': ever,
                    '/ExamData': edata,
                    '/Title': 'Tunnistus',
                    '/Author': 'Haridus- ja Noorteamet',
                    '/Creator': 'EIS',
                    '/Producer': 'EIS',
                    #'/Subject': '',
                    }
        merger.add_metadata(metadata)
        output = BytesIO()
        merger.write(output)
        try:
            return output.getvalue()
        finally:
            output.close()
            input.close()

    def _search_protsessid(self, q):
        q = q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_VALJASTAMINE)
        if self.c.sessioon_id:
            q = q.filter(model.Arvutusprotsess.testsessioon_id==self.c.sessioon_id)
        return q

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    sbuf = S3FileBuf()
    filename = 'proov.pdf'
    data_pdf = b'PROOV'
    sbuf.s3file_put(DIGITEMPEL_PDF_DIR, filename, data_pdf)
    res = DigitempelClient(handler).start()
    print(res)
