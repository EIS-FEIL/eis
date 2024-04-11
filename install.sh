# Paketi installimine
srcdir=$PWD
EISHOME=/srv/eis
rm -r -f build dist # vanad

mkdir $EISHOME/etc $EISHOME/app $EISHOME/var $EISHOME/var/data $EISHOME/var/filecache $EISHOME/log $ESHOME/log/msg $EISHOME/lib/tmp $EISHOME/ttf 2>/dev/null
cp ttf/*ttf /srv/eis/ttf
cp app/*wsgi.py $EISHOME/app
cp etc/sebsample.seb $EISHOME/etc
echo "install..."
$EISHOME/bin/pip install .

