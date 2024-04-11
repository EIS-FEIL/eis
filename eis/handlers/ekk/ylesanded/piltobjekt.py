import urllib.request

from eis.lib.baseresource import *
from .taustobjekt import TaustobjektController
_ = i18n._

log = logging.getLogger(__name__)

class PiltobjektController(TaustobjektController):
    "Faili salvestamine"

    @property
    def _MODEL(self):
        if self.c.sisuplokk.tyyp == const.BLOCK_MEDIA:
            return model.Meediaobjekt
        else:
            return model.Piltobjekt

    def _create(self, **kw):
        args = self._get_parents_from_routes()
        args.update(kw)
        item = self._MODEL.init(**args)
        if self.c.sisuplokk.tyyp in (const.INTER_POS, const.INTER_POS2):
            item.kood = self.c.ylesanne.gen_kysimus_kood()
            item.give_kysimus().kood = item.kood
        elif self.c.sisuplokk.tyyp == const.INTER_GR_GAP:
            item.kood = self.c.sisuplokk.gen_piltobjekt_kood()
        return self._update(item)

    def _update(self, item):
        lang = self.params_lang() or None
        value = self.request.params.get('file')
        res = {}
        rc = False
        if value != None and value != b'' and value.file:
            tr_item = lang and item.give_tran(lang) or item
            old_filename = item.filename
            stream = value.file
            tr_item.from_form_value('filedata', value)
            if not lang and old_filename and \
                   self.c.sisuplokk.tyyp in (const.BLOCK_IMAGE, const.BLOCK_MEDIA):
                # pildi sisuploki korral pildi muutmisel failinime ei muuda,
                # et ei peaks muutma võimalikke pildile viitamisi
                tr_item.filename = old_filename

            model.Session.flush()
            if not lang:
                self._uniq_filename(item)
            if self.c.sisuplokk.tyyp == const.BLOCK_MEDIA:
                # eeldatavasti audio või video
                try:
                    item.set_media_size(stream, lang)
                except Exception as ex:
                    res['error'] = _("Pole multimeediafail")
                    raise
                else:
                    model.Session.commit()
                    res['width'] = tr_item.laius_orig
                    res['height'] = tr_item.korgus_orig                    
                    info = item.get_mediainfo()
                    if info:
                        # duration, format, bit_depth, bit_rate
                        res['mediainfo'] = info
                    rc = True
            else:
                # eeldatavasti pildifail
                try:
                    item.set_image_size(None, stream, tr_item.filename, lang)
                except IOError as e:
                    res['error'] = _("Pole pildifail")
                else:
                    model.Session.commit()
                    res['width'] = tr_item.laius_orig
                    res['height'] = tr_item.korgus_orig
                    rc = True
                    
        elif self.c.sisuplokk.tyyp == const.BLOCK_MEDIA:
            # kui fail puudub ja selle asemel on URL
            url = self.request.params.get('url')
            if url:
                try:
                    url = forms.validators.URL().to_python(url)
                except forms.formencode.api.Invalid as ex:
                    res['error'] = ex.msg
                else:
                    item.fileurl = url
                    item.filename = None
                    model.Session.commit()
                    rc = True
                 
        if rc:
            res['obj_id'] = item.id
            if item.filename:
                res['filename'] = f'images/{item.filename}'
                res['fileurl'] = ''
            else:
                res['filename'] = ''
                res['fileurl'] = item.fileurl
            res['kood'] = item.kood
            res['seq'] = item.seq
            res['href'] = item.get_url(lang)
            selgitus = item.filename and item.filename.rsplit('.', 1)[0][:90] or ''
            res['selgitus'] = selgitus
        elif not res.get('error'):
            res['error'] = _("Fail puudub")
        return Response(json_body=res)

# def check_media_url(handler, url):
#     "Kontrollitakse, kas URL võib olla multimeedia"
#     req = urllib.request.Request(url)
#     http_proxy = handler.request.registry.settings.get('http_proxy')
#     if http_proxy:
#         req.set_proxy(http_proxy, 'https')
#     try:
#         r = urllib.request.urlopen(req)
#     except Exception as ex:
#         return _("URL pole kättesaadav")
#     else:
#         header = r.headers
#         contentType = header.get_content_type()
#         if contentType == const.MIMETYPE_TEXT_HTML:
#             return _("See pole multimeedia URL")
