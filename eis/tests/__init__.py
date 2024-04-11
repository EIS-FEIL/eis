# -*- coding: utf-8 -*-
"""
Automaattestimine

Testimiseks testbaasiga:
Vaadata, et fn väärtus oleks development.test.ini
Eelnevalt peavad olemas olema andmebaasid eisdbtest ja eisdbtesttunnistus.
Eelnevalt peab olema loodud andmebaasistruktuur:
   bash resettest.sh

unit - testitakse üksikuid funktsioone
integration - testitakse vorme protsessisiseselt (WebTest.TestApp vastu)
functional - testitakse vorme eraldi käivitatud serveri vastu

Testide käivitamine:
   python setup.py test
"""
