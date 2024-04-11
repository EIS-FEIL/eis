<%namespace name="tab" file='/common/tab.mako'/>
<% 
  edit = c.is_edit and '_edit' or ''
%>
% if c.user.has_permission('hindajamaaramine', const.BT_SHOW, obj=c.test):
  % if c.toimumisaeg.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I):
${tab.draw('maaramine', h.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id),
_("Läbiviijate määramine"), c.tab1)}
  % else:
${tab.draw('maaramine', h.url('hindamine_hindajad3', toimumisaeg_id=c.toimumisaeg.id),
_("Läbiviijate määramine"), c.tab1)}
  % endif
% endif
% if c.user.has_permission('ekk-hindamine', const.BT_SHOW, obj=c.test):
${tab.draw('arvutused', h.url('hindamine_arvutused', toimumisaeg_id=c.toimumisaeg.id),
_("Tulemuste arvutus"), c.tab1)}
% endif
% if c.user.has_permission('hindamisanalyys', const.BT_SHOW) or c.user.has_permission('vastusteanalyys', const.BT_SHOW, obj=c.test):
${tab.draw('analyys', h.url('hindamine_analyys_protokollid', toimumisaeg_id=c.toimumisaeg.id),
_("Hindamise analüüs"), c.tab1)}
% endif
% if c.user.has_permission('juhendamine', const.BT_SHOW, obj=c.test):
${tab.draw('juhendamine', h.url('hindamine_juhendamised', toimumisaeg_id=c.toimumisaeg.id),
_("Läbiviijate juhendamine"), c.tab1)}
% endif
% if c.user.has_permission('eksperthindamine', const.BT_SHOW, obj=c.test):
${tab.draw('ekspert', h.url('hindamine_eksperttood', toimumisaeg_id=c.toimumisaeg.id),
_("Eksperthindamine"), c.tab1)}
% endif

