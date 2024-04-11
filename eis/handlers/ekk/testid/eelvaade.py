from simplejson import dumps
import pickle
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from eis.lib.feedbackreport import FeedbackReport
from eis.handlers.avalik.sooritamine import sooritus
from eis.lib.helpers import fstr
from eis.lib.examclient import ExamClient
from eis.lib.testsaga import TestSaga
log = logging.getLogger(__name__)

class EelvaadeController(sooritus.SooritusController):
    """Testi sooritamise eelvaade testi koostajale
    """
    _permission = 'ekk-testid'
    _actions = 'index,new,create,show,update,edit,download,delete' # võimalikud tegevused
    _actionstask = 'edittask,showtask,updatetask,correct,showtool'
    _EDIT_TEMPLATE = 'ekk/testid/eelvaade.mako'
    _on_eelvaade = True
    
    def new(self):
        """Testi sooritamise vormi kuvamine
        """
        c = self.c
        linear = self.request.params.get('linear')
        if linear == '1':
            # d-testi lineaarne eelvaade
            c.e_komplekt_id = 'L'
            c.is_linear = True
        elif linear == '0':
            c.e_komplekt_id = ''
            c.is_linear = False
        return self.create()

    def create(self):
        c = self.c
        # kustutame varasemad eelvaated
        self.prf()
        self._remove_eelvaated()
        self.prf()

        test = model.Test.get(c.test_id)
        self.prf()
        if not c.testiosa_id:
            # avalikus vaates mõnes kohas pole testiosa_id urlis
            c.testiosa_id = test.testiosad[0].id
        c.lang = lang = self.params_lang() or test.lang
        kursus = self.request.params.get('kursus') or None
        added, sooritaja = \
            model.Sooritaja.registreeri(c.user.get_kasutaja(),
                                      test.id,
                                      None,
                                      lang,
                                      None,
                                      const.REGVIIS_EELVAADE,
                                      c.user.id,
                                      c.user.koht_id or None,
                                      alustamata=True,
                                      mittekorduv=False)
        self.prf()
        sooritaja.kursus_kood = kursus
        sooritus = sooritaja.get_sooritus(c.testiosa_id)
        self.prf()
        model.Session.commit()
        self.prf()
        
        return HTTPFound(location=self._url_edit(sooritus.id))

    def _check_test_staatus(self):
        return True

    def _check_vastvorm(self, item, sooritaja):
        return True, None

    def _check_reg(self, item, ta, testiruum):
        return True, None, False
    
    def _show(self, item):
        c = self.c
        if c.action == 'show':
            c.read_only = True
        # leitakse c.sooritus ja c.sooritaja
        super()._show(item)
        # eelvaates peale sooritamist tagasiside kuvamine
        if c.action == 'show':
            #c.sooritus = model.Sooritus.get(c.sooritus_id)
            #sooritaja = model.Sooritaja.get(c.sooritaja_id)
            if c.sooritaja:
                # tagasiside vajab päris testi kirjet
                test = model.Test.get(c.test_id)
                fr = FeedbackReport.init_opilane(self, test, c.sooritaja.lang, c.sooritaja.kursus_kood)
                if fr:
                    err, c.tagasiside_html = fr.generate(c.sooritaja)
                    if err:
                        log.info(err)
        return self.response_dict

    def _download(self, id, format=None):
        """Eelvaates tagasiside allalaadimine"""
        f_id = self.request.matchdict.get('id')
        c = self.c
        sooritaja = model.Sooritaja.get(c.sooritaja_id)
        test = c.test or sooritaja.test
        fr = FeedbackReport.init_opilane(self, test, sooritaja.lang, sooritaja.kursus_kood)
        if fr:
            if format == 'pdf':
                filedata = fr.generate_pdf(sooritaja)
                if filedata:
                    return utils.download(filedata, 'tagasiside.pdf', const.CONTENT_TYPE_PDF)
            elif format == 'xls':
                filedata = fr.generate_xls(sooritaja)
                return utils.download_xls_file(filedata, 'tagasiside.xlsx')

        self.error(_("Faili ei leitud"))
        return self._redirect('show', id=f_id)

    def _remove_eelvaated(self):
        "Kustutatakse see ja teised sama kasutaja eelvaated"
        test_id = self.c.test_id
        kasutaja_id = self.c.user.id
        
        found = False
        # leiame eelvaated
        self.prf()
        q = (model.Session.query(model.Sooritaja)
             .filter(model.Sooritaja.test_id==test_id)
             .filter(model.Sooritaja.kasutaja_id==kasutaja_id)
             .filter(model.Sooritaja.regviis_kood==const.REGVIIS_EELVAADE))
        for old in q.all():
            # kustutame eelvaate
            self.prf()
            ExamSaga(self).delete_sooritaja(old)
            found = True
        self.prf()
        if found:
            model.Session.flush()
        return found

    def _delete_except(self, item):
        if self._remove_eelvaated():
            model.Session.commit()

    def _after_delete(self, parent_id=None):
        return HTTPFound(location=self._url_out())
            
    def _url_quit(self, sooritus_id):
        "URL, mida kasutatakse kasutaja testi sooritamiselt välja viimisel"
        c = self.c
        if not sooritus_id:
            # updatetask korral, kui kasutaja on välja logitud
            return self._url_out()
        tos = model.Sooritus.get(sooritus_id)
        if not tos or tos.staatus != const.S_STAATUS_TEHTUD:
            # kui test katkestati, siis ei ole midagi vaadata
            return self._url_out()
        return self.url_current('show', id=sooritus_id, rid=True, alatest_id='')

    def _url_edit(self, id):
        "URL, mis peale eelvaate loomist avab selle"
        c = self.c
        return self.url_current('edit', alatest_id='', id=id, e_komplekt_id=c.e_komplekt_id)
    
    def _url_out(self):
        "URL, mida kasutatakse eelvaatest väljumisel"
        c = self.c
        test = model.Test.get(c.test_id)
        if test.diagnoosiv:
            return self.url('test_struktuur', test_id=c.test_id)
        else:
            return self.url('test_valitudylesanded',
                            test_id=c.test_id, testiosa_id=c.testiosa_id,
                            komplekt_id=c.e_komplekt_id)

    def _has_permission(self):
        c = self.c
        action = c.action
        #if action in ('create', 'alusta', 'jatka', 'edit', 'new', 'index', 'show'):
        log.debug(f'ACTION={action}')
        if action in ('create', 'edit', 'new', 'index'):
            return BaseResourceController._has_permission(self)
        else:
            return self._is_allowed_tos(c.sooritus_id)

    
    def _get_perm_bit(self):
        return const.BT_SHOW
    
    def _perm_params(self):
        return {'obj':self.c.test}

    def __before__(self):
        c = self.c
        c.preview = True
        super().__before__()
        c.test = model.Test.get(c.test_id)
        c.e_komplekt_id = self.request.matchdict.get('e_komplekt_id')
        if c.e_komplekt_id == 'L':
            c.is_linear = True
        else:
            c.is_linear = False
            try:
                c.e_komplekt_id = int(c.e_komplekt_id)
            except:
                c.e_komplekt_id = ''
