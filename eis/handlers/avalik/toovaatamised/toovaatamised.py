from eis.lib.baseresource import *
_ = i18n._
from eis.lib.feedbackreport import FeedbackReport

log = logging.getLogger(__name__)

class ToovaatamisedController(BaseResourceController):

    _permission = 'toovaatamine'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'avalik/toovaatamised/otsing.mako'
    _LIST_TEMPLATE = 'avalik/toovaatamised/otsing_list.mako'
    _EDIT_TEMPLATE = 'avalik/toovaatamised/toovaatamine.mako'
    _DEFAULT_SORT = '-sooritaja.id'
    _actions = 'index,download,show'
    
    def _query(self):
        c = self.c
        today = date.today()
        q = (model.Session.query(model.Sooritaja,
                                 model.Kasutaja)
             .join((model.Toovaataja, model.Toovaataja.sooritaja_id==model.Sooritaja.id))
             .filter(model.Toovaataja.kasutaja_id==c.user.id)
             .filter(model.Toovaataja.kehtib_kuni>=today)
             .join(model.Sooritaja.kasutaja)
             )
        return q

    def _search(self, q):
        c = self.c
        if c.test_id:
            q = q.filter(model.Sooritaja.test_id==c.test_id)
        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))
        if c.isikukood:
            usp = validators.IsikukoodP(c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))

        c.prepare_item = self._prepare_item
        c.prepare_header = self._prepare_header
        return q

    def _search_default(self, q):
        return self._search(q)

    def _prepare_header(self):
        header = [('test.nimi', _("Test")),
                  ('test.id', _("ID")),
                  ('kasutaja.isikukood kasutaja.synnikpv', _("Isikukood")),
                  ('sooritaja.perenimi', _("Nimi")),
                  (None, _("Testi aeg")),
                  ('sooritaja.staatus', _("Olek")),
                  ('sooritaja.pallid', _("Tulemus")),
                  ]
        return header

    def _prepare_item(self, rcd, n=None):
        """Päringutulemuste paigutamine väljastamiseks sobivale kujule"""
    
        def millal(alates, kuni):
            buf = ''
            if alates:
                buf = alates.strftime('%d.%m.%Y')
                if kuni and kuni != alates:
                    buf += '–' + kuni.strftime('%d.%m.%Y')
            return buf

        sooritaja, kasutaja = rcd
        test = sooritaja.test
        if sooritaja.hindamine_staatus == const.H_STAATUS_HINNATUD \
               and sooritaja.staatus == const.S_STAATUS_TEHTUD:
            tulem = self.h.fstr(sooritaja.pallid)

        item = [test.nimi,
                sooritaja.test_id,
                kasutaja.isikukood or self.h.str_from_date(kasutaja.synnikpv),
                sooritaja.nimi,
                self.h.str_from_date(sooritaja.algus),
                sooritaja.staatus_nimi,
                tulem or '',
                ]
        return item

        
    def _show(self, item):
        c = self.c
        id = self.request.matchdict.get('id')
        test = item.test
        # if item.staatus == const.S_STAATUS_TEHTUD and \
        #        item.hindamine_staatus == const.H_STAATUS_HINNATUD and \
        #        test.testiliik_kood != const.TESTILIIK_KOOLIPSYH:

        #         fr = FeedbackReport.init_opilane(self, test, item.lang)
        #         if fr:
        #             err, c.tagasiside_html = fr.generate(item)
        
    def _download(self, id, format=None):
        """Näita faili"""
        item = self._MODEL.get(id)
        tk = item.testimiskord
        test = item.test
        # if item.staatus == const.S_STAATUS_TEHTUD and \
        #        item.hindamine_staatus == const.H_STAATUS_HINNATUD and \
        #        test.testiliik_kood != const.TESTILIIK_KOOLIPSYH:               
        #         # genereerida item jaoks
        #         fr = FeedbackReport.init_opilane(self, test, item.lang)
        #         if fr:
        #             filedata = fr.generate_pdf(item)                
        #             filename = 'tagasiside.pdf'
        #             if filedata:
        #                 return utils.download(filedata, filename, const.CONTENT_TYPE_PDF)
        raise NotFound('Faili ei leitud')

    def _perm_params(self):
        id = self.request.matchdict.get('id')
        if id:
            return {'sooritaja_id': id}

