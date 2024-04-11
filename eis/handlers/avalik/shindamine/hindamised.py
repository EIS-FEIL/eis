# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._
from eis.lib.resultentry import ResultEntry

log = logging.getLogger(__name__)

class HindamisedController(BaseResourceController):
    """Suuliste vastajate hindamine"""

    _permission = 'shindamine'
    #_MODEL = model.Hindamine
    _INDEX_TEMPLATE = 'avalik/shindamine/hindamised.mako' 
    _EDIT_TEMPLATE = 'avalik/shindamine/hindamised.mako'     
    _DEFAULT_SORT = 'kasutaja.nimi'
    _ITEM_FORM = forms.avalik.hindamine.SHindamisedForm
    _is_small_header = True
    _get_is_readonly = False
    
    def _query(self):
        c = self.c

        if self.request.method == 'POST':
            # create vigade korral
            c.sooritused_id = []
            for key in self.request.params.mixed():
                if re.match(r'^hmine-\d+\.sooritus_id$', key):
                    value = self.request.params.get(key)
                    c.sooritused_id.append(value)
        else:
            c.sooritused_id = list(map(int, self.request.params.getall('sooritus_id')))

        # leiame teised sooritajad, kellega koos on heli salvestatud
        Helivastus2 = model.sa.orm.aliased(model.Helivastus)
        sq = (model.Session.query(Helivastus2.sooritus_id)
              .filter(~ Helivastus2.sooritus_id.in_(c.sooritused_id))
              .join((model.Helivastus, model.Helivastus.helivastusfail_id==Helivastus2.helivastusfail_id))
              .filter(model.Helivastus.sooritus_id.in_(c.sooritused_id))
              )
        qt = (model.Session.query(model.Sooritus)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritus.id.in_(sq))
             )
        c.teised_helifailis = list(qt.all())

        # leiame hinnatavad tööd
        q = (model.Sooritus.query
             .join(model.Sooritus.sooritaja)
             .join(model.Sooritaja.kasutaja)
             .filter(model.Sooritus.id.in_(c.sooritused_id))
             )
        if c.testiruum:
            q = q.filter(model.Sooritus.testiruum_id==c.testiruum.id)
        c.hindamiskogum_opt = [(k.id, k.tahis) \
                               for k in c.testiosa.hindamiskogumid \
                               if k.staatus]
        hkogum_id = self.request.params.get('hindamiskogum_id')
        if not hkogum_id:
            # hindamiskogum pole valitud
            if len(c.hindamiskogum_opt):
                # on olemas kasutaja loodud hindamiskogumeid, 
                # võtame neist esimese
                hkogum_id = c.hindamiskogum_opt[0][0]
            else:
                # ei ole olemas kasutaja loodud hindamiskogumeid,
                # kasutame vaikimisi hindamiskogumit
                kv = c.testiosa.get_komplektivalik()
                hkogum = kv.get_default_hindamiskogum()
                #hkogum = c.testiosa.get_default_hindamiskogum()
                hkogum_id = hkogum.id

        if hkogum_id:
            c.hindamiskogum = model.Hindamiskogum.get(hkogum_id)
            c.hindamiskogum_id = c.hindamiskogum.id
            is_add = False
            for tos in q.all():
                holek = tos.give_hindamisolek(c.hindamiskogum)
                is_add |= not holek.id
            if is_add:
                if not c.app_ekk:
                    model.Session.commit()
        
        if c.hindamiskogum:
            self._detect_komplekt(q, c.hindamiskogum)

        return q

    def _detect_komplekt(self, q, hindamiskogum):
        c = self.c
        ta = c.toimumisaeg
        kvalik = hindamiskogum.get_komplektivalik()
        c.opt_komplektid = kvalik.get_opt_komplektid(c.toimumisaeg)
        if len(c.opt_komplektid) == 1:
            # saab olla ainult üks komplekt
            c.komplekt_id = c.opt_komplektid[0][0]
            c.komplekt = model.Komplekt.get(c.komplekt_id)
        else:
            c.komplekt_id = self.request.params.get('komplekt_id')
            if c.komplekt_id:
                # komplekt on juba kasutaja poolt valitud
                c.komplekt = model.Komplekt.get(c.komplekt_id)
                c.komplekt_id = c.komplekt.id
            else:
                # kui hindamine on juba pooleli, 
                # siis saame komplekti esimese pooleli soorituse kirjest
                for tos in q.all():
                    holek = tos.give_hindamisolek(hindamiskogum)
                    if holek.komplekt_id:
                        c.komplekt = holek.komplekt
                        c.komplekt_id = holek.komplekt_id
                        break

        if c.komplekt_id:
            li = []
            for tos in q.all():
                holek = tos.give_hindamisolek(hindamiskogum)
                if holek.komplekt_id and holek.komplekt_id != c.komplekt_id:
                   li.append(tos.tahis)
            if len(li):
                buf = _("Sooritajatele {s} on juba määratud teine komplekt! ").format(s=', '.join(li))
                buf += _("Jätkamise korral tuleb seni sisestatud hindamised asendada.") 
                self.error(buf)
            
        return q

    def _index_d(self):
        self.c.items = self._query().all()
        return self.response_dict

    def _url_back(self):
        "Tagasi tööde valikusse"
        c = self.c
        if c.testiruum:
            # ruumiga seotud hindaja
            url = self.url('shindamine_vastajad', testiruum_id=c.testiruum.id)
        else:
            # EKK määratud SH hindaja, kes pole seotud ruumiga
            lv = c.labiviija
            url = self.url('khindamine_vastajad', toimumisaeg_id=lv.toimumisaeg_id, hindaja_id=lv.id)
        return url
    
    def _index_start(self):
        """Hindamise alustamine
        """
        # Kasutaja alustab valitud testisoorituste hindamist.
        c = self.c
        # kasutaja poolt märgitud soorituste id
        uued = set(map(int, self.request.params.getall('sooritus_id')))
        if len(uued) == 0:
            self.error(_("Palun vali vastajad"))
            return HTTPFound(location=self._url_back())
        
        q = (model.Session.query(model.Sooritus)
             .filter(model.Sooritus.id.in_(uued)))
        if c.testiruum:
            q = q.filter_by(testiruum_id=c.testiruum.id)

        for tos in q.all():
            sooritus_id = tos.id
            if c.eksam_kaib:
                # kui eksam käib ja kedagi hinnatakse, siis võib järeldada, 
                # et sellel on parajasti vastamine pooleli
                if not tos.algus:
                    tos.algus = datetime.now()

            # kui olen hindaja, siis tekitatakse hindamise kirjed
            for holek in tos.hindamisolekud:
                hindamine = holek.give_hindamine(c.labiviija.liik)
                if not c.eksam_kaib and hindamine.staatus == const.H_STAATUS_HINNATUD:
                    # kui eksam on juba läbi, siis kinnitatud hindamisi uuesti
                    # hinnata enam ei saa
                    self.error(_("Soorituse {s} hindamine on juba kinnitatud").format(s=tos.tahis))
                    return HTTPFound(location=self._url_back())
                hindamine.labiviija = c.labiviija
                hindamine.hindaja_kasutaja_id = c.user.id
                hindamine.staatus = const.H_STAATUS_POOLELI
        model.Session.commit()

        d = self._index_d()
        if isinstance(d, dict):
            # kui ei tagastatud valmis vastust, siis vormistatakse vastus
            return self._showlist()
        else:
            # tagastatakse vastus
            return d

    def _download(self, id, format=None):
        """Laadi helifail alla"""
        c = self.c
        item = model.Helivastusfail.get(id)
        if not item:
            raise NotFound('Kirjet %s ei leitud' % id)        
        q = (model.Session.query(model.Helivastus.id)
             .filter_by(helivastusfail_id=item.id)
             .join(model.Helivastus.sooritus)
             )
        if not q.count():
            raise NotFound('Puudub ligipääsuõigus')

        mimetype = item.mimetype
        if not mimetype:
            (mimetype, encoding) = mimetypes.guess_type(item.filename)
            
        return utils.download(item.filedata, item.filename, mimetype)

    def _error_create(self):
        html = self.form.render(self._INDEX_TEMPLATE,
                                extra_info=self._index_d())            
        return Response(html)

    def _create(self):
        """Komplekti määramine või hinnete salvestamine
        """
        c = self.c
        sooritused_id = [hmine['sooritus_id'] for hmine in self.form.data['hmine']] # list
        komplekt = model.Komplekt.get(self.form.data['komplekt_id'])
        hindamiskogum_id = self.form.data['hindamiskogum_id']
        hindamiskogum = model.Hindamiskogum.get(hindamiskogum_id)
        intervjuu_labiviija_id = self.form.data['intervjuu_labiviija_id']
        labiviija = c.labiviija
        sisestus = 1
        resultentry = ResultEntry(self, const.SISESTUSVIIS_PALLID, c.testiosa.test, c.testiosa)
        
        # kas hindamine lõpetada
        lopeta = self.request.params.get('lopeta') and True or False
        for n, rcd in enumerate(self.form.data['hmine']):
            tos = model.Sooritus.get(rcd['sooritus_id'])
            sooritaja = tos.sooritaja

            holek = tos.give_hindamisolek(hindamiskogum)
            hindamine = holek.give_hindamine(labiviija.liik)

            hindamine.hindaja_kasutaja_id = labiviija.kasutaja_id
            hindamine.labiviija_id = labiviija.id
            hindamine.intervjuu_labiviija_id = intervjuu_labiviija_id

            sk = ExamSaga(self).give_soorituskomplekt(tos.id, komplekt.komplektivalik_id)
            resultentry._save_komplekt(hindamine, komplekt, sk, holek, tos)
            resultentry.save_hindamine(sooritaja, rcd, lopeta, 'hmine-%d' % n, tos, holek, c.testiosa, hindamine, None, False)

            self._set_sooritus_staatus(tos, lopeta)

        if resultentry.errors:
            raise ValidationError(self, resultentry.errors)

        model.Session.flush()
        labiviija.calc_toode_arv()

        model.Session.commit()
        self.success()

        # salvestamiseks vajutati kas nupule "lopeta" või "salvesta"
        if lopeta:
            # kõigi vastajate loetellu
            return HTTPFound(location=self._url_back())

        if self.request.params.get('hindakoos'):
            # kasutaja valis teisi sooritajaid ja klikkis nupule "Hindan koos"
            # lisame sooritajaid, kellega koos hinnata
            for s_id in self.request.params.getall('sooritus_id'):
                sooritused_id.append(s_id)
                
        # samale lehele tagasi
        return HTTPFound(location=self.url_current('index', hindaja_id=c.labiviija.id, hindamiskogum_id=hindamiskogum_id, sooritus_id=sooritused_id))

    def _set_sooritus_staatus(self, tos, lopeta):
        c = self.c
        # kui soorituse kõik hindamisolekud on hinnatud,
        # siis on hinne olemas, muidu on hindamisprobleem

        #on_vastamata = False # kas vastamine pole veel lõppenud
        on_hindeta = False # kas lõplik hinne panemata
        pallid = 0
        for hkogum in c.testiosa.hindamiskogumid:
            if hkogum.staatus == const.B_STAATUS_KEHTIV:
                holek = tos.give_hindamisolek(hkogum)
                pallid += holek.pallid or 0
                #log.debug('holek.%s.pallid=%s' % (holek.id, holek.pallid))
                #log.debug('holek.staatus=%s' % holek.staatus)

                if holek.staatus != const.H_STAATUS_HINNATUD:
                    on_hindeta = True
                    #for hindamine in holek.hindamised:
                    #    if hindamine.staatus != const.H_STAATUS_HINNATUD:
                    #        on_vastamata = True
                    #        break
                    
        if on_hindeta:
            tos.pallid = None
        else:
            tos.pallid = pallid

        if c.eksam_kaib:
            if lopeta:
                tos.staatus = const.S_STAATUS_TEHTUD
                tos.lopp = datetime.now()
            elif tos.staatus < const.S_STAATUS_POOLELI:
                tos.staatus = const.S_STAATUS_POOLELI

    def __before__(self):
        c = self.c
        c.labiviija = model.Labiviija.get(self.request.matchdict.get('hindaja_id'))
        if not c.labiviija:
            return
        c.toimumisaeg = c.labiviija.toimumisaeg
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testiosa.test
        
        c.eksam_kaib = False
        if c.labiviija.testiruum_id:
            # kooli määratud hindaja on seotud ruumiga
            c.testiruum = c.labiviija.testiruum # EKK määratud hindajal ruum puudub
            c.testikoht = c.testiruum and c.testiruum.testikoht
            for tpakett in c.testiruum.testikoht.testipaketid:
                toimumisprotokoll = tpakett.toimumisprotokoll
                if not toimumisprotokoll or toimumisprotokoll.staatus == const.B_STAATUS_KEHTIV:
                    c.eksam_kaib = True
                    break

    def _has_permission(self):
        return self.c.labiviija and self.c.labiviija.kasutaja_id == self.c.user.id
