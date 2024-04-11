from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.vaatlejateade import VaatlejateadeDoc
from .labiviijateated import send_epost_labiviija
log = logging.getLogger(__name__)

class VaatlejateatedController(BaseResourceController):
    """Vaatlejate teadete otsimine
    """
    _permission = 'aruanded-vaatlejateated'
    _MODEL = model.Kasutaja
    _INDEX_TEMPLATE = 'ekk/otsingud/vaatlejateated.mako'
    _SEARCH_FORM = forms.ekk.otsingud.VaatlejateatedForm
    _DEFAULT_SORT = 'kasutaja.perenimi,kasutaja.eesnimi,kasutaja.id' # vaikimisi sortimine
    _get_is_readonly = False
    _ignore_default_params = ['csv','xls','op']
    
    def _query(self):
        q = model.Kasutaja.query
        return q

    def _get_opt(self):
        self.c.opt_sessioon = self.c.opt.testsessioon
        if not self.c.sessioon_id and len(self.c.opt_sessioon):
            self.c.sessioon_id = self.c.opt_sessioon[0][0]
        if self.c.sessioon_id:
            self.c.opt_toimumisaeg = model.Toimumisaeg.get_opt(self.c.sessioon_id)

        k = self.c.user.get_kasutaja()
        piirkonnad_id = k.get_piirkonnad_id('kasutajad', const.BT_INDEX)
        if None not in piirkonnad_id:
            # kasutajal on antud õigus ainult teatud piirkonnis
            self.c.piirkond_filtered = piirkonnad_id
            # ja ta tohib saata ainult meeldetuletusi
            self.c.ltyyp = model.Kiri.TYYP_LABIVIIJA_MEELDE

    def _search_default(self, q):
        self._get_opt()
        return None

    def _search(self, q):
        self._get_opt()
        q = self._search_query(q)
        if self.c.sessioon_id:
            self.c.arv = q.count()
            self._get_protsessid()

        create_params = self._get_default_params(upath='vaatlejateated-create')
        if create_params:
            self.c.taiendavinfo = create_params.get('taiendavinfo')

    def create(self):
        "Kirjade saatmine"
        self.form = Form(self.request, schema=self._SEARCH_FORM)
        if self.form.validate():
            self._copy_search_params(self.form.data, save=True, upath='vaatlejateated-create')            
            taiendavinfo = self.request.params.get('taiendavinfo')
            self._get_opt()
            q = self._query()
            q = self._search_query(q)
            if q and self.c.sessioon_id:
                op = self.request.params.get('op')
                if op == 'epost':
                    cnt = q.count()
                    if self.c.toimumisaeg_id:
                        ta = model.Toimumisaeg.get(self.c.toimumisaeg_id)
                        tahised = ta.tahised
                    elif self.c.testimiskord_id:
                        tk = model.Testimiskord.get(self.c.testimiskord_id)
                        tahised = tk.tahised
                    elif self.c.test_id:
                        tahised = self.c.test_id
                    else:
                        tahised = ''
                    desc = 'Vaatlejate teadete saatmine %s (%d kirja)' % (tahised, cnt)
                    params = {'liik': model.Arvutusprotsess.LIIK_M_VAATLEJA,
                              'kirjeldus': desc,
                              'test_id': self.c.test_id or None,
                              'testimiskord_id': self.c.testimiskord_id or None,
                              'toimumisaeg_id': self.c.toimumisaeg_id or None,
                              'testsessioon_id': self.c.sessioon_id or None,
                              }
                    childfunc = lambda protsess: self._send_eposts(protsess, q, taiendavinfo)
                    model.Arvutusprotsess.start(self, params, childfunc)
                    self.success('Saatmise protsess käivitatud')

                elif op == 'tpost':
                    q = self._order(q)
                    return self._send_tpost(q, taiendavinfo)
        return self._redirect('index', getargs=True)
        
    def _filter_labiviija(self):
        f = []
        f.append(model.Labiviija.kasutajagrupp_id==const.GRUPP_VAATLEJA)
        if self.c.toimumisaeg_id:
            f.append(model.Labiviija.toimumisaeg_id==int(self.c.toimumisaeg_id))
        elif self.c.sessioon_id:
            f.append(model.Labiviija.toimumisaeg.has(\
                    model.Toimumisaeg.testimiskord.has(\
                        model.Testimiskord.testsessioon_id==int(self.c.sessioon_id))))

        if self.c.piirkond_id:
            piirkond = model.Piirkond.get(self.c.piirkond_id)
            piirkonnad_id = piirkond.get_alamad_id()
            f.append(model.Labiviija.testikoht.has(\
                model.Testikoht.koht.has(\
                    model.Koht.piirkond_id.in_(piirkonnad_id))))
        elif self.c.piirkond_filtered:
            # piirkondlik korraldaja saab ainult oma piirkondades tegutseda
            f.append(model.Labiviija.testikoht.has(\
                model.Testikoht.koht.has(\
                    model.Koht.piirkond_id.in_(self.c.piirkond_filtered))))
            
        if not self.c.kordus:
            # otsime ainult need, kellele ei ole veel kirja saadetud
            if self.c.ltyyp == model.Kiri.TYYP_LABIVIIJA_MEELDE:
                f.append(model.Labiviija.meeldetuletusaeg==None)
            elif self.c.ltyyp == model.Kiri.TYYP_LABIVIIJA_TEADE:
                f.append(model.Labiviija.teateaeg==None)
            
        return sa.and_(*f)

    def _search_query(self, q):
        f = self._filter_labiviija()
        q = q.filter(model.Kasutaja.labiviijad.any(f))

        if self.c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))                                        
        if self.c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(self.c.eesnimi))
        if self.c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(self.c.perenimi))

        f = []
        if self.c.koolitusaeg_alates:
            f.append(model.Profiil.v_koolitusaeg>=self.c.koolitusaeg_alates)
        if self.c.koolitusaeg_kuni:
            f.append(model.Profiil.v_koolitusaeg<self.c.koolitusaeg_kuni + timedelta(1))
        if len(f):
            q = q.filter(model.Kasutaja.profiil.has(sa.and_(*f)))
        return q

    def _get_labiviijad(self,kasutaja):
        f = self._filter_labiviija()
        q = model.Labiviija.query.\
            filter(model.Labiviija.kasutaja_id==kasutaja.id).\
            filter(f).\
            outerjoin(model.Labiviija.testiruum).\
            order_by(model.Testiruum.algus)
        return q.all()

    def _search_protsessid(self, q):
        sessioon_id = self.c.sessioon_id or self.request.params.get('sessioon_id')
        q = (q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_M_VAATLEJA)
             .filter(model.Arvutusprotsess.testsessioon_id==sessioon_id)
             )
        return q

    def _send_eposts(self, protsess, q, taiendavinfo):
        sessioon = model.Testsessioon.get(self.request.params.get('sessioon_id'))
        testiliik = sessioon.testiliik_kood
        total = q.count()

        def itemfunc(k):
            if not k.epost:
                return False, k.nimi
            else:
                labiviijad = list(self._get_labiviijad(k))
                if send_epost_labiviija(self, self.c.ltyyp, k, const.GRUPP_VAATLEJA, labiviijad, testiliik, taiendavinfo):
                    return True, None
                else:
                    return False, '%s (%s)' % (k.nimi, k.epost)

        model.Arvutusprotsess.iter_mail(protsess, self, total, q.all(), itemfunc)
        
    def _send_tpost(self, q, taiendavinfo=None):
        doc = VaatlejateadeDoc(self, self.c.ltyyp)
        data = doc.generate(items=q.all(),
                            get_labiviijad=self._get_labiviijad,
                            taiendavinfo=taiendavinfo)

        # salvestame teate aja läbiviija kirjes
        model.Session.commit()
        if self.c.ltyyp == model.Kiri.TYYP_LABIVIIJA_MEELDE:
            filename = 'vaatlejameeldetuletus.pdf'
        else:
            filename = 'vaatlejateade.pdf'
        mimetype = const.CONTENT_TYPE_PDF
        return utils.download(data, filename, mimetype)
