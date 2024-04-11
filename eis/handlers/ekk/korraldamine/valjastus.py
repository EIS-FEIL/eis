import math
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
from eis.lib.pdf import pages_loader
from eis.lib.pdf.valjastusymbrik import ValjastusymbrikDoc
from eis.lib.pdf.tagastusymbrik import TagastusymbrikDoc, PdfGenException
from eis.lib.pdf.materjal import MaterjalDoc
from eis.lib.pdf.turvakotikleebis import TurvakotikleebisDoc
from eis.lib.pdf.turvakotiakt import TurvakotiaktDoc

log = logging.getLogger(__name__)
_UPATH_KOGUSED = 'ekk-korraldamine-valjastus-kogused'

class ValjastusController(BaseResourceController):
    _permission = 'korraldamine'
    _INDEX_TEMPLATE = '/ekk/korraldamine/valjastus.mako'
    _get_is_readonly = False
    _upath = 'korraldamine_valjastus'

    def valjastusymbrikud(self):
        return self.index()

    def tagastusymbrikud(self):
        return self.index()

    def protokollid(self):
        return self.index()

    def turvakotikleebised(self):
        return self.index()

    def turvakotiaktid(self):
        return self.index()

    def lisatingimused(self):
        return self.index()
    
    def index(self):
        c = self.c
        if c.action != 'index':
            c.subtab = c.action
            c.is_edit = True
            self._get_protsessid()

        sub = self._get_sub()
        if sub == 'progress':
            return self._index_progress()

        dparams = self._get_default_params(_UPATH_KOGUSED, True)
        if dparams:
            self.c.sailitakoodid = dparams.get('sailitakoodid')
            self.c.sordi = dparams.get('sordi')
        else:
            self.c.sailitakoodid = True

        # tehakse töö
        d = self._index_d()
        if isinstance(d, dict):
            # kui ei tagastatud valmis vastust, siis vormistatakse vastus
            return self._showlist()
        else:
            # tagastatakse vastus
            return d
       
    def _query(self):
        # mallide valikud
        self.c.pdf_templates = pages_loader.get_templates_opt_dict()
        log.debug(self.c.pdf_templates)
        # ainele kehtiv vaikimisi valik
        self.c.pdf_default = model.Ainepdf.get_default_dict(self.c.toimumisaeg.testiosa.test.aine_kood)

        # kuupäevade kaupa ruumide arv ja sooritajate arv 
        q = (model.SessionR.query(model.Toimumispaev.id,
                                 model.Toimumispaev.aeg,
                                 sa.func.count(model.Testiruum.id))
             .join(model.Testiruum.testikoht)
             .filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id)
             .outerjoin(model.Testiruum.toimumispaev)
             .group_by(model.Toimumispaev.aeg, model.Toimumispaev.id)
             .order_by(model.Toimumispaev.aeg))
        self.c.kpv_cnt = []
        for tp_id, tp_aeg, tr_cnt in q.all():
            q = (model.SessionR.query(model.Sooritaja.lang, sa.func.count(model.Sooritaja.id))
                 .join(model.Sooritaja.sooritused)
                 .join(model.Sooritus.testiruum)
                 .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
                 .filter(model.Testiruum.toimumispaev_id==tp_id)
                 .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
                 .group_by(model.Sooritaja.lang))
            dij = {lang:cnt for (lang, cnt) in q.all()}
            lang_cnt = [(model.Klrida.get_lang_nimi(lang), dij[lang]) \
                        for lang in self.c.opt.sorted_lang(list(dij.keys()))]
            self.c.kpv_cnt.append((tp_aeg, tr_cnt, lang_cnt))

        # väljastusymbrike koguste tabel (p-testis)
        self.c.v_kogused = {}
        q = (model.SessionR.query(sa.func.sum(model.Valjastusymbrik.ymbrikearv),
                                 sa.func.sum(model.Valjastusymbrik.toodearv),
                                 model.Valjastusymbrikuliik.tahis,
                                 model.Testipakett.lang,
                                 model.Valjastusymbrik.kursus_kood)
             .join(model.Valjastusymbrik.valjastusymbrikuliik)
             .filter(model.Valjastusymbrikuliik.toimumisaeg_id==self.c.toimumisaeg.id)
             .join(model.Valjastusymbrik.testipakett)
             .group_by(model.Valjastusymbrikuliik.tahis,
                       model.Testipakett.lang,
                       model.Valjastusymbrik.kursus_kood))
        for rcd in q.all():
            ymbrikearv, toodearv, liik_tahis, lang, kursus = rcd
            self.c.v_kogused[(lang,kursus,liik_tahis)] = (ymbrikearv, toodearv)

        # tagastusymbrike koguste tabel (p-testis)
        self.c.t_kogused = {}
        q = (model.SessionR.query(sa.func.sum(model.Tagastusymbrik.ymbrikearv),
                                 sa.func.sum(model.Testiprotokoll.toodearv),
                                 model.Tagastusymbrikuliik.tahis,
                                 model.Testipakett.lang,
                                 model.Testiprotokoll.kursus_kood)
             .join(model.Tagastusymbrik.tagastusymbrikuliik)
             .filter(model.Tagastusymbrikuliik.toimumisaeg_id==self.c.toimumisaeg.id)
             .join(model.Tagastusymbrik.testiprotokoll)
             .join(model.Testiprotokoll.testipakett)
             .group_by(model.Tagastusymbrikuliik.tahis,
                       model.Testipakett.lang,
                       model.Testiprotokoll.kursus_kood))
        for rcd in q.all():
            ymbrikearv, toodearv, liik_tahis, lang, kursus = rcd
            self.c.t_kogused[(lang, kursus, liik_tahis)] = (ymbrikearv, toodearv)
             
        # turvakottide koguste tabel (p-testis)
        self.c.kogused = {}
        q = (model.SessionR.query(sa.func.sum(model.Testipakett.valjastuskottidearv),
                                sa.func.sum(model.Testipakett.tagastuskottidearv),
                                model.Testipakett.lang)
             .join(model.Testipakett.testikoht)
             .filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id)
             .group_by(model.Testipakett.lang))
        for rcd in q.all():
            vkottidearv, tkottidearv, lang = rcd
            self.c.kogused[lang] = (vkottidearv, tkottidearv)

        # leiame sisestamata kotinumbritega turvakottide arvu (p-testis)
        q = (model.SessionR.query(sa.func.count(model.Turvakott.id), 
                                 model.Turvakott.suund)
             .filter(model.Turvakott.kotinr==None)
             .join(model.Turvakott.testipakett)
             .join(model.Testipakett.testikoht)
             .filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id)
             .group_by(model.Turvakott.suund))
        self.c.sisestamata_valjastuskotid = 0
        self.c.sisestamata_tagastuskotid = 0
        for rcd in q.all():
            if rcd.suund == const.SUUND_VALJA:
                self.c.sisestamata_valjastuskotid = rcd[0]
            elif rcd.suund == const.SUUND_TAGASI:
                self.c.sisestamata_tagastuskotid = rcd[0]

        if self.request.params.get('op') == 'kontrolli':
            # Kui midagi on puudu, siis kuvatakse nt, test on salastatud, kogused on arvutamata vms.
            li_err = kontrolli(self, self.c.toimumisaeg)
            self.c.kontroll_err = '<br/>'.join(li_err)
            if not self.c.kontroll_err:
                self.c.kontroll_ok = _("Toimumisaeg on testi läbiviimiseks valmis")

        return None

    def _search_protsessid(self, q):
        # valimi eraldamise protsessi loomine vt valim.py
        c = self.c
        q = (q.filter(model.Arvutusprotsess.test_id==c.test.id)
             .filter(model.Arvutusprotsess.toimumisaeg_id==c.toimumisaeg.id)
             .filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_MATERJAL)
             .filter(model.Arvutusprotsess.param==c.subtab)
             )
        return q
    
    def _create_kogused(self):
        "Arvuta kogused"

        sailitakoodid = bool(self.request.params.get('sailitakoodid'))      
        sordi = bool(self.request.params.get('sordi'))      

        dparams = self._get_default_params() or {}
        dparams['sailitakoodid'] = sailitakoodid
        dparams['sordi'] = sordi
        self._set_default_params(dparams, _UPATH_KOGUSED)
                
        err = create_kogused(self, self.c.toimumisaeg, sailitakoodid, sordi)
        if err:
            self.error(err)
        else:
            model.Session.commit()
            self.success()

        return self._redirect('index')
           
    def _create_hindamisprotokollid(self):
        "Loome hindamisprotokollid ja muud hindamiseks vajalikud kirjed"

        if not self.c.toimumisaeg.on_kogused:
            self.error(_("Kogused on arvutamata"))
            return self._redirect('index')

        err = create_hindamisprotokollid(self, self.c.toimumisaeg)
        if err:
            self.error(err)
        else:
            model.Session.commit()
            self.success()
        return self._redirect('index')
           
    def _create_ymbrikud(self):
        "Loo ümbrikud ja turvakotid"
        if not self.c.toimumisaeg.on_kogused:
            self.error(_("Kogused on arvutamata"))
            return self._redirect('index')

        err, msg = create_ymbrikud(self, self.c.toimumisaeg)
        if err:
            self.error(err)
        else:
            if msg:
                self.notice(msg)
            model.Session.commit()
            self.success()

        return self._redirect('index')


    def _create_pr_valjastusymbrikud(self):
        self._validate_pdf()
        doc = ValjastusymbrikDoc(self.c.toimumisaeg,
                                 self.form.data,
                                 self.request.params.getall('y_jrk'))
        buf = _("Väljastusümbrike genereerimine")
        return self._gen_pdf(doc, 'valjastusymbrikud.pdf', buf, 'valjastusymbrikud')

    def _create_pr_tagastusymbrikud(self):
        self._validate_pdf()
        doc = TagastusymbrikDoc(self.c.toimumisaeg, 
                                self.form.data,
                                self.request.params.getall('y_jrk'))
        buf = _("Tagastusümbrike genereerimine")
        return self._gen_pdf(doc, 'tagastusymbrikud.pdf', buf, 'tagastusymbrikud')

        
    def _create_pr_protokollid(self):
        self._validate_pdf()
        doc = MaterjalDoc(self.c.toimumisaeg, 
                          self.form.data,
                          self.request.params.getall('m_jrk'))
        buf = _("Protokollide ja nimekirjade genereerimine")
        return self._gen_pdf(doc, 'materjalid.pdf', buf, 'protokollid')

    def _create_pr_turvakotikleebised(self): 
        self._validate_pdf()
        doc = TurvakotikleebisDoc(self.c.toimumisaeg, 
                                  self.form.data,
                                  self.request.params.getall('k_jrk'))
        buf = _("Turvakotikleebiste genereerimine")
        return self._gen_pdf(doc, 'turvakotid.pdf', buf, 'turvakotikleebised')

    def _create_pr_turvakotiaktid(self):
        self._validate_pdf()
        doc = TurvakotiaktDoc(self.c.toimumisaeg,
                              self.form.data)
        buf = _("Turvakotiaktide genereerimine")
        return self._gen_pdf(doc, 'turvakottide_akt.pdf', buf, 'turvakotiaktid')

    def _create_pr_lisatingimused(self):
        self._validate_pdf()
        doc = MaterjalDoc(self.c.toimumisaeg, 
                          self.form.data,
                          self.request.params.getall('m_jrk'))
        buf = _("Lisatingimuste nimekirja genereerimine")
        return self._gen_pdf(doc, 'lisatingimused.pdf', buf, 'lisatingimused')

    def _validate_pdf(self):
        self.form = Form(self.request, schema=forms.ekk.korraldamine.ValjastusPDFForm)
        self.form.validate()
        self._copy_search_params(self.form.data, save=True)
        self._save_default_ainepdf()

    def _get_current_upath(self):
        "Tegevuse tunnus, mille järgi jäetakse meelde, millised PDFid on valitud"
        upath = 'korraldamine_valjastus'
        if self.request.method == 'POST':
            # PDFi genereerimisel
            sub = self.request.params.get('sub')
            if sub and sub.startswith('pr_'):
                upath += '_' + sub[3:]
        else:
            # Vormi kuvamisel kuvame postitamisel kasutatud märkeruute
            upath += '_' + self.c.action
        return upath
        
    def _save_default_ainepdf(self):
        """Mallide valiku salvestamine kasutamiseks vaikeväärtustena 
        järgmisel korral, kui sama aine testi materjale prinditakse.
        """
        aine_kood = self.c.toimumisaeg.testiosa.test.aine_kood
        is_changed = False
        for key in list(self.form.data.keys()):
            if key.endswith('_t'):
                tyyp = key[:-2]
                is_checked = self.form.data.get(tyyp)
                if is_checked:
                    nimi = self.form.data[key]
                    rcd = (model.Ainepdf.query
                           .filter_by(aine_kood=aine_kood)
                           .filter_by(tyyp=tyyp)
                           .first())
                    if not rcd:
                        rcd = model.Ainepdf(aine_kood=aine_kood,
                                            tyyp=tyyp,
                                            nimi=nimi)
                        is_changed = True
                    elif rcd.nimi != nimi:
                        rcd.nimi = nimi
                        is_changed = True
        if is_changed:
            model.Session.commit()
            
    def _gen_pdf(self, doc, fn, kirjeldus, subtab):
        """Väljatrükid
        """
        def childfunc(protsess):
            # PDF genereerimise protsess, võib võtta aega
            data = err = None
            try:
                data = doc.generate()
            except PdfGenException as ex:
                err = str(ex)
            else:
                err = doc.error

            if err:
                # tekkis viga
                if protsess:
                    protsess.viga = err
                else:
                    self.error(err)
            elif data:
                # tekkis fail
                if protsess:
                    protsess.filename = fn
                    protsess.filedata = data
                else:
                    return {'data': data}

        # täiendame kirjeldust soorituskoha või piirkonnaga, kui need on valitud
        c = self.c
        testikoht_id = self.request.params.get('testikoht_id')
        piirkond_id = self.request.params.get('piirkond_id')
        if testikoht_id:
            testikoht = model.Testikoht.get(testikoht_id)
            if testikoht:
                koht = testikoht.koht
                kirjeldus += ' (%s)' % koht.nimi
        elif piirkond_id:
            piirkond = model.Piirkond.get(piirkond_id)
            if piirkond:
                kirjeldus += ' (%s)' % piirkond.nimi

        # arvutusprotsessi parameetrid
        params = {'toimumisaeg_id': c.toimumisaeg.id,
                  'test_id': c.test.id,
                  'liik': model.Arvutusprotsess.LIIK_MATERJAL,
                  'param': subtab,
                  'kirjeldus': kirjeldus,
                  }
        debug = self.request.params.get('debug')
        res = model.Arvutusprotsess.start(self, params, childfunc, debug=debug)
        self.success(_("Materjalide genereerimise protsess on käivitatud"))
        if isinstance(res, dict):
            # protsessi ei käivitatud, vastus on fail
            return utils.download(res['data'], fn, 'application/pdf')
        else:
            # protsess käivitati või saadi viga
            return HTTPFound(location=self.url_current(subtab, testikoht_id=testikoht_id, piirkond_id=piirkond_id))
        
    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.test = self.c.toimumisaeg.testiosa.test
        
    def _perm_params(self):
        return {'obj':self.c.test}

def create_kogused(handler, toimumisaeg, sailitakoodid=True, sordi=False):
    
    err = _check_testiprotokollid(handler, toimumisaeg, sailitakoodid, True)
    if err:
        return err

    # eemaldame ruumidest sooritused, mis on tühistatud või vabastatud
    q_tos = (model.Sooritus.query
             .filter_by(toimumisaeg_id=toimumisaeg.id)
             .filter(model.Sooritus.staatus.in_(
                 (const.S_STAATUS_VABASTATUD, const.S_STAATUS_TYHISTATUD)))
             .filter(model.Sooritus.testiprotokoll_id!=None)
             )
    for tos in q_tos.all():
        tos.testiprotokoll_id = tos.testiruum_id = tos.testikoht_id = None
    model.Session.flush()

    # eemaldame need sooritusruumid, kus pole sooritajaid
    _remove_empty(handler, toimumisaeg)
    model.Session.commit()

    testiosa = toimumisaeg.testiosa
    if testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
        toimumisaeg.ruumide_jaotus = False
        toimumisaeg.labiviijate_jaotus = False
        toimumisaeg.kohad_kinnitatud = True

    # määrame soorituste tähised
    for tkoht in toimumisaeg.testikohad:
        if not sailitakoodid or not tkoht.sooritused_seq:
            tkoht.sooritused_seq = 0
        # sordime sooritused testiruumide sees
        # tähiste järgi (kui on olemas) või nime järgi (kui tähist pole)
        q_tos = (model.Sooritus.query
                 .filter_by(testikoht_id=tkoht.id)
                 .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
                 .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA)
                 .join(model.Sooritus.sooritaja)
                 .join(model.Sooritus.testiruum)
                 .outerjoin(model.Sooritus.testiprotokoll))

        if sordi:
            # järjestame protokollirühma sees nime järgi
            q_tos = q_tos.order_by(model.Testiruum.tahis,
                                   model.Testiprotokoll.tahis,
                                   model.Sooritaja.perenimi,
                                   model.Sooritaja.eesnimi)
        else:
            # järjestame senise soorituse tähise järgi, et säiliks kasutaja valitud järjestus
            q_tos = q_tos.order_by(model.Testiruum.tahis,
                                   model.Testiprotokoll.tahis,
                                   model.Sooritus.tahis,
                                   model.Sooritaja.perenimi,
                                   model.Sooritaja.eesnimi)
        if not sailitakoodid and q_tos.filter(model.Sooritus.klastrist_toomata==True).count() > 0:
            # sooritamine juba käib klastris, enam ei või tööde tähiseid muuta
            sailitakoodid = True
        
        for tos in q_tos.all():
            if not tos.testiprotokoll_id:
                # kui millegipärast pole veel protokolliryhma, siis loome selle
                rc, err = tos.suuna(tkoht, tos.testiruum, err=True, valim_kontroll=False)
                if not rc:
                    return err
                elif err:
                    handler.error(err)
            if not sailitakoodid:
                tos.tahis = None
            if not tos.tahis:
                tos.gen_tahis()

    calc_tos_max_pallid(toimumisaeg)

    set_testikoht_current(toimumisaeg)

    toimumisaeg.on_kogused = 1
    toimumisaeg.on_ymbrikud = 0
    toimumisaeg.on_hindamisprotokollid = 0
    
    err = create_toimumisprotokollid(handler, toimumisaeg)
    return err

def set_testikoht_current(toimumisaeg):
    # salvestame testikoha juurde koha praeguse nime, aadressi ja piirkonna,
    # et hiljem tulemuste statistikas saaks kasutada testi toimumise ajal kehtinud andmeid

    Koolinimi1 = sa.orm.aliased(model.Koolinimi)
    q = (model.Session.query(model.Testikoht, model.Koolinimi.id)
         .join(model.Testikoht.koht)
         .join(model.Koht.koolinimed)
         .filter(~ sa.exists().where(sa.and_(
             Koolinimi1.koht_id==model.Koht.id,
             Koolinimi1.alates>model.Koolinimi.alates))
                 )
         .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
         )
    #model.log_query(q)
    for testikoht, koolinimi_id in q.all():
        testikoht.koolinimi_id = koolinimi_id

    upd = (model.Testikoht.__table__.update()
           .values(koht_aadress_kood1=model.Aadress.kood1,
                   koht_aadress_kood2=model.Aadress.kood2)
           .where(sa.and_(model.Aadress.id==model.Koht.aadress_id,
                          model.Koht.id==model.Testikoht.koht_id))
           .where(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
           )
    #print(upd)
    model.Session.execute(upd)

    upd = (model.Testikoht.__table__.update()
           .values(koht_aadress_kood1=None,
                   koht_aadress_kood2=None)
           .where(sa.and_(model.Koht.aadress_id==None,
                          model.Koht.id==model.Testikoht.koht_id))
           .where(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
           )
    #print(upd)
    model.Session.execute(upd)

    upd = (model.Testikoht.__table__.update()
           .values(koht_piirkond_id=model.Koht.piirkond_id)
           .where(model.Koht.id==model.Testikoht.koht_id)
           .where(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
           )
    #print(upd)
    model.Session.execute(upd)
    
def calc_tos_max_pallid(toimumisaeg):
    "Arvutame testiosa soorituste max pallid"
    testiosa = toimumisaeg.testiosa
        
    # märgime max_pallid=0 vabastatud testiosasooritustele
    upd = model.Sooritus.__table__.update().values(max_pallid=0).where(
        sa.and_(model.Sooritus.toimumisaeg_id==toimumisaeg.id,
                model.Sooritus.staatus==const.S_STAATUS_VABASTATUD,
                sa.or_(model.Sooritus.max_pallid==None,
                       model.Sooritus.max_pallid!=0)
                ))
    model.Session.execute(upd)

    if testiosa.max_pallid:
        # märgime max_pallid mittevabastatud testiosasooritustele
        # (ei märgi siis, kui testiosal pole max palle, sest siis sõltub komplektist)
        upd = model.Sooritus.__table__.update().values(max_pallid=testiosa.max_pallid).where(
            sa.and_(model.Sooritus.toimumisaeg_id==toimumisaeg.id,
                    model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD,
                    model.Sooritus.staatus>const.S_STAATUS_REGAMATA,
                    sa.or_(model.Sooritus.max_pallid==None,
                           model.Sooritus.max_pallid!=testiosa.max_pallid),
                    ~sa.exists().where(sa.and_(
                        model.Alatestisooritus.sooritus_id==model.Sooritus.id,
                        model.Alatestisooritus.staatus==const.S_STAATUS_VABASTATUD))
                    ))
        model.Session.execute(upd)
    
    # arvutame max_pallid vabastatud alatestidega testiosasooritustele
    q = (model.Sooritus.query
         .filter(model.Sooritus.toimumisaeg_id==toimumisaeg.id)
         .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
         .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA))

    f1 = sa.exists().where(sa.and_(
        model.Alatestisooritus.sooritus_id==model.Sooritus.id,
        model.Alatestisooritus.staatus==const.S_STAATUS_VABASTATUD))
    if testiosa.max_pallid:
        # leiame ka need, kes varem olid alatestist vabastatud, aga enam mitte
        f1 = sa.or_(f1, model.Sooritus.max_pallid!=testiosa.max_pallid)
    q = q.filter(f1)

    for tos in q.all():
        tos.calc_max_pallid()
    
def create_toimumisprotokollid(handler, toimumisaeg, check=False):
    testimiskord = toimumisaeg.testimiskord
    on_testikohakaupa = not testimiskord.prot_tulemusega
    on_ruumikaupa = testimiskord.on_ruumiprotokoll
    on_paketid = toimumisaeg.on_paketid
    if on_paketid:
        f_lang = model.Toimumisprotokoll.lang==model.Testipakett.lang
    else:
        f_lang = model.Toimumisprotokoll.lang==None
    
    # leiame kirjed, millele veel ei ole toimumisprotokolli loodud
    if on_ruumikaupa:
        # testiruumi ja keele kaupa
        # (TE/SE ja ei ole tulemusega protokoll)
        q = (model.Session.query(model.Testikoht.koht_id,
                                 model.Testikoht.id,
                                 model.Testipakett.lang,
                                 model.Testiruum.id)
             .distinct()
             .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
             .outerjoin(model.Testikoht.testipaketid)
             .join(model.Testikoht.testiruumid)
             )
        if on_paketid:
            q = q.filter(model.Testiruum.testiprotokollid.any(
                   model.Testiprotokoll.testipakett_id==model.Testipakett.id))
        q = q.filter(~ sa.exists()
                     .where(f_lang)
                     .where(model.Toimumisprotokoll.testikoht_id==model.Testikoht.id)
                     .where(model.Toimumisprotokoll.testiruum_id==model.Testiruum.id)
                     )
             
    elif on_testikohakaupa:
        # toimumisaja ja koha ja keele kaupa
        # (ei ole TE/SE ja ei ole tulemusega protokoll)
        q = (model.Session.query(model.Testikoht.koht_id,
                                 model.Testikoht.id,
                                 model.Testipakett.lang)
             .distinct()
             .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)             
             .outerjoin(model.Testikoht.testipaketid)
             .filter(~ sa.exists()
                     .where(f_lang)
                     .where(model.Toimumisprotokoll.testikoht_id==model.Testikoht.id)
                     .where(model.Toimumisprotokoll.testiruum_id==None)
                     )
             )
    else:
        # testimiskorra ja koha kaupa
        # (tulemusega protokoll)
        q_ta1 = (model.Session.query(model.Toimumisaeg.id)
                 .filter(model.Toimumisaeg.testimiskord_id==testimiskord.id)
                 .join(model.Toimumisaeg.testiosa)
                 .order_by(model.Testiosa.seq)
                 )
        esimene_toimumisaeg_id = q_ta1.first()[0]

        q = (model.Session.query(model.Testikoht.koht_id,
                                 model.Testikoht.id)
             .distinct()
             .outerjoin(model.Testikoht.testipaketid)
             .filter(model.Testikoht.toimumisaeg_id==esimene_toimumisaeg_id)
             .filter(~ sa.exists()
                     .where(model.Toimumisprotokoll.testikoht_id==model.Testikoht.id)
                     .where(model.Toimumisprotokoll.testiruum_id==None)
                     .where(model.Toimumisprotokoll.lang==None)
                     )
             )
    model.log_query(q)
    for row in q.all():
        if check:
            # ainult kontroll
            return _("Kogused on vaja üle arvutada, sest mõned toimumise protokollid puuduvad")
        koht_id = row[0]
        testikoht_id = row[1]
        lang = len(row) > 2 and row[2] or None
        testiruum_id = len(row) > 3 and row[3] or None
        log.debug('loon toimumisprotokolli koht=%s testikoht=%s lang=%s testiruum=%s' % \
                  (koht_id, testikoht_id, lang, testiruum_id))
        model.Toimumisprotokoll(testimiskord=testimiskord,
                                koht_id=koht_id,
                                lang=lang,
                                staatus=const.B_STAATUS_KEHTIV,
                                testikoht_id=testikoht_id,
                                testiruum_id=testiruum_id)

    # eemaldame tyhjaks jäänud toimumisprotokollid
    def del_mpr(q):
        #request = handler.request # i18n jaoks
        for mpr in q.all():
            if check:
                # ainult kontroll
                return _("Kogused on vaja üle arvutada, sest toimumise protokolle pole uuendatud")
            elif mpr.staatus in (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD):
                return _("Protokoll {s} on juba kinnitatud").format(s=mpr.tahistus)
            else:
                log.debug('eemaldan toimumisprotokolli %s' % mpr.id)
                mpr.delete()

    # eemaldame testikohaga seotud protokollid
    q = (model.Toimumisprotokoll.query
         .filter(model.Toimumisprotokoll.testimiskord_id==testimiskord.id)
         )
    if on_ruumikaupa or on_testikohakaupa:
        if on_paketid:
            # peavad olema mitte-NULL: lang,testikoht_id
            # ja lang peab vastama mõnele testipaketile
            f_lang = sa.or_(model.Toimumisprotokoll.lang==None,
                            ~ sa.exists().where(
                                sa.and_(model.Testipakett.testikoht_id==model.Toimumisprotokoll.testikoht_id,
                                        model.Testipakett.lang==model.Toimumisprotokoll.lang)
                            ))
        else:
            # peavad olema mitte-NULL: testikoht_id
            # ja lang peab olema NULL
            f_lang = model.Toimumisprotokoll.lang!=None

        if on_ruumikaupa:
            # peab olema mitte-NULL: testiruum_id
            q = q.filter(sa.or_(f_lang,
                                model.Toimumisprotokoll.testiruum_id==None))
        elif on_testikohakaupa:
            # peavad olema NULL: testiruum_id
            q = q.filter(sa.or_(f_lang,
                                model.Toimumisprotokoll.testiruum_id!=None))

    else:
        # protokoll tulemusega
        # peab olema mitte-NULL: testikoht_id 
        # ja NULL: lang, testiruum_id
        # ja testikoht_id peab vastama esimesele toimumisajale
        q = q.filter(sa.or_(model.Toimumisprotokoll.lang!=None,
                            model.Toimumisprotokoll.testiruum_id!=None,
                            ~ sa.exists().where(
                                sa.and_(model.Testikoht.id==model.Toimumisprotokoll.testikoht_id,
                                        model.Testikoht.toimumisaeg_id==esimene_toimumisaeg_id)
                                )
                            )
                     )
        
    err = del_mpr(q)
    if err:
        return err

def create_hindamisprotokollid(handler, toimumisaeg):
    "Loome hindamisprotokollid ja muud hindamiseks vajalikud kirjed"
    err = _check_hindamisprotokollid(handler, toimumisaeg)
    if err:
        return err
    testiosa = toimumisaeg.testiosa

    toimumisaeg.update_hindamisolekud()

    q = (model.Session.query(model.Testikoht, model.Testiruum)
         .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
         .join(model.Testikoht.testiruumid))

    for (testikoht, testiruum) in q.all():
        protokollid = list(testiruum.testiprotokollid)
        for tpr in protokollid:
            # testiprotokolli all on iga hindamisliigi ja sisestuskogumi 
            # kohta eraldi hindamisprotokoll
            for skogum in testiosa.sisestuskogumid:
                # kas sisestuskogumis esineb kahekordset hindamist 
                # ja kas on vaja hindamisprotokolli?
                if testiosa.vastvorm_kood in (const.VASTVORM_SP, const.VASTVORM_SH) or skogum.on_hindamisprotokoll:
                    # hindamisprotokolli läheb vaja siis, 
                    # kui on suuline test või 
                    # kui on kirjalik p-test, mida sisestatakse 
                    # hindamisprotokollilt, mitte testitöölt
                    kahekordne_hindamine = False
                    for hkogum in skogum.hindamiskogumid:
                        if hkogum.kahekordne_hindamine or hkogum.kahekordne_hindamine_valim:
                            kahekordne_hindamine = True

                    # esimese hindaja hindamisprotokolli genereerimine
                    hpr = tpr.give_hindamisprotokoll(const.HINDAJA1, skogum.id)
                        
                    # arvutame juba ka tehtud tööde arvu, see on vajalik siis,
                    # kui peale toimumise protokolli sisestamist on vaja 
                    # hindamisprotokolle genereerida
                    hpr.calc_tehtud_toodearv(tpr.id)

                    # teise hindaja hindamisprotokoll
                    if kahekordne_hindamine:
                        hpr = tpr.give_hindamisprotokoll(const.HINDAJA2, skogum.id)
                        hpr.calc_tehtud_toodearv(tpr.id)
                    else:
                        r = tpr.get_hindamisprotokoll(const.HINDAJA2, skogum.id)
                        if r:
                            r.delete()

    toimumisaeg.update_aeg()
    toimumisaeg.on_hindamisprotokollid = 1
    
def create_ymbrikud(handler, toimumisaeg):
    msg = None
    testiosa = toimumisaeg.testiosa
    valjastuskoti_maht = toimumisaeg.valjastuskoti_maht
    tagastuskoti_maht = toimumisaeg.tagastuskoti_maht
    if not toimumisaeg.on_paketid:
        # e-test, testipakette ei ole
        return _("E-testis ei kasutata ümbrikke"), msg
    
    if not valjastuskoti_maht:
        return _("Väljastuskoti maht on määramata"), msg

    if not tagastuskoti_maht:
        return _("Tagastuskoti maht on määramata"), msg
        
    on_kirjalik = testiosa.vastvorm_kood == const.VASTVORM_KP
    arvutus = random.randrange(1,100000)
    log.debug('Arvutus %s' % arvutus)

    ####################################
    # väljastusymbrike funktsioonid

    def _give_valjastusymbrik(vyl, sooritajatearv, testiruum, testipakett_id, kursus):
        if on_kirjalik:
            # igale sooritajale vaikimisi 1 töö
            toodearv = sooritajatearv
        else:
            # suulises testis on ruumi kohta vaikimisi 1 töö
            toodearv = 1
        tmp1 = toodearv
        if vyl.lisatoode_koef:
            toodearv = int(math.ceil(toodearv * vyl.lisatoode_koef))
        if vyl.lisatoode_arv:
            toodearv += vyl.lisatoode_arv
        if vyl.ymarduskordaja:
            jaak = toodearv % vyl.ymarduskordaja
            if jaak:
                toodearv += vyl.ymarduskordaja - jaak

        if testiruum:
            # ruumikaupa ymbrikud
            ymbrik = testiruum.give_valjastusymbrik(vyl.id, testipakett_id, kursus)
        else:
            # paketikaupa ymbrikud
            pakett = model.Testipakett.get(testipakett_id)
            ymbrik = pakett.give_valjastusymbrik(vyl.id, kursus)
            
        ymbrik.arvutus = arvutus
        if vyl.maht:
            ymbrikearv = int(math.ceil(float(toodearv) / vyl.maht))
        else:
            ymbrikearv = 1

        ymbrik.toodearv = toodearv
        ymbrik.ymbrikearv = ymbrikearv

    def _genv_paketi_ruumikaupa(vyliigid):
        # väljastusymbrikud, mis luuakse iga keele ja kursuse jaoks eraldi igas ruumis
        if not vyliigid:
            return
        q = (model.Session.query(sa.func.count(model.Sooritus.id), 
                                 model.Testiruum.id, 
                                 model.Testipakett.id,
                                 model.Testiprotokoll.kursus_kood)
             .join(model.Testiruum.testikoht)
             .join(model.Testikoht.testipaketid)
             .join(model.Testipakett.testiprotokollid)
             .join(model.Testiprotokoll.sooritused)
             .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)             
             .filter(model.Sooritus.toimumisaeg_id==toimumisaeg.id)
             .filter(model.Sooritus.testiruum_id==model.Testiruum.id)
             .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
             .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA)
             .group_by(model.Testipakett.id,
                       model.Testiruum.id,
                       model.Testiprotokoll.kursus_kood))
        for rcd in q.all():
            sooritajatearv = rcd[0]
            testiruum = model.Testiruum.get(rcd[1])
            testipakett_id = rcd[2]
            kursus = rcd[3]
            for vyl in vyliigid:
                _give_valjastusymbrik(vyl, sooritajatearv, testiruum, testipakett_id, kursus)

    def _genv_ruumikaupa(vyliigid):
        # väljastusymbrikud, mis luuakse yhiselt kõigile keeltele ja kursustele igas ruumis
        q = (model.Session.query(sa.func.count(model.Sooritus.id), 
                                 model.Testiruum.id)
             .join(model.Testiruum.sooritused)
             .filter(model.Sooritus.toimumisaeg_id==toimumisaeg.id)
             .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
             .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA)
             .group_by(model.Testiruum.id))
        for rcd in q.all():
            sooritajatearv = rcd[0]
            testiruum = model.Testiruum.get(rcd[1])

            # leiame ruumi keeled
            q0 = (model.Session.query(model.Sooritaja.lang).distinct()
                  .join(model.Sooritaja.sooritused)
                  .filter(model.Sooritus.testiruum_id==testiruum.id))
            r_langs = [r[0] for r in q0.all()]
            if r_langs:
                # kuigi ymbrik ei ole seotud keelega, peame selle paigutama mõnda testipaketti,
                # sest väljastuskotid on testipakettide kaupa
                q1 = (model.Session.query(model.Testipakett.id)
                      .filter(model.Testipakett.testikoht_id==testiruum.testikoht_id)
                      .filter(model.Testipakett.lang.in_(r_langs))
                      .order_by(sa.func.lang_sort(model.Testipakett.lang)))
                testipakett_id = q1.first()[0]
                for vyl in vyliigid:
                    _give_valjastusymbrik(vyl, sooritajatearv, testiruum, testipakett_id, None)

    def _genv_paketikaupa(vyliigid):
        # väljastusymbrikud, mis luuakse iga keele ja kursuse jaoks eraldi, kogu paketi kohta
        if not vyliigid:
            return
        q = (model.Session.query(sa.func.count(model.Sooritus.id), 
                                 model.Testipakett.id,
                                 model.Testiprotokoll.kursus_kood)
             .join(model.Testikoht.testipaketid)
             .join(model.Testipakett.testiprotokollid)
             .join(model.Testiprotokoll.sooritused)
             .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
             .filter(model.Sooritus.toimumisaeg_id==toimumisaeg.id)
             .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
             .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA)
             .group_by(model.Testipakett.id,
                       model.Testiprotokoll.kursus_kood))
        for rcd in q.all():
            sooritajatearv = rcd[0]
            testipakett_id = rcd[1]
            kursus = rcd[2]
            testiruum = None
            for vyl in vyliigid:
                _give_valjastusymbrik(vyl, sooritajatearv, testiruum, testipakett_id, kursus)

    def _genv_koolikaupa(vyliigid):
        # väljastusymbrikud, mis luuakse yhiselt kõigile keeltele ja kursustele, kogu soorituskoha kohta
        q = (model.Session.query(sa.func.count(model.Sooritus.id), 
                                 model.Sooritus.testikoht_id)
             .filter(model.Sooritus.toimumisaeg_id==toimumisaeg.id)
             .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
             .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA)
             .group_by(model.Sooritus.testikoht_id))
        for rcd in q.all():
            sooritajatearv = rcd[0]
            testikoht_id = rcd[1]
            # kuigi ymbrik ei ole seotud keelega, peame selle paigutama mõnda testipaketti,
            # sest väljastuskotid on testipakettide kaupa
            q1 = (model.Session.query(model.Testipakett.id)
                  .filter(model.Testipakett.testikoht_id==testikoht_id)
                  .order_by(sa.func.lang_sort(model.Testipakett.lang)))
            for testipakett_id, in q1.all():
                testiruum = None
                for vyl in vyliigid:
                    _give_valjastusymbrik(vyl, sooritajatearv, testiruum, testipakett_id, None)
                break
            
    ##########################################
    # tagastusymbrike funktsioonid
    def _gent_tpr(tyliigid):
        # arvutame iga protokolli tööde arvu
        # ning tagastusymbrikud, mis luuakse igale protokollile
    
        # arvutame iga testiprotokolli tagastusymbrike kogused
        # esmalt leiame, kui palju on sooritajaid protokollide lõikes
        q = model.Session.query(sa.func.count(model.Sooritus.id), 
                                model.Testiprotokoll.id)
        q = (q.join(model.Testiprotokoll.sooritused)
             .filter(model.Sooritus.toimumisaeg_id==toimumisaeg.id)
             .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
             .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA))
        q = q.group_by(model.Testiprotokoll.id)

        protok_ryhma_suurus = toimumisaeg.protok_ryhma_suurus
        li_err_protok = []
        for rcd in q.all():
            tpr = model.Testiprotokoll.get(rcd[1])
            tpr.toodearv = sooritajatearv = rcd[0]
            if protok_ryhma_suurus and sooritajatearv > protok_ryhma_suurus:
                li_err_protok.append(tpr.tahised)

            for tyl in tyliigid:
                # teeme iga liigi kohta igale protokollile ühe tagastusümbriku kirje
                ymbrik = tpr.give_tagastusymbrik(tyl)
                ymbrik.tahised = tpr.tahised + '-' + tyl.tahis
                ymbrik.arvutus = arvutus
                if tyl.maht:
                    ymbrikearv = int(math.ceil(float(sooritajatearv) / tyl.maht))
                else:
                    ymbrikearv = 1
                ymbrik.ymbrikearv = ymbrikearv

        if li_err_protok:
            msg = _("Hoiatus: protokollirühma {s} suurus ületab lubatud {n}").format(
                s=', '.join(li_err_protok), n=protok_ryhma_suurus)

    def _gent_pakett(tyliigid_pakett, tyliigid_tpr2):
        # tagastusymbrikud, mis luuakse igale paketile või protokollipaaridele

        # koostame paketiymbrikud
        q = model.Session.query(model.Testipakett).\
            join(model.Testipakett.testikoht).\
            filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
        for pakett in q.all():
            if tyliigid_pakett:
                # paketi ymbriku teeme esimesele protokollile
                q2 = (model.Session.query(model.Testiprotokoll)
                      .filter(model.Testiprotokoll.testipakett_id==pakett.id)
                      .order_by(model.Testiprotokoll.tahis))
                tpr = q2.first()
                if tpr:
                    for tyl in tyliigid_pakett:
                        if tyl.sisukohta == model.Tagastusymbrikuliik.SISUKOHTA_PAKETT:
                            ymbrik = tpr.give_tagastusymbrik(tyl)
                            ymbrik.tahised = tpr.tahised + '-' + tyl.tahis
                            ymbrik.arvutus = arvutus
                            toodearv = pakett.toodearv
                            maht = tyl.maht or 20
                            ymbrik.ymbrikearv = math.ceil(toodearv / maht)

            if tyliigid_tpr2:
                # kahe protokolli ymbrikud
            
                # Paketi protokollirühmad jagatakse paaridesse
                paarid = {}
                q2 = (model.Session.query(model.Testiprotokoll.id,
                                          model.Testiprotokoll.testiruum_id)
                      .filter(model.Testiprotokoll.testipakett_id==pakett.id)
                      .order_by(model.Testiprotokoll.testiruum_id,
                                model.Testiprotokoll.tahis))
                prev_key = prev_testiruum_id = None
                for tpr_id, tr_id in q2.all():
                    if tr_id != prev_testiruum_id:
                        # algab uus ruum
                        if prev_key:
                            # viimasel eelmise ruumi protokollil pole paarilist
                            paarid[prev_key] = None
                        prev_testiruum_id = tr_id
                        prev_key = None
                    if prev_key is None:
                        # paariline 1
                        prev_key = tpr_id
                    else:
                        # paariline 2
                        paarid[prev_key] = tpr_id
                        prev_key = None
                if prev_key:
                    paarid[prev_key] = None

                # paaridele luuakse ymbrikud
                for tpr_id, tpr2_id in paarid.items():
                    tpr = model.Testiprotokoll.get(tpr_id)
                    tpr2 = tpr2_id and model.Testiprotokoll.get(tpr2_id)
                    for tyl in tyliigid_tpr2:
                        ymbrik = tpr.give_tagastusymbrik(tyl)
                        ymbrik.testiprotokoll2_id = tpr2_id
                        tahised = tpr.tahised
                        if tpr2:
                            tahised += '/' + tpr2.tahis
                        ymbrik.tahised = tahised + '-' + tyl.tahis
                        ymbrik.arvutus = arvutus
                        toodearv = tpr.toodearv + (tpr2 and tpr2.toodearv or 0)
                        maht = tyl.maht or 20
                        ymbrik.ymbrikearv = math.ceil(toodearv / maht)

    ##############################################################
    # VÄLJASTUSYMBRIKUD
                        
    # jagame väljastusümbrikuliigid selle järgi, mille kaupa neid kasutatakse
    paketi_ruumikaupa = []
    ruumikaupa = []
    paketikaupa = []
    koolikaupa = []
    for vyl in toimumisaeg.valjastusymbrikuliigid:
        if vyl.sisukohta == model.Valjastusymbrikuliik.SISUKOHTA_RUUM:
            if vyl.keeleylene:
                ruumikaupa.append(vyl)
            else:
                paketi_ruumikaupa.append(vyl)
        else:
            if vyl.keeleylene:
                koolikaupa.append(vyl)
            else:
                paketikaupa.append(vyl)
    # arvutame väljastusymbrike kogused
    _genv_paketi_ruumikaupa(paketi_ruumikaupa)
    _genv_ruumikaupa(ruumikaupa)
    _genv_paketikaupa(paketikaupa)
    _genv_koolikaupa(koolikaupa)

    # kui vahepeal ei commiti, siis järgnev DELETE tekitab StaleDataErrori
    model.Session.commit() 
    
    # eemaldame varem arvutatud ymbrikud, millele vastavaid sooritajaid enam pole
    sql = 'DELETE FROM valjastusymbrik WHERE arvutus<>:arvutus '+\
          'AND testipakett_id IN ('+\
          'SELECT testipakett.id FROM testipakett, testikoht '+\
          'WHERE testipakett.testikoht_id=testikoht.id '+\
          'AND testikoht.toimumisaeg_id=:toimumisaeg_id)'
    params = {'arvutus':arvutus, 'toimumisaeg_id':toimumisaeg.id}
    model.Session.execute(sa.text(sql), params)
    model.Session.commit()
    
    ##################################################################
    # TAGASTUSYMBRIKUD
    # koostame peaümbrikud, mida on iga paketi kohta üks
    q = model.Session.query(model.Testipakett).\
        join(model.Testipakett.testikoht).\
        filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
    for pakett in q.all():
        ymbrik = pakett.give_peaymbrik()
        ymbrik.tahised = pakett.testikoht.tahised # peaümbrikul on neljakohaline tähis
        ymbrik.arvutus = arvutus

    # jagame tagastusymbrikuliigid selle järgi, mille kaupa neid kasutatakse
    tyliigid_tpr = []
    tyliigid_tpr2 = []
    tyliigid_pakett = []
    for tyl in toimumisaeg.tagastusymbrikuliigid:
        if tyl.sisukohta == model.Tagastusymbrikuliik.SISUKOHTA_TPR:
            tyliigid_tpr.append(tyl)
        elif tyl.sisukohta == model.Tagastusymbrikuliik.SISUKOHTA_TPR2:
            tyliigid_tpr2.append(tyl)
        elif tyl.sisukohta == model.Tagastusymbrikuliik.SISUKOHTA_PAKETT:
            tyliigid_pakett.append(tyl)

    # arvutame protokollirühmade sooritajate arvud ja tagastusymbrike kogused
    _gent_tpr(tyliigid_tpr)
    model.Session.flush()
    _gent_pakett(tyliigid_pakett, tyliigid_tpr2)
    model.Session.commit()
    
    # eemaldame varem arvutatud ymbrikud, millele vastavaid sooritajaid enam pole
    sql = 'DELETE FROM tagastusymbrik WHERE arvutus<>:arvutus '+\
          'AND testipakett_id IN ('+\
          'SELECT testipakett.id FROM testipakett, testikoht '+\
          'WHERE testipakett.testikoht_id=testikoht.id '+\
          'AND testikoht.toimumisaeg_id=:toimumisaeg_id)'
    params = {'arvutus':arvutus, 'toimumisaeg_id':toimumisaeg.id}
    model.Session.execute(sa.text(sql), params)
    model.Session.commit()

    #################################################################
    # TESTIPAKETI KOONDKOGUSED
    
    # leiame iga paketi soorituste arvu
    q = (model.Session.query(sa.func.count(model.Sooritus.id),
                             model.Testipakett.id)
         .join(model.Sooritus.testiprotokoll)
         .join(model.Testiprotokoll.testipakett)
         .filter(model.Sooritus.toimumisaeg_id==toimumisaeg.id)
         .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
         .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA)
         .group_by(model.Testipakett.id))
    for rcd in q.all():
        sooritusi, testipakett_id = rcd
        pakett = model.Testipakett.get(testipakett_id)
        pakett.toodearv = sooritusi


    # leiame iga paketi väljastusymbrike arvu
    q = (model.Session.query(sa.func.sum(model.Valjastusymbrik.ymbrikearv),
                             model.Testipakett.id)
         .join(model.Testipakett.testikoht)
         .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
         .outerjoin(model.Testipakett.valjastusymbrikud)
         .group_by(model.Testipakett.id))
    for rcd in q.all():
        valjastusymbrikearv, testipakett_id = rcd
        pakett = model.Testipakett.get(testipakett_id)
        pakett.valjastusymbrikearv = valjastusymbrikearv or 0

        if testiosa.vastvorm_kood == const.VASTVORM_KP:
            # kirjalik
            if valjastuskoti_maht:
                pakett.valjastuskottidearv = math.ceil(float(pakett.toodearv or 0) / valjastuskoti_maht)               
            else:
                pakett.valjastuskottidearv = 1
        else:
            # suuline
            pakett.valjastuskottidearv = 1

    # leiame iga paketi tagastusymbrike arvu
    q = (model.Session.query(sa.func.sum(model.Tagastusymbrik.ymbrikearv),
                             model.Testipakett.id)
         .join(model.Testipakett.testikoht)
         .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
         .outerjoin(model.Testipakett.tagastusymbrikud)
         .group_by(model.Testipakett.id))
    for rcd in q.all():
        tagastusymbrikearv, testipakett_id = rcd
        pakett = model.Testipakett.get(testipakett_id)
        pakett.tagastusymbrikearv = tagastusymbrikearv

        if testiosa.vastvorm_kood == const.VASTVORM_KP:
            # kirjalik
            if tagastuskoti_maht:
                pakett.tagastuskottidearv = math.ceil(float(pakett.toodearv or 0) / tagastuskoti_maht)
            else:
                pakett.tagastuskottidearv = 1
        else:
            # suuline
            pakett.tagastuskottidearv = 1


        # Kui tööde väljastamise või tagastamise turvakottide kirjete arv 
        # on väiksem testisoorituspaketi kohta arvutatud turvakottide arvust, 
        # siis süsteem loob puuduvad turvakottide kirjed

        valjastuskotid = pakett.valjastuskotid
        tegelikarv = len(valjastuskotid)
        puudu = int(pakett.valjastuskottidearv) - tegelikarv
        # lisame puuduvad kotid
        for n in range(puudu):
            kott = model.Turvakott(testipakett=pakett,
                                   suund=const.SUUND_VALJA)
            pakett.turvakotid.append(kott)
        # kustutame liigsed kotid
        for n in range(tegelikarv, int(pakett.valjastuskottidearv), -1):
            valjastuskotid[n-1].delete()

        tagastuskotid = pakett.tagastuskotid
        tegelikarv = len(tagastuskotid)                
        puudu = int(pakett.tagastuskottidearv) - tegelikarv
        # lisame puuduvad kotid
        for n in range(puudu):
            kott = model.Turvakott(testipakett=pakett,
                                   suund=const.SUUND_TAGASI)
            pakett.turvakotid.append(kott)                   
        # kustutame liigsed kotid
        for n in range(tegelikarv, int(pakett.tagastuskottidearv), -1):
            tagastuskotid[n-1].delete()
                
    model.Session.commit()
    
    # eemaldame testipaketid, millele vastavaid sooritajaid enam pole
    q = (model.Testipakett.query
         .filter(model.Testipakett.toodearv==None)
         .join(model.Testipakett.testikoht)
         .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id))
    for pakett in q.all():
        pakett.delete()
    toimumisaeg.on_ymbrikud = 1
    err = create_toimumisprotokollid(handler, toimumisaeg)
    return err, msg

def kontrolli(handler, toimumisaeg):
    li = list()
    testimiskord = toimumisaeg.testimiskord
    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    if not len(toimumisaeg.testikohad):
        li.append(_("Pole ühtki soorituskohta"))
    if not len(toimumisaeg.sooritused):
        li.append(_("Pole ühtki sooritajat"))
    if not len(testiosa.testiylesanded):
        li.append(_("Testiosas pole ühtki ülesannet"))
    if test.staatus != const.T_STAATUS_KINNITATUD:
        li.append(_("Testi staatus on {s}").format(s=test.staatus_nimi))
    if test.avaldamistase != const.AVALIK_EKSAM:
        li.append(_("Testi kasutatavus on {s}").format(s=test.avaldamistase_nimi))
    if test.salastatud > const.SALASTATUD_SOORITATAV:
        li.append(_("Test on salastatud"))
    else:
        kinnitamata_k = [k.id for k in toimumisaeg.komplektid if k.staatus != const.K_STAATUS_KINNITATUD]
        if len(kinnitamata_k):
            li.append(_("Kõik toimumisaja komplektid pole kinnitatud"))

        komplektid_id = [k.id for k in toimumisaeg.komplektid]
        q = (model.SessionR.query(model.Ylesanne.id)
             .filter(model.Ylesanne.salastatud > const.SALASTATUD_SOORITATAV)
             .join(model.Ylesanne.valitudylesanded)
             .filter(model.Valitudylesanne.komplekt_id.in_(komplektid_id))
             .order_by(model.Ylesanne.id))
        salastatud_id = [str(r[0]) for r in q.all()]
        if salastatud_id:
            li.append(_("Ülesanded {s} on salastatud").format(s=', '.join(salastatud_id)))
            
    err = _check_testiprotokollid(handler, toimumisaeg, True, False)
    if err:
        li.append(err)

    err = _check_hindamisprotokollid(handler, toimumisaeg)
    if err:
        li.append(err)
        
    if not toimumisaeg.on_hindamisprotokollid:
        li.append(_("Hindamiskirjed on loomata"))
        
    if not toimumisaeg.on_ymbrikud:
        if testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
            li.append(_("P-testi ümbrikud ja turvakotid on loomata"))
    if toimumisaeg.admin_maaraja:
        q = (model.SessionR.query(model.Testiruum)
             .join(model.Testiruum.testikoht)
             .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
             .filter(~ model.Testiruum.labiviijad.any(
                 sa.and_(model.Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN,
                         model.Labiviija.kasutaja_id!=None))
                     )
             )
        cnt = q.count()
        if cnt:
            li.append(_("{n} ruumis on testi administraator määramata").format(n=cnt))

    if toimumisaeg.ruum_noutud:
        q = (model.SessionR.query(model.Testiruum.id)
             .join(model.Testiruum.testikoht)
             .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
             .filter(model.Testiruum.ruum_id==None)
             .filter(model.Testiruum.sooritused.any())
             )
        cnt = q.count()
        if cnt:
            li.append(_("{n} soorituskohas on sooritajad ruumi määramata").format(n=cnt))

    err = create_toimumisprotokollid(handler, toimumisaeg, True)
    if err:
        li.append(err)
        
    return li

def _remove_empty(handler, toimumisaeg):
    """Eemaldatakse need sooritusruumid, kus pole sooritajaid.
    """
    testiliik = toimumisaeg.testiosa.test.testiliik_kood
    if testiliik == const.TESTILIIK_TASE:
        # tasemeeksamite korral tyhje ruume automaatselt ei eemaldata, sest
        # Sulvi arvutab koguseid enne sooritajate ruumidesse määramist (ES-743)
        return
    q = (model.Testiruum.query
         .join(model.Testiruum.testikoht)
         .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
         .filter(model.Testiruum.sooritajate_arv==0)
         #filter(~ model.Testiruum.sooritused.any(Sooritus.staatus>=const.S_STAATUS_TASUMATA))
         )
    for truum in q.all():
        log.debug('eemaldan testiruumi %s' % (truum.id))
        truum.delete()
    model.Session.flush()

    q = (model.Labiviija.query
         .join(model.Labiviija.testikoht)
         .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
         .filter(~ model.Testikoht.testiruumid.any())
         )
    for lv in q.all():
        log.debug('eemaldan lv %s' % (lv.id))
        lv.delete()
    model.Session.flush()
    
    q = (model.Testikoht.query
         .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
         .filter(~ model.Testikoht.testiruumid.any()))
    for tkoht in q.all():
        log.debug('eemaldan testikoha %s' % tkoht.id)
        tkoht.delete()

def _check_testiprotokollid(handler, toimumisaeg, sailitakoodid, fix):
    # kui peale sooritajate lisamist muudetakse testiliiki, siis võib olla vajadus muuta pakette:
    # kas paketid on ruumide kaupa või kohtade kaupa
    err = None
    on_ruumikaupa = toimumisaeg.on_ruumiprotokoll
    on_paketid = toimumisaeg.on_paketid
    if not on_paketid:
        # e-test, testipakette ei ole
        q = (model.Testipakett.query
             .join(model.Testipakett.testikoht)
             .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id))
        for pakett in q.all():
            pakett.delete()
        model.Session.flush()
        
    elif on_ruumikaupa:
        # jagame ruumita paketid ruumiga pakettideks
        q = (model.Testipakett.query
             .join(model.Testipakett.testikoht)
             .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
             .filter(model.Testipakett.testiruum_id==None))
        vigased = list(q.all())
        if len(vigased):
            err = _("Leitud {n} ilma ruumita paketti").format(n=len(vigased))
            if fix:
                log.info(err)
                for tp in vigased:
                    testikoht = tp.testikoht
                    for tr in testikoht.testiruumid:
                        pakett = testikoht.give_testipakett(tp.lang, tr)
                    for vy in tp.valjastusymbrikud:
                        vy.testipakett = testikoht.give_testipakett(tp.lang, vy.testiruum)
                    for tpr in tp.testiprotokollid:
                        tpr.testipakett = testikoht.give_testipakett(tp.lang, tpr.testiruum)
                        for vy in tpr.tagastusymbrikud:
                            vy.testipakett = testikoht.give_testipakett(tp.lang, tpr.testiruum)                        
            
                model.Session.flush()
                for tp in vigased:
                    tp.delete()
                model.Session.flush()
    else:
        # liidame ruumiga paketid ruumita pakettideks
        q = (model.Testipakett.query
             .join(model.Testipakett.testikoht)
             .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
             .filter(model.Testipakett.testiruum_id!=None)
             .order_by(model.Testipakett.testikoht_id))
        vigased = list(q.all())
        if len(vigased):
            err = _("Leitud {n} ruumiga paketti").format(n=len(vigased))
            if fix:
                for tp in vigased:
                    testikoht = tp.testikoht
                    pakett = testikoht.give_testipakett(tp.lang, None)
                    for tpr in tp.testiprotokollid:
                        tpr.testipakett = pakett
                        for vy in tpr.tagastusymbrikud:
                            vy.testipakett = pakett                        
                    for vy in tp.valjastusymbrikud:
                        vy.testipakett = pakett
                model.Session.flush()
                for tp in vigased:
                    tp.delete()
                model.Session.flush()
    if err and not fix:
        return _("Tuleb kogused arvutada.") + ' %s' % err

    # eemaldame testiprotokollid, milles pole sooritajaid
    # (sooritajad on välja tõstetud)
    # ja loendame protokollid uuesti, alates 1-st
    q = (model.Testikoht.query
         .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id))
    for tkoht in q.all():
        tkoht.reset_testiprotokollid(sailitakoodid)


    # kontrollime, et testipakettide keeled ja testimiskorra keeled klapivad
    kord = toimumisaeg.testimiskord
    keeled = kord.get_keeled()
    q = (model.Session.query(model.Testikoht.tahised).distinct()
         .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
         .join(model.Testikoht.testipaketid)
         .filter(~ model.Testipakett.lang.in_(keeled)))
    tahised = [tahised for tahised, in q.all()]
    if tahised:
        return _("{n} soorituskohas on testipakett keelele, mida testimiskord ei võimalda: {s}").format(
            n=len(tahised), s=', '.join(tahised))

    # kontrollime, et protokollide kursused ja testi kursused klapivad
    kursused = kord.test.get_kursused() or [None]       
    q = (model.Session.query(model.Testiprotokoll.kursus_kood).distinct()
         .join(model.Testiprotokoll.testiruum)
         .join(model.Testiruum.testikoht)
         .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id))
    for r in q.all():
        kursus = r[0]
        if kursus not in kursused:
            return _("Protokollirühmad ei vasta enam testi kursustele")
        
    q = (model.Session.query(model.Testiprotokoll.tahised).distinct()
         .join(model.Testiprotokoll.testipakett)
         .join(model.Testipakett.testikoht)
         .filter(model.Testikoht.toimumisaeg_id==toimumisaeg.id)
         .join(model.Testiprotokoll.sooritused)
         .join(model.Sooritus.sooritaja))
    
    # kontrollime, et testipakettide keeled ja sooritajate keeled klapivad
    tahised = [tahised for tahised, in q.filter(model.Testipakett.lang!=model.Sooritaja.lang).all()]
    if tahised:
        return _("{n} protokollirühmas on sooritajad vale keelega: {s}").format(
            n=len(tahised), s=', '.join(tahised))
    
    # kontrollime, et protokollide kursused ja sooritajate kursused klapivad
    f_sooritaja_k = sa.func.coalesce(model.Sooritaja.kursus_kood, '')
    f_protokoll_k = sa.func.coalesce(model.Testiprotokoll.kursus_kood, '')
    tahised = [tahised for tahised, in q.filter(f_sooritaja_k != f_protokoll_k).all()]
    if tahised:
        return _("{n} protokollirühmas on sooritajad vale kursusega: {s}").format(
            n=len(tahised), s=', '.join(tahised))
        
def _check_hindamisprotokollid(handler, toimumisaeg):
    if not toimumisaeg.on_kogused:
        return _("Kogused on arvutamata")

    testiosa = toimumisaeg.testiosa

    if len(toimumisaeg.komplektid) == 0:
        return _("Toimumisajal kasutatavad ülesandekomplektid on valimata")

    kvalikud = set([k.komplektivalik_id for k in toimumisaeg.komplektid])
    for k in testiosa.komplektivalikud:
        if k.id not in kvalikud:
            return _("Toimumisajal kasutatavad komplektid ei kata kogu testiosa")

    if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I):
        # kirjaliku testi mitte-arvutihinnatavad ülesanded 
        # peavad olema hindamiskogumis
        if testiosa.lotv:
            for k in toimumisaeg.komplektid:
                for vy in k.valitudylesanded:
                    if vy.ylesanne_id and not vy.hindamiskogum_id:
                        return _("Komplekt {s} sisaldab ülesandeid, mis ei ole hindamiskogumis").format(s=k.tahis)
    elif testiosa.vastvorm_kood == const.VASTVORM_SP:
        # suulisel p-testil peavad olema hindamisprotokollidega hindamiskogumid
        q = (model.Session.query(model.Testiylesanne)
             .filter(model.Testiylesanne.testiosa_id==testiosa.id)
             .join(model.Testiylesanne.hindamiskogum))
        cnt = q.filter(model.Hindamiskogum.on_hindamisprotokoll==False).count()
        if cnt:
            return _("Testiosas on {n} ülesannet hindamisprotokollita").format(n=cnt)

    for hk in testiosa.hindamiskogumid:
        hk.arvuta_pallid(testiosa.lotv)
        if hk.on_kriteeriumid:
            # hindamiskogumil on kriteeriumid
            if hk.arvutihinnatav:
                return _("Hindamiskogumil {s} ei või olla hindamiskriteeriume, kuna see hindamiskogum on arvutihinnatav").format(s=hk.tahis)
            elif testiosa.vastvorm_kood == const.VASTVORM_SH:
                return _("Hindamiskogumil {s} ei või olla hindamiskriteeriume, kuna testiosa ei ole kirjalik").format(s=hk.tahis)
            elif testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
                return _("Hindamiskogumil {s} ei või olla hindamiskriteeriume, kuna testiosa ei lahendata e-testina").format(s=hk.tahis)                

            # leiame alatestide arvu
            q = model.SessionR.query(sa.func.count(sa.distinct(model.Testiylesanne.alatest_id)))
            if testiosa.lotv:
                q = (q.join(model.Testiylesanne.valitudylesanded)
                     .filter(model.Valitudylesanne.hindamiskogum_id==hk.id))
            else:
                q = q.filter(model.Testiylesanne.hindamiskogum_id==hk.id)
            if q.scalar() > 1:
                return _("Hindamiskogumi {s} ülesanded ei ole ühes alatestis. Hindamiskriteeriumitega hindamiskogumi kõik ülesanded peavad kuuluma samasse alatesti").format(s=hk.tahis)
                
    if testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
        # p-testil peavad olemas olema sisestuskogumid
        q = model.Testiylesanne.queryR.\
            filter(model.Testiylesanne.testiosa_id==testiosa.id).\
            join(model.Testiylesanne.hindamiskogum)
        cnt = q.filter(model.Hindamiskogum.sisestuskogum_id==None).count()
        if cnt:
            return _("Testiosas on {n} ülesannet sisestuskogumisse määramata").format(n=cnt)

    cnt = (model.SessionR.query(sa.func.count(model.Sooritus.id))
           .filter(model.Sooritus.toimumisaeg_id==toimumisaeg.id)
           .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
           .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA)
           .filter(model.Sooritus.testiruum_id==None)
           .scalar())
    if cnt:
        return _("{n} sooritajale pole veel testikohta määratud").format(n=cnt)

