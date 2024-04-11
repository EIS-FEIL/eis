"EISi andmemudeli formaadis importimine"
import sys
import os
import pickle
import re

from eis.lib.base import *
from eis.lib.importpackage import ImportPackage, ImportException

log = logging.getLogger(__name__)

class RawImportPackage(ImportPackage):
    def __init__(self, filename, storage):
        """Tabelite sisu importimine.
        Objekti atribuudid:
        is_error - kas õnnestus importimine või mitte
        messages - jada teadetest kasutajale (infoks)
        items - jada imporditud kirjetest
        """
        super(RawImportPackage, self).__init__()
        if filename:
            f = open(filename, 'rb')
            filedata = f.read()
            f.close()
        else:
            filedata = storage.value
            
        map = {} # vanade ja uute ID-de vastavus
        unmapped = [] # kirjed, mis loodi enne viidatud kirjet ja on vaja lõpus mappida
        main_item = None
        li = pickle.loads(filedata)
        # li on list yhe ylesande kirjetest
        for di in li:
            cls_name = di.pop('class')
            if cls_name == 'meta':
                for key, value in di.items():
                    self.notice('%s: %s' % (key, value))
            else:
                if cls_name.startswith('T_') and di.get('ylesandeversioon_id'):
                    # ignoreerime ylesandeversiooni kirjeid
                    continue
                cls, item = self._import_raw_obj(cls_name, di, map, unmapped)
                if isinstance(item, (model.Ylesanne,
                                     model.Test,
                                     model.Rveksam,
                                     model.Klassifikaator)):
                    # impordi tulemuste seas eraldi välja toodav tähtis objekt
                    self.items.append(item)

        self._map_unmapped(map, unmapped)
        if not self.items:
            self.is_error = True

    def _map_unmapped(self, map, unmapped):
        # vastavused, mida võidi hiljem luua
        for item, item_unmapped in unmapped:
            for key, (tbl_name, old_fk_id) in item_unmapped:
                try:
                    new_fk_id = map[(tbl_name, old_fk_id)]
                except KeyError:
                    buf = '%s ei leia %s ID=%s vastet' % (cls_name, tbl_name, old_fk_id)
                    print(buf)
                    self.error(buf)
                    raise Exception(buf)                
                item.__setattr__(key, new_fk_id)       
            
    def _import_raw_obj(self, cls_name, di, map, unmapped):
        item_unmapped = []
        cls = eval('model.' + cls_name)
        #print(cls_name)
        # kirje ID ei säili
        old_id = 'id' in di and di.pop('id')
        for key in list(di.keys()):
            if key.endswith('_id') and key not in ('kasutajagrupp_id',):
                old_fk_id = di[key]
                if cls_name == 'Ylesanne' and key == 'alus_id' or \
                       cls_name == 'Test' and key == 'eeltest_id' or \
                       cls_name == 'Test' and key == 'rveksam_id' or \
                       cls_name == 'Test' and key == 'tookogumik_id' or \
                       cls_name == 'Testiosa' and key == 'rvosaoskus_id' or \
                       cls_name == 'Alatest' and key == 'rvosaoskus_id' or \
                       cls_name == 'Ylopitulemus' and key == 'opitulemus_klrida_id':
                    # väljad, mida ei impordita
                    di[key] = None
                elif cls_name == 'Klrida' and key == 'ylem_id':
                    # omistatakse ylem_kood kaudu
                    pass
                elif old_fk_id:
                    tbl_name = key.split('_')[-2]
                    if tbl_name == 'orig':
                        # minu tabeli tõlketabel
                        tbl_name = cls_name[2:].lower()
                    elif cls_name == 'Tagasisidevorm' and key == 'ylem_id':
                        tbl_name = 'tagasisidevorm'
                    try:
                        new_fk_id = map[(tbl_name, old_fk_id)] 
                    except KeyError:
                        if cls_name + '.' + key in ('Tulemus.oigsus_kysimus_id',
                                                    'Valikvastus.valik1_kysimus_id',
                                                    'Valikvastus.valik2_kysimus_id'):
                            # vastavuse võib luua hiljem
                            new_fk_id = None
                            item_unmapped.append((key, (tbl_name, old_fk_id)))
                        else:
                            # vastavust ei saanud luua
                            print(map)
                            buf = '%s ei leia ID (%s, %s)' % (cls_name, tbl_name, old_fk_id)
                            print(buf)
                            self.error('%s ei leia ID (%s, %s)' % (cls_name, tbl_name, old_fk_id))
                            #sys.exit(1)
                            raise Exception(buf)
                    #print('  map %s %s > %s' % (key, di[key], new_fk_id))
                    di[key] = new_fk_id

            if cls_name == 'Ylesandeisik' and key == '_kasutaja_ik':
                isikukood = di[key]
                kasutaja = model.Kasutaja.get_by_ik(isikukood)
                if not kasutaja:
                    self.notice('Andmebaasis pole kasutajat isikukoodiga %s' % isikukood)
                    return cls, None
                di['kasutaja_id'] = kasutaja.id

            if cls_name == 'Ylopitulemus' and key == '_opitulemus_klrida_idurl':
                idurl = di[key]
                kl = (model.SessionR.query(model.Klrida)
                      .filter_by(klassifikaator_kood='OPITULEMUS')
                      .filter_by(idurl=idurl)
                      .first())
                if not kl:
                    self.notice(f'Andmebaasis pole õpitulemust {idurl}')
                    return cls, None
                di['opitulemus_klrida_id'] = kl.id

            elif cls_name == 'Klrida' and key == '_ylem_kood':
                kl = model.Klassifikaator.getR(di['klassifikaator_kood'])
                ylem = model.Klrida.get_by_kood(kl.ylem_kood, di[key])
                if not ylem:
                    raise Exception('Puudub ylem {s}'.format(s=di[key]))
                di['ylem_id'] = ylem.id

            elif cls_name == 'Komplekt' and key == 'lukus':
                # kuna sooritusi ei impordita, siis pole vaja säilitada sooritatuse lukku
                lukus = di[key]
                if lukus and lukus > const.LUKUS_KINNITATUD:
                    di[key] = const.LUKUS_KINNITATUD

            elif key.endswith('_kood'):
                liik_kood = key.split('_')[-2].upper()
                value = di[key]
                if value and liik_kood == 'VAHEND':
                    r = model.Abivahend.get_by_kood(value)
                    if not r:
                        buf = 'Abivahendite seast puudub %s' % (value)
                        print(buf)
                        self.error(buf)
                        raise ImportException(buf)

            elif cls_name == 'Test' and key == 'testityyp':
                # avaliku vaate testi impordime EKK vaate testiks
                if di[key] in (const.TESTITYYP_AVALIK, const.TESTITYYP_TOO):
                    di[key] = const.TESTITYYP_EKK

            elif cls_name == 'Ylesanne' and key == 'staatus':
                # avaliku vaate ylesande impordime EKK vaate ylesandeks
                if di[key] in const.Y_ST_AV:
                    di[key] = const.Y_STAATUS_TEST

        # loome uue kirje
        item = None
        if cls_name == 'Klassifikaator':
            item = model.Klassifikaator.getR(di['kood'])
        elif cls_name == 'Klrida':
            item = model.Klrida.get_by_kood(di['klassifikaator_kood'],
                                            di['kood'],
                                            ylem_kood=di.get('_ylem_kood') or None)
        elif cls_name == 'T_Klrida':
            item = (model.Session.query(model.T_Klrida)
                    .filter_by(orig_id=di['orig_id'])
                    .filter_by(lang=di['lang'])
                    .first())
        if item:
            for key, value in di.items():
                item.__setattr__(key, value)
        else:
            item = cls.init(**di)
        model.Session.flush()

        # jätame meelde uue kirje id, seotuna failis kasutatud vana id-ga
        if old_id:
            new_id = item.id
            map[(cls_name.lower(), old_id)] = new_id
            tbl_name = item.__table__.name
            map[(tbl_name, old_id)] = new_id
            #print('  loodud:%s %s > %s' % (tbl_name, old_id, new_id))

        if item_unmapped:
            unmapped.append((item, item_unmapped))
        return cls, item

