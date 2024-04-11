from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class TestinimekirjadController(BaseResourceController):
    """(Avaliku) testi sooritajate nimekirja kuvamine
    ja sinna sooritajate lisamine
    """
    _permission = 'omanimekirjad'
    _MODEL = model.Nimekiri
    _INDEX_TEMPLATE = 'avalik/testid/nimekirjad.mako'
    _SHOW_TEMPLATE = 'avalik/testid/nimekirjad.mako' 
    _EDIT_TEMPLATE = 'avalik/testid/nimekiri.nimi.mako' 
    _DEFAULT_SORT = 'nimekiri.nimi'
    _get_is_readonly = False
    _actions = 'index,create,new,show,update,delete,edit' # võimalikud tegevused
    _DEFAULT_SORT='-nimekiri.staatus,-nimekiri.id'
    
    @property
    def _ITEM_FORM(self):
        if self.request.params.get('op') == 'nimi':
            return forms.avalik.testid.TestinimekiriNimiForm
        elif self.request.params.get('staatus'):
            return forms.NotYetImplementedForm
        else:
            return forms.avalik.testid.TestinimekiriForm            

    def index(self):
        c = self.c
        item = c.nimekiri
        if not item:
            # valime mõne selle kasutaja tehtud nimekirja
            item = self._get_nimekiri(None)

        hidden = self.request.params.get('hidden')
        if not c.testiruum_id and item:
            tr = item.testiruum1
            c.testiruum_id = tr and tr.id or 0
        return self._redirect(action='show',
                              id=item and item.id or 0,
                              testiruum_id=c.testiruum_id,
                              hidden=hidden)

    def _show_d(self):
        id = self.request.matchdict.get('id')
        if id == '0':
            # kuvame sooritajate lisamise nuppe ka siis, kui nimekirja veel pole
            self.c.item = NewItem(id=0, nimi='Nimekiri')
        else:
            self.c.item = self._MODEL.get(id)
            if not self.c.item:
                raise NotFound('Kirjet %s ei leitud' % id)        
        self._show(self.c.item)
        return self.response_dict

    def _query(self):
        c = self.c
        q = model.Nimekiri.query.filter_by(test_id=c.test_id)
        if c.test.eeltest_id:
            q = q.filter(sa.or_(model.Nimekiri.testimiskord_id==None,
                                model.Nimekiri.testimiskord.has(
                                    model.Testimiskord.tahis=='EELTEST')))
        else:
            q = q.filter(model.Nimekiri.testimiskord_id==None)
        if c.user.on_pedagoog:
            # tingimus lisatud selleks, et olla sarnane omanimekirjad.py
            q = q.filter(model.Nimekiri.esitaja_koht_id==c.user.koht_id)

        if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
            # koolipsühholoogi testi kasutaja peab olema nimekirja omanik
            q = q.filter_by(esitaja_kasutaja_id=c.user.id)
        elif c.user.koht_id and c.user.has_permission('klass', const.BT_SHOW, obj=c.user.koht):
            # muidu, kui kasutaja on pedagoog, siis võib ta kõiki oma kooli nimekirju näha, mis on pedag nähtavad
            q = (q.filter(model.sa.or_(model.Nimekiri.esitaja_kasutaja_id==c.user.id,
                                       model.sa.and_(model.Nimekiri.esitaja_koht_id==c.user.koht_id,
                                                     model.Nimekiri.pedag_nahtav==True))
                          ))
        else:
            # muidu peab olema nimekirja omanik
            q = q.filter_by(esitaja_kasutaja_id=c.user.id)

        if c.hidden != '1':
            # vaikimisi kuvame ainult mitte-peidetud nimekirjad
            c.on_peidus = q.filter(model.Nimekiri.staatus==const.B_STAATUS_KEHTETU).count()
            if c.on_peidus:
                q = q.filter(model.Nimekiri.staatus==const.B_STAATUS_KEHTIV) 
        return q

    def _get_nimekiri(self, id):
        # leiame nimekirja id järgi
        item = id and model.Nimekiri.get(id)
        if not item:
            # leiame selle kasutaja esimese nimekirja, kui on
            q = self._query()
            q = q.filter_by(esitaja_kasutaja_id=self.c.user.id)
            item = self._order(q).first()
        return item
            
    def _give_nimekiri(self, id, add=False):
        c = self.c
        item = not add and self._get_nimekiri(id)
        if not item:
            item = model.Nimekiri.lisa_nimekiri(c.user, 
                                                const.REGVIIS_KOOL_EIS,
                                                c.test)
            if c.test.testityyp == const.TESTITYYP_EKK and c.test.eeltest_id:
                # Innove tehtud eeltest, mis on määratud pedagoogidele proovimiseks
                # sooritajad pannakse testimiskorda, et saaks EKK vaates statistikat arvutada
                item.testimiskord = c.test.get_testimiskord()
            if c.test.testiliik_kood == const.TESTILIIK_TKY:
                # taustakysitluse õpetaja osa suunata õpetajale
                kasutaja = c.user.get_kasutaja()
                model.Sooritaja.reg_tky_opetaja(kasutaja, c.test, item)

        return item

    def new(self):
        # uue objekti väljad
        item_args = self.request.params.mixed()
        item_args.update(self._get_parents_from_routes())
        q = self._query()
        nimi = nimi_pref = 'Nimekiri'
        for cnt in range(2, 101):
            if q.filter(model.Nimekiri.nimi==nimi).count() == 0:
                break
            nimi = '%s %d' % (nimi_pref, cnt)
        item_args['nimi'] = nimi
        item_args['alates'] = date.today()
        item_args['pedag_nahtav'] = True
        self.c.item = self._MODEL.init(**item_args)

        # lülitame autoflushi välja, et ID ei genereeritaks
        model.Session.autoflush = False
        self.c.item.post_create()
        self._edit(self.c.item)
        return self.render_to_response(self._EDIT_TEMPLATE)
        
    def _create(self, **kw):
        c = self.c
        item = self._give_nimekiri(None, True)
        self._update(item)
        c.testiruum_id = '0'
        c.testiruum = None
        # testi koostajale saadetakse teade uue nimekirja loomisest
        send_nimekirjateade(self, item, c.test)
        return item
    
    def _edit(self, item):
        c = self.c
        c.hidden = item.staatus == const.B_STAATUS_KEHTETU and '1' or self.request.params.get('hidden')
        q = self._order(self._query())
        c.items = list(q.all())
        if not c.testiruum or c.testiruum.nimekiri != item:
            c.testiruum = item.testiruum1
            c.testiruum_id = c.testiruum and c.testiruum.id or '0'

    def _edit_nimi(self, id):
        self.c.item = self._give_nimekiri(id)
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _update(self, item):
        c = self.c
        data = self.form.data
        staatus = data.get('staatus')
        if staatus:
            self._update_staatus(item, staatus)
        elif data.get('op') == 'nimi':
            item.nimi = data['f_nimi']
            if data['f_alates']:
                item.alates = data['f_alates']
            elif not item.alates:
                item.alates = date.today()

            item.tulemus_nahtav = data['n_tulemus_nahtav']
            c.testiruum = self._give_testiruum(item)
            c.testiruum.aja_jargi_alustatav = data['r_aja_jargi_alustatav']
            c.testiruum.algusaja_kontroll = data['r_algusaja_kontroll']
            
            algus = None
            on_kutse = c.test.testiliik_kood == const.TESTILIIK_KUTSE and \
                       c.test.avaldamistase == const.AVALIK_MAARATUD
            if on_kutse:
                # toimumise kuupäev ja alustamise kellaaegade vahemik
                item.kuni = item.alates
                item.pedag_nahtav = True
                item.alatestitulemus_nahtav = data['n_alatestitulemus_nahtav']
                item.vastus_peidus = not data['n_vastus_nahtav']
                c.testiruum.on_arvuti_reg = data['r_on_arvuti_reg']
                if not c.user.koht_id:
                    raise ValidationError(self, _("Kutseeksami korraldaja peab olema seotud soorituskohaga"))
                if item.esitaja_koht_id != c.user.koht_id:
                    raise ValidationError(self, _("Nimekiri kuulub teise kooli juurde"))
            else:
                # alguse ja lõpu kuupäevad
                item.kuni = data['f_kuni']
                algus = item.alates == item.kuni and item.alates or None
                item.alatestitulemus_nahtav = item.tulemus_nahtav

                if c.test.avalik_kuni and item.kuni and item.kuni > c.test.avalik_kuni:
                    err = _("Lahendamise viimane võimalik kuupäev on {kpv}").format(kpv=self.h.str_from_date(c.test.avalik_kuni))
                    raise ValidationError(self, errors={'f_kuni': err})

            # alguskell esimesel kuupäeval
            kell = data['r_kell']
            if kell:
                algus = datetime.combine(item.alates, time(kell[0], kell[1]))
            else:
                # kell 00.00 tähendab, et kellaaeg on määramata
                algus = datetime.combine(item.alates, time(0,0))
                if c.testiruum.algusaja_kontroll:
                    raise ValidationError(self,
                                          errors={'r_kell': _("Väärtus puudub")})
                
            # alustamise ajavahemiku lõpp esimesel kuupäeval
            lopp = data['r_lopp']
            if c.testiruum.aja_jargi_alustatav:
                if not kell:
                    raise ValidationError(self,
                                          errors={'r_kell': _("Väärtus puudub")})
                if not lopp:
                    raise ValidationError(self,
                                          errors={'r_lopp': _("Väärtus puudub")})
                if lopp < kell:
                    raise ValidationError(self,
                                          errors={'r_lopp': _("Vahemiku algus ei saa olla peale lõppu")})
                c.testiruum.alustamise_lopp = datetime.combine(item.alates, time(lopp[0], lopp[1]))
            else:
                c.testiruum.alustamise_lopp = None

            # lõpetamise kell viimasel kuupäeval
            t_lopp = data['t_lopp']
            if t_lopp:
                if not item.kuni:
                    item.kuni = item.alates
                c.testiruum.lopp = datetime.combine(item.kuni, time(t_lopp[0], t_lopp[1]))
                if c.testiruum.lopp < algus:
                    raise ValidationError(self,
                                          errors={'t_lopp': _("Vahemiku algus ei saa olla peale lõppu")})
            else:
                c.testiruum.lopp = None                

            # ruumi alguse ja sooritajate alguse muutmine, kui vaja
            if c.testiruum.algus != algus:
                c.testiruum.muuda_algus(algus)

            item.staatus = not data.get('notstaatus') and const.B_STAATUS_KEHTIV or const.B_STAATUS_KEHTETU
        else:
            # pedag_nahtav linnukese muutmine ajaxiga, ei ole kutseeksam
            item.pedag_nahtav = data['f_pedag_nahtav']
            model.Session.commit()
            return Response(json_body={'rc':'ok'})

    def _give_testiruum(self, item):
        koht_id = self.c.user.koht_id
        for osa in reversed(self.c.test.testiosad):
            testikoht = model.Testikoht.give_testikoht(koht_id, osa.id, None)
            testiruum = item.give_avalik_testiruum(testikoht)
        return testiruum
        
    def _error_update(self):
        extra_info = self._edit_d()
        if isinstance(extra_info, (HTTPFound, Response)):
            return extra_info
        if self.request.params.get('op') == 'nimi':
            mako = self._EDIT_TEMPLATE
        elif self.request.params.get('staatus'):
            mako = self._SHOW_TEMPLATE
        else:
            return Response(json_body={'error':'Tekkis viga'})
        html = self.form.render(mako, extra_info=extra_info)            
        return Response(html)

    def delete(self):
        """Nimekirja kustutamine.
        """
        id = self.request.matchdict.get('id')
        item = model.Nimekiri.get(id)
        if not item:
            return self._redirect('index')

        if not self.c.user.has_permission('avtugi', const.BT_DELETE):
            # ainult Harno tugi võib kustutada tehtud sooritusi
            q = (model.Sooritaja.query
                .filter_by(nimekiri_id=item.id)
                .filter(model.Sooritaja.staatus.in_((const.S_STAATUS_POOLELI,
                                                    const.S_STAATUS_KATKESTATUD,
                                                    const.S_STAATUS_KATKESPROT,
                                                    const.S_STAATUS_TEHTUD)))
                )
            if q.count() > 0:
                self.error(_('Nimekirja ei saa kustutada, sest sooritamist on juba alustatud'))
                return self._redirect('show',  id=item.id)

        q = (model.Session.query(model.Kysimusestatistika)
             .filter_by(nimekiri_id=item.id))
        for kst in q.all():
            kst.delete()
        q = (model.Session.query(model.Arvutusprotsess)
             .filter_by(nimekiri_id=item.id))
        for kst in q.all():
            kst.delete()

        item.delete()
        model.Session.commit()
        self.success(_('Nimekiri on kustutatud!'))
        return self._redirect('index', testiruum_id=0)

    def _update_staatus(self, item, staatus):
        """Muudame sooritajate olekut - lubame kohe alustada testi sooritamist.
        See on vajalik siis, kui on niisugune test, mida pole vaja klassiruumis teha.
        """
        if staatus and int(staatus) == const.S_STAATUS_ALUSTAMATA:
            # anname loa kohe alustada
            cnt = 0
            for rcd in item.sooritajad:
                rc = False
                if rcd.staatus == const.S_STAATUS_REGATUD:
                    rcd.staatus = const.S_STAATUS_ALUSTAMATA
                    rc = True
                for rcd2 in rcd.sooritused:
                    if rcd2.staatus == const.S_STAATUS_REGATUD:
                        rcd2.staatus = const.S_STAATUS_ALUSTAMATA
                        rc = True
                if rc:
                    cnt += 1

            model.Session.flush()
            if cnt:
                self.success(_('{d} sooritaja olek muudetud').format(d=cnt))
            else:
                self.success(_('Loa ootel sooritajaid ei olnud'))

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            self.success()
            return self._redirect('show', id, testiruum_id=self.c.testiruum_id)
        else:
            return self._redirect('edit', id, testiruum_id=self.c.testiruum_id)

    def __before__(self):
        c = self.c
        c.test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(c.test_id)
        c.nimekiri_id = self.request.matchdict.get('id')
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        if c.nimekiri_id:
            c.nimekiri = model.Nimekiri.get(c.nimekiri_id)
            if c.nimekiri:
                c.testiruum = c.nimekiri and c.nimekiri.testiruum1
                c.testiruum_id = c.testiruum and c.testiruum.id
        elif c.testiruum_id:
            c.testiruum = model.Testiruum.get(c.testiruum_id)
            if c.testiruum:
                c.nimekiri = c.testiruum.nimekiri
                c.nimekiri_id = c.testiruum.nimekiri_id
        if not c.testiruum_id:
            if c.testiruum_id and c.testiruum_id != '0':
                c.testiruum = model.Testiruum.get(c.testiruum_id)
                if not c.nimekiri:
                    c.nimekiri = c.testiruum.nimekiri
                    c.nimekiri_id = c.nimekiri and c.nimekiri.id
            else:
                c.testiruum_id = '0'
            
    def _perm_params(self):
        # testi vaatamise õigus, et igaüks saaks oma teste suunata
        # õppealajuhatajatel peab olema neile suunata lubatud testidele see õigus
        c = self.c
        if not c.test:
            return False
        if c.nimekiri:
            if c.nimekiri.test_id and c.nimekiri.test_id != c.test.id:
                return False
            if c.testiruum and c.testiruum.nimekiri != c.nimekiri:
                return False
        return {'obj': c.testiruum or c.nimekiri or c.test}

def send_nimekirjateade(handler, nimekiri, test):
    """Uue nimekirja loomisel saadetakse testi koostajale kiri,
    kui on kutseeksam ja määratud korraldajatele
    """
    if test.testiliik_kood == const.TESTILIIK_KUTSE and \
      test.avaldamistase == const.AVALIK_MAARATUD:
        # leiame koostajad
        today = date.today()
        q = (model.Session.query(model.Kasutaja.id,
                                 model.Kasutaja.nimi,
                                 model.Kasutaja.epost)
             .join(model.Testiisik.kasutaja)
             .filter(model.Testiisik.test_id==test.id)
             .filter(model.Testiisik.kasutajagrupp_id==const.GRUPP_T_KOOSTAJA)
             .filter(model.Testiisik.kehtib_alates<=today)
             .filter(model.Testiisik.kehtib_kuni>=today)
             .filter(model.Kasutaja.epost!=None)
             .filter(model.Kasutaja.epost!='')
             )
        kasutajad = list(q.all())
        li_epost = [r[2] for r in kasutajad]
        if len(li_epost):
            # koostame teate
            user = handler.c.user
            isik_nimi = user.fullname
            koht = user.koht
            koht_nimi = koht and koht.nimi
            data = {'isik_nimi': isik_nimi,
                    'koht_nimi': koht_nimi,
                    'test_id': test.id,
                    'test_nimi': test.nimi,
                    }
            subject, body = handler.render_mail('mail/nimekiri.koostajale.mako', data)
            body = Mailer.replace_newline(body)
            if not Mailer(handler).send(li_epost, subject, body):
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                for k_id, nimi, epost in kasutajad:
                    model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
                model.Session.commit()
