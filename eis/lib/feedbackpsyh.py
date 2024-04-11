"Koolipsühholoogi testi tulemuste tagasiside"
import plotly.graph_objects as go
import pickle
from eis.lib.base import *

class FeedbackPsyh:
    _STUDENT_TEMPLATE = '/avalik/tagasiside/profiilileht.psyh.mako'
    
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
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        is_pdf = format == 'pdf'
        header = ['Ülesanded',
                  is_pdf and 'V' or 'Valed vastused',
                  is_pdf and 'Õ' or 'Õiged vastused',
                  is_pdf and 'Summa*' or 'Summa',
                  'Protsentiil',
                  '10',
                  '25',
                  '50',
                  '75',
                  '90']

        items = []
        dgm_data = []
        testiosa = sooritus.testiosa

        q = model.Npvastus.queryR.filter_by(sooritus_id=sooritus.id)
        npvastused = {nv.normipunkt_id: nv for nv in q.all()}
        
        ind_y = 0
        prev_grupp_id = None
        for np in testiosa.normipunktid:
            grupp_id = np.alatestigrupp_id
            if grupp_id and grupp_id != prev_grupp_id:
                grupp_nimi = grupp_id and np.alatestigrupp.nimi or ''
                items.append([grupp_nimi,])
                prev_grupp_id = grupp_id
            ind_y += 1
            npitem, dgm_item = self._prepare_item(sooritus, np, ind_y, npvastused)
            items.append(npitem)
            if dgm_item:
                dgm_data.append(dgm_item)

        # dgm_data on list paaridest (label_x, value_y)
        # neist tuleb moodustada diagramm
        fig_json = self._gen_dgm(dgm_data)
        return header, items, fig_json

    def _gen_dgm(self, data):
        fig = go.Figure()
        if data:
            x_labels = [r[0] for r in data]
            values = [r[1] for r in data]
            line = go.Scatter(x=x_labels, y=values, name="Profiil")
            fig.add_trace(line)
            fig.update_layout(
                yaxis=dict(range=[0,100],
                           tickvals=list(range(0, 101, 10)),
                           ),
                margin=dict(l=5, r=5, t=2, b=2))
        return fig.to_json()
    
    def _prepare_item(self, sooritus, normipunkt, ind_y, npvastused):
        "Normipunkti andmed"
        def _nstr(value):
            if value is None:
                return ''
            else:
                return str(value)

        valede_arv = oigete_arv = ''
        alatest = atos = yv = None

        if normipunkt.on_oigedvaled:
            ty = normipunkt.testiylesanne
            if ty:
                yv = sooritus.get_ylesandevastus(ty.id) or False
                if yv:
                    valede_arv = _nstr(yv.valede_arv)
                    oigete_arv = _nstr(yv.oigete_arv)
            elif not ty:
                alatest = normipunkt.alatest
                if alatest:
                    atos = sooritus.get_alatestisooritus(alatest.id) or False
                    if atos:
                        valede_arv = _nstr(atos.valede_arv)
                        oigete_arv = _nstr(atos.oigete_arv)
                
        title = normipunkt.nimi or normipunkt.default_nimi

        d_title = '%s. %s' % (ind_y, title)

        npv = npvastused.get(normipunkt.id)
        if npv:
            value = npv.nvaartus
        else:
            value = None
                    
        s_protsent, protsent2, p_data = self._get_prots(normipunkt, value)
        dgm_item = protsent2 is not None and (d_title, protsent2) or None
        item = [d_title,
                valede_arv or '',
                oigete_arv or '',
                self.h.fstr(value) or '', # Summa (protsentiili aluseks olev väärtus)
                s_protsent, # Protsentiil
                ] + p_data
        return item, dgm_item

    def _get_prots(self, normipunkt, value):
        "Protsentiili väärtuse leidmine"
        # võrdleme kahe komakohaga
        debugbuf = '#%s:' % normipunkt.id
        CNT_P = 5 # protsentiilide arv
        p_data = [''] * CNT_P            
        s_protsent = ''
        protsent1 = protsent2 = None # protsendivahemiku algus ja lõpp
        protsentiilid = list(normipunkt.normiprotsentiilid)
        if value is not None and protsentiilid:
            value100 = round(value * 100)
            on_tapne = False
            ind_p1 = ind_p2 = None # mis veergudes kuvada X
            prev_protsent = None # eelmise protsentiili protsent
            for ind_p, r in enumerate(protsentiilid):
                debugbuf += ' %s,' % r.protsentiil
                if r.protsentiil is None:
                    continue
                protsentiil100 = round(r.protsentiil * 100)
                if protsent1 is None:
                    # vahemik pole veel alanud
                    if protsentiil100 == value100:
                        # leidsime vahemiku alguse
                        ind_p1 = ind_p2 = ind_p
                        protsent1 = protsent2 = r.protsent
                        on_tapne = True
                    elif not normipunkt.pooratud and protsentiil100 > value100 or \
                             normipunkt.pooratud and protsentiil100 < value100:
                        # leidsime vahemiku alguse, mis on yhtlasi lõpp
                        ind_p1 = ind_p2 = ind_p
                        protsent2 = r.protsent
                        if prev_protsent is not None:
                            protsent1 = prev_protsent
                        else:
                            protsent1 = protsent2
                        break
                    else:
                        # vahem ei alanud ka siin
                        pass
                else:
                    if protsentiil100 == value100:
                        # vahemik jätkub
                        ind_p2 = ind_p
                        protsent2 = r.protsent
                        on_tapne = True
                    else:
                        # vahemik sai eelmisel sammul läbi
                        break
                prev_protsent = r.protsent

            if protsent1 is None:
                # viimane protsentiil
                p_data[CNT_P-1] = 'X→'
                s_protsent = '> 90'
                protsent2 = 90
            elif ind_p1 < ind_p2:
                # on vahemik ja kuvatakse mitmes veerus
                p_data[ind_p1] = 'X─'
                for ind_p in range(ind_p1+1, ind_p2):
                    p_data[ind_p] = '─'
                p_data[ind_p2] = '─X'
                s_protsent = '%d - %d' % (protsent1, protsent2)
            elif protsent1 < protsent2:
                # on vahemik, kuid kuvatakse yhes veerus
                p_data[ind_p1] = '←X'
                s_protsent = '%d - %d' % (protsent1, protsent2)
            elif on_tapne:
                # täpne vaste
                p_data[ind_p1] = 'X'
                s_protsent = '%s' % protsent1
            else:
                # väiksem kui esimene veerg
                p_data[ind_p1] = '←X'
                s_protsent = '< %d' % protsent1

        return s_protsent, protsent2, p_data
                    
