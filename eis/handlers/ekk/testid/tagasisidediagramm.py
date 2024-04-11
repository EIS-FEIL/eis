from lxml import etree
import base64
import json
import html
from pyramid.response import FileResponse
from eis.lib.baseresource import *
from eis.lib.feedbackdgm import FeedbackDgmGtbl, FeedbackDgmKtbl
_ = i18n._

log = logging.getLogger(__name__)

class TagasisidediagrammController(BaseResourceController):
    """Tagasisidevormi diagrammi parameetrid
    """
    _permission = 'ekk-testid'
    _EDIT_TEMPLATE = 'ekk/testid/tagasiside.diagramm.mako'
    _actions = 'edit,create,show'
    _ITEM_FORM = forms.ekk.testid.TagasisideDiagrammForm

    def new(self):
        "Uue diagrammi loomine peale diagrammi liigi valikut"
        c = self.c
        c.dname = self.request.params.get('dname')

        # vaikimisi seaded uue diagrammi loomisel
        if c.dname == const.DGM_GTBL:
           c.avg_row = [const.FBR_SOORITAJA]
           
        return self._edit()
    
    def edit(self):
        "Diagrammi dialoogiakna avamine (pluginist)"
        c = self.c
        c.kursus = self.request.params.get('kursus')
        _data = self.request.params.get('data')
        if _data:
            # olemasolev diagramm kindla liigiga
            parse_diagram_params(c, _data)
            return self._edit()
        else:
            # uus diagramm, esmalt kuvame liigi valiku
            return self._choose_diagram_type()

    def _edit(self):
        self._get_opt()
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _get_tk_test(self, tk_tahis):
        "Leitakse diagrammile ette antud testimiskord"
        error = tk = None
        try:
            test_id, tahis = tk_tahis.split('-')
            test_id = int(test_id)
        except:
            error = _("Vigane testimiskorra tähis {s}").format(s=tk_tahis)
        else:
            tk = (model.Session.query(model.Testimiskord)
                .filter_by(tahis=tahis)
                .filter_by(test_id=test_id)
                .first())
            if not tk:
                error = _("Testimiskorda {s} ei leitud").format(s=tk_tahis)
        return tk, error

    def _get_opt(self):
        c = self.c
        # test, mille andmeid diagramm näitab, vaikimisi tagasisidevormi test
        test = c.test
        if c.tk_tahis:
            # teine test, mis on määratud testimiskorra tähisega
            tk, error = self._get_tk_test(c.tk_tahis)
            if tk:
                test = tk.test
                
        if c.dname == const.DGM_BARNP:
            if not c.colors:
                c.colors = ('#006400','#ffd700', '#ff0000')
            if not c.colornivs:
                c.colornivs = (70, 50)
        if c.dname == const.DGM_TUNNUSED2:
            c.opt_sugu = (('', _("Kokku")),
                          (const.SUGU_M, _("Poisid")),
                          (const.SUGU_N, _("Tüdrukud"))
                          )

        if c.dname in (const.DGM_TUNNUSED1, const.DGM_TUNNUSED2, const.DGM_TUNNUSED3):
            osa = test.testiosad[0]
            c.koik_nptunnused = [np.kood for np in osa.normipunktid if np.kood]
        if c.dname == const.DGM_HINNANG:
            q = (model.Session.query(model.Kysimus.kood).distinct()
                 .join(model.Kysimus.sisuplokk)
                 .join((model.Valitudylesanne,
                        model.Valitudylesanne.ylesanne_id==model.Sisuplokk.ylesanne_id))
                 .join(model.Valitudylesanne.testiylesanne)
                 .filter(model.Testiylesanne.liik==const.TY_LIIK_K)
                 .join(model.Testiylesanne.testiosa)
                 .filter(model.Testiosa.test_id==test.id)
                 .order_by(model.Kysimus.kood)
                 )
            c.koik_kysimused = [f'Q.{kood}' for kood, in q.all()]
        # tabel
        if c.dname == const.DGM_GTBL:
            c.opt_expr = FeedbackDgmGtbl.get_opt_expr(self, test, c.kursus)
            c.opt_displaytype = [(const.FBD_TULEMUS, _("Tulemus")),
                                 (const.FBD_PROTSENT, _("Protsendid")),
                                 (const.FBD_G_PROTSENT, _("Protsendid graafikul")),
                                 (const.FBD_TEKST, _("Tagasiside tekst")),
                                 (const.FBD_AJAKULU, _("Kasutatud aeg")),
                                 ]
            for r in test.testitasemed:
                c.opt_displaytype.append((const.FBD_TASE, _("Tase")))
                break
        if c.dname == const.DGM_KTBL:
            c.opt_expr = FeedbackDgmKtbl.get_opt_expr(self, test)
            
        if c.dname == const.DGM_KLASSYL:
            # millised ylesanded on diagrammil
            q = (model.Session.query(model.Testiosa.seq,
                                     model.Testiylesanne.tahis)
                 .join(model.Testiylesanne.testiosa)
                 .filter(model.Testiosa.test_id==test.id)
                 .filter(model.Testiylesanne.liik==const.TY_LIIK_Y)
                 .order_by(model.Testiosa.seq,
                           model.Testiylesanne.alatest_seq,
                           model.Testiylesanne.seq)
                 )
            c.opt_tykoodid = []
            tykoodid = list()
            for o_seq, ty_tahis in q.all():
                ty_kood = f'{o_seq}_{ty_tahis}'
                label = f'{o_seq}.{ty_tahis}'
                if ty_kood not in tykoodid:
                    c.opt_tykoodid.append((ty_kood, label))
                    tykoodid.append(ty_kood)

        # tky = c.test.opilase_taustakysitlus
        # if tky:
        #     opt_reltest = []
        #     # lisame põhikoolieksamite õppeained
        #     q = (model.Session.query(model.Test.aine_kood).distinct()
        #          .filter(model.Test.testiliik_kood==const.TESTILIIK_POHIKOOL))
        #     for aine, in q.all():
        #         key = f'PKTEST,{aine}'
        #         value = '%s - %s' % (_("Põhikooli lõpueksam"), model.Klrida.get_str('AINE', aine))
        #         opt_reltest.append((key, value))
        #     opt_reltest.sort(key=lambda r: r[1])
        #     opt_reltest.insert(0, ('', _("Taustaküsitlus")))
        #     c.opt_reltest = opt_reltest
                    
    def _choose_diagram_type(self):
        "Kasutajale kuvatakse diagrammi liikide valik"
        c = self.c
        # tagasisidevormi liik
        liik = self.request.params.get('liik')
        try:
            liik = int(liik)
        except:
            pass

        opts = c.opt.opt_feedbackdgm()
        if liik == model.Tagasisidevorm.LIIK_KIRJELDUS:
            # testi kirjeldus, ainult staatiline sisu
            buf = _("Testi kirjelduse osas ei saa diagramme kasutada!")
            return Response(buf)
        else:
            c.opt_dname = [(dname, title, subtitle) \
                           for (dname, title, subtitle) in opts \
                           if model.Tagasisidevorm.can_dgm(liik, dname)]

        template = 'ekk/testid/tagasiside.diagramm.liik.mako'
        return self.render_to_response(template)

    def _create(self):
        "Diagrammi dialoogiaknas salvestamine"
        # vormil olevad andmed pakitakse kokku
        # hiljem plugin lisab need tekstitoimetisse <img> atribuudina params
        c = self.c
        data = self.form.data
        c.dname = dname = data['dname']
        c.width = width = data['width']
        c.height = height = data['height']
        js = {'dname': dname,
              'width': width,
              'height': height,
              }
        # reltest = data.get('reltest')
        # if reltest:
        #     js['reltest'] = reltest
        tk_tahis = data.get('tk_tahis')
        if tk_tahis:
            js['tk_tahis'] = tk_tahis
            tk, error = self._get_tk_test(tk_tahis)
            if error:
                raise ValidationError(self, {}, error)
            
        # tavalise diagrammi värvid (mitte barnp)
        if not data.get('colors_def'):
            # kui pole märgitud, et soovitakse vaikimisi värve
            colors = [col for col in data['color'] if col]
            if colors:
                js['colors'] = colors

        if dname == const.DGM_HINNANG:
            ty_kood = data['ty_kood']
            if ty_kood:
                js['ty_kood'] = ty_kood
            reverse = data.get('reverse')
            if reverse:
                js['reverse'] = True
                
        if dname == const.DGM_BARNP:
            np_kood = data['np_kood']
            if np_kood:
                js['np_kood'] = np_kood

        if dname == const.DGM_TUNNUSED2:
            js['sex'] = data['sex'] or None

        if dname == const.DGM_TUNNUSED1 or dname == const.DGM_TUNNUSED2:
            if data['x_label']:
                js['x_label'] = data['x_label']
            if data['y_label']:
                js['y_label'] = data['y_label']
                
            npkoodid = [v for v in data['npkoodid'] if v]
            if npkoodid:
                js['npkoodid'] = npkoodid

            # tasemed kuni viimase sisestatud tasemeni
            li = []
            cnt = 0
            for ind, v in enumerate(data['tasemed']):
                li.append(v)
                if v:
                    cnt = ind + 1
            js['tasemed'] = li[:cnt]

        if dname == const.DGM_TUNNUSED3:
            np_kood = data['np_kood']
            if np_kood:
                js['np_kood'] = np_kood

            # tasemed kuni viimase sisestatud tasemeni
            li = []
            cnt = 0
            for ind, v in enumerate(data['tasemed']):
                li.append(v)
                if v:
                    cnt = ind + 1
            js['tasemed'] = li[:cnt]

        if dname == const.DGM_KLASSYL:
            if not data.get('tykoodid_all'):
                tykoodid = data['tykoodid']
                if tykoodid:
                    js['tykoodid'] = tykoodid

        if dname == const.DGM_BARNP:
            colornivs = [float(n.replace(',','.')) for n in data['colornivs'] if n]
            if colornivs:
                js['colornivs'] = colornivs

        if dname == const.DGM_GTBL:
            js['tcol'] = data['tcol']
            js['avg_row'] = data.get('avg_row') or []
            js['heading'] = data.get('heading')
            #js['cmp_valim'] = data.get('cmp_valim') and True or None
            
        if dname == const.DGM_KTBL:
            js['tcol2'] = data['tcol2']
            js['avg_row'] = data.get('avg_row') or []
            
        log.debug('create: %s' % js)
        buf = json.dumps(js).encode('utf-8')
        c.buf_params = base64.b64encode(buf).decode('ascii')
        log.debug('BUF=%s' % c.buf_params)

    def _error_create(self):
        self.c.dname = self.request.params.get('dname')
        self.c.tk_tahis = self.request.params.get('tk_tahis')
        self._get_opt()
        html = self.form.render(self._EDIT_TEMPLATE, extra_info=self.response_dict)
        return Response(html)

    def _after_create(self, id):
        return self.render_to_response(self._EDIT_TEMPLATE)
              
    def show(self):
        "Diagrammi kuvamine koostajale"
        tv_id = self.request.matchdict.get('tv_id')
        fn = self.request.matchdict.get('fn')
        
        IMAGES_DIR = os.path.join(
            os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.dirname(__file__)
                            )
                        )
                    ),
                'static'),
            'images_pdf')
        filename = 'feedbackdiagram.png'
        fn = f'{IMAGES_DIR}/{filename}'
        response = FileResponse(fn, request=self.request)
        response.cache_control = None
        response.last_modified = datetime.now()
        return response
            
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        c = self.c
        c.test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(c.test_id)
        c.testiosa_id = self.request.matchdict.get('testiosa_id')
        
    def _perm_params(self):
        return {'obj':self.c.test}

def parse_diagram_params(c, b64data):
    data = json.loads(base64.b64decode(b64data))
    c.dname = data.get('dname')
    #c.reltest = data.get('reltest')
    c.tk_tahis = data.get('tk_tahis')
    c.heading = data.get('heading')
    c.x_label = data.get('x_label')
    c.npkoodid = data.get('npkoodid')
    c.tykoodid = data.get('tykoodid')
    c.y_label = data.get('y_label')
    c.tase_max = data.get('tase_max')
    c.tasemed = data.get('tasemed')
    c.ty_kood = data.get('ty_kood')
    c.np_kood = data.get('np_kood')
    c.reverse = data.get('reverse')
    c.width = data.get('width')
    c.height = data.get('height')
    c.tcol = data.get('tcol') or []
    c.tcol2 = data.get('tcol2') or []
    c.avg_row = data.get('avg_row')
    #c.cmp_valim = data.get('cmp_valim')
    c.colors = data.get('colors')
    c.colornivs = data.get('colornivs')
    c.sex = data.get('sex')
    if c.dname == 'barnp' and not c.colornivs:
        try:
            # teisendame vanemast formaadist
            old_colors = c.colors
            c.colors = [r[0] for r in old_colors]
            c.colornivs = [r[1] for r in old_colors]
        except:
            pass
