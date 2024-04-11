grep "$1" ../eiscore/eiscore/*.py
grep "$1" ../eistest/eistest/*.py
grep "$1" ../eistest/eistest/*/*.py
grep "$1" ../eisexam/eisexam/*.py
grep "$1" ../eisexam/eisexam/*/*.py
grep "$1" eis*/*.py
grep "$1" eis*/*/*.py
grep "$1" eis*/*/*/*.py
grep "$1" eis*/*/*/*/*.py
grep "$1" eis*/*/*/*/*/*.py
grep "$1" eis*/templates/*[kj][os]
grep "$1" eis*/templates/*/*[kj][os]
grep "$1" eis*/templates/*/*/*[kj][os]

grep -H "$1" ../eiscore/eiscore/locale/et/LC_MESSAGES/eis.po

grep "$1" ../plank/eis_plank/*.py
grep "$1" ../plank/eis_plank/*/*.py
grep "$1" ../plank/eis_plank/*/*/*.py
grep "$1" ../plank/eis_plank/*/*/*/*.py
grep "$1" ../plank/eis_plank/templates/*/*[kj][os]

grep -H "$1" ../staticapp/static/eis/source/*
grep -H "$1" ../staticapp/static/lib/web-audio-recorder-app/js/app.js
grep -H "$1" ../staticapp/static/lib/web-audio-recorder-app/js/WebAudioRecorder.js
