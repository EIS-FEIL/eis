## -*- coding: utf-8 -*- 
<%namespace name="tab" file='/common/tab.mako'/>
${tab.draw('isikuvalik', None, _("Isiku valik"), c.tab1, disabled='notcurrent')}
${tab.draw('isikuandmed', None, _("Isiku andmed"), c.tab1, disabled='notcurrent')}
${tab.draw('testivalik', None, _("Testi valik"), c.tab1, disabled='notcurrent')}
${tab.draw('kinnitamine', None, _("Kinnitamine"), c.tab1, disabled='notcurrent')}
