from cgi import FieldStorage

from eis.lib.baseresource import *
from eis.handlers.avalik.protokollid.osalejad import OsalejadController
_ = i18n._
log = logging.getLogger(__name__)

class ProtokollilosalejadController(OsalejadController):
    """Testi toimumise protokolli sisestamine
    """
    _permission = 'sisestamine'
    _INDEX_TEMPLATE = 'ekk/sisestamine/protokoll.osalejad.mako'
    _no_paginate = True
    
    def _create(self):
        res = OsalejadController._create(self)
        # kui EKK salvestab protokolli, siis loetakse protokoll kohe kinnitatuks
        # aga see ei takista EKKil endal pärast muudatusi tegemast
        tprot = self.c.toimumisprotokoll
        if self.request.params.get('kinnitatud'):
            model.Session.commit()
            err = self._osalemine_margitud()
            if err:
                self.error(err)
            elif tprot.staatus not in (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD): 
                tprot.staatus = const.B_STAATUS_KINNITATUD
        else:
            tprot.staatus = const.B_STAATUS_KEHTIV
        return res

    def _osalemine_margitud(self):
        """Kas kõigi osaliste osaline on märgitud?
        Kui pole, siis ei tohi saada protokolli kinnitada.
        """
        prot_tulemusega = self.c.testimiskord.prot_tulemusega
        testiruum_id = self.c.testiruum and self.c.testiruum.id or None
        testikohad_id = not testiruum_id and [tk.id for tk in self.c.testikohad] or None

        q = (model.SessionR.query(sa.func.count(model.Sooritus.id))
             .filter(model.Sooritus.staatus.in_((const.S_STAATUS_REGATUD,
                                                 const.S_STAATUS_ALUSTAMATA,
                                                 const.S_STAATUS_POOLELI)))
             )
        if testiruum_id:
            q = q.filter(model.Sooritus.testiruum_id==testiruum_id)
        else:
            q = q.filter(model.Sooritus.testikoht_id.in_(testikohad_id))
        if q.scalar() > 0:
            model.log_query(q)
            return _("Protokolli ei saa kinnitada, kuna kõigi osalejate olekud pole märgitud")
        
        if prot_tulemusega:
            q = (model.SessionR.query(sa.func.count(model.Sooritus.id))
                 .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                 .filter(model.Sooritus.pallid==None))
            if testiruum_id:
                q = q.filter(model.Sooritus.testiruum_id==testiruum_id)
            else:
                q = q.filter(model.Sooritus.testikoht_id.in_(testikohad_id))
            if q.scalar() > 0:
                return _("Protokolli ei saa kinnitada, kuna kõigi osalejate tulemused pole sisestatud")

        else:
            lvgrupid_id = (const.GRUPP_T_ADMIN,
                           const.GRUPP_VAATLEJA,
                           const.GRUPP_HINDAJA_S,
                           const.GRUPP_HINDAJA_S2,
                           const.GRUPP_INTERVJUU,
                           const.GRUPP_HIND_INT,
                           const.GRUPP_KOMISJON,
                           const.GRUPP_KOMISJON_ESIMEES,
                           const.GRUPP_KONSULTANT)
            q = (model.SessionR.query(sa.func.count(model.Labiviija.id))
                 .filter(model.Labiviija.staatus==const.L_STAATUS_MAARATUD)
                 .filter(model.Labiviija.kasutajagrupp_id.in_(lvgrupid_id)))
            if testiruum_id:
                q = q.filter(model.Labiviija.testiruum_id==testiruum_id)
            else:
                q = q.filter(model.Labiviija.testikoht_id.in_(testikohad_id))
            if q.scalar() > 0:
                return _("Protokolli ei saa kinnitada, kuna kõigi läbiviijate olekud pole märgitud")
   
    def __before__(self):
        toimumisprotokoll_id = self.request.matchdict.get('toimumisprotokoll_id')
        self.voib_koik_ruumid = True
        self.c.toimumisprotokoll = model.Toimumisprotokoll.get(toimumisprotokoll_id)
        self.c.testimiskord = self.c.toimumisprotokoll.testimiskord
        self.c.testikohad = list(self.c.toimumisprotokoll.testikohad)
        self.c.testikoht = self.c.toimumisprotokoll.testikoht
        self.c.testiruum = self.c.toimumisprotokoll.testiruum
        for testikoht in self.c.testikohad:
            toimumisaeg = testikoht.toimumisaeg
            if not toimumisaeg.on_kogused:
                self.error(_("Toimumisaja {s} kogused on eksamikeskuses veel arvutamata").format(s=toimumisaeg.tahised))
                self.c.is_edit = False
            if not toimumisaeg.on_hindamisprotokollid:
                self.error(_("Toimumisaja hindamiskirjed on eksamikeskuses veel loomata"))
                self.c.is_edit = False            
        if self.c.is_edit and self.c.app_ekk:
            self.c.can_edit = True
        
    def _perm_params(self):
        # kirjutame yle baasklassi meetodi
        pass

    def _has_permission(self):
        for testikoht in self.c.testikohad:
            if not testikoht.toimumisaeg.on_hindamisprotokollid and self._is_modify():
                return False
        return BaseController._has_permission(self)
