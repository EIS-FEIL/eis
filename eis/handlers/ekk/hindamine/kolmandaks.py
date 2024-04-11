import random
from eis.lib.baseresource import *
from eis.lib.resultentry import ResultEntry
_ = i18n._

log = logging.getLogger(__name__)

class KolmandaksController(BaseResourceController):
    "Valitakse osa I hindamise läbinud töödest ja märgitakse III hindamist vajavaks (ilma II hindamiseta)"
    _permission = 'hindajamaaramine'
    _INDEX_TEMPLATE = 'ekk/hindamine/maaramine.kolmandaks.mako'
    _EDIT_TEMPLATE = 'ekk/hindamine/maaramine.kolmandaks.mako'    
    _ITEM_FORM = forms.ekk.hindamine.KolmandaksForm
    
    def new(self, format='html'):
        self._new_d()
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _new_d(self):
        c = self.c
        params = self.request.params
        c.hindamiskogum_id = params.get('hindamiskogum_id')
        if c.hindamiskogum_id:
            c.hindamiskogum = model.Hindamiskogum.get(self.c.hindamiskogum_id)
        c.lang = self.params_lang()
        c.piirkond_id = params.get('piirkond_id')
        return self.response_dict

    def _create(self):
        c = self.c
        protsent = self.form.data['protsent']
        hindamiskogum_id = self.form.data['hindamiskogum_id']
        lang = self.form.data['lang']
        piirkond_id = self.form.data['piirkond_id']

        valimist = self.form.data.get('valim')
        if valimist == '1':
            valimist = True
        elif valimist == '0':
            valimist = False
        else:
            valimist = None
        
        class Hindajatood(object):
            "Ühe hindaja tööde arvud"
            def __init__(self, cnt):
                self.cnt1 = cnt # I hinnatud 
                self.cnt3 = 0 # III hindamisel
                self.juurde = 0 # juurde määrata III hindamisele

            @property
            def vana_protsent(self):
                return self.cnt3 * 100. / self.cnt1

            @property
            def uus_protsent(self):
                return (self.cnt3 + self.juurde) * 100. / self.cnt1

        def _filter(q):
            qf = (q.join(model.Hindamisolek.sooritus)
                  .filter_by(toimumisaeg_id=self.c.toimumisaeg_id)
                  .filter_by(staatus=const.S_STAATUS_TEHTUD)
                  .join(model.Hindamisolek.hindamised)
                  .filter(model.Hindamine.sisestus==1)
                  .filter(model.Hindamine.liik==const.HINDAJA1)
                  .filter(model.Hindamine.staatus==const.H_STAATUS_HINNATUD)
                  .filter(model.Hindamisolek.hindamistase > const.HTASE_ARVUTI)
                  )
            if hindamiskogum_id:
                qf = qf.filter(model.Hindamisolek.hindamiskogum_id==hindamiskogum_id)
            if lang or (valimist is not None):
                qf = qf.join(model.Sooritus.sooritaja)
                if lang:
                    qf = qf.filter(model.Sooritaja.lang==lang)
                if valimist is not None:
                    qf = qf.filter(model.Sooritaja.valimis==valimist)
            if piirkond_id:
                qf = (qf.join(model.Sooritus.testikoht)
                      .join(model.Testikoht.koht)
                      .filter(model.Koht.piirkond_id==piirkond_id))
            return qf

        q1 = model.Session.query(model.Hindamine.labiviija_id,
                                 model.sa.func.count(model.Hindamisolek.id))
        q1 = _filter(q1)
        
        # leiame esimese hindamise arvu hindajate kaupa
        htood = dict()
        total1 = 0
        for lv_id, cnt in q1.group_by(model.Hindamine.labiviija_id).all():
            htood[lv_id] = Hindajatood(cnt)
            total1 += cnt
        log.debug('total1=%d' % total1)

        # leiame seni kolmanda hindamiseni jõudnud tööde arvu I hindaja kaupa
        # ja jagame uue kolmandat hindamist vajavate tööde arvu
        # võimalikult võrdselt I hindajate vahel
        total3 = 0
        q3 = q1.filter(model.Hindamisolek.hindamistase >= const.HINDAJA3)
        juurde = 0
        for lv_id, cnt in q3.group_by(model.Hindamine.labiviija_id).all():
            ht = htood[lv_id]
            # senine kolmanda hindamise tööde arv
            ht.cnt3 = cnt
            total3 += cnt
            # juurde määratavate kolmanda hindamise tööde arv
            log.debug('lv_id=%d I=%d III=%d juurde=%0.1f' % \
                      (lv_id, ht.cnt1, ht.cnt3, ht.cnt1*protsent/100.-ht.cnt3))
            ht.juurde = max(0, round(ht.cnt1 * protsent / 100. - ht.cnt3))
            juurde += ht.juurde
            
        # uue protsendi järgi vajalik kolmanda hindamiseni jõudnud tööde arv
        uus_total3 = round(total1 * protsent / 100.)
        log.debug('total3=%d, uus=%d, juurde=%d' % (total3, uus_total3, juurde))
        if uus_total3 <= total3:
            # kui soovitud protsent pole suurem senisest protsendist,
            # siis ei ole midagi määrata kolmandale hindamisele
            cnt = 0
        else:
            # parandame määratavate tööde arvu
            ymardusviga = uus_total3 - total3 - juurde
            while ymardusviga > 0:
                sorted_htood = sorted(list(htood.values()), key=lambda ht: ht.uus_protsent)
                for ht in sorted_htood:
                    # ht on madalaima protsendiga läbiviija
                    if ht.cnt1 > ht.cnt3 + ht.juurde:
                        # kui saab juurde määrata, siis määrame
                        ht.juurde += 1
                        ymardusviga -= 1
                        break
            while ymardusviga < 0:
                sorted_htood = sorted(list(htood.values()), key=lambda ht: 0 - ht.uus_protsent)
                for ht in sorted_htood:
                    # ht on kõrgeima protsendiga läbiviija
                    if ymardusviga < 0 and ht.juurde > 0:
                        # kui on midagi määratud, siis võtame ära
                        ht.juurde -= 1
                        ymardusviga += 1
                        break

            cnt = self._suuna(htood, _filter)
            model.Session.commit()
            
        self.success(_("Kolmandat hindamist vajavaks märgiti {n} tööd").format(n=cnt))
        return HTTPFound(location=self.url('hindamine_hindajad3',
                                           toimumisaeg_id=c.toimumisaeg_id,
                                           hindamiskogum_id=hindamiskogum_id,
                                           lang=lang,
                                           piirkond_id=piirkond_id))

    def _suuna(self, htood, _filter):
        ta = model.Toimumisaeg.get(self.c.toimumisaeg_id)
        testiosa = ta.testiosa
        test = testiosa.test
        resultentry = ResultEntry(self, None, test, testiosa)
        cnt = 0
        for lv_id in htood:
            ht = htood[lv_id]

            log.debug('lv_id=%d I=%d, sh III=%d (%.02f%%), juurde %d (%.02f%%)' % \
                      (lv_id, ht.cnt1, ht.cnt3, ht.vana_protsent, ht.juurde, ht.uus_protsent))
            
            if ht.juurde:
                # leiame selle läbiviija tööd,
                # mida pole veel III hindamisele suunatud
                q1 = model.Session.query(model.Hindamisolek.id)
                q1 = _filter(q1)
                q1 = q1.filter(model.Hindamisolek.hindamistase < const.HINDAJA3)
                tood_id = [ho_id for ho_id, in q1.all()]
                while ht.juurde > 0:
                    # leiame juhuslikult yhe töö 
                    total = len(tood_id)
                    ind = int(random.random() * total)
                    ho_id = tood_id.pop(ind)
                    ho = model.Hindamisolek.get(ho_id)
                    if ho.hindamistase < const.HINDAJA3:
                        # määrame töö kolmandale hindamisele
                        sooritus = ho.sooritus
                        sooritaja = sooritus.sooritaja
                        ho.hindamistase = ho.min_hindamistase = const.HINDAJA3
                        ho.hindamisprobleem = const.H_PROBLEEM_SISESTAMATA
                        ho.selgitus = None
                        ho.staatus = const.H_STAATUS_POOLELI
                        sooritus.hindamine_staatus = const.H_STAATUS_POOLELI
                        sooritaja.hindamine_staatus = const.H_STAATUS_POOLELI
                        #resultentry.update_sooritus(sooritaja, sooritus)
                        ht.juurde -= 1
                        cnt += 1
        return cnt

    def __before__(self):
        self.c.toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(self.c.toimumisaeg_id)
        self.c.test = self.c.toimumisaeg.testiosa.test
        self.c.testimiskord = self.c.toimumisaeg.testimiskord
        
    def _perm_params(self):
        return {'obj': self.c.test}
        
