# -*- coding: utf-8 -*- 
from smtplib import SMTPRecipientsRefused
import requests
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import ehis

log = logging.getLogger(__name__)

class KohadController(BaseResourceController):
    _permission = 'kasutajad'
    _MODEL = model.Koht
    _SEARCH_FORM = forms.admin.KohadForm
    _ITEM_FORM = forms.admin.KohtForm
    _INDEX_TEMPLATE = 'admin/kohad.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = 'admin/koht.mako' # muutmisvormi mall
    _LIST_TEMPLATE = '/admin/kohad_list.mako'
    _DEFAULT_SORT = 'nimi'

    def _query(self):
        # leiame kasutajale lubatud piirkondade loetelu
        lubatud = self.c.user.get_kasutaja().get_piirkonnad_id('kasutajad', const.BT_SHOW)
        if None not in lubatud:
            self.c.piirkond_filtered = lubatud
        else:
            self.c.piirkond_filtered = None

        return model.Koht.query.\
            outerjoin(model.Koht.aadress)
    
    def _search_default(self, q):
        return None 

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.kool_id:
            q = q.filter(model.Koht.kool_id==self.c.kool_id)
        if self.c.nimi:
            q = q.filter(model.Koht.koolinimed.any(\
                    model.Koolinimi.nimi.ilike(self.c.nimi)))
        if self.c.koolityyp:
            q = q.filter(model.Koht.koolityyp_kood==self.c.koolityyp)
        if self.c.maakond_kood:
            tase, kood = self.c.maakond_kood.split('.')
            q = q.filter(model.Aadress.kood1==kood)
        if self.c.piirkond:
            prk = model.Piirkond.get(self.c.piirkond)
            if prk is not None:
                li = prk.get_alamad_id()
                if len(li) == 1:
                    q = q.filter(model.Koht.piirkond_id==li[0])
                else:
                    q = q.filter(model.Koht.piirkond_id.in_(li))

        # kas pole õigust kõigi piirkondade korraldamiseks?
        if self.c.piirkond_filtered:
            # piirkondlik korraldaja ei või kõiki piirkondi vaadata, 
            q = q.filter(model.Koht.piirkond_id.in_(self.c.piirkond_filtered))

        return q

    def _index_ehis(self):
        # kui EHISest uuendamise POST päring lõppeb veaga ja kasutaja vajutab ise URLil reavahetust
        # suuname tavalisse indexisse
        return HTTPFound(location=self.url('admin_kohad'))

    def _create_ehis(self):
        """Õppeasutuste andmete küsimine EHISest
        """
        # klassifikaatorite sisu uuendamine:
        # http://enda.ehis.ee/avaandmed/rest/klassifikaatorid/LISAOPE/1/JSON
        
        # koolide andmed X-tee kaudu
        if from_ehis_xtee(self):
            # kontaktandmed avaandmetest
            from_ehis_opendata(self)
        return HTTPFound(location=self.url('admin_kohad'))

    def _create_ehisjson(self):
        """Õppeasutuste andmete küsimine EHISest, ainult avaandmed (debug)
        """
        from_ehis_opendata(self)
        return HTTPFound(location=self.url('admin_kohad'))

    def _new_mail(self):
        self.c.to_list = []
        self.c.miss_list = []
        kohad_id = self.request.params.getall('koht_id')
        for koht_id in kohad_id:
            k = model.Koht.get(koht_id)
            to = k.epost
            if to:
                self.c.to_list.append(to)
            else:
                self.c.miss_list.append(k.nimi)

        if not self.c.to_list:
            self.error(_("Pole e-posti aadresse"))
        if self.c.miss_list:
            self.error(_("Pole e-posti aadresse") + ': ' + ', '.join(self.c.miss_list))

        data = {'user_nimi': self.c.user.fullname,
                }
        self.c.subject, self.c.body = self.render_mail('mail/soorituskohtadele.mako', data)
        return self.render_to_response('admin/kohad.mail.mako')

    def _create_mail(self):
        self.form = Form(self.request, schema=forms.admin.KohadMailForm)
        if not self.form.validate():
            html = self.form.render('admin/kohad.mail.mako',
                                    extra_info=self.response_dict)            
            return Response(html)
        to = self.form.data['to']
        subject = self.form.data['subject']
        body = self.form.data['body']
        body = Mailer.replace_newline(body)
        if not Mailer(self).send(to, subject, body):
            self.success(_("Teade on saadetud"))
            log.debug('Message sent to: %s' % to)
        return HTTPFound(location=self.url('admin_kohad'))

    def _update(self, item, lang=None):
        # omistame vormilt saadud andmed
        old_piirkond_id = item.piirkond_id
        oli_plangikoht = item.on_plangikoht
        item.from_form(self.form.data, self._PREFIX, lang=lang)
        item.on_soorituskoht = self.form.data['on_soorituskoht']
        item.on_plangikoht = bool(item.on_soorituskoht or item.valitsus_tasekood)
        #item.on_kysitluskoht = self.form.data['on_kysitluskoht']
        if item.on_soorituskoht or item.on_plangikoht:
            item.staatus = const.B_STAATUS_KEHTIV
        else:
            item.staatus = const.B_STAATUS_KEHTETU
        model.Aadress.adr_from_form(item, self.form.data, 'a_')
        item.haldusoigus = bool(self.form.data.get('haldusoigus'))
        item.allikas = model.Kohalogi.ALLIKAS_EKK
        if not item.id:
            model.Session.flush()
        item.set_name()

        # kui piirkond muutus, siis lisame ka seotud isikutele uue piirkonna
        if item.piirkond_id and item.piirkond_id != old_piirkond_id:
            prk = model.Piirkond.get(item.piirkond_id)
            for kk in item.kasutajakohad:
                model.Kasutajapiirkond.give(kk.kasutaja, prk)

        if oli_plangikoht and not item.on_plangikoht:
            send_kaotatud_plangikoha_teade(self, [item.nimi])
                
    def _edit(self, item):
        pass

    def _perm_params(self):
        if self.c.item:
            return {'piirkond_id':self.c.item.piirkond_id}

    def __before__(self):
        koht_id = self.request.matchdict.get('id')
        if koht_id:
            self.c.item = model.Koht.get(koht_id)
            piirkond_id = self.c.item.piirkond_id
        else:
            piirkond_id = None
        self.c.can_edit = self.c.user.has_permission('kohad', const.BT_UPDATE, piirkond_id=piirkond_id)

def _save_grid(collection, MODEL, items, f_del=None):
    if not items:
        # kui andmeid ei tulnud, siis ei muuda midagi
        return
    for r in list(collection):
        equal = None
        for item in items:
            equal = item
            for key in list(item.keys()):
                if item.get(key) != r.__getattr__(key):
                    equal = None
                    break
            if equal is not None:
                break
        if equal is not None:
            # on olemas
            items.remove(equal)
        else:
            # enam ei ole
            if f_del:
                f_del(r)
            else:
                r.delete()
    for item in items:
        # uued
        r = MODEL(**item)
        collection.append(r)

def send_kaotatud_plangikoha_teade(handler, kaotatud_plangikohad):
    q = (model.Session.query(model.Kasutaja.id, model.Kasutaja.epost, model.Kasutaja.nimi)
         .distinct()
         .filter(model.Kasutaja.epost!=None)
         .filter(model.Kasutaja.epost!='')
         .filter(model.Kasutaja.kasutajarollid.any(
             sa.and_(model.Kasutajaroll.kasutajagrupp_id==const.GRUPP_PLANK,
                     model.Kasutajaroll.kehtib_alates<=datetime.now(),
                     model.Kasutajaroll.kehtib_kuni>=datetime.now())))
         )
    kasutajad = [(k_id, epost, nimi) for (k_id, epost, nimi) in q.all()]
    to = [r[1] for r in kasutajad]
    if to:
        data = {'kohad': kaotatud_plangikohad,
                }
        mako = 'mail/kaotatud.plangikohad.mako'
        subject, body = handler.render_mail(mako, data)
        body = Mailer.replace_newline(body)
        if not Mailer(handler).send(to, subject, body):
            log.info('Saadetud kaotatud plangikohtade teade aadressile %s' % (','.join(to)))
            kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                              sisu=body,
                              teema=subject,
                              teatekanal=const.TEATEKANAL_EPOST)
            for k_id, epost, nimi in kasutajad:
                model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
            model.Session.commit()
            return True
        else:
            return False
        
def from_ehis_opendata(handler):
    # http://enda.ehis.ee/avaandmed/rest/oppeasutused/{REG_NR}/{NIMETUS}/{EHIS_ID}/{OPPEKEEL}/{OMANDIVORM}/{OPPEVORM}/
    #             {OPPEASUTUS_LIIK}/{OMANIK}/{ASUKOHT}/{VORM}/{VANA_NIMETUS}/{SULETUD_OPPEASUTUS}/{VORMING}    
    url = 'http://enda.ehis.ee/avaandmed/rest/oppeasutused/-/-/-/-/-/-/-/-/-/-/1/1/JSON'
    http_proxy = handler.request.registry.settings.get('http_proxy')
    data = None
    try:
        if http_proxy:
            resp = requests.get(url=url, proxies={'http': http_proxy})
        else:
            resp = requests.get(url=url)
        content = resp.content.decode('utf-8')
        log_label = f'GET {url}'
        handler.log_add(const.LOG_USER, content, log_label)
        data = resp.json()
        oppeasutused = data['body']['oppeasutused']['oppeasutus']
    except Exception as ex:
        error = 'EHISe avaandmete päring ei tööta'
        handler.error(error)
        handler._error(ex, error)
        return None
    else:
        log.info('Avaandmed %d kooli kohta' % len(oppeasutused))
        cnt = 0
        for rcd in oppeasutused:
            kool_id = rcd['koolId']
            koht = model.Koht.query.filter_by(kool_id=kool_id).first()
            if not koht:
                continue
            cnt += 1
            koht.allikas = model.Kohalogi.ALLIKAS_EHIS
            adr = rcd.get('juriidilineAadress')
            if adr:
                adr_id = adr.get('adrId')
                if adr_id and model.Aadress.get(adr_id):
                    koht.aadress_id = adr_id
            kontakt = rcd.get('kontaktAndmed')
            if kontakt:
                telefon = kontakt.get('telefon')
                if telefon:
                    koht.telefon = telefon
                epost = kontakt.get('epost')
                if epost:
                    koht.epost = epost
        model.Session.commit()
        handler.notice('Uuendatud %d kooli kontaktandmed' % cnt)
                    
def from_ehis_xtee(handler):
    kaotatud_plangikohad = list()
    reg = ehis.Ehis(handler=handler)
    error, oppeasutused = reg.oppeasutused()
    if not error:
        dt = datetime.now()
        cnt_new = 0
        cnt_update = 0
        cnt_remove = 0

        kl_koolityyp = model.Klassifikaator.getR('KOOLITYYP')
        koolityybid = {}
        for klrida in kl_koolityyp.read:
            koolityybid[klrida.kood] = klrida
        tundmatud_koolityybid = dict()
        for item in oppeasutused:
            kool_id = int(item.koolId)
            koht = model.Koht.query.filter_by(kool_id=kool_id).first()
            if koht is None:
                cnt_new += 1
                koht = model.Koht(kool_id=kool_id)
            else:
                cnt_update += 1
            koht.allikas = model.Kohalogi.ALLIKAS_EHIS
            if item.registrikood:
                regnr = str(item.registrikood).strip()
                if len(regnr) > 8:
                    error = 'EHISe andmetes on vigane registrikood %s' % regnr
                    break
                koht.kool_regnr = regnr
            koht.nimi = item.kooliNimi
            # kui kooliliiki pole EISi klassifikaatoris, siis lisatakse
            koolityyp_kood = item.kooliLiik
            if koolityyp_kood:
                if koolityyp_kood not in koolityybid:
                    if koolityyp_kood not in tundmatud_koolityybid:
                        tundmatud_koolityybid[koolityyp_kood] = 0
                    tundmatud_koolityybid[koolityyp_kood] += 1
                else:
                    koht.koolityyp_kood = koolityyp_kood

            kooli_alamliik = item.kooliAlamliik 
            if kooli_alamliik:
                koht.alamliik_kood = kooli_alamliik

            omandivorm = item.omandivorm
            if omandivorm:
                koht.omandivorm_kood = omandivorm

            klassi_kompl_arv = int(item.klassiKomplArv) if item.klassiKomplArv else None
            if klassi_kompl_arv is not None:
                koht.klassi_kompl_arv = klassi_kompl_arv

            opilased_arv = int(item.opilasedArv) if item.opilasedArv else None
            if opilased_arv is not None:
                koht.opilased_arv = opilased_arv

            keeled = []
            li = item.find('oppekeeled/oppekeel')
            if li:
                for r in li:
                    keeled.append(dict(oppekeel=str(r)))
            _save_grid(koht.oppekeeled, model.Oppekeel, keeled)

            tasemed = []
            li = item.find('oppetasemed/oppetase')
            if li:
                for r in li:
                    value = str(r)
                    if value in (const.E_OPPETASE_YLD,
                                 const.E_OPPETASE_GYMN,
                                 const.E_OPPETASE_ERIVAJADUS,
                                 const.E_OPPETASE_ERIKASVATUS):
                        # yldhariduse korral on väljundis õppetase
                        oppetase_kood = const.OPPETASE_YLD
                    elif value == const.E_OPPETASE_KUTSE or value[0] in '234':
                        # kutsehariduse korral peab olema õppekava (numbritega)
                        oppetase_kood = const.OPPETASE_KUTSE
                    elif value == const.E_OPPETASE_KORG or value[0] in '567':
                        # kõrghariduse korral peab olema õppekava (numbritega)
                        oppetase_kood = const.OPPETASE_KORG
                    else:
                        # alusharidus, huviharidus
                        oppetase_kood = None
                    tasemed.append(dict(oppetase_kood=oppetase_kood, kavatase_kood=value))
            f_del = lambda r: r.on_ehisest and r.delete()
            _save_grid(koht.koolioppekavad, model.Koolioppekava, tasemed, f_del)

            if len(tasemed) > 2:
                log.info('%s/alam %s/omand %s/kompl %s/opil %s/keeled %s/tasemed %s' % (koht.nimi, kooli_alamliik, omandivorm, klassi_kompl_arv, opilased_arv, keeled, tasemed))

            koht.ehis_seisuga = dt
            koht.set_name()
            koht.on_soorituskoht = koht.on_plangikoht = True
            koht.staatus = const.B_STAATUS_KEHTIV
            
        if not error:
            model.Session.flush()
            for koht in model.Koht.query.\
                    filter(model.Koht.kool_id != None).\
                    filter(model.Koht.ehis_seisuga < dt).all():
                cnt_remove += 1
                koht.allikas = model.Kohalogi.ALLIKAS_EHIS
                koht.staatus = const.B_STAATUS_KEHTETU
                if koht.on_plangikoht:
                    kaotatud_plangikohad.append(koht.nimi)
                koht.on_soorituskoht = koht.on_plangikoht = False

            model.Session.commit()
            txt = _("Andmed on salvestatud (lisatud {n1}, muudetud {n2}, kehtetuks seatud {n3})").format(
                n1=cnt_new, n2=cnt_update, n3=cnt_remove)
            handler.notice(txt)
            buf = ', '.join(['%s - %s tk' % (tyyp, cnt) for tyyp, cnt in tundmatud_koolityybid.items()])
            if buf:
                handler.error(_("Leidub koolitüüpe, mida EISi klassifikaatoris pole: ") + buf)

    if kaotatud_plangikohad:
        send_kaotatud_plangikoha_teade(handler, kaotatud_plangikohad)
    if error:
        handler.error(error)
        return False
    return True
