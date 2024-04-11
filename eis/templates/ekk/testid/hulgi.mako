<%inherit file="/common/page.mako"/>

<%def name="page_title()">
${_("Testide hulgi muutmine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(_("Testide hulgi muutmine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>

<%def name="page_headers()">
</%def>

<%
  can_classify = True
  can_update_roll = True
  can_kvaliteet = True
%>
<br/>
${h.form_save(None)}
<table class="table table-borderless table-striped"  style="min-width:900px">
  <caption>${_("Testid")}</caption>
  <col width="50px"/>
  <col/>
  <thead>
    <tr>
      <th>${_("ID")}</th>
      <th>${_("Nimetus")}</th>
      <th>${_("Õppeaine")}</th>
      <th>${_("Olek")}</th>
      <th>${_("Salastamine")}</th>
      <th>${_("Autor")}</th>
      <th>${_("Kooliastmed")}</th>
      <th>${_("Testi liik")}</th>
      <th>${_("Kvaliteedimärk")}</th>
      <th>${_("Tähemärkide arv")}</th>
    </tr>
  </thead>
  <tbody>
    <%
       salastatud = set()
       tahemargid = {}
    %>
    % for t_id in c.t_id:
    <% 
       t = model.Test.get(t_id)
       if not c.can_testhulgi and not t.salastatud and not c.user.has_permission('ekk-testid', const.BT_VIEW, obj=t):
          # kasutajal poleks õigust testile ligipääsuks, kui see oleks salastatud
          # ei või salastada
          can_classify = False
       salastatud.add(t.salastatud)
       kooliastmed = t.kooliastmed
       t_tahemargid = {}
       for tr_t in t.trans:
          if tr_t.tahemargid is not None:
             t_tahemargid[tr_t.lang] = tr_t.tahemargid
             tahemargid[tr_t.lang] = (tahemargid.get(tr_t.lang) or 0) + t_tahemargid[tr_t.lang]
       t_tahemargid[t.lang] = t.tahemargid or 0
       tahemargid[t.lang] = (tahemargid.get(t.lang) or 0) + t_tahemargid[t.lang]
       for lang in t.keeled:
          if lang not in t_tahemargid:
             t_tahemargid[lang] = 0
       can_update_roll &= c.user.has_permission('testiroll', const.BT_UPDATE, t)
       can_kvaliteet &= c.user.has_permission('ylkvaliteet', const.BT_UPDATE, t)
    %>
    <tr>
      <td>
        ${t_id}
        ${h.hidden('t_id', t_id)}
      </td>
      <td>${h.link_to(t.nimi, h.url('edit_test', id=t.id))}</td>
      <td>${t.aine_nimi}</td>
      <td>${t.staatus_nimi}<br/>${t.avaldamistase_nimi}</td>
      <td>${t.salastatud_nimi()}</td>
      <td>${t.autor}</td>
      <td>
        % for aste in kooliastmed:
        <div>${model.Klrida.get_str('ASTE', aste)}</div>
        % endfor
      </td>
      <td>${t.testiliik_nimi}</td>
      <td>${t.kvaliteet_nimi}</td>
      <td>
        % if t_tahemargid:
        <% li = [(c.opt.lang_sort(lang), lang, cnt) for lang, cnt in t_tahemargid.items()] %>
        % for r in sorted(li):
        ${model.Klrida.get_lang_nimi(r[1])} ${r[2]}<br/>
        % endfor
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
  <tfoot>
    <tr>
      <td colspan="9" align="right">${_("Kokku")}</td>
      <td>
        <% li = [(c.opt.lang_sort(lang), lang, cnt) for lang, cnt in tahemargid.items()] %>
        % for r in sorted(li):
        ${model.Klrida.get_lang_nimi(r[1])} ${r[2]}<br/>
        % endfor
      </td>
    </tr>
  </tfoot>
</table>
<br/>

<p>
${h.btn_to_dlg(_("Muuda õppeaine"), h.url_current('edit', id=c.testid_id, sub='aine', partial=True), 
title=_("Testi õppeaine"), width=560)}  
${h.btn_to_dlg(_("Muuda olek"), h.url_current('edit', id=c.testid_id, sub='olek', partial=True), 
title=_("Testi olek"), width=560)}
% if const.SALASTATUD_POLE in salastatud and can_classify:
${h.btn_to_dlg(_("Salasta"), h.url_current('edit', id=c.testid_id, sub='secret',partial=True), 
title=_("Salasta"), width=560)}
% endif
% if const.SALASTATUD_LOOGILINE in salastatud or const.SALASTATUD_SOORITATAV in salastatud:
${h.btn_to_dlg(_("Lõpeta salastatus"), h.url_current('edit', id=c.testid_id, sub='nosecret',partial=True), title=_("Lõpeta salastatus"), width=560)}
% endif

${h.btn_to_dlg(_("Muuda autor"), h.url_current('edit', id=c.testid_id, sub='autor', partial=True), 
title=_("Autor"), width=560)}
${h.btn_to_dlg(_("Muuda kooliaste"), h.url_current('edit', id=c.testid_id, sub='aste', partial=True), 
title=_("Kooliastmed"), width=750)}
${h.btn_to_dlg(_("Muuda testiliik"), h.url_current('edit', id=c.testid_id, sub='testiliik', partial=True), 
title=_("Testi liik"), width=750)}

% if can_kvaliteet:
${h.btn_to_dlg(_("Muuda kvaliteedimärk"), h.url_current('edit', id=c.testid_id, sub='kvaliteet', partial=True), 
title=_("Testi kvaliteedimärk"), width=560)}
% endif
${h.btn_to_dlg(_("Lisa tõlkekeel"), h.url_current('edit', id=c.testid_id, sub='tolge', partial=True), 
title=_("Tõlkekeele lisamine"), width=560)}
</p>
<br/>

<table border="0"  class="table table-borderless table-striped tablesorter" style="min-width:900px">
  <col/>
  <col/>
  <col/>
  % if can_update_roll:
  <col width="20px"/>
  % endif
  <caption>${_("Testidega seotud isikud")}</caption>
  <thead>
    <tr>
      <th>${_("Nimi")}</th>
      <th>${_("Roll")}</th>
      <th>${_("Ülesanne")}</th>
      % if can_update_roll:
      <th sorter="false"></th>
      % endif
    </tr>
  </thead>
  <tbody>
    % for k_id, grupp_id, nimi, yisikud in c.testiisikud:
    <tr>
      <td>${nimi}</td>
      <td>${model.Kasutajagrupp.get(grupp_id).nimi}</td>
      <td>
        % for yisik in yisikud:
        ${_("Testi ID")} ${yisik.test_id} 
        % if yisik.kehtib_kuni_ui:
          (${_("kehtib kuni {s}").format(s=h.str_from_date(yisik.kehtib_kuni_ui))})
        % endif
        <br/>
        % endfor
      </td>
      % if can_update_roll:
      <td>
        ${h.remove(h.url('testid_delete_hulga', id=c.testid_id,
        kasutaja_id=k_id, grupp_id=grupp_id, sub='isik'))}
      </td>
      % endif
    </tr>
    % endfor
  </tbody>
% if can_update_roll:
  <tfoot>
    <tr>
      <td colspan="4" class="field_body">
        ${h.btn_to_dlg(_("Lisa"), h.url('testid_hulgi_isikud', testid_id=c.testid_id, partial=True), title=_("Testiga seotud isikute lisamine"), width=500)}
      </td>
    </tr>
  </tfoot>
% endif  
</table>
<br/>

${h.btn_back(url=h.url('testid'))}
