from eis.lib.baseresource import *
from eis.lib.feedbackreport import FeedbackReport
import eis.lib.sebconfig as sebconfig
_ = i18n._
log = logging.getLogger(__name__)

class AlustamineController(BaseController):

    _permission = 'sooritamine,testpw'
    _get_is_readonly = False
    
    def index(self):
        c = self.c
        test_id = self.request.matchdict.get('test_id')
        try:
            c.test = model.Test.getR(test_id)
        except:
            pass
        if not c.test:
            self.error(_("Testi ei leitud"))
            return HTTPFound(location=self.h.url('sooritamised'))
        elif c.test.staatus != const.T_STAATUS_KINNITATUD:
            self.error(_("Test ei ole veel sooritamiseks valmis!"))
            return HTTPFound(location=self.h.url('sooritamised'))

        sooritaja_id = self.convert_id(self.request.matchdict.get('sooritaja_id'))
        if sooritaja_id:
            # seatakse c.sooritaja
            res = self._check_sooritaja(sooritaja_id, c.test.id)
            if res:
                # suunatakse mujale, sest sooritaja kirje ei sobinud
                return res
        else:
            # kui sooritaja ID pole URLis, siis vaatame, kas sooritaja kirje on olemas
            is_permitted, c.sooritaja, error = TestSaga(self).get_sooritaja_for(c.test, c.user.id)
            if not is_permitted:
                if error:
                    self.error(error)
                return HTTPFound(location=self.h.url('sooritamised'))                
                
        c.now = datetime.now()
        if c.test.on_jagatudtoo and c.nimekiri:
            sooritus = c.sooritaja.sooritused[0]
            url = self.h.url('sooritamine_tooylesanded', test_id=c.test.id, sooritus_id=sooritus.id)
            return HTTPFound(location=url)
        else:
            if c.sooritaja and c.sooritaja.staatus == const.S_STAATUS_TEHTUD and \
                   c.sooritaja.hindamine_staatus == const.H_STAATUS_HINNATUD and \
                   c.test.testiliik_kood != const.TESTILIIK_KOOLIPSYH:
                if not c.testimiskord or c.testimiskord.koondtulemus_avaldet or \
                       c.test.testiliik_kood == const.TESTILIIK_DIAG2:
                    # test on lõpetatud, aga osalemist ei kuvata, tagasiside kuvatakse siinsamas
                    fr = FeedbackReport.init_opilane(self, c.test, c.sooritaja.lang, c.sooritaja.kursus_kood)
                    if fr:
                        err, c.tagasiside_html = fr.generate(c.sooritaja)

            if c.user.get_seb_id():
                c.hide_header_footer = True
            template = 'avalik/sooritamine/alustamine.mako' 
        return self.render_to_response(template)

    def _check_sooritaja(self, sooritaja_id, test_id):
        "Kontrollitakse, kas sooritaja kirje sobib"
        c = self.c
        try:
            c.sooritaja = model.Sooritaja.get(sooritaja_id)
        except:
            pass
        if not c.sooritaja or c.sooritaja.regviis_kood == const.REGVIIS_EELVAADE:
            self.error(_("Registreering puudub"))
            return HTTPFound(location=self.url('sooritamised'))
        else:
            if c.sooritaja.kasutaja_id == c.user.id:
                olen_tugi = False
            elif self._olen_tugiisik(c.sooritaja):
                olen_tugi = True
            else:
                # ei ole sooritaja ega tugiisik
                self.error(_("Registreering puudub"))
                return HTTPFound(location=self.url('sooritamised'))

            if c.sooritaja.test_id != test_id:
                # vigane URL, kus sooritaja_id ja test_id ei sobi omavahel
                return HTTPFound(location=self.url('sooritamised'))
            
            c.testimiskord = c.sooritaja.testimiskord
            # kas võin soorituse kirjet näha?
            osalemine = c.sooritaja.osalemine_nahtav(olen_tugi, c.test, c.testimiskord)
            if not osalemine and not olen_tugi:
                # kui ei või näha, siis võib näha tugiisikuta lahendatavaid testiosi enne sooritamist
                ise_teen = [tos for tos in c.sooritaja.sooritused \
                            if not tos.tugiisik_kasutaja_id]
                if not ise_teen:
                    self.error(_("Test on suunatud sooritamiseks tugiisikuga"))
                    return HTTPFound(location=self.h.url('sooritamised'))

            if c.user.testpw_id and c.user.testpw_id != c.sooritaja.id:
                # testiparooli korral kontrollime, et on õige sooritus
                sooritaja = model.Sooritaja.get(c.user.testpw_id)
                self.error(_("Testiparooliga ei saa teisi teste sooritada"))
                url = self.url('sooritamine_alustamine', test_id=sooritaja.test_id, sooritaja_id=sooritaja.id)
                return HTTPFound(location=url)
                    
            c.nimekiri = c.sooritaja.nimekiri
            if c.nimekiri:
                if c.nimekiri.kuni and c.nimekiri.kuni < date.today():
                    self.error(_("Lahendamise ajavahemik on juba läbi"))
                    return HTTPFound(location=self.h.url('sooritamised'))
                if c.nimekiri.alates and c.nimekiri.alates > date.today():
                    self.error(_("Lahendamise ajavahemik pole veel alanud"))
                    return HTTPFound(location=self.h.url('sooritamised'))

            if c.sooritaja.staatus == const.S_STAATUS_TEHTUD and \
              c.sooritaja.hindamine_staatus == const.H_STAATUS_HINNATUD and \
              c.test.testiliik_kood != const.TESTILIIK_KOOLIPSYH and \
              osalemine and not c.test.on_jagatudtoo:
                if not c.testimiskord or c.testimiskord.koondtulemus_avaldet:
                    # kui test on lõpetatud, siis suuname tulemuste lehele
                    return HTTPFound(location=self.h.url('tulemus', id=c.sooritaja.id))
                eeltest = c.test.eeltest
                if eeltest and eeltest.tagasiside_sooritajale:
                    return HTTPFound(location=self.h.url('tulemus', id=c.sooritaja.id))
    
    def _olen_tugiisik(self, sooritaja):
        "Kas olen selle sooritaja tugiisik mõnes testiosas"
        q = (model.SessionR.query(model.Sooritus.id)
             .filter_by(sooritaja_id=sooritaja.id)
             .filter_by(tugiisik_kasutaja_id=self.c.user.id)
             )
        return q.count() > 0

    def download(self):
        """Näita faili"""
        id = self.request.matchdict.get('sooritaja_id')
        format = self.request.matchdict.get('format')
        item = model.Sooritaja.getR(id)
        tk = item.testimiskord
        if item.staatus == const.S_STAATUS_TEHTUD and \
               item.hindamine_staatus == const.H_STAATUS_HINNATUD:
            if not tk or tk.koondtulemus_avaldet or \
                   tk.on_eeltest and test.testiliik_kood == const.TESTILIIK_DIAG2:
                # genereerida item jaoks
                fr = FeedbackReport.init_opilane(self, item.test, item.lang, item.kursus_kood)
                if fr:
                    filedata = fr.generate_pdf(item)                
                    filename = 'tagasiside.pdf'
                    if filedata:
                        return utils.download(filedata, filename, const.CONTENT_TYPE_PDF)            
        raise NotFound('Faili ei leitud')
    
