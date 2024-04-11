"PostgreSQLi kommentaaridest dokumentatsiooni genereerimine"
# python gen_tbl_doc.py [schema]> ../docs/tbl_doc.html

import eiscore.tbldoc as tbldoc
from eis.scripts.scriptuser import *
import eis.model_s as model_s
import eis.model_log as model_log

if __name__ == '__main__':

    if len(noname_args) >= 1:
        schemaname = noname_args[0]
    else:
        schemaname = 'public'
    do_csv = named_args.get('csv') and True or False
    if not do_csv:
        tbldoc.gen_header()
    else:
        print(f'Tabel;Väli;Selgitus')        
        
    chapter = 0
    if schemaname == 'public':
        chapter += 1
        if not do_csv:
            print(f'<h1>{chapter}. Põhibaas</h1>')
    tbldoc.gen_doc_tables(model.Session, schemaname, do_csv, chapter)
    if schemaname == 'public':
        chapter += 1
        if not do_csv:
            print(f'<h1>{chapter}. Seansihalduse andmebaas</h1>')
        tbldoc.gen_doc_tables(model_s.DBSession, schemaname, do_csv, chapter)    
        chapter += 1
        if not do_csv:
            print(f'<h1>{chapter}. Logi andmebaas</h1>')
        tbldoc.gen_doc_tables(model_log.DBSession, schemaname, do_csv, chapter)    
    if not do_csv:
        tbldoc.gen_footer()

