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

from .feedbackdgm import FeedbackDgm, go, px

log = logging.getLogger(__name__)
_ = i18n._

class FeedbackDgmBarnp(FeedbackDgm):

    def data_by_params(self, data):
        width = data.get('width')
        height = data.get('height')
        np_kood = data.get('np_kood')
        colors = data.get('colors')
        colornivs = data.get('colornivs')
        if not colornivs and colors:
            # teisendame vanemast formaadist
            colornivs = [r[0] for r in colors]
            colors = [r[1] for r in colors]
        return np_kood, colors, colornivs, width, height

    def figure(self, np_kood, colors, colornivs, width, height):
        # np_kood - tagasiside tunnuse kood, mille väärtust kuvatakse
        # colorlist - list tupledest (x, värv), kus on x on arv,
        #      millest suurema väärtuse korral kasutatakse antud värvi
        value = self.fl.np_val1f(np_kood)

        if value is None:
            value = 0

        # leiame värvi
        for i, color in enumerate(colors):
            if len(colornivs) > i:
                min_val = colornivs[i]
            else:
                min_val = None
            if min_val is None or value > min_val:
                break

        y_values = [round(value),]
        x_values = ['m',]
        data = [go.Bar(x=y_values, y=x_values, orientation='h')]
        fig = go.Figure(data=data)
        fig.update_layout(
            yaxis=dict(
                showgrid=False,
                showline=False,
                showticklabels=False,
                ),
            xaxis=dict(
                zeroline=False,
                showline=False,
                showticklabels=False,
                showgrid=False,
                range=[0,100],
                ),
            margin=dict(l=2, r=2, t=2, b=2),
            hovermode='y',
            width=width,
            height=height,
            font_size=12,
            )
        fig.update_traces(marker_color=color)
        annotations = []

        # Adding labels
        for yd, xd in zip(y_values, x_values):
            if value < 70:
                # arv tuleb bari järele
                annotations.append(dict(xref='x', yref='y',
                                        y=xd, x=80,#x=yd + 3,
                                        text=str(round(yd)) + '%',
                                        font=dict(color='black'),
                                        showarrow=False))
            else:
                # arv tuleb bari peale
                annotations.append(dict(xref='x', yref='y',
                                        y=xd, x=30,
                                        text=str(round(yd)) + '%',
                                        font=dict(color='white'),
                                        showarrow=False))
                
        fig.update_layout(annotations=annotations)
        return fig
