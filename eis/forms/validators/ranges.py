# -*- coding: utf-8 -*-

import re
from datetime import datetime, date
import formencode
from formencode.validators import *
import eiscore.i18n as i18n
_ = i18n._

class Range(FormValidator):
    """
    Kontrollitakse jargnevust
    """
    field_names = None
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')

    def _validate_python(self, field_dict, state):
        nameStart = self.field_names[0]
        nameEnd = self.field_names[1]
        if len(self.field_names) >= 3:
            message = self.field_names[2]
        else:
            message = None
        errors = {}

        dtStart = field_dict[nameStart]
        dtEnd = field_dict[nameEnd]        
        if dtStart and dtEnd:
            if dtStart > dtEnd:
                if message:
                    errors[nameEnd] = message
                else:
                    errors[nameEnd] = _("Peab olema suurem")
            
        if errors:
            error_list = list(errors.items())
            error_list.sort()
            error_message = '<br>\n'.join(
                ['%s: %s' % (name, value) for name, value in error_list])
            raise Invalid(error_message,
                          field_dict,
                          state,
                          error_dict=errors)    


class AnyNotEmpty(FormValidator):
    """
    Kontrollitakse, et oleks midagi olemas
    """
    field_names = None
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')

    def _validate_python(self, field_dict, state):
        found = False
        for key in self.field_names:
            value = field_dict.get(key)
            if value or (value != None and value != ''):
                found = True
                break

        if not found:
            errors = {}
            for key in self.field_names:
                errors[key] = _("Palun sisestada")
                break
            error_list = list(errors.items())
            error_list.sort()
            error_message = '<br>\n'.join(
                ['%s: %s' % (name, value) for name, value in error_list])
            raise Invalid(error_message,
                          field_dict,
                          state,
                          error_dict=errors)    

class NotEmptyIffNotEmpty(FormValidator):
    """
    Tingimuslik kohustuslikkus.
    Esimese välja väärtuse olemasolul on ülejäänud väljade väärtused kohustuslikud.
    Esimese välja väärtuse puudumisel tehakse ülejäänud väljad tühjaks.
    """
    
    field_names = None
    validate_partial_form = True
    empty_others = True # kas esimese välja väärtuse puudumisel teha muud väljad ka tühjaks
    __unpackargs__ = ('*', 'field_names')

    def _validate_python(self, field_dict, state):
        errors = {}
        condition = field_dict.get(self.field_names[0])

        if condition:
            for n in range(1, len(self.field_names)):
                fieldName = self.field_names[n]
                fieldValue = field_dict[fieldName]
                if fieldValue == None or fieldValue == '':
                    errors[fieldName] = _("Palun sisestada")
        elif self.empty_others:
            # teeme tyhjaks muud väljad
            for n in range(1, len(self.field_names)):
                fieldName = self.field_names[n]
                #if field_dict[fieldName]:
                field_dict[fieldName] = None
            
        if errors:
            error_list = list(errors.items())
            error_list.sort()
            error_message = '<br>\n'.join(
                ['%s: %s' % (name, value) for name, value in error_list])
            raise Invalid(error_message,
                          field_dict,
                          state,
                          error_dict=errors)    

class NotEmptyIfNotEmpty(NotEmptyIffNotEmpty):
    """
    Tingimuslik kohustuslikkus.
    Esimese välja väärtuse olemasolul on ülejäänud väljade väärtused kohustuslikud.
    Esimese välja väärtuse puudumisel teisi ei puututa.
    """
    empty_others = False

class NotEmptyIffSetTo(FormValidator):
    """
    Tingimuslik kohustuslikkus.
    Esimese välja teatud väärtuse olemasolul on ülejäänud väljade väärtused kohustuslikud.
    Esimese välja teatud väärtuse puudumisel tehakse ülejäänud väljad tühjaks.
    """
    
    field_names = None
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')

    def _validate_python(self, field_dict, state):
        errors = {}
        condition = field_dict.get(self.field_names[0])
        valuelist = self.field_names[1]

        if condition in valuelist:
            for n in range(2, len(self.field_names)):
                fieldName = self.field_names[n]
                fieldValue = field_dict[fieldName]
                if fieldValue == None or fieldValue == '':
                    errors[fieldName] = _("Palun sisestada")
        else:
            # teeme tyhjaks
            for n in range(2, len(self.field_names)):
                fieldName = self.field_names[n]
                #if field_dict[fieldName]:
                field_dict[fieldName] = None
            
        if errors:
            error_list = list(errors.items())
            error_list.sort()
            error_message = '<br>\n'.join(
                ['%s: %s' % (name, value) for name, value in error_list])
            raise Invalid(error_message,
                          field_dict,
                          state,
                          error_dict=errors)    

class AllOrNothingEmpty(FormValidator):
    """
    Kõik väljad peavad olema täidetud, välja arvatud juhul, kui kõik on täitmata.
    """
    
    field_names = None
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')

    def _validate_python(self, field_dict, state):
        errors = {}
        any_not_empty = False
        for name in self.field_names:
            value = field_dict[name]
            if not (value == None or value == ''):
                # mõni väli pole tühi
                any_not_empty = True
        if any_not_empty:
            # kui mõni on täidetud, siis kontrollime, et kõik oleks täidetud
            for name in self.field_names:
                value = field_dict[name]
                if value == None or value == '':                
                    errors[name] = _("Palun sisestada")

        if errors:
            error_list = list(errors.items())
            error_list.sort()
            error_message = '<br>\n'.join(
                ['%s: %s' % (name, value) for name, value in error_list])
            raise Invalid(error_message,
                          field_dict,
                          state,
                          error_dict=errors)    

class MustBeCopy(FormValidator):
    """
    E-posti aadress sisestatakse kaks korda, kontrollime, et on sama
    """
    field_names = None
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')

    def _validate_python(self, field_dict, state):
        errors = {}
        value = field_dict[self.field_names[0]] or ''
        #if not value:
        #    # kui esimest väärtust ei ole, siis ei pea teisi kontrollima
        #    return
        for key in self.field_names[1:]:
            value2 = field_dict[key] or ''
            if value.strip() != value2.strip():
                errors = {key: _("Erineb")}
                raise Invalid(None,
                              field_dict,
                              state,
                              error_dict=errors)    

class AtLeastOne(formencode.ForEach):
    def _to_python(self, value, state=None):
        value = super(AtLeastOne, self)._to_python(value, state)
        if len(value) < 1:
            raise Invalid(_("Palun valida vähemalt üks"),
                          value, state)
        return value
