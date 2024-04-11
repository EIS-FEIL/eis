from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class AnalyyshindajadController(BaseResourceController):
    _permission = 'hindamisanalyys'
    _MODEL = model.Kasutaja
    _INDEX_TEMPLATE = 'ekk/hindamine/analyys.hindajad.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/analyys.hindajad_list.mako'
    _DEFAULT_SORT = 'kasutaja.nimi,hindamiskogum.tahis,testiylesanne.alatest_seq,testiylesanne.seq' # vaikimisi sortimine
    _no_paginate = True
    
    def _search_default(self, q):
        return self._search(q)

    def _search(self, q1):

        if self.c.punktides:
            self.c.punktides = int(self.c.punktides)

        # statistika hindajate ja ylesannete kaupa
        if self.c.punktides:
            f_pallid = model.Ylesandehinne.toorpunktid
            f_max = model.Ylesanne.max_pallid
        else:
            f_pallid = model.Ylesandehinne.pallid
            f_max = model.Testiylesanne.max_pallid

        q = model.SessionR.query(model.Kasutaja.nimi,
                                model.Kasutaja.id,
                                model.Hindamiskogum.tahis,
                                model.Testiylesanne.id,
                                model.Hindamiskogum.kursus_kood,
                                model.Testiylesanne.tahis,
                                model.Testiylesanne.alatest_seq,
                                model.Testiylesanne.seq,
                                f_max,
                                sa.func.count(model.Ylesandehinne.id),
                                sa.func.max(f_pallid),
                                sa.func.min(f_pallid),
                                sa.func.avg(f_pallid),
                                sa.func.stddev(f_pallid))
        q = (q.join(model.Testiylesanne.valitudylesanded)
             .join(model.Testiylesanne.hindamiskogum)
             .join((model.Ylesandevastus,
                    model.Ylesandevastus.valitudylesanne_id==model.Valitudylesanne.id))
             .join((model.Sooritus,
                    model.Sooritus.id==model.Ylesandevastus.sooritus_id))
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             .join((model.Ylesandehinne,
                    model.Ylesandehinne.ylesandevastus_id==model.Ylesandevastus.id))
             .join(model.Ylesandehinne.hindamine)
             .filter(model.Hindamine.staatus==const.H_STAATUS_HINNATUD)
             .filter(model.Hindamine.sisestus==1)
             .join(model.Hindamine.hindaja_kasutaja))
        if self.c.punktides:
            q = q.join(model.Valitudylesanne.ylesanne)
        if self.c.hindamiskogum_id:
            q = q.filter(model.Testiylesanne.hindamiskogum_id==self.c.hindamiskogum_id)

        q = q.group_by(model.Kasutaja.nimi,
                       model.Kasutaja.id,
                       model.Hindamiskogum.tahis,
                       model.Testiylesanne.id,
                       model.Hindamiskogum.kursus_kood,
                       model.Testiylesanne.tahis,
                       model.Testiylesanne.alatest_seq,
                       model.Testiylesanne.seq,
                       f_max)

        # statistika ylesannete kaupa
        q2 = model.SessionR.query(model.Testiylesanne.id,
                                 sa.func.avg(model.Ylesandehinne.pallid))
        q2 = (q2.join(model.Testiylesanne.valitudylesanded)
              .join((model.Ylesandevastus,
                    model.Ylesandevastus.valitudylesanne_id==model.Valitudylesanne.id))
              .join((model.Sooritus,
                     model.Sooritus.id==model.Ylesandevastus.sooritus_id))
              .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
              .join((model.Ylesandehinne,
                     model.Ylesandehinne.ylesandevastus_id==model.Ylesandevastus.id))
              .filter(model.Ylesandehinne.sisestus==1)
              .join(model.Ylesandehinne.hindamine)
              .filter(model.Hindamine.staatus==const.H_STAATUS_HINNATUD))

        if self.c.hindamiskogum_id:
            q2 = q2.filter(model.Testiylesanne.hindamiskogum_id==self.c.hindamiskogum_id)
           
        q2 = q2.group_by(model.Testiylesanne.id)

        self.c.total = {}
        for rcd in q2.all():
            ty_id, t_avg = rcd
            self.c.total[ty_id] = t_avg
        
        self._query_by_hk()
        if self.c.csv:
            return self._index_csv(q)
        self.c.header = self._prepare_header()
        return q

    def _query_by_hk(self):

        # statistika hindajate ja hindamiskogumite kaupa
        q = model.SessionR.query(model.Hindamine.hindaja_kasutaja_id,
                                model.Hindamiskogum.tahis,
                                model.Hindamiskogum.max_pallid,
                                model.Hindamiskogum.kursus_kood,
                                sa.func.count(model.Hindamine.id),
                                sa.func.max(model.Hindamine.pallid),
                                sa.func.min(model.Hindamine.pallid),
                                sa.func.avg(model.Hindamine.pallid),
                                sa.func.stddev(model.Hindamine.pallid))
        q = q.join(model.Hindamiskogum.hindamisolekud).\
            join(model.Hindamisolek.sooritus).\
            filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id).\
            join(model.Hindamisolek.hindamised).\
            filter(model.Hindamine.staatus==const.H_STAATUS_HINNATUD).\
            filter(model.Hindamine.sisestus==1)
        if self.c.hindamiskogum_id:
            q = q.filter(model.Hindamisolek.hindamiskogum_id==self.c.hindamiskogum_id)
        q = q.group_by(model.Hindamine.hindaja_kasutaja_id,
                       model.Hindamiskogum.tahis,
                       model.Hindamiskogum.max_pallid,
                       model.Hindamiskogum.kursus_kood)
        self.c.items_hk = {}
        for rcd in q.all():
            kasutaja_id = rcd[0]
            hk_tahis = rcd[1]
            self.c.items_hk[(kasutaja_id, hk_tahis)] = rcd


        # statistika hindamiskogumite kaupa
        q1 = model.SessionR.query(model.Hindamiskogum.tahis,
                                 sa.func.avg(model.Hindamine.pallid))
        q1 = q1.join(model.Hindamiskogum.hindamisolekud).\
            join(model.Hindamisolek.sooritus).\
            filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id).\
            join(model.Hindamisolek.hindamised).\
            filter(model.Hindamine.sisestus==1).\
            filter(model.Hindamine.staatus==const.H_STAATUS_HINNATUD)
        if self.c.hindamiskogum_id:
            q1 = q1.filter(model.Hindamisolek.hindamiskogum_id==self.c.hindamiskogum_id)
        q1 = q1.group_by(model.Hindamiskogum.tahis)

        self.c.total_hk = {}
        for rcd in q1.all():
            hk_tahis, t_avg = rcd
            self.c.total_hk[hk_tahis] = t_avg

    def _prepare_header(self):
        "Loetelu päis"
        c = self.c
        header = [(None, _("Läbiviija")),
                  (None, _("Kursus")),
                  (None, _("Kogum")),
                  (None, _("Ülesanne")),
                  (None, c.punktides and _("Suurim toorpunktide arv") or 'Suurim hindepallide arv'),
                  (None, _("Hinnatud arv")),
                  (None, _("Läbiviija vähim hinne")),
                  (None, _("Läbiviija suurim hinne")),
                  (None, _("Läbiviija keskmine hinne")),
                  (None, _("Kõikide hindajate keskmine")),
                  (None, _("Läbiviija erinevus")),
                  (None, _("Erinevuse %")),
                  (None, _("Erinevuse suund")),
                  (None, _("Hälve")),
                  ]
        if not c.on_kursused:
            header.pop(1)
        return header

    def _prepare_items(self, q):
        "Loetelu ridade andmete väljastamine (CSV jaoks)"
        c = self.c
        h = self.h
        header = self._prepare_header()
        items = []
        prev_hk = None
        prev_k_id = None
        for n, rcd in enumerate(q.all()):
            k_nimi, k_id, hkogum_tahis = rcd[:3]

            if not c.punktides:
                if k_id != prev_k_id or hkogum_tahis != prev_hk:
                    hk_item = self._prepare_hk_item(k_id, hkogum_tahis, k_nimi)
                    if hk_item:
                        items.append(hk_item)

            item = self._prepare_item(rcd, n)
            items.append(item)
            
            prev_hk = hkogum_tahis
            prev_k_id = k_id

        return header, items

    def _prepare_item(self, rcd, n):
        "Loetelu rida"
        c = self.c
        h = self.h
        k_nimi, k_id, hkogum_tahis, ty_id, kursus_kood, ty_tahis, a_seq, ty_seq, ty_max, h_count, h_min, h_max, h_avg, h_dev = rcd

        t_avg = c.total[ty_id]
        if t_avg is not None and h_avg is not None:
            erinevus = h_avg - t_avg 
            protsent = t_avg > 0 and erinevus * 100 / t_avg or 0
        else:
            erinevus = None
            protsent = None
        item = [k_nimi]
        if c.on_kursused:
            item.append(model.Klrida.get_str('KURSUS', kursus_kood, ylem_kood=c.aine_kood))
        item.append(hkogum_tahis)
        item.append(ty_tahis)

        s_erinevus = ''
        if erinevus:
            if erinevus > 0:
                s_erinevus = 'leebe'
            elif erinevus < 0:
                s_erinevus = 'range'
                
        item.extend([h.fstr(ty_max),
                     h_count,
                     h.fstr(h_max),
                     h.fstr(h_min),
                     h.fstr(h_avg),
                     h.fstr(t_avg),
                     h.fstr(erinevus),
                     h.fstr('%s%%' % (protsent or '')),
                     s_erinevus,
                     h.fstr(h_dev)])
        return item

    def _prepare_hk_item(self, kasutaja_id, hkogum_tahis, k_nimi):
        c = self.c
        h = self.h
        rcd = c.items_hk.get((kasutaja_id, hkogum_tahis))
        if rcd:
            k_id, hk_tahis, max_pallid, kursus_kood, h_count, h_max, h_min, h_avg, h_dev = rcd
            t_avg = c.total_hk[hk_tahis]
            if t_avg is not None and h_avg is not None:
                erinevus = h_avg - t_avg 
                protsent = t_avg > 0 and erinevus * 100 / t_avg or 0
            else:
                erinevus = None
                protsent = None

            s_erinevus = ''
            if erinevus:
                if erinevus > 0:
                    s_erinevus = 'leebe'
                elif erinevus < 0:
                    s_erinevus = 'range'

            item = [k_nimi]
            if c.on_kursused:
                item.append(model.Klrida.get_str('KURSUS', kursus_kood, ylem_kood=c.aine_kood))
            item.extend([hkogum_tahis,
                         h.fstr(max_pallid),
                         h_count,
                         h.fstr(h_min),
                         h.fstr(h_max),
                         h.fstr(h_avg),
                         h.fstr(t_avg),
                         h.fstr(erinevus),
                         h.fstr('%s%%' % (protsent or '')),
                         s_erinevus,
                         h.fstr(h_dev)])
            return item

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.test = self.c.toimumisaeg.testimiskord.test

    def _perm_params(self):
        return {'obj':self.c.test}
