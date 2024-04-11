import cgi
import formencode
from collections import defaultdict
from eis.forms import validators
from eis.lib.xtee import Rahvastikuregister, set_rr_pohiandmed
from eis.handlers.admin.ehisopetajad import uuenda_pedagoogid
from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class KohakasutajadController(BaseResourceController):
    _permission = 'kohad'
    _INDEX_TEMPLATE = 'admin/koht.kasutajad.mako' # otsinguvormi mall
    _index_after_create = True # et peale volitamata muutmiskatset mindaks indeksisse
    _no_paginate = True
    _SEARCH_FORM = forms.admin.KohakasutajadForm # valideerimisvorm otsinguvormile
    _ignore_default_params = ['csv','xls','otsi','ehis']
    _get_is_readonly = False
    
    def _query(self):
        return None

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        self._get_opt_grupid()

        if c.ehis:
            uuenda_pedagoogid(self, c.koht, True)
            model.Session.commit()
        
        data = {}
        GRUPP_SEOTUD = 1000
        if not c.grupp_id or c.grupp_id in (const.GRUPP_OPETAJA, const.GRUPP_K_JUHT):
            for p in self._search_pedagoogid():
                ik = p.isikukood
                if ik not in data:
                    data[ik] = [(p.kasutaja_id, ik, p.eesnimi, p.perenimi), [], [], []]
                if p.on_ehisest:
                    data[ik][1].append(p)
                else:
                    data[ik][2].append(p)

        if not c.grupp_id or c.grupp_id not in (const.GRUPP_OPETAJA, GRUPP_SEOTUD):
            for r in self._search_kasutajarollid():
                k_id, ik, eesnimi, perenimi, kroll = r
                if ik not in data:
                    data[ik] = [(k_id, ik, eesnimi, perenimi), [], [], []]
                data[ik][2].append(kroll)

        if not c.grupp_id or c.grupp_id == GRUPP_SEOTUD:
            for r in self._search_kasutajakohad():
                k_id, ik, eesnimi, perenimi, kkoht = r
                if ik not in data:
                    data[ik] = [(k_id, ik, eesnimi, perenimi), [], [], []]
                data[ik][3].append(kkoht)

        # isikud järjestatakse nime järgi
        c.items = list(sorted(data.values(), key=lambda r: (r[0][2] or '', r[0][3] or '')))

    def _get_opt_grupid(self):
        c = self.c
        GRUPP_SEOTUD = 1000 # sellist gruppi pole olemas, on Kasutajakoht kirje
        c.opt_grupid = [(const.GRUPP_OPETAJA, _("Pedagoog"))] + \
            c.opt.get_antav_kooligrupp(c.app_ekk) +\
            [(GRUPP_SEOTUD, _("Soorituskohaga seotud isik"))]
        
    def _search_kasutajarollid(self):
        c = self.c
        q = (model.Session.query(model.Kasutaja.id,
                                 model.Kasutaja.isikukood,
                                 model.Kasutaja.eesnimi,
                                 model.Kasutaja.perenimi,
                                 model.Kasutajaroll)
             .join(model.Kasutaja.kasutajarollid)
             .filter(model.Kasutajaroll.koht_id==c.koht.id)
             )
        if c.grupp_id:
            q = q.filter(model.Kasutajaroll.kasutajagrupp_id==c.grupp_id)
        else:
            kooligrupid = [r[0] for r in c.opt.kooligrupp]
            q = q.filter(model.Kasutajaroll.kasutajagrupp_id.in_(kooligrupid))
        if c.kehtiv:
            today = date.today()
            q = (q.filter(model.Kasutajaroll.kehtib_alates<=today)
                 .filter(model.Kasutajaroll.kehtib_kuni>=today))
        return q.all()

    def _search_kasutajakohad(self):
        c = self.c
        q = (model.Session.query(model.Kasutaja.id,
                                 model.Kasutaja.isikukood,
                                 model.Kasutaja.eesnimi,
                                 model.Kasutaja.perenimi,
                                 model.Kasutajakoht)
             .join(model.Kasutaja.kasutajakohad)
             .filter(model.Kasutajakoht.koht_id==c.koht.id))
        return q.all()

    def _search_pedagoogid(self):
        c = self.c
        q = (model.Session.query(model.Pedagoog)
             .filter(model.Pedagoog.koht_id==c.koht.id))
        if c.grupp_id:
            q = q.filter(model.Pedagoog.kasutajagrupp_id==c.grupp_id)
        if c.kehtiv:
            today = date.today()
            q = q.filter(sa.or_(model.Pedagoog.kehtib_kuni>=today,
                                model.Pedagoog.kehtib_kuni==None))
        return q.all()
    
    def _new_roll(self):
        return self.render_to_response('/admin/koht.kasutajavalik.mako')
    
    def _create_roll(self):
        self.form = Form(self.request, schema=forms.admin.KoharollForm)
        if not self.form.validate():
            self.c.roll = self.c.new_item()
            self.c.nosub = True
            isikukood = self.request.params.get('oigus')
            self.c.items = model.Kasutaja.query.filter_by(isikukood=isikukood).all()
            return Response(self.form.render('admin/koht.kasutajavalik.mako', 
                                             extra_info=self.response_dict))            

        if not self.c.can_roll:
            self.error(_("Puudub õigus hallata rolle"))
            return HTTPFound(location=self.url('admin_koht_kasutajad', koht_id=self.c.koht.id))
        
        data = self.form.data
        kasutajagrupp_id = data.get('kasutajagrupp_id')
        GRUPP_SEOTUD = 1000
        try:
            if kasutajagrupp_id == GRUPP_SEOTUD:
                rc = self._create_kasutajakoht(data)
            elif kasutajagrupp_id == const.GRUPP_OPETAJA:
                rc = self._create_pedagoog(data)
            else:
                rc = self._create_kasutajaroll(data)
        except ValitationError as ex:
            mako = '/admin/koht.kasutajavalik.mako'
            
        if rc:
            model.Session.commit()
            self.success()
        return HTTPFound(location=self.url('admin_koht_kasutajad', koht_id=self.c.koht.id))

    def _create_kasutajaroll(self, data):
        # create_roll kutsub
        kasutajagrupp_id = data.get('kasutajagrupp_id')
        if kasutajagrupp_id == const.GRUPP_AINEOPETAJA:
            aine_kood = data.get('aine_kood')
        else:
            aine_kood = None
        kehtib_kuni = data.get('kehtib_kuni')
        if not kehtib_kuni:
            if self.c.app_eis:
                self.error(_("Palun sisestada kehtivuse kuupäev"))
                return False
            kehtib_kuni = const.MAX_DATE        
        rc = False
        for isikukood in self.request.params.getall('oigus'):
            kasutaja = model.Kasutaja.get_by_ik(isikukood)
            if kasutaja:
                if model.Kasutajaroll.query.\
                        filter_by(kasutaja_id=kasutaja.id).\
                        filter_by(koht_id=self.c.koht.id).\
                        filter_by(aine_kood=aine_kood).\
                        filter_by(kasutajagrupp_id=kasutajagrupp_id).\
                        count() > 0:
                    self.error(_("Kasutaja {s} juba on antud rollis").format(s=kasutaja.nimi))
                    continue

            if not kasutaja:
                # RRist saadud nimi
                eesnimi = self.request.params.get('eesnimi')
                perenimi = self.request.params.get('perenimi')
                kasutaja = model.Kasutaja.add_kasutaja(isikukood,eesnimi,perenimi)
                kasutaja.on_labiviija = True
                model.Session.flush()
            if not kasutaja.on_labiviija:
                kasutaja.on_labiviija = True
            item = model.Kasutajaroll(kasutajagrupp_id=kasutajagrupp_id,
                                      kasutaja_id=kasutaja.id,
                                      koht_id=self.c.koht.id,
                                      aine_kood=aine_kood,
                                      kehtib_alates=date.today(),
                                      kehtib_kuni=kehtib_kuni)
            self._log_roll(item, False)
            rc = True
        return rc

    def _create_kasutajakoht(self, data):
        # create_roll kutsub
        rc = False
        for isikukood in self.request.params.getall('oigus'):
            kasutaja = model.Kasutaja.get_by_ik(isikukood)
            if kasutaja:
                q = (model.Kasutajakoht.query
                     .filter_by(kasutaja_id=kasutaja.id)
                     .filter_by(koht_id=self.c.koht.id))
                if q.count() > 0:
                    model.log_query(q)
                    self.error(_("Kasutaja {s} on juba soorituskohaga seotud").format(s=kasutaja.nimi))
                    continue

            if not kasutaja:
                # RRist saadud nimi
                eesnimi = self.request.params.get('eesnimi')
                perenimi = self.request.params.get('perenimi')
                kasutaja = model.Kasutaja.add_kasutaja(isikukood,eesnimi,perenimi)
                model.Session.flush()
            if not kasutaja.on_labiviija:
                kasutaja.on_labiviija = True
                
            item = model.Kasutajakoht(kasutaja=kasutaja,
                                      koht_id=self.c.koht.id)
            model.Kasutajapiirkond.give(kasutaja, self.c.koht.piirkond)
            rc = True
        return rc
    
    def _create_pedagoog(self, data):
        # create_roll kutsub
        rc = False
        kehtib_kuni = data.get('kehtib_kuni') or None
        if not kehtib_kuni:
            if self.c.app_eis:
                self.error(_("Palun sisestada kehtivuse kuupäev"))
                return False

        for isikukood in self.request.params.getall('oigus'):
            rc1, err = self._insert_pedagoog(isikukood, None, kehtib_kuni)
            if err:
                self.error(err)
            if rc1:
                rc = True
        return rc
    
    def _edit_roll(self, id):
        # muuta saab ainult kasutajarolli kehtivust
        self.c.roll = model.Kasutajaroll.get(id)
        return self.render_to_response('/admin/kasutaja.kehtib_kuni.mako')
    
    def _update_roll(self, id):
        # kasutajarolli kehtivuse muutmine
        self.c.roll = model.Kasutajaroll.get(id)
        self.form = Form(self.request, schema=forms.admin.KehtibkuniForm)
        if not self.form.validate():        
            return Response(self.form.render('admin/kasutaja.kehtib_kuni.mako', 
                                             extra_info=self.response_dict))
        
        self.c.roll.kehtib_kuni = self.form.data.get('kehtib_kuni') or const.MAX_DATE
        self._log_roll(self.c.roll, False)
        model.Session.commit()
        self.success()
        return HTTPFound(location=self.url('admin_koht_kasutajad', koht_id=self.c.koht.id))

    def _delete_roll(self, id):
        rcd = model.Kasutajaroll.get(id)
        if rcd:
            assert rcd.koht_id == self.c.koht.id, _("Vale koht")
            self._log_roll(rcd, True)
            rcd.delete()
            model.Session.commit()
        return HTTPFound(location=self.url('admin_koht_kasutajad', koht_id=self.c.koht.id))        

    def _delete_kasutaja(self, id):
        rcd = model.Kasutajakoht.get(id)
        if rcd:
            assert rcd.koht_id == self.c.koht.id, _("Vale koht")
            rcd.delete()
            model.Session.commit()
        return HTTPFound(location=self.url('admin_koht_kasutajad', koht_id=self.c.koht.id))        

    def _delete_pedagoog(self, id):
        rcd = model.Pedagoog.get(id)
        if rcd:
            assert rcd.koht_id == self.c.koht.id, _("Vale koht")
            assert not rcd.on_ehisest , "EHISe kirjet ei saa muuta"
            rcd.delete()
            model.Session.commit()
        return HTTPFound(location=self.url('admin_koht_kasutajad', koht_id=self.c.koht.id))        

    # pedagoogide andmed failist
    def _new_pedagoogfail(self):
        return self.render_to_response('/admin/koht.pedagoogfail.mako')
    
    def _create_pedagoogfail(self):
        err = None
        self.form = Form(self.request, schema=forms.admin.KehtibkuniForm)
        if not self.form.validate():
            err = _("Vigane kuupäev")
        else:
            today = date.today()
            YEAR_END = date(today.year, 12, 31)
            kehtib_kuni = self.form.data.get('kehtib_kuni') or YEAR_END
            cnt = 0
            value = self.request.params.get('fail')
            if not isinstance(value, cgi.FieldStorage):
                err = _("Fail puudub")
            else:
                # value on FieldStorage objekt
                value = value.value
                for ind, line in enumerate(value.splitlines()):
                    line = utils.guess_decode(line).strip()
                    if line:
                        li, err = self._split_line(line, 2, 1)
                        if not (err or not li):
                            ik, epost = li
                            rc, err = self._insert_pedagoog(ik, epost, kehtib_kuni)
                        if err:
                            err = _('Viga real {n}.').format(n=ind+1) + '\n' + err
                            break
                        elif rc:
                            cnt += 1
        if err:
            self.error(err)
        else:
            self.success(_("Laaditud {n} isiku andmed").format(n=cnt))
            model.Session.commit()
            self.success()
        return HTTPFound(location=self.url('admin_koht_kasutajad', koht_id=self.c.koht.id))

    def _insert_pedagoog(self, ik, epost, kehtib_kuni):
        err = None
        usp = validators.IsikukoodP(ik)
        if not usp.isikukood:
            err = _('Vigane isikukood "{s}"').format(s=ik)
            return False, err

        if epost:
            try:
                validators.Email().to_python(epost)
            except formencode.api.Invalid as ex:
                err = _('Vigane e-posti aadress "{s}"').format(s=epost)
                return False, err
        
        kasutaja = usp.get(model.Kasutaja)
        if not kasutaja and usp.isikukood_ee and self.request.is_ext():
            kasutaja = set_rr_pohiandmed(self, None, usp.isikukood, True)
            if kasutaja:
                model.Session.commit()                
                    
        if kasutaja:
            q = (model.Pedagoog.query
                 .filter_by(kasutaja_id=kasutaja.id)
                 .filter_by(koht_id=self.c.koht.id))
            item = q.first()
            if item:
                err = _("Isik {s} on juba selles koolis ametis").format(s=ik)
                return False, err
            if not item:
                item = model.Pedagoog(kasutaja_id=kasutaja.id,
                                      isikukood=ik,
                                      koht_id=self.c.koht.id,
                                      kool_id=self.c.koht.kool_id,
                                      eesnimi=kasutaja.eesnimi,
                                      perenimi=kasutaja.perenimi,
                                      kasutajagrupp_id=const.GRUPP_OPETAJA,
                                      seisuga=datetime.now(),
                                      kehtib_kuni=kehtib_kuni,
                                      on_ehisest=False)
            elif kehtib_kuni:
                # muutub kehtivuse kpv
                item.seisuga = datetime.now()
                item.kehtib_kuni = kehtib_kuni
            if epost:
                item.epost = epost
            self._log_pedagoog(item, False)
            return True, err
        return False, err
    
    def _delete_pedagoog(self, id):
        rcd = model.Pedagoog.get(id)
        if rcd and not rcd.on_ehisest:
            assert rcd.koht_id == self.c.koht.id, _("Vale koht")
            self._log_pedagoog(rcd, True)
            rcd.delete()
            model.Session.commit()
        return HTTPFound(location=self.url('admin_koht_kasutajad', koht_id=self.c.koht.id))        

    def _log_roll(self, roll, is_delete):
        grupp_id = roll.kasutajagrupp_id
        if is_delete:
            sisu = 'Eemaldamine\n' + roll.get_str()
        else:
            old_values, new_values = roll._get_changed_values()
            if not new_values:
                return
            #sisu = roll.get_str_values(new_values)
            sisu = roll.get_str()
            
        krl = model.Kasutajarollilogi(kasutaja_id=roll.kasutaja_id,
                                      muutja_kasutaja_id=self.c.user.id,
                                      aeg=datetime.now(),
                                      sisu=sisu,
                                      kasutajagrupp_id=grupp_id,
                                      kasutajaroll=not is_delete and roll or None,
                                      tyyp=const.USER_TYPE_KOOL)

    def _log_pedagoog(self, rcd, is_delete):
        grupp_id = rcd.kasutajagrupp_id
        if is_delete:
            sisu = 'Eemaldamine\n' + rcd.get_str()
        else:
            sisu = rcd.get_str()
        krl = model.Kasutajarollilogi(kasutaja_id=rcd.kasutaja_id,
                                      muutja_kasutaja_id=self.c.user.id,
                                      aeg=datetime.now(),
                                      sisu=sisu,
                                      kasutajagrupp_id=grupp_id,
                                      kasutajaroll=None,
                                      tyyp=const.USER_TYPE_KOOL)

    def _split_line(self, line, cnt, cnt_min=None):
        err = None
        line = line.strip()
        if line:
            li = [s.strip() for s in line.split(';')]
            if len([s for s in li if s]) == 0:
                return
            if cnt_min and len(li) >= cnt_min: 
                while len(li) < cnt:
                    li.append('')
            if len(li) != cnt:
                err = _("Vigane rida {s}. Real peab olema {n} välja.").format(s=line.strip(), n=cnt)
                li = None
            return li, err
        return None, None
                
    def _perm_obj(self):
        return {'piirkond_id':self.c.koht.piirkond_id}

    def __before__(self):
        c = self.c
        c.koht = model.Koht.get(self.request.matchdict.get('koht_id'))
        c.can_edit = c.can_roll = c.user.has_permission('kohad', const.BT_UPDATE, piirkond_id=c.koht.piirkond_id)
        if not c.can_edit:
            c.is_edit = False
