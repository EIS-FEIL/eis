<%namespace name="tab" file='/common/tab.mako'/>
<% 
   edit = c.is_edit and '_edit' or ''
%>
% if not c.testikoht:
${tab.draw('sooritajad', h.url('korraldamine_koht_sooritajad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht_id),
_("Soorituskohata testisooritajad"))}

% elif c.toimumisaeg.testiosa.vastvorm_kood==const.VASTVORM_KONS:
${tab.draw('labiviijad', h.url('korraldamine_koht_labiviijad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id), _("Läbiviijad"))}
${tab.draw('yldandmed', h.url('korraldamine_koht_yldandmed',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id), _("Üldandmed"))}

% else:
${tab.draw('sooritajad', h.url('korraldamine_koht_sooritajad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id), _("Sooritajad"))}
${tab.draw('labiviijad', h.url('korraldamine_koht_labiviijad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id), _("Läbiviijad"))}
% if not c.test or not c.test.on_kutse:
${tab.draw('logistika', h.url('korraldamine_koht_logistika',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id), _("Logistika"))}
${tab.draw('yldandmed', h.url('korraldamine_koht_yldandmed',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id), _("Üldandmed"))}
% endif
% endif
