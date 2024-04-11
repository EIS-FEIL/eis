<%namespace name="tab" file='/common/tab.mako'/>
<% 
   edit = c.is_edit and '_edit' or ''
%>
${tab.draw('soorituskohad', h.url('korraldamine_soorituskohad', toimumisaeg_id=c.toimumisaeg.id),
_("Soorituskohtade planeerimine"), c.tab1)}
% if not c.test or not c.test.on_kutse:
${tab.draw('labiviijad', h.url('korraldamine_labiviijad',
toimumisaeg_id=c.toimumisaeg.id), _("Läbiviijate määramine"), c.tab1)}

% if c.toimumisaeg.testiosa.vastvorm_kood==const.VASTVORM_KONS:
${tab.draw('konsultatsiooninimekirjad', h.url('korraldamine_konsultatsiooninimekirjad',
toimumisaeg_id=c.toimumisaeg.id), _("Konsultatsiooninimekirjad"))}

% else:
${tab.draw('valjastus', h.url('korraldamine_valjastus',
toimumisaeg_id=c.toimumisaeg.id), _("Materjalide väljastus"), c.tab1)}
${tab.draw('tagastus', h.url('korraldamine_tagastuskotid',
toimumisaeg_id=c.toimumisaeg.id), _("Materjalide tagastus"), c.tab1)}
${tab.draw('muu', h.url('korraldamine_eksamilogi',
toimumisaeg_id=c.toimumisaeg.id), _("Muu"), c.tab1)}
% endif
% endif
