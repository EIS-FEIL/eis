from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.mootmisvead import MootmisveadDoc

log = logging.getLogger(__name__)

class MootmisveadController(BaseResourceController):

    _permission = 'hindamisanalyys'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'ekk/hindamine/analyys.mootmisvead.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/analyys.mootmisvead_list.mako'
    _DEFAULT_SORT = 'sooritaja.id' # vaikimisi sortimine 
    _SEARCH_FORM = forms.ekk.hindamine.MootmisveadForm
    
    _ignore_default_params = ['pdf']
    
    def _query(self):

        join_tables = []
        headers = []
        select_fields = [model.Sooritaja.id]

        n_sooritus = 0
        n_alatest = 0
        staatus_jrk = {}
        for testiosa in self.c.toimumisaeg.testimiskord.test.testiosad:
            n_sooritus += 1
            name = 'sooritus_%d' % n_sooritus
            Sooritus = sa.orm.aliased(model.Sooritus, name=name)
            join_tables.append((Sooritus,
                                sa.and_(Sooritus.testiosa_id==testiosa.id,
                                        Sooritus.sooritaja_id==model.Sooritaja.id)))
            select_fields.append(Sooritus.tahised)
            select_fields.append(Sooritus.staatus)
            testiosa_staatus_jrk = len(select_fields)

            headers.append(('%s.tahised' % name, _("Soorituse kood") + ' (%s)' % testiosa.nimi))            
            if testiosa.on_alatestid:
                for alatest in testiosa.alatestid:
                    n_alatest += 1
                    name = 'alatest_%d' % n_alatest
                    Alatestisooritus = sa.orm.aliased(model.Alatestisooritus, name=name)
                    join_tables.append((Alatestisooritus,
                                        sa.and_(Alatestisooritus.alatest_id==alatest.id,
                                                Alatestisooritus.sooritus_id==Sooritus.id)))
                    headers.append(('%s.pallid' % name, '%s' % alatest.nimi))                    
                    select_fields.append(Alatestisooritus.staatus)

                    # alatesti staatuse välja jrk nr-ile vastab alatesti väljade arv 2
                    staatus_jrk[len(select_fields)] = 2
                    select_fields.append(Alatestisooritus.pallid)
                    select_fields.append(Alatestisooritus.tulemus_protsent)
            else:
                headers.append(('%s.pallid' % name, '%s' % testiosa.nimi))
                select_fields.append(Sooritus.pallid)
                select_fields.append(Sooritus.tulemus_protsent)

            # staatuse välja jrk nr-ile vastab selle staatusega testiosa väljade arv
            staatus_jrk[testiosa_staatus_jrk] = len(select_fields) - testiosa_staatus_jrk
            
        if n_sooritus <= 1 and n_alatest <= 1:
            # test koosneb yhestainsast testiosast/alatestist
            # jätame alles ainult soorituse koodi
            select_fields = select_fields[:3]
            headers = headers[:1]
        
        headers.append(('sooritaja.pallid', _("Testi tulemus")))
        select_fields += [model.Sooritaja.pallid,
                          model.Sooritaja.tulemus_protsent]

        self.c.staatus_jrk = staatus_jrk
        self.c.headers = headers
        q = (model.Session.query(*select_fields)
             .filter(model.Sooritaja.testimiskord_id==self.c.toimumisaeg.testimiskord_id)
             .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             )

        for join in join_tables:
            q = q.join(join)

        return q

    def _search_default(self, q):
        #self.c.mootmisviga = self.c.toimumisaeg.testiosa.test.tulemuste_mootmisviga_pr
        return self._search(q)

    def _search(self, q):
        if self.c.mootmisviga is None or self.c.mootmisviga == '':
            self.c.mootmisviga = 2
        test = self.c.toimumisaeg.testimiskord.test
        algus = test.lavi_pr - self.c.mootmisviga - (0.5 + 1e-12)
        lopp = test.lavi_pr + self.c.mootmisviga + (0.5 - 1e-12)

        q = q.filter(model.Sooritaja.tulemus_protsent>algus).\
            filter(model.Sooritaja.tulemus_protsent<lopp)

        if self.c.pdf:
            return self._index_pdf(q)
        return q
    
    def _index_pdf(self, q):
        q = self._order(q)
        doc = MootmisveadDoc(self.c.headers, q.all(),
                             self.c.toimumisaeg.testimiskord, self.c.staatus_jrk)
        data = doc.generate()
        filename = 'mootmisvead.pdf'
        mimetype = const.CONTENT_TYPE_PDF
        return utils.download(data, filename, mimetype)

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.test = self.c.toimumisaeg.testiosa.test
        
    def _perm_params(self):
        return {'obj': self.c.test}
        
