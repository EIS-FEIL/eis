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

class FeedbackDgmKlassyl(FeedbackDgm):
    "Klassi tulemuste tulpdiagramm ülesannete kaupa"

    def data_by_params(self, params):
        width = params.get('width')
        colors = params.get('colors')        
        tykoodid = params.get('tykoodid')
        return tykoodid, colors

    def figure(self, tykoodid, colors):
        stat = self.stat
        test = stat.test
        lang = stat.lang
        tk = stat.testimiskord
        if tk and not tk.ylesandetulemused_avaldet:
            # sellel diagrammil on ylesannete kaupa tulemused
            return
        
        mitu_osa = len(test.testiosad) > 1
        # ylesannete nimetused (x-telg)
        q = (model.Session.query(model.Testiylesanne.id,
                                 model.Testiosa.seq,
                                 model.Testiylesanne.tahis)
             .join(model.Testiylesanne.testiosa)
             .filter(model.Testiosa.test_id==test.id)
             .filter(model.Testiylesanne.liik==const.TY_LIIK_Y)
             .order_by(model.Testiosa.seq,
                       model.Testiylesanne.alatest_seq,
                       model.Testiylesanne.seq)
             )
        tyy_id = {}
        l_ylesanded = []
        for ind, (ty_id, osa_seq, tahis) in enumerate(q.all()):
            tykood = f'{osa_seq}_{tahis}'
            if not tykoodid or tykood in tykoodid:
                if mitu_osa:
                    tahis = f'{osa_seq}.{tahis}'
                l_ylesanded.append(tahis)
                tyy_id[ty_id] = ind
        
        # tulemused
        g_filter = stat.g_filter

        q = (model.Session.query(sa.func.avg(model.Ylesandevastus.pallid/model.Ylesandevastus.max_pallid),
                                 model.Ylesandevastus.testiylesanne_id)
             .filter(model.Ylesandevastus.max_pallid!=None)
             .filter(model.Ylesandevastus.max_pallid!=0)
             .join((model.Sooritus,
                    model.Sooritus.id==model.Ylesandevastus.sooritus_id))
             .join(model.Sooritus.sooritaja)
             )
        if tykoodid:
            # kui ei kuvata kõiki ylesandeid
            li_tyy_id = list(tyy_id.keys())
            q = q.filter(model.Ylesandevastus.testiylesanne_id.in_(li_tyy_id))

        queries = []
        # Eesti tulemused
        q1 = g_filter(q, const.FBR_RIIK)
        q1 = q1.group_by(model.Ylesandevastus.testiylesanne_id)
        queries.append((q1, _("Eesti keskmine")))
        # kooli tulemused
        q2 = g_filter(q, const.FBR_KOOL)
        q2 = q2.group_by(model.Ylesandevastus.testiylesanne_id)
        queries.append((q2, _("Kooli keskmine")))

        # grupi tulemused
        if stat.klassidID or stat.opetajad_id or stat.nimekiri_id:
            label = _("Grupi keskmine")
            q3 = g_filter(q)
            q3 = q3.group_by(model.Ylesandevastus.testiylesanne_id)
            queries.append((q3, label))

        data = []
        for q, label in queries:
            values = [0] * len(tyy_id)
            for suhe, ty_id in q.all():
                ind = tyy_id.get(ty_id)
                if ind is not None:
                    if suhe:
                        values[ind] = round(suhe * 100)
                    else:
                        values[ind] = 0

            data.append(go.Bar(x=l_ylesanded,
                               y=values,
                               name=label,
                               hovertemplate="%{y}%"))

        if not colors:
            colors = self.default_colors

        x_label = _("Ülesanne")
        y_label = _("Keskmine tulemus %")

        fig = go.Figure(data)
        fig.update_layout(xaxis_title=x_label,
                          yaxis_title=y_label,
                          yaxis=dict(range=[0,100],
                                     tickvals=list(range(0, 101, 10))
                                     ),
                          margin=dict(l=5, r=5, t=2, b=2),
                          colorway=colors
                          )
        return fig
