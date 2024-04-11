"""
Vanade failide kustutamine Minio failiserverist

Käivitada crontabist 

python -m eis.scripts.remove_deleted
"""
from eis.scripts.scriptuser import *
from eis.s3file import create_s3client, get_s3_row_by_path

def rund(days):
    "Nende failide kustutamine, millele viitav kirje on kustutatud"
    settings = request.registry.settings
    client, bucket_name = create_s3client(settings)

    dt = date.today() - timedelta(days=days)
    q = (model.Session.query(model.Deletefile)
         .filter(model.Deletefile.created<dt))
    total = q.count()
    n = 0
    log.info(f'Kustutada {total} faili')
    for df in q.all():
        path = df.object_name
        rcd = get_s3_row_by_path(path)
        if rcd:
            raise Exception('Kirje %s pole kustutatud' % rcd)
        #log.info(f"remove_object('{bucket_name}','{path}')")
        n += 1
        buf = '%d/%d %s %s' % (n, total, df.created, path)
        #sys.stdout.write('\r' + buf.ljust(80,' '))
        #sys.stdout.flush()
        print(buf)
        client.remove_object(bucket_name, path)
        df.delete()
    model.Session.commit()

# def runfromtv():
#     "Toorvastuste viimine põhibaasi"
#     settings = request.registry.settings
#     client, bucket_name = create_s3client(settings)

#     dt = date.today() - timedelta(days=1)
#     q = (model.Session.query(model.Ylesandevastus)
#          .filter(model.Ylesandevastus.modified < dt)
#          .filter(model.Ylesandevastus.on_toorvastus==True))
#     n = 0
#     total = q.count()
#     log.info(f'Paigaldada {total} toorvastust')
#     for yv in q.all():
#         yv.from_toorvastus()
#         n += 1
#         buf = '%d/%d %s' % (n, total, yv.id)
#         sys.stdout.write('\r' + buf.ljust(80,' '))
#         sys.stdout.flush()
#         if n % 1000 == 0:
#              model.Session.commit()
#     model.Session.commit()
#     print('\nread %d' % n)

# def runtv(days):
#     "Vanade toorvastuste kustutamine"
#     settings = request.registry.settings
#     client, bucket_name = create_s3client(settings)

#     dt = date.today() - timedelta(days=days)
#     q = (model_s.DBSession.query(sa.func.min(model_s.Toorvastus.ylesandevastus_id),
#                                  sa.func.max(model_s.Toorvastus.ylesandevastus_id))
#          .filter(model_s.Toorvastus.created < dt))
#     try:
#         min_yv_id, max_yv_id = q.first()
#     except TypeError:
#         return
#     if not max_yv_id:
#         return
#     n = 0        
#     while min_yv_id <= max_yv_id:
#         # käivitame tykkhaaval, et päring ei läheks liiga suureks
#         max_step = min_yv_id + 1000
#         q = (model_s.DBSession.query(model_s.Toorvastus)
#              .filter(model_s.Toorvastus.created < dt)
#              .filter(model_s.Toorvastus.ylesandevastus_id>=min_yv_id)
#              .filter(model_s.Toorvastus.ylesandevastus_id<max_step)
#              .order_by(model_s.Toorvastus.ylesandevastus_id))
#         total = q.count()
#         log.info(f'Kontrollida {total} toorvastust {min_yv_id}-{max_step} ({max_yv_id})')
#         min_yv_id = max_step
#         model_s.DBSession.begin()
#         prev_yv_id = yv = None
#         for tv in q.all():
#             yv_id = tv.ylesandevastus_id
#             if prev_yv_id != yv_id:
#                 prev_yv_id = yv_id
#                 yv = model.Ylesandevastus.get(yv_id)
#             if yv and yv.on_toorvastus:
#                 print('   from_tv %s' % yv.id)
#                 yv.from_toorvastus()
#                 model.Session.commit()
#             if not yv or not yv.on_toorvastus:
#                 if tv.has_file:
#                     path = tv._filedata_path
#                     client.remove_object(bucket_name, path)
#                 else:
#                     path = ''
#                 n += 1
#                 buf = '%d %d %s %s' % (n, yv_id, tv.created, path)
#                 #sys.stdout.write('\r' + buf.ljust(80,' '))
#                 #sys.stdout.flush()
#                 print(buf)
#                 model_s.DBSession.delete(tv)
#         model_s.DBSession.commit()

#     print('\ndeleted %d' % n)

def check_clean():
    """Minio kirjete sirvimine.
    Kontrolli, kas kirje on postgresis olemas. Kui pole, siis kustuta
    """
    settings = request.registry.settings
    client, bucket_name = create_s3client(settings)

    tblname = 'toorvastus'

    def check_tbl(tblname, table):
        cnt1 = cnt2 = 0
        prefix1 = f'{tblname}/'
        for dir1 in client.list_objects(bucket_name, prefix=prefix1):
            print(f'check {dir1.object_name}...')
            for dir2 in client.list_objects(bucket_name, prefix=dir1.object_name):
                for obj in client.list_objects(bucket_name, prefix=dir2.object_name):
                    path = obj.object_name
                    rcd = get_s3_row_by_path(path)
                    if rcd:
                        # exists
                        cnt1 += 1
                    else:
                        # missing
                        cnt2 += 1
                        print(f'DELETE {path}')                        
                        client.remove_object(bucket_name, path)
        print(f'{cnt1} exists, {cnt2} missing')
                        
    check_tbl('toorvastus', model_s.Toorvastus)
    check_tbl('kvsisu', model.Kvsisu)

    
def _error(exc, msg=''):
    script_error('Veateade (remove_deleted)', exc, msg)
    sys.exit(1)   
    
if __name__ == '__main__':
    days = 120
    op = named_args.get('op')

    fn_lock = '/srv/eis/log/remove_deleted.lock'
    with FileLock(fn_lock) as lock:
        if not lock:
            log.info('Protsess juba käib (fail %s on lukus)' % fn_lock)
            sys.exit(0)

        if not op or op == 'd':
            # kustutatud viitadega failide kustutamine failiserverist
            try:
                rund(days)
            except Exception as e:
                _error(e, str(e))

        # if op == 'ftv':
        #     # toorvastuste kasutamine
        #     try:
        #         runfromtv()
        #     except Exception as e:
        #         _error(e, str(e))

        # if not op or op == 'tv':
        #     # kasutatud toorvastuste ja nende failide kustutamine
        #     try:
        #         runtv(days)
        #     except Exception as e:
        #         _error(e, str(e))

        if op == 'clean':
            check_clean()
            
