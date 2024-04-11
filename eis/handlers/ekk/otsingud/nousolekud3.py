from itertools import groupby

from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class Nousolekud3Controller(BaseResourceController):
    """III hindamise nõusolekud
    """
    _permission = 'aruanded-nousolekud3'
    _INDEX_TEMPLATE = 'ekk/otsingud/nousolekud3.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/nousolekud3_list.mako'
    _DEFAULT_SORT = 'kasutaja.perenimi,kasutaja.eesnimi'
    _ignore_default_params = ['csv', 'format']
    _SEARCH_FORM = forms.ekk.otsingud.Nousolekud3Form # valideerimisvorm otsinguvormile   
    
    def _query(self):
        # leiame (piirkondlikule) kasutajale lubatud piirkondade loetelu
        kasutaja = self.c.user.get_kasutaja()
        testiliik = self.request.params.get('testiliik')
        lubatud = kasutaja.get_piirkonnad_id(self._permission, const.BT_SHOW, testiliik=testiliik)
        if None not in lubatud:
            self.c.piirkond_filtered = lubatud
        else:
            self.c.piirkond_filtered = None
        
        return model.Session.query(model.Kasutaja.id)

    def _search_default(self, q):
        return None

    def _search(self, q1):
        c = self.c
        self.header, fields = self._header()
        q = model.Session.query(*fields).distinct()
        q = self._filter_q(q)
        return q

    def _header(self):
        c = self.c
        li = [model.Kasutaja.id,
              model.Kasutaja.eesnimi,
              model.Kasutaja.perenimi,
              model.Kasutaja.isikukood,
              model.Leping.nimetus,
              model.Klrida.nimi,
              model.Kasutaja.epost,
              model.Kasutaja.telefon,
              model.Aadress.tais_aadress,
              ]
        header = [('kasutaja.eesnimi', _("Eesnimi")),
                  ('kasutaja.perenimi', _("Perekonnanimi")),
                  ('kasutaja.isikukood', _("Isikukood")),
                  ('leping.nimetus', _("Leping")),
                  ('klrida.nimi', _("Hindaja õppeaines")),
                  ('kasutaja.epost', _("E-posti aadress")),
                  ('kasutaja.telefon', _("Telefon")),
                  ('aadress.tais_aadress', _("Postiaadress")),
                  ]
                  
        return header, li
                
    def _filter_q(self, q):
        c = self.c

        grupid_id = (const.GRUPP_HINDAJA_S, const.GRUPP_HINDAJA_S2, const.GRUPP_HINDAJA_K)
        nousolek_field = model.Nousolek.on_hindaja

        # millistes piirkondades otsime
        piirkonnad_id = None
        if c.piirkond_id:
            piirkond = model.Piirkond.get(c.piirkond_id)
            piirkonnad_id = piirkond.get_alamad_id()

        # kas pole õigust kõigi piirkondade korraldamiseks?
        if c.piirkond_filtered:
            # piirkondlik korraldaja ei või kõiki kohti vaadata
            if piirkonnad_id:
                # jätame otsingust välja piirkonnad, kus pole lubatud
                piirkonnad_id = set(piirkonnad_id).intersection(c.piirkond_filtered)
            else:
                # otsime ainult lubatud piirkondades
                piirkonnad_id = c.piirkond_filtered
        
        if piirkonnad_id is not None:
            # otsime piirkonna järgi, kus isik on nõus läbi viima
            q = q.filter(model.Kasutaja.kasutajapiirkonnad.any(
                model.Kasutajapiirkond.piirkond_id.in_(piirkonnad_id)))
                    
        q = (q.outerjoin(model.Kasutaja.aadress)
             .outerjoin(model.Kasutaja.profiil)
             )
        
        q = (q.join(model.Kasutaja.labiviijalepingud)
             .join(model.Labiviijaleping.leping))
        q = q.filter(model.Labiviijaleping.on_hindaja3==True)

        grupid = (const.GRUPP_HINDAJA_K, const.GRUPP_HINDAJA_S, const.GRUPP_HINDAJA_S2)
        q = q.outerjoin((model.Aineprofiil,
                         sa.and_(model.Aineprofiil.kasutaja_id==model.Kasutaja.id,
                                 model.Aineprofiil.kasutajagrupp_id.in_(grupid),
                                 sa.exists().where(
                                     sa.and_(model.Lepinguroll.leping_id==model.Leping.id,
                                             model.Aineprofiil.aine_kood==model.Lepinguroll.aine_kood,
                                             model.Lepinguroll.kasutajagrupp_id.in_(grupid)))
                                 )
                         ))
        q = q.outerjoin((model.Klrida, sa.and_(model.Klrida.klassifikaator_kood=='AINE',
                                               model.Klrida.kood==model.Aineprofiil.aine_kood)))
        if c.sessioon_id:
            q = q.filter(model.Labiviijaleping.testsessioon_id==c.sessioon_id)
        if c.leping_id:
            q = q.filter(model.Labiviijaleping.leping_id==c.leping_id)
        if c.aine:
            q = q.filter(model.Aineprofiil.aine_kood==c.aine)
        return q

    def _prepare_items(self, c_items=None):
        """Päringutulemuste paigutamine väljastamiseks sobivale kujule"""

        header = [r[:2] for r in self.header]
        items = []

        for rcd in c_items or self.c.items:
            item = []
            for n, r_header in enumerate(self.header):
                value = rcd[n+1]
                if len(r_header) > 2:
                    value = r_header[2](value)
                item.append(str(value or ''))
            items.append(item)

        return header, items

    def _paginate(self, q):
        # et failina laadimisel ei pagineeriks
        format = self.request.params.get('format')
        if format:
            return q.all()
        else:
            return BaseResourceController._paginate(self, q)

    def _showlist(self):
        """Otsingu tulemuste kuvamine.
        """
        format = self.request.params.get('format')       
        if format == 'csv':
            data, filename = self._render_csv()
            mimetype = const.CONTENT_TYPE_CSV
            return utils.download(data, filename, mimetype)            

        self.c.prepare_items = self._prepare_items
        if self.request.params.get('partial'):
            return self.render_to_response(self._LIST_TEMPLATE)
        else:
            return self.render_to_response(self._INDEX_TEMPLATE)

    def _render_csv(self):
        header, items = self._prepare_items()
        data = ';'.join([r[1] for r in header]) + '\n'
        for item in items:
            item = [s and str(s) or '' for s in item]
            data += ';'.join(item) + '\n'

        data = utils.encode_ansi(data)
        filename = 'nousolekud.csv'
        return data, filename

