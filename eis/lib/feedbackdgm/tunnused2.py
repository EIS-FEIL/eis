"""Tagasisidevormi diagramm
"""
import pickle
import sqlalchemy as sa
import base64
import json
import io
import requests
from eis.lib.base import *
from eis.lib.helpers import fstr, literal
from eis.lib.block import _outer_xml

from .feedbackdgm import FeedbackDgm, go

log = logging.getLogger(__name__)
_ = i18n._

class FeedbackDgmTunnused2(FeedbackDgm):
    "Grupi tunnuste diagramm"

    def data_by_params(self, params):
        x_label = params.get('x_label')
        y_label = params.get('y_label')
        tasemed = params.get('tasemed')
        npkoodid = params.get('npkoodid')
        colors = params.get('colors')
        sex = params.get('sex')
        return x_label, y_label, tasemed, npkoodid, colors, sex

    def figure(self, x_label, y_label, tasemed, koodid, colors, sex):
        "Tunnuste diagrammi andmete kogumine, 2018"
        stat = self.stat
        test = stat.test
        testiosa = test.testiosad[0]
        fig_tasemed = [r for r in tasemed if r]
        max_tase = len(tasemed) - 1

        def g_filter(q):
            q = self.stat.g_filter(q)
            if sex:
                q = (q.join(model.Sooritaja.kasutaja)
                     .filter(model.Kasutaja.sugu==sex))
            return q
        
        q = (model.SessionR.query(model.Normipunkt)
             .filter(model.Normipunkt.testiosa_id==testiosa.id)
             .filter(model.Normipunkt.alatest_id==None)
             .order_by(model.Normipunkt.seq)
             )
        all_np = list(q.all())

        # järjestame tunnused
        order_tunnused = []
        for kood in koodid:
            for np in all_np:
                if np.kood and re.match('%s$' % kood, np.kood) and np not in order_tunnused:
                    order_tunnused.append(np)

        if not order_tunnused:
            if not all_np:
                self.handler.error(_("Testi tunnused pole piisavalt kirjeldatud"))
            else:
                self.handler.error(_("Viidatud koodidega tunnuseid testis ei ole"))
        tunnused = []

        tasemearvud = {}
        for tase_txt in tasemed:
            if tase_txt:
                tasemearvud[tase_txt] = []
            
        # tsykkel yle tunnuste (np - tunnus)
        for x, np in enumerate(order_tunnused):
            x_title = np.tran(stat.lang).nimi or np.kood
            # 2017:
            # x_title = np.kood or np.tran(stat.lang).nimi
            if x_title == 'LK_tase':
                x_title = 'LK'
            tunnused.append(x_title)

            if self.handler.c.ekk_preview_rnd:
                # juhuslik eelvaade
                arvud = {}
                maxleft = total = 20
                for value in range(max_tase+1):
                    if tasemed[value]:
                        n = random.randint(0, maxleft)
                        arvud[value] = n
                        maxleft -= n
            else:
                # tsykkel yle selle tunnuse erinevate tasemete
                qv = (model.SessionR.query(model.Npvastus.nvaartus,
                                          sa.func.count(model.Npvastus.id))
                      .filter(model.Npvastus.normipunkt_id==np.id)
                      .join((model.Sooritus, model.Sooritus.id==model.Npvastus.sooritus_id))
                      .filter(model.Sooritus.testiosa_id==testiosa.id)
                      .join(model.Sooritus.sooritaja)
                      )
                qv = g_filter(qv)
                qv = qv.group_by(model.Npvastus.nvaartus)

                total = 0
                arvud = {}
                for value, cnt in qv.all():
                    # value on tase
                    total += cnt
                    arvud[value] = cnt

            for tase_value, tase_txt in enumerate(tasemed):
                if tase_txt:
                    if arvud:
                        cnt = arvud.get(tase_value) or 0
                        protsent = int(round(cnt * 100 / total))
                    else:
                        protsent = 0
                    tasemearvud[tase_txt].append(protsent)

        data = []
        for tase_txt in tasemed:
            if tase_txt:
                yvalues = tasemearvud[tase_txt]
                ytexts = [f'{y}%' for y in yvalues]
                # hovertemplate sees on y kujul %{y:.}, mis tagab,
                # et y on arv (kui sama y esineb ka y-telje skaala tekstide seas,
                # siis võetakse sealt muidu liigne % juurde)
                data.append(go.Bar(name=tase_txt,
                                   x=tunnused,
                                   y=yvalues,
                                   text=ytexts,
                                   hovertemplate="%{x} %{y:.}%",
                                   textposition='auto'))

        fig = go.Figure(data=data)
        tickvals = [0, 20, 40, 60, 80, 100]
        if not colors:
            colors = self.default_colors
        ticktext = [f"{y}%" for y in tickvals]
        fig.update_layout(barmode='stack',
                          xaxis_title=x_label,
                          yaxis_title=y_label,
                          yaxis={'tickvals': tickvals,
                                 'ticktext': ticktext,
                                 'range': [0, 100]
                                 },
                          margin=dict(l=5, r=5, t=2, b=2),
                          colorway=colors
                          )
        return fig
