import os.path
from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class YhisfailidController(BaseResourceController):

    _permission = 'yhisfailid'

    _MODEL = model.Yhisfail
    _INDEX_TEMPLATE = 'ekk/ylesanded/yhisfailid.mako'
    _EDIT_TEMPLATE = 'ekk/ylesanded/yhisfail.mako' 
    _LIST_TEMPLATE = 'ekk/ylesanded/yhisfailid_list.mako'

    _SEARCH_FORM = forms.ekk.ylesanded.YhisfailidForm 
    _ITEM_FORM = forms.ekk.ylesanded.YhisfailForm

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.filename:
            q = q.filter(model.Yhisfail.filename.ilike('%'+self.c.filename+'%'))
        if self.c.teema:
            q = q.filter(model.Yhisfail.teema.ilike('%'+self.c.teema+'%'))
        if self.c.yhisfail:
            q = q.filter(model.Yhisfail.yhisfail_kood==self.c.yhisfail)
        return q
    
    def _create(self, **kw):
        filename, filedata = self._check_filename(None)
        if not filename or not filedata:
            self.error(_("Fail puudub"))
            return self._redirect('new')

        item = model.Yhisfail()
        item.from_form(self.form.data, 'f_')
        item.filename = filename
        item.filedata = filedata
        return item

    def _update(self, item):
        # omistame vormilt saadud andmed
        filename, filedata = self._check_filename(None)
        if filename and filedata:
            item.filename = filename
            item.filedata = filedata
        elif filename:
            item.filename = filename
        item.teema = self.form.data.get('f_teema')
        item.yhisfail_kood = self.form.data.get('f_yhisfail_kood')
        

    def _check_filename(self, item_id):
        filevalue = self.form.data.get('f_filedata')
        filename = filedata = None
        if filevalue != b'':
            # kui anti fail, siis muudame filedata ja filename
            # value on FieldStorage objekt
            filename = _fn_local(filevalue.filename)
            filedata = filevalue.value

            # kontrollime, et failinimi oleks unikaalne
            root, ext = os.path.splitext(filename)
            for n in range(1000):
                q = model.Yhisfail.query.filter_by(filename=filename)
                if item_id:
                    q = q.filter(model.Yhisfail.id!=item_id)
                if q.count():
                    filename = '%s-%d%s' % (root, n, ext)
                    continue
                else:
                    return filename, filedata
        else:
            filename = self.form.data.get('f_filename')
        return filename, None

def _fn_local(fnPath):
    """
    Rajast eraldatakse failinimi.
    """
    pos = max(fnPath.rfind('\\'), fnPath.rfind('/'))
    if pos > -1:
        return fnPath[pos + 1:]
    else:
        return fnPath

