Andmebaaside install
--------------------

PostgreSQL serverites luua andmebaasid eisdb1, eisdb1log, eisdb1sess, kasutades:

```
    ENCODING = 'UTF8'
    LC_COLLATE = 'Estonian_Estonia.1257'
    LC_CTYPE = 'Estonian_Estonia.1257'
```

Igasse andmebaasiserverisse laadida rakenduse kasutajad:

```
psql -U postgres -h HOST eisdb1 < create_user.sql

```

Põhibaasi laadida andmestruktuur, klassifikaatorite algseis, administraatori kasutaja, protseduurid, vaated ja kommentaarid:

```
psql -U postgres -h HOST eisdb1 < tables.sql
psql -U postgres -h HOST eisdb1 < init.sql
psql -U postgres -h HOST eisdb1 < proc.sql
psql -U postgres -h HOST eisdb1 < views.sql
psql -U postgres -h HOST eisdb1 < comments.sql

```

Põhibaas replitseeritakse (streaming replication) ning selle ette seadistatakse haproxy, mis annab pordis 5000 read-write ühendusi ja pordis 5001 read-only ühendusi.


Seansibaasi laadida andmestruktuur kommentaaridega:

```
psql -U postgres -h HOST eisdb1sess < tables_s.sql
psql -U postgres -h HOST eisdb1sess < comments_s.sql

```

Logibaasi laadida andmestruktuur kommentaaridega:

```
psql -U postgres -h HOST eisdb1log < tables_log.sql
psql -U postgres -h HOST eisdb1log < comments_log.sql

```
