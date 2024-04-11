"""Tagasisidevormi diagramm
"""
import pickle
import sqlalchemy as sa
import base64
import json
import io
from eis.lib.base import *
from eis.lib.helpers import fstr, literal
from eis.lib.block import _outer_xml

from .feedbackdgm import FeedbackDgm, px, go

log = logging.getLogger(__name__)
_ = i18n._

class FeedbackDgmTunnused3(FeedbackDgm):
    "Klasside tasemete tunnuste diagramm"

    def data_by_params(self, data):
        tasemed = data.get('tasemed')
        np_kood = data.get('np_kood')
        colors = data.get('colors')
        return tasemed, np_kood, colors

    def figure(self, tasemed, np_kood, colors):
        "Tunnuste diagrammi andmete kogumine, 2021"
        stat = self.stat
        test = stat.test
        testiosa = test.testiosad[0]
        g_filter = stat.g_filter
        data = []
        max_tase = len(tasemed) - 1
        # joonisel on need tasemed, millel on nimetus
        fig_tasemed = [r for r in tasemed if r]
        totals = {}
        
        # leiame tunnuse ID
        q = (model.SessionR.query(model.Normipunkt)
             .filter(model.Normipunkt.testiosa_id==testiosa.id)
             .filter(model.Normipunkt.alatest_id==None)
             #.filter(model.Normipunkt.max_vaartus!=None)
             .filter(model.Normipunkt.kood==np_kood)
             .order_by(model.Normipunkt.seq)
             )
        np = q.first()

        if np and self.handler.c.ekk_preview_rnd:
            # juhuslik eelvaade
            klassid = ('8a','8b','8c')
            for key in klassid:
                cnts = []
                totals[key] = {}
                for n_tase in range(max_tase + 1):
                    totals[key][n_tase] = random.randint(0, 30)
        elif np:
            # leiame klassid ja iga klassi sooritajate koguarvu
            q = model.SessionR.query(model.Sooritaja.klass,
                                    model.Sooritaja.paralleel,
                                    model.Npvastus.nvaartus,
                                    sa.func.count(model.Sooritaja.id))
            q = g_filter(q)
            q = (q.join(model.Sooritaja.sooritused)
                 .join((model.Npvastus,
                        model.Npvastus.sooritus_id==model.Sooritus.id))
                 .filter(model.Npvastus.normipunkt_id==np.id)
                 .group_by(model.Sooritaja.klass,
                           model.Sooritaja.paralleel,
                           model.Npvastus.nvaartus)
                 )
            for klass, paralleel, value, cnt in q.all():
                key = f"{klass or ''}{paralleel or ''}"
                if key not in totals:
                    totals[key] = {}
                totals[key][value] = cnt

        klassid = list(totals.keys())
        klassid.sort()
        max_y = 0
        for key in klassid:
            cnts = []
            cntspr = []
            kl_totals = totals[key]
            kl_total = sum(kl_totals.values())
            for n_tase in range(max_tase + 1):
                if tasemed[n_tase]:
                    # kui on taseme tekst, siis ka tulp
                    cnt = kl_totals.get(n_tase) or 0
                    prot = round(cnt * 100 / kl_total)
                    # y=0 asemel kuvame y=.01, muidu plotly ei kuva tulba teksti
                    cnts.append(prot or .01)
                    cntspr.append(f'{prot}% ({cnt})')
            name = len(klassid) > 1 and key or ''
            data.append(go.Bar(name=name,
                               x=fig_tasemed,
                               y=cnts,
                               text=cntspr,
                               textposition='auto',
                               hovertemplate="%{x} %{y}"))
            max_y = max(max_y, max(cnts))
        log.debug(data)


        if not colors:
            colors = self.default_colors

        max_y = min(100, max(max_y, 30)+10)
        fig = go.Figure(data=data)
        tickvals = [0, 20, 40, 60, 80, 100]
        fig.update_layout(barmode='group',
                          yaxis={'tickvals': tickvals,
                                 'ticktext': [f"{y}%" for y in tickvals],
                                 'range': [0, max_y]
                                 },
                          margin=dict(l=5, r=5, t=2, b=2),
                          colorway=colors
                          )
        #colorway=px.colors.qualitative.Antique
        return fig
