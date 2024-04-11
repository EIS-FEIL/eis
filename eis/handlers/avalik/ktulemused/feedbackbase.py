from eis.lib.feedbackreport import FeedbackReport
from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class FeedbackBaseController:
    "Tagasiside genereerimine"
    _permission = 'avalikadmin,testiadmin,aineopetaja'
    _actions = 'index'
    _tvliik = None
    
    def _query(self):
        pass
    
    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q):
        c = self.c
        if not c.partial:
            self._get_opt()

        klassidID = [model.KlassID.from_id(r) for r in c.klassid_id]
        res = self._get_tagasiside(0, klassidID, c.op_id, c.kursus)
        if c.pdf or c.xls:
            return res
        else:
            c.tagasiside_html = res

    def _get_opt(self):
        "Valikväljade valikute koostamine"
        c = self.c
        c.klassidID = self._get_klassid()
        if not c.klassidID:
            self.notice(_("Testitööd pole hinnatud"))
        c.opt_opetajad = self._get_opetajad()
        
    def _get_klassid(self):
        "Klasside valik"
        c = self.c
        q = (model.SessionR.query(model.Sooritaja.klass, model.Sooritaja.paralleel)
             .distinct()
             .filter(model.Sooritaja.testimiskord_id==c.testimiskord.id)
             .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
             )
        if c.kursus:
            q = q.filter(model.Sooritaja.kursus_kood==c.kursus)
        if c.test.testiliik_kood == const.TESTILIIK_SISSE:
            q = q.filter(model.Sooritaja.kandideerimiskohad.any(
                model.Kandideerimiskoht.koht_id==c.user.koht_id))

        # oma kooli õpilaste klassid
        q1 = q.filter(model.Sooritaja.kool_koht_id==c.user.koht_id)
        q1 = q1.order_by(model.Sooritaja.klass, model.Sooritaja.paralleel)
        li = []
        for klass, paralleel in q1.all():
            li.append(model.KlassID(klass, paralleel))

        if c.test.testiliik_kood == const.TESTILIIK_SISSE:
            # eristame minu kooli kandideerivad (sõltumata koolist ja klassist)
            q2 = q.filter(model.Sooritaja.kandideerimiskohad.any(
                sa.and_(model.Kandideerimiskoht.koht_id==c.user.koht_id,
                        model.Kandideerimiskoht.automaatne==False)))
            cnt = q2.count()
            if cnt:
                li.append(model.KlassID(model.KlassID.KANDIDAADID, None))

        return li       

    def _get_opetajad(self):
        "Aineõpetajate valik"
        c = self.c
        if c.test.testiliik_kood == const.TESTILIIK_SISSE:
            return []
        q = (model.SessionR.query(model.Testiopetaja.opetaja_kasutaja_id,
                                 model.Kasutaja.nimi)
             .distinct()
             .join(model.Testiopetaja.sooritaja)
             .join(model.Testiopetaja.opetaja_kasutaja)
             .filter(model.Sooritaja.testimiskord_id==c.testimiskord.id)
             .filter(model.Sooritaja.kool_koht_id==c.user.koht_id)
             .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)             
             )
        if c.kursus:
            q = q.filter(model.Sooritaja.kursus_kood==c.kursus)
        q = q.order_by(model.Kasutaja.nimi)
        li = [(op_id, op_nimi) for (op_id, op_nimi) in q.all()]
        return li       

    def _get_lang(self, tkorrad_id, kool_id):
        c = self.c
        lang = c.flang
        ql = (model.SessionR.query(model.Sooritaja.lang).distinct()
              .filter(model.Sooritaja.testimiskord_id.in_(tkorrad_id))
              )
        if kool_id:
            ql = ql.filter(model.Sooritaja.kool_koht_id==kool_id)
        c.nk_keeled = c.opt.sorted_lang([lang for lang, in ql.all()])
        if not lang:
            lang = c.nk_keeled and c.nk_keeled[0] or c.test.lang

        ql = (model.SessionR.query(model.Tagasisidevorm.lang).distinct()
              .filter(model.Tagasisidevorm.ylem_id==None)
              .filter(model.Tagasisidevorm.test_id==c.test.id)
              .filter(model.Tagasisidevorm.liik==self._tvliik)
              .filter(model.Tagasisidevorm.staatus==const.B_STAATUS_KEHTIV))
        v_keeled = [lang for lang, in ql.all()]
        if len(v_keeled) == 1:
            # kui vorm on ainult yhes keeles, siis pole vaja keelte valikut
            c.nk_keeled = []
        return lang

    def _get_tagasiside(self, kool_id, klassidID, opetajad_id, kursus, valimis=None):
        "Tagasiside genereerimine"
        c = self.c
        # kogu Eesti tagasiside jaoks anda kool_id=None
        if kool_id == 0:
            kool_id = c.user.koht_id
        tkorrad_id = [c.testimiskord.id]

        # kas on olemas valim?
        self._has_valim()
        
        # kui mall on olemas, siis luuakse tagasiside objekt
        lang = self._get_lang(tkorrad_id, kool_id)
        fr = self._get_fr(c.test, lang, kursus)
        if fr:
            args = dict(testimiskorrad_id=tkorrad_id,
                        klassidID=klassidID,
                        opetajad_id=opetajad_id,
                        kursus=kursus,
                        valimis=valimis)
            if c.test.testiliik_kood == const.TESTILIIK_SISSE:
                args['kand_koht_id'] = kool_id
            else:
                args['kool_koht_id'] = kool_id

            c.tvorm = fr.tvorm
            if c.pdf:
                filedata = fr.generate_pdf(None, **args)
                filename = 'tagasiside.pdf'
                return utils.download(filedata, filename, const.CONTENT_TYPE_PDF)
            elif c.xls:
                filedata = fr.generate_xls(None, **args)
                filename = 'tagasiside.xlsx'
                return utils.download(filedata, filename, const.CONTENT_TYPE_XLS)

            else:
                err, html = fr.generate(None, **args)
                c.can_xls = fr.can_xls
                return html

    def _get_fr(self, test, lang, kursus):
        "Tagasisidevormi objekti loomine vastavalt tagasiside liigile"
        fr = FeedbackReport.init_osalejatetulemused(self, test, lang, kursus)
        return fr

    def _has_valim(self):
        "Kas testimiskorral on valim? (Vajalik valimi tabi kuvamiseks.)"
        c = self.c
        sis_valim_tk_id, valimid_tk_id, v_avaldet = \
            FeedbackReport.leia_valimi_testimiskord(c.test.id, c.testimiskord.id)
        c.on_valim = (sis_valim_tk_id or valimid_tk_id) and True or False

    def _index_fbdqry(self):
        "Tagasisidediagrammi uuendamine eraldi muust tagasisidevormist"
        c = self.c
        params = self.request.params
        klassidID = [model.KlassID.from_id(r) for r in params.getall('klassid_id')]
        op_id = params.getall('op_id')
        fbd_id = params.get('fbd_id')
        tkorrad_id = [c.testimiskord.id]
        kool_id = c.user.koht_id
        lang = self._get_lang(tkorrad_id, kool_id)
            
        # tagasisidevormi leidmine
        fr = self._get_fr(c.test, lang, c.kursus)
        
        # tabeli sisu genereerimine
        args = dict(testimiskorrad_id=tkorrad_id,
                    klassidID=klassidID,
                    opetajad_id=op_id,
                    kursus=c.kursus)
        if c.test.testiliik_kood == const.TESTILIIK_SISSE:
            args['kand_koht_id'] = kool_id
        else:
            args['kool_koht_id'] = kool_id
        
        err, html = fr.generate_dgm(fbd_id, params, **args)
        if err:
            log.error(err)
        return Response(html or '')
                   
    def __before__(self):
        c = self.c
        test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(test_id)
        testimiskord_id = self.request.matchdict.get('testimiskord_id')
        c.testimiskord = model.Testimiskord.get(testimiskord_id)
        c.kursus = self.request.matchdict.get('kursus') or ''
        c.FeedbackReport = FeedbackReport
        
    def _perm_params(self):
        c = self.c
        if not c.user.koht_id:
            return False
        if not c.testimiskord.koondtulemus_avaldet:
            return False
        return {'test': c.test}
