# # -*- coding: utf-8 -*- 

# from eis.lib.baseresource import *
# from eis.handlers.ekk.testid import eelvaade

# log = logging.getLogger(__name__)

# class TooeelvaadeController(eelvaade.EelvaadeController):
#     """Töö sooritamise eelvaade töö koostajale
#     (eelvaates näeb ainult indeksit, ylesandeid sooritada ei saa)
#     """
#     _permission = 'testid'
#     _EDIT_TEMPLATE = 'avalik/sooritamine/tooylesanded.sisu.mako'
#     #_actions = 'index,new,create,show,update,edit' 
#     _actions = 'new,edit' 
   
#     def __before__(self):       
#         c = self.c
#         c.testiruum_id = self.request.matchdict.get('testiruum_id')
#         if c.testiruum_id:
#             testiruum = model.Testiruum.get(c.testiruum_id)
#             c.nimekiri = testiruum and testiruum.nimekiri

#         c.test_id = self.request.matchdict.get('test_id')
#         c.test = model.Test.get(c.test_id)
#         if not c.test:
#             return
#         c.testiosa = c.test.get_testiosa()

#         for k in c.testiosa.get_komplektivalik().komplektid:
#             if k.staatus in (const.K_STAATUS_KINNITATUD, const.K_STAATUS_KOOSTAMISEL):
#                 c.komplekt = k
#                 break
           
#         c.alatest_id = self.request.matchdict.get('alatest_id')
#         if c.alatest_id == 'None':
#             c.alatest_id = None
#         c.lang = self.params_lang() or len(c.test.keeled) and c.test.keeled[0] or None
#         c.preview = True
#         c.avalik = True

#         c.sooritus = c.item = self._get_sooritus()
#         BaseResourceController.__before__(self)
