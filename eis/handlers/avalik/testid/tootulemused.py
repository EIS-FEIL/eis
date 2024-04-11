# jagatud töö tulemused
from eis.lib.baseresource import *
from eis.lib.block import BlockController
from .avylesanded import AvylesandedController

log = logging.getLogger(__name__)

class TootulemusedController(AvylesandedController):

    _permission = 'omanimekirjad'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'avalik/testid/avtulemused.ylesanded.mako'
    _EDIT_TEMPLATE = 'avalik/testid/tootulemused.sooritaja.mako' 
    _DEFAULT_SORT = 'sooritaja.eesnimi,sooritaja.perenimi'
    _no_paginate = True
    _get_is_readonly = False
    _actions = 'index,show,edit' # võimalikud tegevused
    
    def _query_res(self):
        # kuidas tulemusi kuvada, kas pallides või protsentides?
        c = self.c
        c.res_prot = []
        c.res_ts = []
        if c.test.on_jagatudtoo:
            # leiame tagasisidega ylesanded
            q = (model.SessionR.query(model.Valitudylesanne.testiylesanne_id)
                 .join(model.Valitudylesanne.ylesanne)
                 .join(model.Valitudylesanne.testiylesanne)
                 .filter(model.Testiylesanne.testiosa_id==c.testiosa.id)
                 .filter(model.Ylesanne.on_tagasiside==True))
            c.res_ts = [ty_id for ty_id, in q.all()]

            # protsentides on vaja kuvada siis, kui jagatud töös on tagasisidega ylesanne,
            # mille tagasiside on protsentide põhjal
            q = q.filter(model.Ylesanne.on_pallid==False)
            c.res_prot = [ty_id for ty_id, in q.all()]

        # päritakse tulemuste tabel
        q = model.SessionR.query(model.Sooritus.id,
                                model.Testiylesanne.alatest_seq,
                                model.Testiylesanne.seq,
                                model.Ylesandevastus.valitudylesanne_id,
                                model.Ylesandevastus.pallid,
                                model.Ylesandevastus.max_pallid,
                                model.Testiylesanne.id)
        q = self._filter(q)
        q = (q.join((model.Ylesandevastus,
                     model.Ylesandevastus.sooritus_id==model.Sooritus.id))
             .filter(model.Ylesandevastus.kehtiv==True)
             .filter(model.Ylesandevastus.muudetav==False)
             .join((model.Testiylesanne,
                    model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id)))
        res = {}
        model.log_query(q)
        for rcd in q.all():
            sooritus_id, a_seq, ty_seq, vy_id, y_pallid, max_p, ty_id = rcd
            if sooritus_id not in res:
                res[sooritus_id] = {}
            if ty_id in c.res_prot and y_pallid is not None and max_p:
                # kuvada protsentides
                value = y_pallid * 100. / max_p
            else:
                # kuvada pallides
                value = y_pallid
            res[sooritus_id][(a_seq, ty_seq)] = value
        return res

    def _show(self, item):
        c = self.c
        q = (model.SessionR.query(model.Sooritus.id)
             .filter_by(sooritaja_id=item.id)
             .filter_by(testiruum_id=c.testiruum.id))
        for sooritus_id, in q.all():
            break
        
        Ylesandevastus2 = sa.orm.aliased(model.Ylesandevastus)
        q = (model.SessionR.query(model.Testiylesanne.seq,
                                 model.Testiylesanne.id,
                                 model.Valitudylesanne.id,
                                 model.Ylesanne.nimi,
                                 sa.func.count(Ylesandevastus2.id),
                                 model.Ylesandevastus.pallid,
                                 model.Ylesandevastus.max_pallid,
                                 model.Ylesandevastus.ajakulu,
                                 model.Ylesandevastus.id)
             .join(model.Valitudylesanne.ylesanne)
             .join(model.Valitudylesanne.testiylesanne)
             .filter(model.Testiylesanne.testiosa_id==c.testiosa.id)
             .outerjoin((model.Ylesandevastus,
                         sa.and_(model.Ylesandevastus.sooritus_id==sooritus_id,
                                 model.Ylesandevastus.valitudylesanne_id==model.Valitudylesanne.id,
                                 model.Ylesandevastus.muudetav==False,
                                 model.Ylesandevastus.kehtiv==True))
                        )
             .outerjoin((Ylesandevastus2,
                         sa.and_(Ylesandevastus2.sooritus_id==sooritus_id,
                                 Ylesandevastus2.valitudylesanne_id==model.Valitudylesanne.id,
                                 sa.or_(Ylesandevastus2.kehtiv==True,
                                         Ylesandevastus2.kehtiv==None)))
                         )
             .group_by(model.Testiylesanne.seq,
                       model.Testiylesanne.id,
                       model.Valitudylesanne.id,
                       model.Ylesanne.nimi,
                       model.Ylesandevastus.pallid,
                       model.Ylesandevastus.max_pallid,
                       model.Ylesandevastus.ajakulu,
                       model.Ylesandevastus.id)
             .order_by(model.Testiylesanne.seq)
             )
        c.ylesanded = [r for r in q.all()]
        c.sooritaja = item

        # kui ylesannet on mitu korda sooritatud, siis leiame varasemate soorituste ajaloo
        q = (model.SessionR.query(model.Ylesandevastus.valitudylesanne_id,
                                 model.Ylesandevastus.pallid,
                                 model.Ylesandevastus.max_pallid,
                                 model.Ylesandevastus.ajakulu)
             .filter(model.Ylesandevastus.sooritus_id==sooritus_id)
             .filter(model.Ylesandevastus.kehtiv==None)
             .filter(model.Ylesandevastus.pallid!=None)
             .order_by(model.Ylesandevastus.valitudylesanne_id,
                       model.Ylesandevastus.id))
        c.yvhist = {}
        c.yvaeg = {}
        for vy_id, pallid, max_pallid, ajakulu in q.all():
            if max_pallid:
                prot = '%s%%' % self.h.fstr(pallid * 100 / max_pallid, 0)
                ajakulu = self.h.str_from_time_sec(ajakulu) or ''
                if vy_id not in c.yvhist:
                    c.yvhist[vy_id] = [prot]
                    c.yvaeg[vy_id] = [ajakulu]
                else:
                    c.yvhist[vy_id].append(prot)
                    c.yvaeg[vy_id].append(ajakulu)

    def _show_ty(self, id):
        c = self.c
        msg = ''
        c.sooritaja_id = sooritaja_id = int(id)
        c.ty_id = ty_id = self.request.params.get('ty_id')
        c.lang = lang = self.params_lang()
             
        # leiame antud ylesande kõik normipunktid (tegelikult ainsa normipunkti)
        q = (model.SessionR.query(model.Normipunkt, model.Ylesanne)
             .join(model.Normipunkt.ylesanne)
             .join(model.Ylesanne.valitudylesanded)
             .filter(model.Valitudylesanne.testiylesanne_id==ty_id)
             .order_by(model.Normipunkt.seq)
             )
        c.data = []
        for np, ylesanne in q.all():
            # leiame keeled, milles on tagasiside tekstid olemas
            ql = (model.SessionR.query(model.T_Nptagasiside.lang).distinct()
                  .join(model.T_Nptagasiside.orig)
                  .join(model.Nptagasiside.normipunkt)
                  .filter(model.Normipunkt.ylesanne_id==ylesanne.id))
            ts_keeled = [l for l, in ql.all()]
            c.ts_keeled = [l for l in ylesanne.keeled if l in ts_keeled or l==ylesanne.lang]
            c.ts_pohikeel = ylesanne.lang
            
            nptagasisided = list(np.nptagasisided)
            self._set_vahemikud(np, nptagasisided)
            for nts in nptagasisided:
                q2 = (model.SessionR.query(model.Sooritaja.id, model.Sooritaja.eesnimi, model.Sooritaja.perenimi)
                      .join(model.Sooritaja.sooritused)
                      .join((model.Ylesandevastus,
                             model.Ylesandevastus.sooritus_id==model.Sooritus.id))
                      .join(model.Ylesandevastus.npvastused)
                      .filter(model.Npvastus.nptagasiside_id==nts.id)
                      .filter(model.Ylesandevastus.muudetav==False)
                      .filter(model.Ylesandevastus.kehtiv==True)
                      .filter(model.Sooritus.testiruum_id==c.testiruum_id)
                      .order_by(model.Sooritaja.eesnimi, model.Sooritaja.perenimi)
                      )
                sooritajad = [(j_id, eesnimi, perenimi) for (j_id, eesnimi, perenimi) in q2.all()]
                visible = sooritaja_id in [r[0] for r in sooritajad]
                vahemik = nts.vahemik
                msg = nts.tran(lang).op_tagasiside or nts.tran(lang).tagasiside
                c.data.append((nts.id, vahemik, msg, sooritajad, visible))

        mako = 'avalik/testid/tootulemused.sooritaja.ty.mako' 
        return self.render_to_response(mako)

    def _set_vahemikud(self, np, nptagasisided):
        "Vahemikud tekstina, kasutajale kuvamiseks"
        min_v = max_v = None
        if np.normityyp == const.NORMITYYP_PROTSENT:
            min_v = 0
            max_v = 100
        valjaarvatud = []
        for r in nptagasisided:
            value = r.tingimus_vaartus
            if value is None:
                value = r.tingimus_valik

            # antud kirje vahemik buf
            if r.tingimus_tehe == '==':
                buf = self.h.fstr(value)
            else:
                s_min_v = min_v
                s_max_v = max_v
                if r.tingimus_tehe == '<=' or r.tingimus_tehe == '<':
                    s_max_v = value
                elif r.tingimus_tehe == '>=' or r.tingimus_tehe == '>':
                    s_min_v = value
                s_min_v = self.h.fstr(s_min_v)
                s_max_v = self.h.fstr(s_max_v)
                buf = f'{s_min_v} - {s_max_v}'
                if np.normityyp == const.NORMITYYP_PROTSENT:
                    buf += '%'
                mitte = [self.h.fstr(v) for v in valjaarvatud \
                         if (min_v is None or min_v <= v) and (max_v is None or max_v >= v)]
                if mitte:
                    buf += _(" välja arvatud {s}") % (', '.join(mitte))
            r.vahemik = buf

            # järgmiste kirjete vahemiku võimalik ulatus kitseneb selle vahemiku võrra
            if r.tingimus_tehe == '<=' or r.tingimus_tehe == '<':
                if min_v is None or min_v < value:
                    min_v = value
            elif r.tingimus_tehe == '>=' or r.tingimus_tehe == '>':
                if max_v is None or max_v > value:
                    max_v = value
            elif r.tingimus_tehe == '==':
                valjaarvatud.append(value)
    
    def _get_testiruum(self, test_id):
        c = self.c
        testiruum_id = int(self.request.matchdict.get('testiruum_id'))
        if testiruum_id:
            testiruum = model.Testiruum.get(testiruum_id)
        else:
            # leiame viimasena loodud nimekirja
            q = (model.Testiruum.query
                 .join(model.Testiruum.nimekiri)
                 .filter(model.Nimekiri.test_id==test_id)
                 .filter(model.Nimekiri.testimiskord_id==None)
                 .filter(model.Nimekiri.esitaja_kasutaja_id==c.user.id)
                 .filter(model.Nimekiri.esitaja_koht_id==c.user.koht_id)
                 .order_by(model.sa.desc(model.Testiruum.id))
                 )
            testiruum = q.first()
        return testiruum

    def __before__(self):
        c = self.c
        c.test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(c.test_id)
        c.testiruum = self._get_testiruum(c.test_id)
        if c.testiruum:
            c.testiruum_id = c.testiruum.id
            c.nimekiri = c.testiruum.nimekiri
            c.testiosa = c.testiruum.testikoht.testiosa
        else:
            c.testiosa = c.test.testiosad[0]
            c.testiruum_id = 0

    def _perm_params(self):
        nimekiri = self.c.testiruum.nimekiri
        if not nimekiri:
            return False
        return {'obj':nimekiri}
