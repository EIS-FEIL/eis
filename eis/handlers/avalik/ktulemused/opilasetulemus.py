from eis.lib.baseresource import *
_ = i18n._
from eis.lib.feedbackreport import FeedbackReport

log = logging.getLogger(__name__)

class OpilasetulemusController(BaseResourceController):

    _permission = 'avalikadmin,testiadmin'
    _MODEL = model.Sooritaja
    _EDIT_TEMPLATE = 'avalik/ktulemused/opilasetulemus.mako'
    # automaatse tagasisidevormi genereerimisel võib olla vaja see salvestada
    _kohteelvaade_readonly = False

    def _show(self, item):
        c = self.c
        tk = item.testimiskord
        if tk:
            self._has_valim()
            test = item.test
            lang = item.lang
            fr = self._get_fr(test, lang, item.kursus_kood)
            if fr:
                err, c.tagasiside_html = fr.generate(item)                
            
    def _get_fr(self, test, lang, kursus):
        fr = FeedbackReport.init_opilane(self, test, lang, kursus, opetajale=True)
        return fr

    def _has_valim(self):
        "Kas testimiskorral on valim? (Vajalik valimi tabi kuvamiseks.)"
        c = self.c
        sis_valim_tk_id, valimid_tk_id, v_avaldet = \
            eis.lib.feedbackreport.FeedbackReport.leia_valimi_testimiskord(c.test.id, c.testimiskord.id)
        c.on_valim = (sis_valim_tk_id or valimid_tk_id) and True or False
    
    def _download(self, id, format=None):
        """Näita faili"""
        item = self.c.sooritaja
        fr = self._get_fr(item.test, item.lang, item.kursus_kood)
        if fr:
            # genereerida item jaoks
            filedata = fr.generate_pdf(item)                
            filename = 'tagasiside.pdf'
            if filedata:
                return utils.download(filedata, filename, const.CONTENT_TYPE_PDF)            
        raise NotFound('Faili ei leitud')

    def _has_permission(self):
        c = self.c
        if c.test.testiliik_kood == const.TESTILIIK_SISSE:            
            q = (model.Session.query(sa.func.count(model.Kandideerimiskoht.id))
                 .filter_by(sooritaja_id=c.sooritaja.id)
                 .filter_by(koht_id=c.user.koht_id))
            if q.scalar() == 0:
                return False
        elif c.sooritaja.kool_koht_id != c.user.koht_id:
            return False
        return model.Sooritaja.has_permission_ts(c.sooritaja.id, c.testimiskord)
   
    def __before__(self):
        c = self.c
        matchdict = self.request.matchdict
        c.test = model.Test.get(matchdict.get('test_id'))
        c.testimiskord = model.Testimiskord.get(matchdict.get('testimiskord_id'))
        sooritaja_id = matchdict.get('id')
        c.kursus = matchdict.get('kursus') or ''
        c.sooritaja = model.Sooritaja.get(matchdict.get('id'))
        c.ylesanded_avaldet = c.testimiskord.ylesanded_avaldet and not c.test.salastatud
        c.FeedbackReport = FeedbackReport
