<%inherit file="/common/page.mako"/>

<%def name="page_title()">
${_("Ülesannete hulgi muutmine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Ülesandepank"), h.url('ylesanded'))} 
${h.crumb(_("Ülesannete hulgi muutmine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>

<%def name="page_headers()">
<style>
  ## eemaldame valiku ymbert raami ja taustavärvi, lisame alljoone
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice {
  background-color: #fff;
  overflow:hidden;
  border: none;
  border-radius:0;
  border-bottom: .5px solid #afafaf;
  }
  ## proovime eemaldada alljont viimaselt valikult
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice:last-child {
  border-bottom: none;
  }
  ## teeme valikud kogu rea pikkuseks
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice {
    float:none;
  }
  ## ristike veidi suuremaks (muidu on 75%)
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice__remove {
  font-size:150%;
  }
  ## valiku tekst ristikesega samale reale kogu rea laiuses
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice div.row{
  width:99%;
  float:right;
  }
  div.ylesandeaine {
    margin:10px 10px 0 10px;
  }
</style>
</%def>

<%
  can_classify = True
  can_update_roll = True
  can_kvaliteet = True
  can_ylkogu = True
%>
<br/>
${h.form_save(None)}
<table class="table table-borderless table-striped"  style="min-width:900px">
  <caption>${_("Ülesanded")}</caption>
  <col width="50px"/>
  <col/>
  <thead>
    <tr>
      <th>${_("ID")}</th>
      <th>${_("Nimetus")}</th>
      <th>${_("Õppeaine, teema/alateema, õpitulemus")}</th>
      <th>${_("E-kogu")}</th>
      <th>${_("Olek")}</th>
      <th>${_("Disain")}</th>
      <th>${_("Salastamine")}</th>
      <th>${_("Lukus")}</th>
      <th>${_("Autor")}</th>
      <th>${_("Kooliastmed")}</th>
      <th>${_("Testi liik")}</th>
      <th>${_("Ülesande kasutus")}</th>
      <th>${_("Kvaliteedimärk")}</th>
      <th>${_("Tähemärkide arv")}</th>
    </tr>
  </thead>
  <tbody>
    <%
       salastatud = set()
       lukus = 0
       taastalukustus = False
       tahemargid = {}
    %>
    % for yl_id in c.yl_id:
    <% 
       y = model.Ylesanne.get(yl_id)
       if not c.can_ylhulgi and not y.salastatud and not y.has_permission('ylesanded', const.BT_VIEW, None, c.user, True):
          # kasutajal poleks õigust ylesandele ligipääsuks, kui see oleks salastatud
          # ei või salastada
          can_classify = False
       salastatud.add(y.salastatud)
       if y.lukus: 
          lukus = max(lukus, y.lukus)
          lukustusvajadus = False
       else:
          lukustusvajadus = y.get_lukustusvajadus()
          if lukustusvajadus:
             taastalukustus = True
       kooliastmed = y.kooliastmed
       y_tahemargid = {}
       for t_y in y.trans:
          if t_y.ylesandeversioon_id is None and t_y.tahemargid is not None:
             y_tahemargid[t_y.lang] = t_y.tahemargid
             tahemargid[t_y.lang] = (tahemargid.get(t_y.lang) or 0) + y_tahemargid[t_y.lang]
       y_tahemargid[y.lang] = y.tahemargid or 0
       tahemargid[y.lang] = (tahemargid.get(y.lang) or 0) + y_tahemargid[y.lang]
       for lang in y.keeled:
          if lang not in y_tahemargid:
             y_tahemargid[lang] = 0
       can_update_roll &= c.user.has_permission('ylesanderoll', const.BT_UPDATE, y)
       can_kvaliteet &= c.user.has_permission('ylkvaliteet', const.BT_UPDATE, y)
       can_ylkogu &= y.staatus not in const.Y_ST_AV
    %>
    <tr>
      <td>
        ${yl_id}
        ${h.hidden('yl_id', yl_id)}
      </td>
      <td>${h.link_to(y.nimi, h.url('edit_ylesanne', id=y.id))}</td>
      <td>
        % for ya in y.ylesandeained:
        <div>
        ${ya.aine_nimi}
        % for yt in ya.ylesandeteemad:
        <div style="padding-left:8px">
        ${yt.teema_nimi}
        % if yt.alateema_kood:
        / ${yt.alateema_nimi}
        % endif
        </div>
        % endfor
        % for r in ya.ylopitulemused:
          <div style="padding-left:8px">
            ${r.opitulemus_klrida.nimi}
          </div>
        % endfor
        </div>
        % endfor
      </td>
      <td>
        % for ky in y.koguylesanded:
        ${ky.ylesandekogu.nimi}<br/>
        % endfor
      </td>
      <td>${y.staatus_nimi}</td>
      <td>
        % if y.disain_ver == const.DISAIN_EIS1:
        ${_("Vana disain")}
        % else:
        ${_("Uus disain")}
        % endif
      </td>
      <td>${y.salastatud_nimi()}</td>
      <td>
        ${y.lukus_nimi}
        % if lukustusvajadus:
        ${h.alert_error(_("Ülesanne peaks olema lukus, kuid on lukust lahti võetud."))}
        % endif
      </td>
      <td>${y.autor}</td>
      <td>
        % for aste in kooliastmed:
        % if aste == y.aste_kood:
        <u title="${_("Peamine kooliaste")}">
          ${model.Klrida.get_str('ASTE', aste)}
        </u>
        % else:
          ${model.Klrida.get_str('ASTE', aste)}        
        % endif
        <br/>
        % endfor
      </td>
      <td>
        % for r in y.testiliigid:
        ${r.nimi}<br/>
        % endfor
      </td>
      <td>
        % for r in y.kasutliigid:
        ${r.kasutliik_nimi}<br/>
        % endfor       
      </td>
      <td>${y.kvaliteet_nimi}</td>
      <td>
        % if y_tahemargid:
        <% li = [(c.opt.lang_sort(lang), lang, cnt) for lang, cnt in y_tahemargid.items()] %>
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
      <td colspan="12" align="right">${_("Kokku")}</td>
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

${h.btn_to_dlg(_("Muuda õppeaine"), h.url_current('edit', id=c.ylesanded_id, sub='aine', partial=True), 
title=_("Ülesande õppeained"), width=560)}
${h.btn_to_dlg(_("Muuda teema"), h.url_current('edit', id=c.ylesanded_id, sub='teema', partial=True), 
title=_("Ülesande õppeained ja teemad"), width=750)}
${h.btn_to_dlg(_("Muuda õpitulemus"), h.url_current('edit', id=c.ylesanded_id, sub='opitulemus', partial=True), 
title=_("Ülesande õppeained ja õpitulemused"), width=750)}
% if can_ylkogu:
${h.btn_to_dlg(_("Vali e-kogu"), h.url_current('edit', id=c.ylesanded_id, sub='kogu', partial=True), 
title=_("E-kogud"), width=560)}
% endif
${h.btn_to_dlg(_("Muuda olek"), h.url_current('edit', id=c.ylesanded_id, sub='olek', partial=True), 
title=_("Ülesande olek"), width=560)}
${h.btn_to_dlg(_("Muuda disain"), h.url_current('edit', id=c.ylesanded_id, sub='disain', partial=True), 
title=_("Ülesande disain"), width=560)}

% if const.SALASTATUD_POLE in salastatud and can_classify:
${h.btn_to_dlg(_("Salasta"), h.url_current('edit', id=c.ylesanded_id, sub='secret',partial=True), 
title=_("Salasta"), width=560)}
% endif

% if const.SALASTATUD_LOOGILINE in salastatud or const.SALASTATUD_SOORITATAV in salastatud:
${h.btn_to_dlg(_("Lõpeta salastatus"), h.url_current('edit', id=c.ylesanded_id, sub='nosecret',partial=True), title=_("Lõpeta salastatus"), width=560)}

##${h.btn_to_dlg(u'Krüpti', h.url_current('edit', id=c.ylesanded_id, sub='secret',partial=True), title=_("Krüpti"), width=560)}
% endif

##% if const.SALASTATUD_KRYPTITUD in salastatud:
##${h.btn_to_dlg(u'Krüpti lahti',
##h.url_current('edit',sub='decrypt',partial=True),
##title=_("Krüpti lahti"), width=600)}      
##% endif

% if lukus:
% if lukus in (const.LUKUS_KATSE_SOORITATUD, const.LUKUS_KATSE_HINNATUD) or c.user.has_permission('ylesannelukustlahti', const.BT_UPDATE):
    ${h.btn_to(_("Võta lukust lahti"), h.url_current('update', id=c.ylesanded_id, sub='avalukk'),
     method='post',
     confirm=_("Luku eemaldamisel on kerge teha asju, mis viivad andmed ebakõlla. \nKas oled kindel, et soovid lukku eemaldada?"))}
% endif
% endif

% if taastalukustus:
    ${h.btn_to(_("Taasta lukustus"), h.url_current('update', id=c.ylesanded_id, sub='taastalukk'),
    method='post')}
% endif

${h.btn_to_dlg(_("Muuda autor"), h.url_current('edit', id=c.ylesanded_id, sub='autor', partial=True), 
title=_("Autor"), width=560)}

${h.btn_to_dlg(_("Muuda kooliaste"), h.url_current('edit', id=c.ylesanded_id, sub='aste', partial=True), 
title=_("Kooliastmed"), width=750)}

${h.btn_to_dlg(_("Muuda testiliik"), h.url_current('edit', id=c.ylesanded_id, sub='testiliik', partial=True), 
title=_("Testi liik"), width=750)}

${h.btn_to_dlg(_("Muuda kasutus"), h.url_current('edit', id=c.ylesanded_id, sub='kasutus', partial=True), 
title=_("Ülesande kasutus"), width=750)}
% if can_kvaliteet:
${h.btn_to_dlg(_("Muuda kvaliteedimärk"), h.url_current('edit', id=c.ylesanded_id, sub='kvaliteet', partial=True), 
title=_("Ülesande kvaliteedimärk"), width=560)}
% endif
${h.btn_to_dlg(_("Lisa tõlkekeel"), h.url_current('edit', id=c.ylesanded_id, sub='tolge', partial=True), 
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
  <caption>${_("Ülesannetega seotud isikud")}</caption>
## Siin kuvatakse kasutajad, kellele on antud õigused 
## selle konkreetse ülesande kohta. Need isikud omavad 
## ülesandele ligipääsus ka siis, kui ülesanne on salastatud.
## Märkus: õigus võidakse anda ülesande suhtes või tuleneda testist 
## (testi suhtes antud õigused laienevad kõikidele testi valitud ülesannetele).
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
    % for k_id, grupp_id, nimi, yisikud in c.ylesandeisikud:
    <tr>
      <td>${nimi}</td>
      <td>${model.Kasutajagrupp.get(grupp_id).nimi}</td>
      <td>
        % for yisik in yisikud:
        ${_("Ülesande ID")} ${yisik.ylesanne_id} 
        % if yisik.kehtib_kuni_ui:
          (${_("kehtib kuni {s}").format(s=h.str_from_date(yisik.kehtib_kuni_ui))})
        % endif
        <br/>
        % endfor
      </td>
      % if can_update_roll:
      <td>
        ${h.remove(h.url('ylesanded_delete_hulga', id=c.ylesanded_id,
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
        ${h.btn_to_dlg(_("Lisa"), h.url('ylesanded_hulgi_isikud', ylesanded_id=c.ylesanded_id, partial=True), title=_("Ülesandega seotud isikute lisamine"), width=500)}
      </td>
    </tr>
  </tfoot>
% endif  
</table>
<br/>

${h.btn_back(url=h.url('ylesanded'))}
