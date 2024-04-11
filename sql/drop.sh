# eelnevalt teha:
#   export PGPASSWORD=....
host=$1
db=$2
PSQL="psql -h $host -p 5432 -U eisik -t"
if [ "$db" = "" ]; then
    echo "Anna argumendiks andmebaas (eisdb1, eisdb2)"
else
    $PSQL -o a.sql $db < gendrop.sql  
    $PSQL $db < a.sql
fi
