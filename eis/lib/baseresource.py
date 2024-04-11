import sqlalchemy as sa
import mimetypes
import re
from paginate_sqlalchemy import SqlalchemyOrmPage
from eis.lib.base import *
_ = i18n._
log = logging.getLogger(__name__)

class BaseResourceController(BaseController):
    """Baaskontroller RESTful tüüpi ressursside jaoks
    """
    _MODEL = None # model.Item andmemudeli klass
    _INDEX_TEMPLATE = None # pealehe mall
    _LIST_TEMPLATE = None # otsingutulemuste loetelu mall, PARTIAL
    _SHOW_TEMPLATE = None # vaatamisvormi mall (kui puudub, siis kasutatakse muutmisvormi malli)
    _EDIT_TEMPLATE = '/avaleht.mako' # muutmisvormi mall
    _SEARCH_FORM = forms.NotYetImplementedForm # valideerimisvorm otsinguvormile
    _ITEM_FORM = forms.NotYetImplementedForm # valideerimisvorm muutmisvormile
    _PREFIX = 'f_' # HTML vormi väljade nimede prefiks, vastab tabelile
    _DEFAULT_SORT = 'id' # vaikimisi sortimine
    _UNIQUE_SORT = None
    _REDIRECT_AFTER_POST = True # kas peale POST salvestamist suunata GET URLile
    _no_paginate = False # kas kuvada loetelu kõik kirjed korraga
    _sort_options = None # list võimalikest sortimisväljadest
    _actions = 'index,create,new,download,show,update,delete,edit' # võimalikud tegevused
    ###############################################################################

    _default_items_per_page = 20
    
    @property
    def _items_per_page(self):
        if self.c.psize == const.ITEMS_ALL:
            return 1000000
        try:
            psize = int(self.c.psize)
            if 0 < psize <= 100:
                return psize
        except:
            pass
        return self._default_items_per_page

    @property
    def is_error_fullpage(self):
        "Kas ootamatu vea korral kuvada kogu kujundusega avaleht"
        if self.c.action in ('edittask', 'updatetask', 'correct', 'showtool'):
            return False
        else:
            return True
    
    # index - ressursside loetelu või otsing   
    def index(self):
        sub = self._get_sub()
        if sub:
            # kui on vaja mingit muud meetodit kasutada
            try:
                submethod = eval('self._index_%s' % sub)
            except AttributeError as ex:
                log.error(ex)
                raise NotFound()
            else:
                return submethod()        

        # tehakse töö
        d = self._index_d()
        if isinstance(d, dict):
            # kui ei tagastatud valmis vastust, siis vormistatakse vastus
            return self._showlist()
        else:
            # tagastatakse vastus
            return d

    def _index_progress(self):
        """Uuendatakse kuval arvutusprotsesside progressinäidikuid
        (kui kontroller sisaldab taustal arvutusprotsesside käivitamist)
        """
        res = []
        for p_id in self.request.params.getall('p_id'):
            rcd = model.Arvutusprotsess.get(p_id)
            if rcd:
                msg = self.h.html_nl(rcd.viga) or ''
                res.append([rcd.id, rcd.edenemisprotsent, bool(rcd.lopp), msg])

        data = {'protsessid':res}
        return Response(json_body=data)

    def _index_protsessid(self):
        "Protsesside loetelu pagineerimisel lk avamine"
        self._get_protsessid()
        template = '/common/arvutusprotsessid_list.mako'
        return self.render_to_response(template)

    def _get_protsessid(self):
        "Protsesside loetelu pagineerimisel lk avamine"
        q = self._query_protsessid()
        #model.log_query(q)
        self.c.arvutusprotsessid = self._paginate_protsessid(q)
        
    def _query_protsessid(self, pooleli=None):
        "Protsesside loetelu pagineerimisel protsesside päring"
        # kontroller peab ise kirjeldama _search_protsessid(self, q)
        q = self._search_protsessid(model.Arvutusprotsess.query)
        if pooleli:
            q = q.filter(model.Arvutusprotsess.lopp==None)
        return q.order_by(sa.desc(model.Arvutusprotsess.id))

    def _paginate_protsessid(self, q):
        "Protsesside loetelu pagineerimisel lk sisu listi loomine"
        page = self.c.page or self.request.params.get('page') or 1
        items_per_page = 10
        def _url(**kw):
            kw['sub'] = 'protsessid'
            return self.h.url_current_params(kw)
        return SqlalchemyOrmPage(q, page=page, items_per_page=items_per_page, url=_url)

    def _showlist(self):
        template = self.request.params.get('partial') and self._LIST_TEMPLATE or self._INDEX_TEMPLATE
        if not template:
            log.info('Mall puudub: %s.index' % self.c.controller)
            # eemaldame URLi lõpust yhe lyli ja suuname sinna
            location = self.request.path.rsplit('/', 1)[0]
            return HTTPFound(location=location)
        return self.render_to_response(template)
        
    def _index_d(self):
        """GET /admin_ITEMS: All items in the collection"""

        # päringu algus
        q = self._query()
        if not self.form:
            # pole veel valideeritud

            # on eraldi parameeter, mis ütleb, et ei ole parameetreid
            is_default = self.request.params.get('default')
            has_params = self._has_search_params()
            if not is_default:
                # kui pole parameetreid antud, siis vaatame, kas neid on varasemast meeles
                default_params = not has_params and self._get_default_params()
                if has_params or default_params:
                    # mingid parameetrid on olemas
                    q = self._index_handle_params(q, has_params, default_params)
                    has_params = True

            if is_default or not has_params:
                # kui parameetreid ei ole, siis koostatakse vaikimisi päring
                # kui ka vaikimisi päringu korral on mingid parameetrid, siis
                # tuleb siia jõudmiseks anda lisaks veel parameeter "default"

                # kui on kasutusel default, siis võivad mingid parameetrid olla, kopeerime need
                self._copy_search_params()
                # koostame vaikimisi päringu
                q = self._search_default(q)

        if q is not None:
            if isinstance(q, (HTTPFound, Response)):
                # q pole päring, vaid ümbersuunamine
                return q
            # järjestame loetelu
            q = self._order(q)
            # eraldame parajasti kuvatava lehekülje kõigi tulemuste seast
            self.c.items = self._paginate(q)

        # andmete kuvamine
        return self.response_dict

    def _params_into_c(self, upath=None, schema=None):
        """Kui parameetrid on antud, siis jäetakse need meelde.
        Kui parameetreid pole antud, siis kasutatakse meeldejäetud parameetreid.
        Leitud parameetrid kirjutatakse c sisse.
        """
        # kas on mõni parameeter?
        has_params = self._has_search_params()
        if not has_params:
            # kui pole parameetreid antud, siis vaatame, kas neid on varasemast meeles
            default_params = self._get_default_params(upath=upath)
            # taaskasutame varasemast meelde jäetud parameetreid
            self._copy_search_params(default_params, upath=upath)
        else:
            # mingid parameetrid on olemas
            data = None
            if schema:
                # on olemas valideerimisskeem
                form = Form(self.request, schema=schema, method='GET')
                if form.validate():
                    data = form.data
            # kopeerime parameetrid self.c sisse
            self._copy_search_params(data, save=True, upath=upath)

    def _index_handle_params(self, q, has_params, default_params):
        """Sisendparameetrite töötlemine
        has_params - kas on sisendparameetreid?
        default_params - kui pole, siis vaikimisi parameetrid eelmisest korrast
        """
        self.form = Form(self.request, schema=self._SEARCH_FORM, method='GET')
        if has_params and self.form.validate():
            # kopeerime parameetrid self.c sisse
            # kui parameetrid olid kasutaja poolt, siis jätame need meelde ka
            if not self.request.params.get('sort') and not default_params:
                # kui sortimise parameetrit praegu ei antud
                # ning ei toimu parameetrite taaskasutamist,
                # siis taaskasutame ainult sortimise parameetrit
                d_params = self._get_default_params()
                if d_params:
                    self.c.sort = d_params.get('sort')
            self._copy_search_params(self.form.data, save=True)
        if default_params:
            # taaskasutame varasemast meelde jäetud parameetreid
            self._copy_search_params(default_params)                            
        if not self.form.errors:
            # saame teha tavalise otsingu
            try:
                # koostame päringu vastavalt sisendparameetritele
                q = self._search(q)                
            except ValidationError as e:
                self.form.errors = e.errors

        if self.form.errors:                        
            # sisendparameetrid ei valideeru
            template = self.request.params.get('partial') and self._LIST_TEMPLATE or self._INDEX_TEMPLATE
            # vigade korral ei tohi kuvada _query() ilma otsingutingimusteta tulemusi
            #extra_info = self._index_d()
            # aga vbl tehakse _query() sees midagi muud vajalikku
            self._query()
            extra_info = self.response_dict
            if isinstance(extra_info, (HTTPFound, Response)):
                return extra_info    
            html = self.form.render(template, extra_info=extra_info)            
            return Response(html)
        else:
            return q

    def _sub_params_into_c(self, sub=None, form=None, reuse=None, method='GET'):
        """Otsinguparameetrite salvestamine ja lugemine sub korral
        Tagastab False, kui parameetrite valideerimine ei õnnestunud
        """
        # on eraldi parameeter, mis ütleb, et ei ole parameetreid
        upath = self._get_current_upath()
        if sub:
            upath += ':%s' % sub
        has_params = not reuse and self._has_search_params()
        if has_params:
            # valideerime uued parameetrid
            if not form:
                form = forms.NotYetImplementedForm
            self.form = Form(self.request, schema=form, method=method)
            if self.form.validate():
                params = self.form.data
                save = True
            else:
                return False
        else:
            # parameetrite taaskasutus
            params = self._get_default_params(upath)
            save = False

        # parameetrid c sisse, uued parameetrid jäetakse meelde
        self._copy_search_params(params, upath=upath, save=save)
        return True

    def _has_search_params(self):
        "Kas on otsinguparameetreid antud"
        for key in self.request.params:
            if key != 'rid' and key != 'sub':
                return True
        return False

    def _query(self):
        return self._MODEL.queryR

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if q and self.c.csv:
            return self._index_csv(q)
        if q and self.c.xls:
            return self._index_xls(q)        
        return q

    def _search_default(self, q):
        """Otsingu tingimuste seadmine siis, kui otsing toimub 
        kohe otsinguvormi avamisel ja kasutaja pole veel saanud 
        otsingutingimusi valida.
        Kui soovitakse, et sellist vaikimisi otsingut ei tehtaks,
        siis tuleb tagastada None.
        """
        return q

    def _index_csv(self, q, fn='andmed.csv'):
        "Loetelu väljastamine CSV-na"
        q = self._order(q)
        header, items = self._prepare_items(q)
        data = self._csv_data(header, items)
        data = utils.encode_ansi(data)
        return utils.download(data, fn, const.CONTENT_TYPE_CSV)

    def _index_xls(self, q, fn='andmed.xlsx'):
        "Loetelu väljastamine Excelis"
        q = self._order(q)
        header, items = self._prepare_items(q)
        return utils.download_xls(header, items, fn)

    def _csv_data(self, header, items):
        # eemaldame võimaliku sortimisaluse
        t_header = []
        for r in header:
            if isinstance(r, (list, tuple)):
                t_header.append(r[1])
            else:
                t_header.append(r)
        LINESEP = '\r\n'
        data = ';'.join(t_header) + LINESEP
        for item in items:
            row = []
            for s in item:
                if s is None:
                    s = ''
                elif isinstance(s, list):
                    s = ', '.join(s)
                else:
                    s = str(s).replace('\r', ' ')
                if ';' in s or '\n' in s:
                    s = '"%s"' % s.replace('"','""')
                row.append(s)
            data += ';'.join(row) + LINESEP
        return data

    def _prepare_items(self, q):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        header = self._prepare_header()
        items = [self._prepare_item(rcd, n) for n, rcd in enumerate(q.all())]
        return header, items

    def _prepare_header(self):
        "Loetelu päis"
        return []

    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        return []

    def _add_unique_sort(self, order_list):
        # lisame sorteerimistingimuste lõppu unikaalse ID,
        # sest muidu võib juhtuda, et sorditakse välja järgi, mis on paljudel sama
        # ja siis tulevad tulemused iga kord ise järjekorras
        field = self._UNIQUE_SORT
        if field is None:
            try:
                if self._MODEL.id:
                    field = self._MODEL.table.name + '.id'
            except:
                pass
        if field:
            order_list.append((False, field))
    
    def _order(self, q, sort=None):
        """Otsingu sorteerimine.
        """
        self.c.sort = sort or self.request.params.get('sort') or self.c.sort or self._DEFAULT_SORT
        # kui yks tulp sisaldab mitme välja järgi sortimist, siis on eraldaja tyhik ja mitte koma,
        # et oleks tabeli kuvamisel aru saada, millise tulba järgi on sorditud
        f_sort = ''
        for col in self.c.sort.split(','):
            if col:
                if col[0] == '-':
                    # kui tulbas sorditakse mitme välja järgi, siis
                    # tagurpidi sortimise märk on ainult esimese ees, paneme teistele ka
                    col = col.replace(' ',' -')
                f_sort += col.replace(' ',',') + ','

        order_list = []

        # leitakse sortimisväljad ja pannakse listi
        # vajadusel lisame päringusse uusi joine
        for field in f_sort.split(','):
            if field:
                if field[0] == '-':
                    is_desc = True
                    field = field[1:]
                else:
                    is_desc = False
                if re.search(r'[^a-z0-9\_\.]',
                            field.replace('_NUM','').replace('_LS','').replace('_KL','')):
                    # rynnak, ärme sordi yldse 
                    log.error(f'invalid sort: {field}')
                    return q
                li = field.split('.')
                if len(li) == 2:
                    tablename, fieldname = li
                    # kontrollime, et tabel oleks päringus kasutusel
                    q = self._order_join_field(q, tablename, fieldname)

                order_list.append((is_desc, field))
       
        self._add_unique_sort(order_list)
        # tegelik sortimine
        for is_desc, field in order_list:
            q = self._order_field(q, is_desc, field)
        return q

    def _order_field(self, q, is_desc, field):
        "Välja järgi sortimine"
        fieldname = field
        if field.endswith('_NUM'):
            # sortimine numbrilise alguse järgi
            fieldname = field[:-4]
            field = "substring(%s, '^[0-9]+')::int,%s" % (fieldname, fieldname)
        elif field.endswith('_LS'):
            # sortimine keelte sortimise funktsiooniga järjekorras et,ru,en,de,fr
            fieldname = field[:-3]
            field = "lang_sort(%s)" % fieldname
        elif field.endswith('_KL'):
            # sortimine klassifikaatori nimetuse järgi
            # varem on _order_join_field() sees joinitud klassifikaatori kirje
            klrida_alias = field.split('.')[1].lower() # aine_kl
            field = klrida_alias + '.nimi'
        if self._order_able(q, fieldname):
            if is_desc:
                # DESC sort
                q = q.order_by(sa.desc(sa.text(field)))
            else:
                # ASC sort
                q = q.order_by(sa.text(field))
        return q
    
    def _order_join_field(self, q, tablename, fieldname):
        """Otsingupäringu sortimisel lisatakse päringule join 
        tabeliga, mille välja järgi tuleb sortida
        """
        if fieldname.endswith('_KL'):
            # nt aine_KL - et sortida Klrida.nimi järgi, joinida Klrida.kood==TABEL.aine_kood
            join_field = None
            if tablename == 'test' and fieldname == 'aine_KL':
                join_field = model.Test.aine_kood
            if not join_field:
                log.error(f'invalid join: {tablename}.{fieldname}')
            else:
                klrida_alias = fieldname.lower() # aine_kl
                KL = sa.orm.aliased(model.Klrida, name=klrida_alias)
                kl_type = fieldname[:-3].upper()
                q = q.outerjoin(KL, sa.and_(KL.klassifikaator_kood==kl_type,
                                            KL.kood==join_field))
        return self._order_join(q, tablename)

    def _order_join(self, q, tablename):
        """Otsingupäringu sortimisel lisatakse päringule join 
        tabeliga, mille välja järgi tuleb sortida (üle kirjutamiseks)
        """
        return q

    def _order_able(self, q, field):
        """Kontrollitakse, kas antud välja järgi on võimalik sortida
        """
        # kui võimalikud variandid on teada, siis peab olema yks neist
        if self._sort_options:
            return field in self._sort_options
        if field.find('lahliik') > -1:
            # ajutiselt, peale välja eemaldamist
            return False
        try:
            # kui field on: lang_sort(sooritaja.lang)
            m = re.match(r'.+\((.*)\)', field)
            if m:
                field = m.groups()[0]
        except:
            pass

        if '.' not in field:
            # välja nimi ei sisalda tabelit
            return True
        try:
            tbl_name, fld_name = field.split('.')
        except ValueError:
            # mitu punkti
            #log.info(u'ei sordi 1:%s' % field)
            return False

        q_str = str(q.with_labels().statement.compile(dialect=q.session.bind.dialect))
        # see kontroll pole päris täpne
        # kui tabeli nimi esineb päringus, siis loeme, et saab sortida
        if ' %s ' % tbl_name in q_str + ' ':
            # tabeli nimi esineb päringus
            return True
        elif '.%s ' % tbl_name in q_str + ' ':
            # kui tabeli ees on skeem ja punkt
            return True
        else:
            log.info('ei sordi 2:%s' % field)            
            return False

    def _paginate(self, q):
        if self._no_paginate:
            return q.all()
        page = self.c.page or self.request.params.get('page') or 1
        items_per_page = self._items_per_page
        return SqlalchemyOrmPage(q, 
                                 page=page,
                                 items_per_page=items_per_page,
                                 url=self.h.url_current_params)

    ########################################################################################
    # show - ressursi kuvamine vaatamisresiimis
    
    def show(self):
        sub = self._get_sub()
        if sub:
            id = self.request.matchdict.get('id')
            return eval('self._show_%s' % sub)(id)        

        d = self._show_d()
        if isinstance(d, dict):
            template = self._SHOW_TEMPLATE or self._EDIT_TEMPLATE
            if not template:
                log.info('Mall puudub: %s.show' % self.c.controller)
                return self._redirect('index')
            t = self.prf()
            res = self.render_to_response(template)
            model.Session.rollback()
            self.prf('MAKO', t)
            return res
        else:
            return d


    def show_redirect(self):
        """Juhul, kui URLis on id järel kaldkriips (või pole)
        ja seda ei ole vaja (või peab olema),
        siis suunatakse õigele show URLile.
        """
        return self._redirect('show')

    def _show_d(self):
        id = self.request.matchdict.get('id')
        self.c.item = self._MODEL.get(id)
        if not self.c.item:
            raise NotFound('Kirjet %s ei leitud' % id)        
        self._show(self.c.item)
        return self.response_dict

    def _show(self, item):
        self._edit(item)

    def download(self):
        id = self.request.matchdict.get('id')
        format = self.request.matchdict.get('format')
        sub = self.request.params.get('sub')
        return self._download(id, format)

    def _download(self, id, format=None):
        """Näita faili"""
        try:
            item = self._MODEL.get(id)
        except:
            item = None
        filedata = item and item.filedata
        if not filedata:
            raise NotFound('Kirjet %s ei leitud' % id)        

        mimetype = item.mimetype
        if not mimetype:
            (mimetype, encoding) = mimetypes.guess_type(item.filename)

        filename = item.filename
        model.Session.rollback()
        return utils.download(filedata, filename, mimetype)

    def downloadfile(self):
        "Alamfaili allalaadimine, millel on oma file_id"
        id = self.request.matchdict.get('id')
        file_id = self.request.matchdict.get('file_id')
        format = self.request.matchdict.get('format')
        return self._downloadfile(id, file_id, format)

    def _downloadfile(self, id, file_id, format):
        """Näita alamfaili"""
        pass

    ########################################################################################
    # edit - ressursi kuvamine muutmisresiimis
    
    def edit(self):
        sub = self._get_sub()
        if sub:
            id = self.request.matchdict.get('id')
            return eval('self._edit_%s' % sub)(id)
        d = self._edit_d()
        if isinstance(d, dict):
            if not self._EDIT_TEMPLATE:
                log.info('Mall puudub: %s.edit' % self.c.controller)
                return self._redirect('index')
            res = self.render_to_response(self._EDIT_TEMPLATE)
            model.Session.rollback()
            return res
        else:
            return d

    def _edit_d(self):
        id = self.request.matchdict.get('id')
        id = self.convert_id(id)
        self.c.item = self._MODEL.get(id)
        if not self.c.item:
            raise NotFound('Kirjet %s ei leitud' % id)        
        rc = self._edit(self.c.item)
        if isinstance(rc, (HTTPFound, Response)):
            return rc        
        return self.response_dict

    def _edit(self, item):
        pass


    ########################################################################################
    # new - uue ressursi lisamise vormi kuvamine

    def new(self):
        sub = self._get_sub()
        if sub:
            return eval('self._new_%s' % sub)()

        d = self._new_d()
        if isinstance(d, dict):
            if not self._EDIT_TEMPLATE:
                log.info('Mall puudub: %s.edit' % self.c.controller)
                return self._redirect('index')

            res = self.render_to_response(self._EDIT_TEMPLATE)
            model.Session.rollback()
            self.prf()
            return res
        else:
            return d

    def _new_d(self):
        """GET /admin_ITEMS/new: Form to create a new item"""
        # uue objekti väljad
        item_args = self.request.params.mixed()
        item_args.update(self._get_parents_from_routes())
        self.c.item = self._MODEL.init(**item_args)

        # lülitame autoflushi välja, et ID ei genereeritaks
        model.Session.autoflush = False
        # mudeli võimalik täiendav algväärtustamine
        self.c.item.post_create()
        self._new(self.c.item)
        self._edit(self.c.item)
        return self.response_dict
    
    def _new(self, item):
        pass


    ########################################################################################
    # create - uue ressursi salvestamine
    
    def create(self):
        """POST /admin_ITEMS: Create a new item"""
        sub = self._get_sub()
        if sub:
            return eval('self._create_%s' % sub)()

        err = False
        self.form = Form(self.request, schema=self._ITEM_FORM)
        if self.form.validate():
            try:
                item = self._create()
                if isinstance(item, (HTTPFound, Response)):
                    return item
            except ValidationError as e:
                self.form.errors = e.errors
                err = True
        if self.form.errors or err:
            # vead võivad olla tulnud vormi valideerimisest 
            # või olla käsitsi pandud _create() sees
            log.debug(self.form.errors)
            model.Session.rollback()
            return self._error_create()

        model.Session.commit()
        self._after_commit(item)
        return self._after_create(item and item.id or None)

    def _error_create(self):
        extra_info = self._new_d()
        if isinstance(extra_info, (HTTPFound, Response)):
            return extra_info
        html = self.form.render(self._EDIT_TEMPLATE, extra_info=extra_info)
        return Response(html)

    def _create(self, **kw):
        args = self._get_parents_from_routes()
        args.update(kw)
        item = self._MODEL.init(**args)
        self._update(item)
        return item

    def _after_commit(self, item):
        """Juhuks, kui peale commitit, kui on selgunud ID,
        on vaja selle ID-ga midagi teha ja siis uuesti commitida.
        """
        pass

    def _after_create(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        return self._after_update(id)


    ########################################################################################
    # update - ressursi muutmine
    
    def update(self):
        """PUT /admin_ITEMS/id: Update an existing item"""
        sub = self._get_sub()
        if sub:
            id = self.request.matchdict.get('id')
            return eval('self._update_%s' % sub)(id)

        id = self.request.matchdict.get('id')
        item = self._MODEL.get(id)

        err = False
        self.form = Form(self.request, schema=self._ITEM_FORM)
        if self.form.validate():
            try:
                if item:
                    rc = self._update(item)
                    if isinstance(rc, (HTTPFound, Response)):
                        return rc
            except ValidationError as e:
                self.form.errors = e.errors
                err = True

        if self.form.errors or err:
            model.Session.rollback()
            return self._error_update()

        model.Session.commit()
        self._after_commit(item)
        return self._after_update(id)

    def _error_update(self):
        extra_info = self._edit_d()
        if isinstance(extra_info, (HTTPFound, Response)):
            return extra_info    
        html = self.form.render(self._EDIT_TEMPLATE, extra_info=extra_info)            
        return Response(html)
    
    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        self.prf()
        if not self.has_errors() and not self.has_success():
            self.success()
        if self._index_after_create:
            return self._redirect('index')
        else:
            return self._redirect('edit', id)

    def _update(self, item, lang=None):
        # omistame viited vanemobjektile
        self._bind_parent(item)
        # omistame vormilt saadud andmed
        item.from_form(self.form.data, self._PREFIX, lang=lang)

    ########################################################################################
    # delete - ressursi kustutamine
    
    def delete(self):
        """DELETE /admin_ITEMS/id: Delete an existing item"""
        sub = self._get_sub()
        if sub:
            id = self.request.matchdict.get('id')
            return eval('self._delete_%s' % sub)(id)

        id = self.request.matchdict.get('id')
        item = self._MODEL.get(id)
        if not item:
            parent_id = None
        else:
            parent_id = item.parent_id
            rc = self._delete_except(item)
            if isinstance(rc, (HTTPFound, Response)):
                return rc

        return self._after_delete(parent_id)

    def _delete_except(self, item):
        try:
            return self._delete(item)
        except sa.exc.IntegrityError as e:
            msg = _("Ei saa enam kustutada, sest on seotud andmeid")
            #msg = self._error(e, msg)
            try:
                log.info('%s [%s] %s' % (msg, self.request.url, repr(e)))
                log.info(e.statement)
                log.info(e.params)
            except:
                #if self.is_devel: raise
                pass
            self.error(msg)
            model.Session.rollback()

    def _delete(self, item):
        item.delete()
        model.Session.commit()
        self.success(_("Andmed on kustutatud"))
        
    def _after_delete(self, parent_id=None):
        self.prf()
        return self._redirect('index')

    ########################################################################################
    # abifunktsioonid

    def _get_sub(self):
        if self.request.content_type == 'application/json':
            try:
                sub = self.request.json_body.get('sub')
            except Exception as ex:
                # axios: simplejson.errors.JSONDecodeError
                sub = None
        else:
            sub = self.request.params.get('sub')
        if sub and not self.c.nosub:
            if re.search(r'[^a-zA-Z0-9_]', sub):
                raise Exception('Vigane sub')
            return sub

    def _get_parents_from_routes(self):
        # leiame parent_id
        args = {}
        #for key, value in self.request.environ['pylons.routes_dict'].iteritems():
        for key, value in self.request.matchdict.items():        
            if key.endswith('_id'):
                args[key] = value

        return args

    def _bind_parent(self, item):
        "Omistame viite vanemobjektile, kui see on olemas"
        # vanemobjekti id on eeldatavalt ruutingu urlis
        for key, value in list(self.request.matchdict.items()):
            if key != 'id':
                if key.endswith('_id'):
                    item.__setattr__(key, int(value))
                else:
                    item.__setattr__(key, value.encode('utf-8'))

