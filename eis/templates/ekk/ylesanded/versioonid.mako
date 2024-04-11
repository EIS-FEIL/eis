<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.ylesanne.nimi} | ${_("Versioonid")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Ülesandepank"), h.url('ylesanded'))} 
${h.crumb(c.ylesanne.nimi or c.ylesanne.id, h.url('ylesanne', id=c.ylesanne.id))} 
${h.crumb(_("Versioonid"), None, True)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>

<%
   c.can_edit = c.user.has_permission('ylesanded', const.BT_UPDATE,c.ylesanne)
%>
${h.form_search()}
<p>
% if c.can_edit:
${h.btn_to(_("Salvesta uus versioon"), h.url_current('create'), method='post')}
% endif
${h.submit(_("Võrdle versioone"), id="vrdl", style="display:none")}
${h.submit(_("Näita versiooni"), id="naita", style="display:none")}
<script>
function toggle_b()
{
    var cnt = $('input[name="versioon_id"]:checked').length;
    $('input#vrdl').toggle(cnt > 1);
    $('input#naita').toggle(cnt == 1);
}
$(function(){
  $('input[name="versioon_id"]').click(toggle_b);
  toggle_b();
});
</script>
</p>

% if not c.items:
${_("Ühtki versiooni pole salvestatud")}
% else:
<table class="table table-borderless table-striped" border="0" >
  <caption>${_("Ülesande tekstide versioonid")}</caption>
  <col width="20px"/>
  <thead>
    <tr>
      ${h.th('')}
      ${h.th(_("Salvestamise aeg"))}
      ${h.th(_("Salvestaja"))}
      ${h.th(_("Versioon"))}
      ${h.th('')}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <tr>
      <td>
        ${h.checkbox('versioon_id', rcd.id, checkedif=c.versioon_id)}
      </td>
      <td>${h.str_from_datetime(rcd.created)}</td>
      <td>
        ${c.opt.kasutaja_nimi(rcd.creator)}
      </td>
      <td>${rcd.seq}</td>
      <td>
% if c.can_edit:
        ${h.btn_to('', h.url_current('update', id=rcd.id), method='post', confirm=_("Kas oled kindel?"), mdicls='mdi-restore', title=_("Taasta"), level=0)}
        ${h.remove(h.url_current('delete', id=rcd.id))}
% endif
      </td>
    </tr>
    % endfor

    <tr>
      <td>
        ${h.checkbox('versioon_id', 0, checkedif=c.versioon_id)}
      </td>
      <td colspan="4">${_("Jooksev seis")}</td>
    </tr>

  </tbody>
</table>
${h.end_form()}
<br/>
% endif

% if c.versioonid:
  <% 
     c.jooksev = c.versioonid[0] is None 
     c.many = len(c.versioonid) > 1
     list_seq = [str(v.seq) for v in c.versioonid if v]
     if len(list_seq) > 1:
        tahised = ', '.join(list_seq[:-1]) + ' ja ' + list_seq[-1]
     elif len(list_seq) == 1:
        tahised = list_seq[0]
     else:
        tahised = ''
  %>
  <b>
  % if c.jooksev and len(list_seq) > 1:
  ${_("Kuvatakse jooksva versiooni ning versioonide {s} tekstide erinevused").format(s=tahised)}
  % elif c.jooksev and tahised:
  ${_("Kuvatakse jooksva versiooni ning versiooni {s} tekstide erinevused").format(s=tahised)}
  % elif c.jooksev:
  ${_("Kuvatakse tekstid jooksvas versioonis")}
  % elif c.many:
  ${_("Kuvatakse erinevused versioonides {s}").format(s=tahised)}
  % else:
  ${_("Kuvatakse tekstid versioonis {s}").format(s=tahised)}
  % endif
  </b>

  <table class="table" width="100%" cellspacing="5" cellpadding="5">
    <tr>
      <td>
${self.table([c.ylesanne], _("Üldandmed"))}
% if c.ylesanne.lahendusjuhis:
${self.table([c.ylesanne.lahendusjuhis], _("Lahendusjuhis"))}
% endif
${self.table(c.ylesanne.hindamisaspektid, _("Hindamisaspektid"))}
${self.table(c.ylesanne.ylesandefailid, _("Failid"))}
      </td>
    </tr>
  </table>

<br/>
  % for sp in c.ylesanne.sisuplokid:
  <table class="table" width="100%" cellspacing="5" cellpadding="5">
    <tr>
      <td>
  ${self.table([sp], _("Sisuplokk {s1} ({s2})").format(s1=sp.seq, s2=sp.tyyp_nimi), dict(sisuplokk_id=sp.id))}
  ${self.table(sp.sisuobjektid, _("Sisuploki failid"))}
    % for k in sp.kysimused:
     ${self.table([k], _("Küsimus {s}").format(s=k.kood))}
     ${self.table(k.valikud, _("Valikud"))}
     <% tulemus = k.tulemus %>
     % if tulemus:
     ${self.table(tulemus.hindamismaatriksid, _("Küsimuse {s} hindamismaatriks").format(s=k.kood))}
     % endif
    % endfor
      </td>
    </tr>
  </table>
  <br/>
  % endfor
% endif

<%def name="table(orig_list, title, urlargs=None)">
% if orig_list:
<table width="100%" border="0" >
  <tbody>
    <tr>
      <td>
        ${self.table_data(orig_list)}
      </td>
    </tr>
  </tbody>
  <thead>
    <tr>
      <td>
        ${self.table_head(title, urlargs)}
      </td>
    </tr>
  </thead>
</table>
% endif
</%def>

<%def name="table_head(title, urlargs)">
% if c.has_values:
<table cellpadding="5" cellspacing="0">
  <tr>
    <td>
      <h2>${title}</h2>
    </td>
% if urlargs and c.changed and c.can_edit:
    <td align="right">
    % for versioon in c.versioonid:
    % if versioon:
    ${h.btn_to(_("Taasta versioonist {s}").format(s=versioon.seq), 
    h.url_current('update', id=versioon.id, **urlargs), method='post', confirm=_("Kas oled kindel?"))}        
    % endif
    % endfor
    </td>
% endif
  </tr>
</table>
% if not c.changed:
${_("Tekstid ei erine")}
% endif
% endif
</%def>

<%def name="table_data(orig_list)">
<table width="100%" class="table table-borderless table-striped" border="0" >
  <col width="80px"/>
  <col width="80px"/>
  <col width="120px"/>
  <tbody>
    ${self.tr_data(orig_list)}
  </tbody>
% if c.changed:
  <thead>
    <tr>
      <th>${_("ID")}</th>
      <th>${_("Keel")}</th>
      <th>${_("Valdkond")}</th>
% for versioon in c.versioonid:
      <th>
        % if versioon:
        ${_("Versioon")} ${versioon.seq}
        % else:
        ${_("Jooksev seis")}
        % endif
      </th>
% endfor
    </tr>
  </thead>
% endif
</table>
</%def>

<%def name="tr_data(orig_list)">
<% 
   c.changed = c.has_values = False 
%>
% for lang in c.ylesanne.keeled:
% for orig in orig_list:
    <%
       trans = [orig.tran(lang, True, versioon and versioon.id or None) for versioon in c.versioonid]
       t_table = orig.get_translation_class().__table__
       columns = [column.name for column in t_table.columns if column.name not in model.t_meta_fields]
    %>
    % for column in columns:
    <%
       data = []
       changed = False
       for tran in trans:
           if tran:
              value = tran.__getattr__(column) 
              #value = str(tran.id) + ': ' + (value or '')
           else:
              value = None
           if len(data) and value not in data:
              # kui võrdleme mitut versiooni, siis kuvame ainult muudatused
              changed = True
           data.append(value)
       has_values = len([v for v in data if v is not None and v != ''])
       if not c.many and has_values:
          # kui vaatame yhtainust versiooni, siis kuvame selle kõik sisukad tekstid
          changed = True

       c.has_values |= has_values
       c.changed |= changed
     %>
    % if changed:
    <tr>
      <td>${orig.id}</td>
      <td>${model.Klrida.get_lang_nimi(lang)}</td>
      <td>${column}</td>
      % for value in data:
      <td>
        % if isinstance(value, bytes):
        <i>${_("Fail")}</i>
        % else:
        ${value}
        % endif
      </td>
      % endfor
    </tr>
    % endif
    % endfor
% endfor
% endfor
</%def>
