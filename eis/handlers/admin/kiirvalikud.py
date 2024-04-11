# # -*- coding: utf-8 -*- 
# # $Id: kiirvalikud.py 383 2016-02-29 16:28:53Z ahti $

# from eis.lib.baseresource import *
# _ = i18n._

# log = logging.getLogger(__name__)

# class KiirvalikudController(BaseResourceController):
#     """Kiirvalikud
#     """
#     _permission = 'kiirvalikud'

#     _ITEM = 'kiirvalik'
#     _ITEMS = 'kiirvalikud'
#     _MODEL = model.Kiirvalik
#     _EDIT_TEMPLATE = 'admin/kiirvalikud.mako'
#     _INDEX_TEMPLATE = 'admin/kiirvalikud.mako'
#     _ITEM_FORM = forms.admin.KiirvalikForm

#     def index(self):
#         self.c.items = model.Kiirvalik.query.all()
#         return self.render_to_response(self._INDEX_TEMPLATE)

#     def _edit(self, item):
#         self.c.items = model.Kiirvalik.query.all()

#     def _edit_test(self, id):
#         """Testimiskorra asendamine sama testi mõne teise testimiskorraga
#         """
#         self.c.item = model.Kiirvalik.get(id)
#         kord_id = self.request.params.get('testimiskord_id')
#         testimiskord = model.Testimiskord.get(kord_id)
#         self.c.f_test = testimiskord.test
#         return self.render_to_response('admin/kiirvalik.test.mako')

#     def _update_test(self, id):
#         self.c.item = model.Kiirvalik.get(id)
#         f_test_id = int(self.request.params.get('f_test_id'))
        
#         li = list(map(int, self.request.params.getall('kord_id')))
        
#         remove = []
#         for rcd in self.c.item.testimiskorrad:
#             if rcd.test_id == f_test_id:
#                 if rcd.id in li:
#                     li.remove(rcd.id)
#                 else:
#                     remove.append(rcd)

#         for rcd in remove:
#             self.c.item.testimiskorrad.remove(rcd)

#         for kord_id in li:
#             rcd = model.Testimiskord.get(kord_id)
#             if rcd.test_id == f_test_id:
#                 self.c.item.testimiskorrad.append(rcd)
#         model.Session.commit()
#         self.success()
#         return HTTPFound(location=self.url('admin_kiirvalik', id=id))

#     def _edit_kord(self, id):
#         self.c.item = model.Kiirvalik.get(id)
#         self.c.testsessioon_id = self.request.params.get('testsessioon_id')
#         if self.c.testsessioon_id:
#             testsessioon = model.Testsessioon.get(self.c.testsessioon_id)
#             self.c.items = testsessioon.testimiskorrad
        
#         return self.render_to_response('admin/kiirvalik.kord.mako')

#     def _update_kord(self, id):
#         self.c.item = model.Kiirvalik.get(id)
#         self.c.testsessioon_id = int(self.request.params.get('testsessioon_id'))
#         testsessioon = model.Testsessioon.get(self.c.testsessioon_id)
#         li = list(map(int, self.request.params.getall('kord_id')))
        
#         remove = []
#         for rcd in self.c.item.testimiskorrad:
#             if rcd.testsessioon_id == self.c.testsessioon_id:
#                 if rcd.id in li:
#                     li.remove(rcd.id)
#                 else:
#                     remove.append(rcd)

#         for rcd in remove:
#             self.c.item.testimiskorrad.remove(rcd)

#         for kord_id in li:
#             rcd = model.Testimiskord.get(kord_id)
#             if rcd.testsessioon_id == self.c.testsessioon_id:
#                 log.info('LISAN %s' % rcd.id)
#                 self.c.item.testimiskorrad.append(rcd)
#         model.Session.commit()
#         self.success()
#         return HTTPFound(location=self.url('admin_kiirvalik', id=id))

#     def _delete_kord(self, id):
#         self.c.item = model.Kiirvalik.get(id)
#         kord_id = self.request.params.get('testimiskord_id')
#         rcd = model.Testimiskord.get(kord_id)
#         self.c.item.testimiskorrad.remove(rcd)
#         model.Session.commit()
#         self.success(_('Seos on kustutatud'))
#         return HTTPFound(location=self.url('admin_kiirvalik', id=id))

