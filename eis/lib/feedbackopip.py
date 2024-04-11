"Õpipädevustesti profiililehe genereerimine"
import pickle
from eis.lib.base import *

class FeedbackOpip:
    _STUDENT_TEMPLATE = '/avalik/tagasiside/profiilileht.opip.mako'
    
    def __init__(self, handler):
        self.handler = handler
        self.h = handler.h
        self.request = handler.request

    def gen_opilane(self, sooritaja):
        "Õpilase tagasiside genereerimine"
        template = self._STUDENT_TEMPLATE
        c = self.handler.c
        c.sooritaja = sooritaja
        c.prepare_sooritus = self.prepare_sooritus
        c.pickle_dumps = lambda data: pickle.dumps(data, 0).hex()
        data = self.handler.render(template)
        return data

    def prepare_sooritus(self, sooritus, format=None):
        "Loetelu ridade andmete väljastamine (CSV,PDF jaoks)"
        is_pdf = format == 'pdf'
        header = ['',
                  'Min-max',
                  'Tulemus',
                  'Madal',
                  'Keskmine',
                  'Kõrge',
                  ]
            
        items = []
        dgm_data = []
        testiosa = sooritus.testiosa

        q = model.Npvastus.queryR.filter_by(sooritus_id=sooritus.id)
        npvastused = {nv.normipunkt_id: nv for nv in q.all()}

        sooritaja = self.handler.c.sooritaja or sooritus.sooritaja
        lang = sooritaja.lang
        ind_y = 0
        # grupiga normipunktid ja grupid ilma normipunktideta
        for atg in testiosa.alatestigrupid:
            items.append([atg.tran(lang).nimi or '',])
            for np in atg.normipunktid:
                if np.on_opilane and (not np.lang or np.lang == lang):
                    ind_y += 1
                    npitem = self._prepare_item(sooritus, np, ind_y, npvastused, lang, format)
                    items.append(npitem)
        # grupita normipunktid
        for np in testiosa.normipunktid:
            if not np.alatestigrupp_id:
                if np.on_opilane and (not np.lang or np.lang == lang):
                    ind_y += 1
                    npitem = self._prepare_item(sooritus, np, ind_y, npvastused, lang, format)
                    items.append(npitem)
            
        return header, items, dgm_data

    def _prepare_item(self, sooritus, normipunkt, ind_y, npvastused, lang, format):
        def _nstr(value):
            if value is None:
                return ''
            else:
                return str(value)

        title = normipunkt.tran(lang).nimi or normipunkt.default_nimi        
        #d_title = '%s. %s' % (ind_y, title)
        d_title = title.replace('\n', '<br/>')
        
        debugbuf = '#%s:' % normipunkt.id
        npv = npvastused.get(normipunkt.id)
        if npv:
            value = npv.get_value()
            svalue = npv.get_str_value()
        else:
            value = svalue = None

        min_max = normipunkt.min_max or ''

        item = [d_title,
                min_max,
                svalue or '',
                ]
        p_data = self._get_sooritusryhm(normipunkt, value)
        if p_data:
            item.extend(p_data)

        if not format or format == 'pdf':
            # iga rea viimaseks elemendiks normipunkt, et sellest võtta kujunduse andmed
            item.append(normipunkt)
        return item

    def _get_sooritusryhm(self, normipunkt, value):
        "Sooritusrühma leidmine"
        # võrdleme kahe komakohaga
        debugbuf = '%s#%s(value=%s):' % (normipunkt.nimi, normipunkt.id, value)
        sryhmad = [r for r in normipunkt.sooritusryhmad if r.ryhm in \
                   (model.Normiprotsentiil.OPIP_KESK, model.Normiprotsentiil.OPIP_KORGE)]
        CNT_P = 3 # rühmade arv
        p_data = None
        if value is not None and sryhmad:
            try:
                try:
                    value100 = round(value * 100)
                except TypeError:
                    value100 = round(float(value) * 100)
            except Exception as e:
                log.error('value=%s' % value)
                log.error(e)
                return
                    
            on_tapne = False
            ind_p1 = ind_p2 = 0 # mis veergudes kuvada X, vaikimisi alumine ryhm
            prev_lavi100 = round((normipunkt.min_vaartus or 0)*100) # eelmise protsentiili väärtus
            for ind_p, r in enumerate(sryhmad):
                debugbuf += ' %d) %s,' % (ind_p, r.lavi)
                if r.lavi is None:
                    continue
                lavi100 = round(r.lavi * 100)
                if lavi100 <= value100:
                    # vahemik jätkub
                    ind_p2 = ind_p + 1
                    debugbuf += ' jatkub p2=%s' % ind_p2
                    # kas vahemik algas?
                    if lavi100 > prev_lavi100:
                        ind_p1 = ind_p + 1
                        debugbuf += ' algas p1=%s' % ind_p1
                    prev_lavi100 = lavi100
                    debugbuf += ' prev=%s' % lavi100
                else:
                    # vahemik on läbi:
                    break
            p_data = [''] * CNT_P            
            for ind in range(ind_p1, ind_p2+1):
                p_data[ind] = 'X'
        return p_data
    
