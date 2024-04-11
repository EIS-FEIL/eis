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

class FeedbackDgmTunnused1(FeedbackDgm):
    "Õpilase tunnuste diagramm"

    # def data(self, x_label, l_tunnused, y_label, d_tasemed, koodid, values, width=600):
    #     data_set = [('mina', list(enumerate([r or 0 for r in values])))]
    #     params = [data_set, x_label, l_tunnused, y_label, d_tasemed]
    #     return params

    def data_by_params(self, params):
        width = params.get('width')
        x_label = params.get('x_label')
        y_label = params.get('y_label')
        tasemed = params.get('tasemed')
        npkoodid = params.get('npkoodid')
        colors = params.get('colors')        
        return x_label, y_label, tasemed, npkoodid, colors

    def figure(self, x_label, y_label, tasemed, npkoodid, colors):
        test = self.stat.test
        lang = self.stat.lang
        
        # tunnuste nimetused
        l_tunnused = []
        q = (model.Session.query(model.Normipunkt)
             .join(model.Normipunkt.testiosa)
             .filter(model.Testiosa.test_id==test.id)
             )
        for kood in npkoodid:
            np = q.filter(model.Normipunkt.kood==kood).first()
            label = np and np.tran(lang).nimi or kood
            l_tunnused.append(label)

        # tunnuste väärtused
        values = []
        for kood in npkoodid:
            value = self.fl.np_val1n(kood)
            values.append(value or 0)
        max_tase = len(tasemed) - 1
        ytexts = []
        for y in values:
            if 0 <= y <= max_tase:
                # taseme nimetus
                ytexts.append(tasemed[y])
            else:
                # tasemete loetelu ei kata kõiki tasemeid
                ytexts.append(str(y))

        # määrame 0 pikkusega tulpadele väikese pikkuse, muidu plotly ei kuva tulba teksti
        y_values = [y or .01 for y in values]
        data = [go.Bar(x=l_tunnused, y=y_values, text=ytexts)]

        if not colors:
            colors = self.default_colors
        
        fig = go.Figure(data)
        fig.update_layout(xaxis_title=x_label,
                          yaxis_title=y_label,
                          yaxis=dict(range=[0,max_tase],
                                     tickvals=list(range(0, max_tase+1)),
                                     ),
                          margin=dict(l=5, r=5, t=2, b=2),
                          colorway=colors
                          )
        return fig

    def figure_ex(self, x_label, y_label, tasemed, npkoodid, l_tunnused, values):
        data = [go.Bar(x=l_tunnused, y=values)]

        fig = go.Figure(data)
        fig.update_layout(xaxis_title=x_label,
                          yaxis_title=y_label)
        return fig
    
