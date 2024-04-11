"""Püsiandmete laadimine installimisel
"""
import logging
import datetime

from eis.model import *

from .oigus import insert_kasutajaoigus
from .kasutajagrupp import insert_kasutajagrupp, insert_kasutaja, insert_testkasutaja
from .klassifikaator import insert_klassifikaator, insert_koht, insert_tulemusmall
from .test import insert_testandmed, insert_testpedagoog

def insert_eksam():
    pass

def insert():
    insert_kasutajaoigus()
    insert_kasutajagrupp()
    insert_koht()
    insert_kasutaja()
    insert_klassifikaator()
    insert_tulemusmall()

