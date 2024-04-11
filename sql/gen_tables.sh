#!/bin/bash
# eelnevalt teha:
#   export PGPASSWORD=....

SCHEMA=public
DBG=eisdbg
DBGSESS=eisdbgsess
DBGLOG=eisdbglog
DBHOST=192.168.107.1
PSQL="psql -q -U eisik -h $DBHOST -p 5432"
PGDUMP="pg_dump -n $SCHEMA -s -U eisik -h $DBHOST -p 5432"
EISHOME=/srv/eis
PYTHON=/srv/eis/bin/python

cd ..
. tmp/eis.sh

echo
echo teeme andmebaasi tühjaks
cd sql
bash drop.sh $DBHOST $DBG
bash drop.sh $DBHOST $DBGSESS
bash drop.sh $DBHOST $DBGLOG
cd ..

echo installime uue andmebaasi...
$PYTHON -m eis.scripts.create_db tmp/development.dbg.ini
if [ ! "$PIPESTATUS" == "0" ] ; then
    exit
fi
echo lisame indeksid...
$PSQL $DBG < sql/index_ex.sql

echo genereerime kommentaarid...
$PYTHON scripts/gen_comments.py > sql/comments.sql
echo "laadime kommentaarid..."

cat sql/comments_ex.sql >> sql/comments.sql

$PSQL $DBG < sql/beaker_cache.sql
$PSQL $DBG < sql/comments.sql

echo genereerime model_s kommentaarid...
$PYTHON scripts/gen_comments.py eis/model_s > sql/comments_s.sql
$PSQL $DBGSESS < sql/comments_s.sql

echo genereerime model_log kommentaarid...
$PYTHON scripts/gen_comments.py eis/model_log > sql/comments_log.sql
$PSQL $DBGLOG < sql/comments_log.sql

cd scripts
echo "gen_tbl_doc.py..."
$PYTHON gen_tbl_doc.py -f ../tmp/development.dbg.ini > ../docs/tbl_doc.html
$PYTHON gen_tbl_doc.py -csv 1 -f ../tmp/development.dbg.ini > ../docs/tbl_doc.csv

echo genereerime grupiõigused...
$PYTHON gen_gruppoigus.py -f ../tmp/development.dbg.ini > ../sql/init/kasutajagrupp_oigus.sql

cd ../sql
echo genereerime pysiandmete skriptid
bash gen_init.sh $DBHOST

echo genereerime andmebaasist skripti, sisesta andmebaasi parool...
$PGDUMP $DBG > tables.sql
$PGDUMP $DBGSESS > tables_s.sql
$PGDUMP $DBGLOG > tables_log.sql

