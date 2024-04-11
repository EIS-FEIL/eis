<div class="d-flex justify-content-between">
<h2>${c.item.nimi}</h2>

<div>
${h.btn_to_dlg(_('Muuda nimetus'),
h.url_current('edit', id=c.item.id, sub='nimi', partial=True),
dlgtitle=c.item.nimi, mdicls="mdi-file-edit")}
</div>
</div>

% if not c.ryhmaliikmed:
${h.alert_notice(_("Rühmas ei ole õpilasi"))}
% else:
<table class="table table-striped" border="0" >
  <col/>
  <col/>
  <col/>
  <col/>
  <col/>
  <col width="25px"/>
  <thead>
    <tr>
      ${h.th(_('Jrk'))}
      ${h.th(_('Isikukood'))}
      ${h.th(_('Nimi'))}
      ${h.th(_('Keel'))}
      ${h.th(_('Klass'))}
      ${h.th('')}
    </tr>
  </thead>
  <tbody>
    % for ind, (rl_id, isikukood, nimi, oppekeel, klass, paralleel) in enumerate(c.ryhmaliikmed):
    <tr>
      <td>${ind+1}</td>
      <td>${isikukood}</td>
      <td>${nimi}</td>
      <td>${const.EHIS_LANG_NIMI.get(oppekeel)}</td>
      <td>${klass}${paralleel}</td>
      <td>${h.remove(h.url('opperyhm_delete_otsiopilane', id=rl_id, opperyhm_id=c.item.id), _('Kas oled kindel?'))}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
<p>
${_("Lisa õpilased:")}
${h.btn_to_dlg(_('Isikukoodiga'), h.url('opperyhm_otsiopilased', opperyhm_id=c.item.id, sub='ik'),
title=_('Õpilase lisamine'), width=700)}
% if c.user.koht_id and c.user.has_permission('klass', const.BT_UPDATE, obj=c.user.koht):
${h.btn_to_dlg(_('EHISest'), h.url('opperyhm_otsiopilased', opperyhm_id=c.item.id, sub='ehis'),
title=_('Õpilaste lisamine'), width=700)}
% endif
${h.btn_to_dlg(_('Failist'), h.url('opperyhm_otsiopilased', opperyhm_id=c.item.id, sub='fail'),
title=_('Õpilaste lisamine'), width=700)}

<span style="float:right;">
  ${h.btn_remove(value=_('Kustuta rühm'))}
</span>
</p>

% if c.ryhmatood:
<h2>${_("Rühma liikmetele jagatud tööd")}</h2>
<table width="100%" class="table table-striped" border="0" >
  <thead>
    <tr>
      ${h.th(_('Nimetus'))}
      ${h.th(_('Õppeaine'))}
      ${h.th(_('Ülesannete arv'))}
      ${h.th(_('Osalejate arv'))}
    </tr>
  </thead>
  <tbody>
    % for nimekiri_id, test_id, t_nimi, aine, cnt_ty, cnt_j in c.ryhmatood:
    <tr>
      <td>${h.link_to(t_nimi, h.url('test_nimekiri', test_id=test_id, testiruum_id=0, id=nimekiri_id))}</td>
      <td>${model.Klrida.get_str('AINE', aine)}</td>
      <td>${cnt_ty}</td>
      <td>${cnt_j}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

