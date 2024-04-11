# -*- coding: utf-8 -*-
import logging
log = logging.getLogger(__name__)

class BaseGridController:
    "Kontroller, mis korraga töötleb mitut kirjet"
    def __init__(self, collection, model, parent=None, parent_controller=None, pkey='id', supercollection=None, pkey_empty=False):
        """
        collection
          parenti atribuut, jada kirjetest, mida muudetakse
        model
          muudetava kirje klass
        parent
          parent objekt (vajalik üksikjuhtudel)
        """
        self._COLLECTION = collection
        self.supercollection = supercollection
        self._MODEL = model
        self.parent = parent
        self.parent_controller = parent_controller
        self.seq = 0
        self.pkey = pkey
        self.pkey_empty = pkey_empty
        self.deleted = []
        
    def save(self, rcd_list, lang=None, update_only=False, delete_hidden=False):
        self.seq = 0
        
        log.debug('BaseGridController ' + str(rcd_list))
        log.debug('collection=%s, model=%s' % (self._COLLECTION, self._MODEL))

        # kustutame enne muutmist,
        # juhuks kui mõni muudetav sisaldab kustutavaga sama koodi
        if delete_hidden:
            # kustutada read, millel on märge "deleted"
            rcd_list = self.delete_hidden(rcd_list)
        elif not update_only:
            # kustutada read, mida enam pole
            self.delete(rcd_list)
            
        # muudame olemasolevad
        upd_rcd_list = self.update(rcd_list, lang)

        if not update_only:
            # lisame uued
            self.create(rcd_list, upd_rcd_list, lang)

    def delete(self, rcd_list):
        for subitem in list(self._COLLECTION):
            # leiame selle objekti postitatud listist
            rcd = self._find_rcd(rcd_list, subitem)
            if not rcd:
                # kui objekt pole praegu vaadeldavast klassist,
                # siis seda ei kustutata
                if self.is_deletable(subitem):
                    # kustutame kustutatud kirjed
                    try:
                        if self.can_delete(subitem):
                            self.deleted.append(subitem) # et saaks hiljem aru, mis on kustutatud
                            self.delete_subitem(subitem)
                    except Exception as ex:
                        log.info('viga kirje kustutamisel %s' % ex)
                        
    def delete_hidden(self, rcd_list):
        li = []
        for rcd in rcd_list:
            if rcd.get('deleted') and self.pkey == 'id':
                rcd_id = rcd['id']
                if rcd_id:
                    subitem = self._MODEL.get(rcd_id)
                    if subitem and subitem in self._COLLECTION:
                        subitem.delete()
            else:
                li.append(rcd)
        return li

    def create(self, rcd_list, upd_rcd_list, lang=None):
        for rcd in rcd_list:
            # uued kirjed
            if rcd not in upd_rcd_list:
                #log.debug('create %s' % rcd)
                self.create_subitem(rcd, lang)

    def update(self, rcd_list, lang=None):       
        upd_rcd_list = []
        for subitem in self._COLLECTION:
            rcd = self._find_rcd(rcd_list, subitem)
            if rcd:
                # muudame olemasolevad kirjed
                upd_rcd_list.append(rcd)
                self.update_subitem(subitem, rcd, lang=lang)
        return upd_rcd_list

    def is_deletable(self, rcd):
        return isinstance(rcd, self._MODEL)        

    def can_delete(self, rcd):
        return True

    def delete_subitem(self, rcd):
        rcd.delete()
        self._COLLECTION.remove(rcd)
        if self.supercollection is not None:
            self.supercollection.remove(rcd)
            
    def update_subitem(self, subitem, rcd, lang=None):
        """
        subitem - mudeli objekt
        rcd - vormilt postitatud andmed valideerituna
        """
        subitem.from_form(rcd, lang=lang)
        self.seq += 1
        if 'seq' not in rcd and not lang:
            # tõlkimisel ei muuda põhikirje seq
            subitem.seq = self.seq
        return subitem

    def create_subitem(self, rcd, lang=None):
        subitem = self._MODEL()
        subitem.from_form(rcd, lang=lang)
        self.seq += 1
        if 'seq' not in rcd or not rcd.get('new_seq'):
            subitem.seq = self.seq        
        self._COLLECTION.append(subitem)
        if self.supercollection is not None:
            self.supercollection.append(subitem)
        if self.parent and self.parent.id:
            subitem.parent_id = self.parent.id
        return subitem

    def _find_rcd(self, rcd_list, subitem):
        """Postitatud andmete listist rcd_list leitakse esimene kirje, mille identifikaator
        võrdub antud subitemi identifikaatoriga.
        """
        for rcd in rcd_list:
            if self.pkey == 'id':
                if rcd['id'] and subitem.id == int(rcd['id']):
                    return rcd
            else:
                sub_value = subitem.__getattr__(self.pkey)
                if (rcd[self.pkey] or self.pkey_empty) and sub_value == rcd[self.pkey]:
                    return rcd
