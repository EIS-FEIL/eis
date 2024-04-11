from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

from eis.lib.pdf import pages_loader
from eis.lib.pdf.materjal import MaterjalDoc

class MaterjalidController(BaseResourceController):
    _permission = 'avalikadmin'
    _INDEX_TEMPLATE = '/avalik/korraldamine/materjalid.mako'
    _EDIT_TEMPLATE = '/avalik/korraldamine/materjalid.mako'

    def _query(self):
        self.c.pdf_templates = pages_loader.get_templates_opt_dict()

    def create(self):
        """Loo väljatrükk
        """
        c = self.c
        self._validate_pdf()
        if c.toimumisaeg.on_paketid:
            # p-testi korral peab EKK olema eelnevalt kogused arvutanud ja hindamiskirjed loonud
            if not c.toimumisaeg.on_hindamisprotokollid or len(c.testikoht.testipaketid) == 0:
                self.error(_("Väljatrükke ei saa teha, sest eksamikeskuses on testipaketid veel koostamata"))
                return self._redirect('index')

        doc = MaterjalDoc(c.toimumisaeg, 
                          self.form.data,
                          ['testipakett.lang'])
        doc.testikoht_id = c.testikoht.id
        return self._gen_pdf(doc, 'materjalid.pdf')

    def _validate_pdf(self):
        self.form = Form(self.request, schema=forms.ekk.korraldamine.ValjastusPDFForm)
        self.form.validate()
        self._copy_search_params(self.form.data, save=True)

    def _gen_pdf(self, doc, fn):
        """Väljatrükid
        """
        data = doc.generate()
        if doc.error:
            self.error(doc.error)
            self.c.nosub = True
            return self.index()
        else:
            return utils.download(data, fn, 'application/pdf')

    def __before__(self):
        self.c.testikoht = model.Testikoht.get(self.request.matchdict.get('testikoht_id'))
        self.c.toimumisaeg = self.c.testikoht.toimumisaeg

    def _perm_params(self):
        if self.c.testikoht.koht_id != self.c.user.koht_id:
            return False
