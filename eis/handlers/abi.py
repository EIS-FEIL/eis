from eis.lib.base import *
_ = i18n._

log = logging.getLogger(__name__)

class AbiController(BaseController):
    """Abiinfo salvestamine ja kuvamine
    """
    _permission = 'abi'
    _index_after_create = True
    _actions = 'index,update,edit' 
    
    def index(self):
        """Abiinfo näitamine
        """
        id = self.request.matchdict.get('id')
        page_id = self.request.matchdict.get('page_id')
        
        self.c.item = model.Abiinfo.get(page_id, id)
        if self.c.item:
            buf = self.c.item.sisu.replace('\n','<br/>')
            buf = re.sub(r'(https?://[a-zA-Z0-9/:_\-.]+)', r'<a href="\1" target="_blank">link</a>', buf)
        else:
            if id == 'pagehelp':
                buf = _("Selle lehe kohta pole abiinfot kirjutatud")
            else:
                buf = _("Selle välja kohta pole abiinfot kirjutatud ")
            buf = '<i>%s</i>' % buf
        return Response(buf)

    def edit(self):
        id = self.request.matchdict.get('id')
        page_id = self.request.matchdict.get('page_id')

        self.c.item = model.Abiinfo.get(page_id, id)
        if not self.c.item:
            self.c.item = model.Abiinfo(vorm=page_id, kood=id)
            model.Session.autoflush = False
        return self.render_to_response('/common/abi.mako')

    def update(self):
        id = self.request.matchdict.get('id')
        page_id = self.request.matchdict.get('page_id')
        params = self.request.params
        sisu = (params.get('f_sisu') or '').strip()
        url = params.get('f_url')
        if url:
            url = url.strip()
        self._save(page_id, id, sisu, url)
                
        model.Session.commit()
        buf = self.h.literal("<script>hide_help(); </script>")
        return Response(buf)

    def _save(self, page_id, id, sisu, url):
        item = model.Abiinfo.get(page_id, id)
        if sisu or url:
            if not item:
                item = model.Abiinfo(vorm=page_id, kood=id, sisu=sisu, url=url)
            else:
                item.sisu = sisu
                item.url = url
        elif item:
            item.delete()

    def _do_authorize(self):
        if self._is_modify() and not self.c.user.helpmaster:
            return BaseController._do_authorize(self)


            
