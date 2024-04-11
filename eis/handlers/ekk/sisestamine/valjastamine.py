from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class ValjastamineController(BaseResourceController):
    """Toimumisaja otsimine, 
    et hiljem selle ümbrikke hindajatele väljastama hakata.
    """
    _permission = 'sisestamine'
    _MODEL = model.Toimumisaeg
    _INDEX_TEMPLATE = 'ekk/sisestamine/valjastamine.otsing.mako'
    _LIST_TEMPLATE = 'ekk/sisestamine/valjastamine.otsing_list.mako'
    _DEFAULT_SORT = '-toimumisaeg.id' # vaikimisi sortimine
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.tahis:
            self.c.tahis = self.c.tahis.replace('+','-').upper()
            if len(self.c.tahis.split('-')) == 3:
                # on antud terve tähis
                ta = model.Toimumisaeg.query.\
                     filter(model.Toimumisaeg.tahised.ilike(self.c.tahis)).first() 
                if ta:
                    return HTTPFound(location=self.url('sisestamine_valjastamine_hindamispaketid', toimumisaeg_id=ta.id))
                else:
                    self.error(_('Sisestatud tähisega toimumisaega ei ole olemas'))
            else:
                # on antud tähise algus
                q = q.filter(model.Toimumisaeg.tahised.ilike(self.c.tahis+'%'))

        if self.c.aine:
            q = q.filter(model.Test.aine_kood==self.c.aine)
            
        if self.c.sessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==self.c.sessioon_id)

        liigid = self.c.user.get_testiliigid(self._permission)
        if None not in liigid:
            q = q.filter(model.Test.testiliik_kood.in_(liigid))

        return q

    def _query(self):
        q = (model.Toimumisaeg.query
             .join(model.Toimumisaeg.testiosa)
             .filter(model.Testiosa.vastvorm_kood==const.VASTVORM_KP)
             .join(model.Testiosa.test)
             .join(model.Toimumisaeg.testimiskord))
        return q

    def _search_default(self, q):
        return None
