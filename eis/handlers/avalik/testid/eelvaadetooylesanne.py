# # -*- coding: utf-8 -*- 

# from eis.lib.baseresource import *
# _ = i18n._
# from eis.handlers.avalik.sooritamine import tooylesanne
# log = logging.getLogger(__name__)

# class EelvaadetooylesanneController(tooylesanne.TooylesanneController):
#     """Ühe ülesande lahendamine jagatud töös
#     """
#     _EDIT_TEMPLATE = 'avalik/testid/eelvaade.tooylesanne.mako'
#     _permission = 'ekk-testid'
#     _log_params_post = False
#     _log_params_get = False
    
#     def _get_index_url(self):
#         c = self.c
#         return self.url('test_komplekt_eelvaade', test_id=c.test.id, testiruum_id=c.testiruum_id, id=c.sooritus_id, komplekt_id=0)

#     def _get_algus(self, sooritus_id, vy_id):
#         return datetime.now()

#     def _get_too_staatus(self, staatus):
#         c = self.c
#         if staatus != const.S_STAATUS_TEHTUD and c.sooritus.staatus != const.S_STAATUS_TEHTUD:
#             # kas kõik ylesanded on vastatud?
#             pooleli = False
#             for ty in c.testiosa.testiylesanded:
#                 yv = c.sooritus.get_ylesandevastus(ty.id, kehtiv=True)
#                 if not yv:
#                     pooleli = True
#                     break
#             if not pooleli:
#                 # kõik ylesanded on vastatud
#                 staatus = const.S_STAATUS_TEHTUD
#         return staatus
        
#     def __before__(self):
#         """Väärtustame testimiskorra id
#         """
#         c = self.c
#         c.test_id = self.request.matchdict.get('test_id')
#         c.test = model.Test.get(c.test_id)
#         c.testiosa = c.test.testiosad[0]
#         c.testiruum_id = self.request.matchdict.get('testiruum_id') or 0
#         #if int(c.testiruum_id):
#         #    testiruum = model.Testiruum.get(c.testiruum_id)
#         #    c.nimekiri = testiruum.nimekiri
#         c.sooritus = self._get_sooritus()
#         c.sooritaja = c.sooritus.sooritaja
#         vy_id = self.request.matchdict.get('id')
#         c.vy = model.Valitudylesanne.get(vy_id)
#         c.preview = True

#     def _get_sooritus(self):
#         sooritus_id = self.request.matchdict.get('sooritus_id')
#         if sooritus_id:
#             sooritus_id = int(sooritus_id)
#             li = self.request.session.get('tempsooritused') or []
#             for r in li:
#                 if r.id == sooritus_id:
#                     r.modified = datetime.now()
#                     self.c.sooritus = r
#                     self.c.lang = r.lang
#                     return self.c.sooritus
#             self.error(_("Eelvaade on aegunud, palun alusta uuesti"))
#             raise HTTPFound(location=self._get_index_url())

#     def _has_permission(self):
#         if not self.c.test:
#             return False
#         return BaseController._has_permission(self)

#     def _get_perm_bit(self):
#         # kõik vaatamisõigusega kasutajad võivad käivitada statistika arvutamise
#         return const.BT_SHOW

#     def _perm_params(self):
#         return {'obj':self.c.test}
