# -*- coding: utf-8 -*- 

import os.path
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class ToofailidController(BaseResourceController):

    _permission = 'failid'

    _MODEL = model.Toofail
    _INDEX_TEMPLATE = 'avalik/admin/toofailid.mako'
    _LIST_TEMPLATE = 'avalik/admin/toofailid_list.mako'
    _DEFAULT_SORT = '-toofail.id' # vaikimisi sortimine
    _SEARCH_FORM = forms.avalik.admin.ToofailidForm 

    def _query(self):
        koht_id = self.c.user.koht_id
        # leiame tööfailid, mille testi siin koolis sooritatakse
        # ja mille õppetase ja kavatase vastab selle kooli tasemetele
        q = (model.Toofail.query
             .filter(model.Toofail.avalik_alates < datetime.now())
             .filter(sa.and_(sa.or_(model.Toofail.test_id==None,
                                    sa.exists().where(
                                        sa.and_(model.Toofail.test_id==model.Sooritaja.test_id,
                                                model.Sooritaja.id==model.Sooritus.sooritaja_id,
                                                model.Sooritus.testikoht_id==model.Testikoht.id,
                                                model.Testikoht.koht_id==koht_id))),
                             sa.or_(model.Toofail.oppetase_kood==None,
                                    sa.exists().where(
                                        sa.and_(model.Toofail.oppetase_kood==model.Koolioppekava.oppetase_kood,
                                                model.Koolioppekava.koht_id==koht_id,
                                                model.Toofailitase.kavatase_kood==model.Koolioppekava.kavatase_kood,
                                                model.Toofailitase.toofail_id==model.Toofail.id)))
                             )
                     )
             )
        return q

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.filename:
            q = q.filter(model.Toofail.filename.ilike('%'+self.c.filename+'%'))
        if self.c.kirjeldus:
            q = q.filter(model.Toofail.kirjeldus.ilike('%'+self.c.kirjeldus+'%'))
        return q

    def _download(self, id, format=None):
        """Näita faili"""
        q = self._query() # kontrollime, et on õigus
        try:
            item = q.filter(model.Toofail.id==id).first()
            model.log_query(q)
        except:
            item = None
        filedata = item and item.filedata
        if not filedata:
            raise NotFound(_('Faili ei leitud või pole sellele ligipääsu'))        

        mimetype = item.mimetype
        if not mimetype:
            (mimetype, encoding) = mimetypes.guess_type(item.filename)
            
        return utils.download(filedata, item.filename, mimetype)

    def _perm_params(self):
        if not self.c.user.koht_id:
            return False
