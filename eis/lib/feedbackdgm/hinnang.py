"""Tagasisidevormi diagramm
"""
import sqlalchemy as sa
import base64
import json
from eis.lib.base import *
from eis.lib.helpers import fstr, literal
from eis.lib.block import _outer_xml

from .feedbackdgm import FeedbackDgm, go, px

log = logging.getLogger(__name__)
_ = i18n._

class FeedbackDgmHinnang(FeedbackDgm):
    "Küsitluse valikvastusega küsimuse diagrammi andmete kogumine"

    def data_by_params(self, data):
        ty_kood = data.get('ty_kood')
        reverse = data.get('reverse')
        colors = data.get('colors')
        return ty_kood, reverse, colors

    def figure(self, ty_kood, reverse, colors):
        stat = self.stat
        if not ty_kood:
            return [], None
        test = stat.test
        fl = self.fl
        g_filter = stat.g_filter
        testiosa = test.testiosad[0]
        koht_id = stat.kool_koht_id
        ty_id, k_kood = fl._get_tykood_id(ty_kood)        
        
        def _get_q_stat(kysimus_id):
            "Vastuste päring statistika põhjal"
            # statistika on arvutatud ainult kogu testimiskorra kohta, mitte koolide kaupa
            # eeldame, et testimiskorra statistika on arvutatud
            # statistika põhjal saab kiiremini kui vastuste tabelist
            if koht_id or stat.klass or stat.paralleel or stat.nimekiri_id or stat.opetajad_id:
                # statistika on ainult kogu testimiskorra kohta
                return

            if stat.testimiskord_id:
                qk = model.SessionR.query(model.Kvstatistika.vastuste_arv, model.Kvstatistika.kood1)
            elif stat.testimiskorrad_id:
                qk = model.SessionR.query(sa.func.sum(model.Kvstatistika.vastuste_arv), model.Kvstatistika.kood1)
            else:
                # statistika on ainult testimiskorraga sooritamise kohta
                return

            qk = (qk.join(model.Kvstatistika.kysimusestatistika)
                  .filter(model.Kysimusestatistika.kysimus_id==kysimus_id)
                  .join(model.Kysimusestatistika.valitudylesanne)
                  )
            if len(ty_id) == 1:
                qk = qk.filter(model.Valitudylesanne.testiylesanne_id==ty_id[0])
            else:
                qk = qk.filter(model.Valitudylesanne.testiylesanne_id.in_(ty_id))
            if stat.testimiskord_id:
                qk = qk.outerjoin((model.Toimumisaeg,
                                   sa.and_(model.Kysimusestatistika.toimumisaeg_id==model.Toimumisaeg.id,
                                           model.Toimumisaeg.testimiskord_id==stat.testimiskord_id)))
            elif stat.testimiskorrad_id:
                qk = qk.outerjoin((model.Toimumisaeg,
                                   sa.and_(model.Kysimusestatistika.toimumisaeg_id==model.Toimumisaeg.id,
                                           model.Toimumisaeg.testimiskord_id.in_(stat.testimiskorrad_id))))
                qk = qk.group_by(model.Kvstatistika.kood1)
            else:
                return

            return qk

        def _get_q_kv(kysimus_id):
            "Vastuste päring otse vastuste tabelist"
            qk = (model.SessionR.query(sa.func.count(model.Kvsisu.id), model.Kvsisu.kood1)
                  .join(model.Kvsisu.kysimusevastus)
                  .filter(model.Kysimusevastus.kysimus_id==kysimus_id)
                  .join(model.Kysimusevastus.ylesandevastus)
                  .filter(model.Ylesandevastus.loplik==True)
                  .join((model.Sooritus,
                         model.Sooritus.id==model.Ylesandevastus.sooritus_id))
                  .filter(model.Sooritus.testiosa_id==testiosa.id)
                  .join(model.Sooritus.sooritaja)
                  )
            if len(ty_id) == 1:
                qk = qk.filter(model.Ylesandevastus.testiylesanne_id==ty_id[0])
            else:
                qk = qk.filter(model.Ylesandevastus.testiylesanne_id.in_(ty_id))
            qk = g_filter(qk)
            qk = qk.group_by(model.Kvsisu.kood1)
            return qk

        data = []
        x_ticks = []
        
        q = (model.SessionR.query(model.Kysimus.id).distinct()
             .filter(model.Kysimus.kood==k_kood)
             .join(model.Kysimus.sisuplokk)
             .filter(model.Sisuplokk.tyyp==const.INTER_CHOICE)
             .join((model.Valitudylesanne,
                    model.Valitudylesanne.ylesanne_id==model.Sisuplokk.ylesanne_id))
             )
        if len(ty_id) == 1:
            q = q.filter(model.Valitudylesanne.testiylesanne_id==ty_id[0])
        else:
            q = q.filter(model.Valitudylesanne.testiylesanne_id.in_(ty_id))
        x_values = []
        y_values = []
        ix_x = 0
        for kysimus_id, in q.all():
            # vastuste päring
            # kogu testimiskorra aruande jaoks kasutame statistikat
            # kooli aruande jaoks teeme otse päringu vastuste tabelist
            qk = _get_q_stat(kysimus_id) or _get_q_kv(kysimus_id)

            #t1 = datetime.now().timestamp()
            diqk = {}
            total = 0
            for kcnt, kood1 in qk.all():
                diqk[kood1] = kcnt
                total += kcnt
            #model.log_query(qk)
            #t12 = datetime.now().timestamp()
            #dt1 = t12 - t1
            #t1sum += dt1
            #log.debug('   %s - q k%s' % (dt1, kysimus_id))

            # kysimuse valikute päring
            qv = (model.SessionR.query(model.Valik.kood)
                  .filter(model.Valik.kysimus_id==kysimus_id)
                  )
            if reverse:
                qv = qv.order_by(sa.desc(model.Valik.seq))
            else:
                qv = qv.order_by(model.Valik.seq)
            qv_all = list(qv.all())

            for v_kood, in qv_all:
                # selle vastuse valinute arv
                x_label = str(ix_x+1)
                x_values.append(x_label)
                ix_x = ix_x + 1
                
                cnt = diqk.get(v_kood)
                if cnt:
                    protsent = int(round(cnt * 100. / total))
                else:
                    protsent = 0

                y_values.append(protsent)

        if not colors:
            colors = self.default_colors
        max_y = min(100, max(y_values and max(y_values) or 0, 30) + 10)
        texts = [f'{y}%' for y in y_values]
        data = [go.Bar(x=x_values, y=y_values, name='', text=texts, hovertemplate="%{y}%")]
        fig = go.Figure(data=data)
        tickvals = [0, 20, 40, 60, 80, 100]
        fig.update_layout(yaxis_title=_("Õpilaste osakaal"),
                          yaxis=dict(ticktext = [f'{y}%' for y in tickvals],
                                     tickvals = tickvals,
                                     range = [0, max_y]),
                          margin=dict(l=5, r=5, t=2, b=2),
                          colorway=colors
                          )
        return fig
