"Kommentaaride genereerimine SQLAlchemy klasside kommentaaridest"
# python scripts/gen_comments.py eis/model > sql/comments.sql

import os
import re
import sys

def generate(path):
    for root, dirs, files in os.walk(path):
        if root.find('/.') > -1:
            continue

        for fn in files:
            if fn.endswith('.py') and fn[0] not in '.#':
                commentFile(root + '/' + fn)

def commentFile(fn):
    classname = None
    isNextToClass = False
    classcomment = ''
    isClassComment = False
    tablename = ''
    colcomment = ''
    commented_tables = []
    
    def table_comment(tablename, classcomment, baseclassname):
        if baseclassname.find('EntityHelper') > -1 or baseclassname.find('EntityBase') > -1:
            print("COMMENT ON COLUMN %s.created IS 'kirje loomise aeg';" % (tablename))
            print("COMMENT ON COLUMN %s.modified IS 'kirje viimase muutmise aeg';" % (tablename))
            print("COMMENT ON COLUMN %s.creator IS 'kirje looja isikukood';" % (tablename))
            print("COMMENT ON COLUMN %s.modifier IS 'kirje viimase muutja isikukood';" % (tablename))
        if tablename not in commented_tables:
            # päritava klassi korral jätame alles ainult baasklassi kommentaari
            commented_tables.append(tablename)
            print("COMMENT ON TABLE %s IS '%s';" % (tablename, classcomment))
        print("")

    f = open(fn, 'r')
    print('-- %s' % fn)
    for line in f.readlines():

        # logi.tyyp_id jaoks
        line = line.replace('#!','')

        #if not classname:
        m = re.match(r"class (?P<classname>[a-zA-Z0-9_]+)\((?P<baseclassname>[^\)]+)\).*", line)
        if m:
            if m.group('baseclassname') == 'object':
                # pole andmeklass
                m = None
        if m:
            if tablename:
                # eelmise tabeli kommentaar
                table_comment(tablename, classcomment, baseclassname)

            classname = m.group('classname')
            baseclassname = m.group('baseclassname')
            if baseclassname.find('EntityHelper') > -1 or baseclassname.find('Base') > -1:
                # uus tabel
                # Entity on siis, kui ei taheta metavälju
                # Base - SQLAlchemy
                # EntityHelper, Entity - Elixir
                tablename = classname.lower()
            else:
                # kui baasklass on midagi muud, siis on tegu tollest tabelist 
                # tuletatud klassiga
                tablename = baseclassname.lower()

            #print "KLASS "+classname
            isNextToClass = True
        elif isNextToClass:
            # järgmine rida peale klassi definitsiooni
            #print "isNextToClass"
            if line.find('"""') > -1:
                isClassComment = True
                classcomment = line[line.find('"""')+3:]
            isNextToClass = False
        elif isClassComment:
            if line.find('"""') > -1:
                # klassi kommentaari lõpp
                classcomment = classcomment + line[:line.find('"""')]
                isClassComment = False
                classcomment = _stripComment(classcomment)
                # siin kohe ei saa kommentaari väljastada,
                # sest tabeli skeem pole veel teada
            else:
                classcomment = classcomment + line
                
        elif tablename:
            colname = None
            m = re.match(r" +(?P<attrname>[a-zA-Z0-9_]+) *= *[deferred\(]*Column\(([^']|'(?P<colname>[a-z_0-9]+)').* # (?P<comment>.+)", line)            
            #m = re.match(r" +(?P<colname>[a-zA-Z0-9_]+) *= *[deferred\(]*Column\(.* # (?P<comment>.+)", line)
            if m:
                colname = m.group('colname') or m.group('attrname')
                comment = m.group('comment')                
            else:
                m = re.match(r" +(?P<colname>[a-zA-Z0-9_]+) *= *ManyToOne.* # (?P<comment>.+)", line)
                if m:
                    colname = m.group('colname') + '_id'
                    comment = m.group('comment')
                else:
                    if line.find(' id = Column') > -1:
                        # tabelil on esmane võti ID
                        colname = 'id'
                        comment = 'kirje identifikaator'
            if colname and comment:
                print("COMMENT ON COLUMN %s.%s IS '%s';" % (tablename, colname, _stripComment(comment)))
            else:
                m = re.match(r' *schema.*"(?P<schema>.+)".*\) *', line)
                if m:
                    schemaname = m.group('schema')
                    tablename = '%s.%s' % (schemaname, tablename)

    if tablename:
        # viimase tabeli kommentaar
        table_comment(tablename, classcomment, baseclassname)

    f.close()

def _stripComment(txt):
    """
    Kommentaari viimine kujule, mida passib sqlplusis sisse lugeda.
    """
    return txt.strip().replace(';\n','\n').replace("'","")
    

if __name__ == '__main__':
    print("-- Kommentaarid genereeritud SQLAlchemy klasside kommentaaridest.")
    print("-- Muudatused teha SQLAlchemy klassides, mitte käsitsi siin.")
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    else:
        model_path = 'eis/model'
    generate(model_path)

