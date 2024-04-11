#!/bin/bash
host=$1
DBG=eisdbg
PGDUMP="pg_dump -U eisik -h $host -p 5432"
echo $PGDUMP
for tbl in klassifikaator klrida piirkond koht kasutajaoigus kasutajagrupp kasutaja kasutajaroll asukohamaarus abivahend
do
    echo $tbl...
    # ekspordime ja asendame created, modified
    $PGDUMP -a --column-inserts -t $tbl $DBG| sed -r "s/'201[2-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.[0-9]{0,6}', '201[2-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.[0-9]{0,6}', /current_timestamp, current_timestamp, /" > init/$tbl.sql
done
# faili kasutajagrupp_oigus genereerib scripts/gen_gruppoigus.py

