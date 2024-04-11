<%namespace name="tab" file='/common/tab.mako'/>
<% 
  edit = c.is_edit and '_edit' or ''
  ta = c.testikoht.toimumisaeg
  testiosa = ta.testiosa
%>
${tab.draw('sooritajad', h.url('korraldamine_sooritajad', testikoht_id=c.testikoht.id), _("Ruumid ja sooritajad"), c.tab1)}
${tab.draw('labiviijad', h.url('korraldamine_labiviijad', testikoht_id=c.testikoht.id), _("Läbiviijad"), c.tab1)}
${tab.draw('materjalid', h.url('korraldamine_materjalid', testikoht_id=c.testikoht.id), _("Materjalid"), c.tab1)}
## kas siin võiks olla ka VASTVORM_SH ?
% if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I):
<%
  on_hindajad = \
     ta.hindaja1_maaraja in const.MAARAJA_KOHAD or \
     ta.hindaja1_maaraja_valim in const.MAARAJA_KOHAD or \
     ta.hindaja2_maaraja in const.MAARAJA_KOHAD or \
     ta.hindaja2_maaraja_valim in const.MAARAJA_KOHAD
%>
% if on_hindajad:
## soorituskoht tohib kirjalikku hindajat määrata
${tab.draw('hindajad', h.url('korraldamine_hindajad', testikoht_id=c.testikoht.id), _("Hindajad"), c.tab1)}
% endif
% endif
