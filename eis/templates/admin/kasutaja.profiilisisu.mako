<%
   # avalikus vaates seame bit=1, et saada ainult need ained, milles
   # soorituskoha admin saab läbiviijaid lisada
   bit = not c.app_ekk and 1 or None
   c.opt_aine = c.opt.klread_kood('AINE', bit=bit)
   if c.app_ekk and c.is_edit and not c.user.has_permission('kasutajad', const.BT_UPDATE):
      # ainespetsialist ei tohi teiste ainete profiile sättida saada
      li = []
      for row in c.opt_aine:
         aine_kood = row[0]
         if c.user.has_permission('profiil', const.BT_UPDATE, aine=aine_kood):
            li.append(row)
      c.opt_aine = li
%>

<h2>${_("Vaatleja profiil")}</h2>
<div class="rounded border p-2 mb-2">
  ${self.vaatlejaprofiil()}
</div>

<h2>${_("Läbiviija ja intervjueerija profiil")}</h2>
<div class="rounded border p-2 mb-2">

${self.aineprofiilid()}
${self.hindamiskeeled()}
</div>

${h.checkbox1('f_on_testiadmin', 1, checked=c.profiil.on_testiadmin, 
disabled=not c.app_ekk and c.profiil.on_testiadmin or not c.can_update_profiil,
label=_("Isik on testide administraator"))}        

% if len(c.profiil.ainelabiviijad):
${self.labiviijatahised()}
% endif


<%def name="vaatlejaprofiil()">
<div class="form-group row">
  <div class="col-12">
    ${h.checkbox1('f_on_vaatleja', 1, checked=c.profiil.on_vaatleja, 
    disabled=not c.app_ekk and c.profiil.on_vaatleja,
    label=_("Isik on vaatleja"))}
  </div>
</div>
<div class="form-group row">
  ${h.flb3(_("Vaatlemise keeled"),'keeled')}
  <div class="col-md-9" id="keeled">
                <%
                   p_keeled = c.profiil.v_skeeled or ''
                %>
                % for (value, lang_name, value_id) in c.opt.SOORKEEL:
                  <% checked = value in p_keeled %>
                  ${h.checkbox('v_skeel', value=value, checked=checked,
                               disabled=not c.app_ekk and checked, label=lang_name)}
                % endfor
  </div>
</div>
<div class="form-group row">
  ${h.flb3(_("Koolituse aeg"),'f_v_koolitusaeg')}
  <div class="col-md-9">
    ${h.date_field('f_v_koolitusaeg', c.profiil.v_koolitusaeg,
    disabled=not c.app_ekk, wide=False)}
  </div>
</div>
<div class="form-group row">
  ${h.flb3(_("Käskkirja lisatud"),'f_v_kaskkirikpv')}
  <div class="col-md-9">
    ${h.date_field('f_v_kaskkirikpv', c.profiil.v_kaskkirikpv,
    disabled=not c.app_ekk, wide=False)}
  </div>
</div>
</%def>

<%def name="aineprofiilid()">
<% prefix="a" %>
<table width="100%" class="table table-borderless table-striped"  id="choicetbl_${prefix}">
          <thead>
            ${h.th(_("Õppeaine"))}
            ${h.th(_("Roll"))}
            ${h.th(_("Keeletase"))}
            % if c.app_ekk:
            ${h.th(_("Rangus"))}
            ${h.th(_("Standardhälve"))}
            % endif
            ${h.th(_("Koolituse aeg"))}
            ${h.th(_("Käskkirja lisatud"))}            
            <th></th>
          </thead>
          <tbody>
            % if c._arrayindexes != '':
            ## valideerimisvigade korral
            %   for cnt in c._arrayindexes.get(prefix) or []:
            ${self.aine(c.new_item(),prefix,'-%s' % cnt)}
            %   endfor
            % else:
            ## tavaline kuva
            %   for cnt,item in enumerate(c.kasutaja.aineprofiilid):
                 % if c.app_ekk and c.user.has_permission('profiil', const.BT_UPDATE, aine=item.aine_kood):
                 ${self.aine(item,prefix,'-%s' % cnt)}
                 % else:
                 ${self.aine_disabled(item,prefix,'-%s' % cnt)}
                 % endif
            %   endfor
            % endif
            <tr>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td colspan="5">
% if c.is_edit and c.can_update_profiil:
${h.button(_("Lisa"), onclick=f"grid_addrow('choicetbl_{prefix}',null,null,true);",
level=2, mdicls='mdi-plus')}
<div id="sample_choicetbl_${prefix}" class="invisible">
          <!--
             ${self.aine(c.new_item(kood='__kood__'),prefix, '__cnt__')}
            -->
</div>

<script>
function enable_tase(item)
{
    var url="${h.url('pub_formatted_valikud', kood='KEELETASE', format='json')}";
    var target=$(item).closest('tr').find('select[name*="keeletase_kood"]');
    update_options($(item), url, 'ylem_kood', target);
}
</script>
% endif
              </td>
            </tr>
          </tfoot>
</table>
</%def>

<%def name="hindamiskeeled()">
<div class="form-group row">
  ${h.flb3(_("Suulise hindamise ja intervjueerimise keeled"), "skeeled")}
  <div class="col-md-9" id="skeeled">
                <%
                   p_keeled = c.profiil.s_skeeled or ''
                %>
                % for (value, lang_name, value_id) in c.opt.SOORKEEL:
                  <% checked = value in p_keeled %>
                  ${h.checkbox('s_skeel', value=value, checked=checked,
                               disabled=not c.app_ekk and checked or not c.can_update_profiil, label=lang_name)}
                % endfor               
  </div>
</div>
<div class="form-group row">
  ${h.flb3(_("Kirjaliku hindamise keeled"),'kkeeled')}
  <div class="col-md-9" id="kkeeled">
                <%
                   p_keeled = c.profiil.k_skeeled or ''
                %>
                % for (value, lang_name, value_id) in c.opt.SOORKEEL:
                  <% checked = value in p_keeled %>
                  ${h.checkbox('k_skeel', value=value, checked=checked,
                               disabled=not c.app_ekk and checked or not c.can_update_profiil, label=lang_name)}
                % endfor
  </div>
</div>
</%def>

<%def name="aine(item, baseprefix, cnt)">
## Ühe aine rida tabelis
    <% 
       prefix = '%s%s' % (baseprefix, cnt) 
    %>
    <tr>
      <td>${h.select('%s.aine_kood' % prefix, item.aine_kood,  c.opt_aine,  onchange="enable_tase(this)")}</td>
      <td>${h.select('%s.kasutajagrupp_id' % prefix, item.kasutajagrupp_id,
      c.opt.ainelabiviijagrupp)}</td>
      <td>
        ${h.select('%s.keeletase_kood' % prefix, item.keeletase_kood, 
        c.opt.klread_kood('KEELETASE', ylem_kood=item.aine_kood,
        ylem_required=True, empty=True))}
      </td>
      % if c.app_ekk:
      <td>${h.int5('%s.rangus' % (prefix), item.rangus)}</td>
      <td>${h.int5('%s.halve' % (prefix), item.halve)}</td>
      % endif
      <td>${h.date_field('%s.koolitusaeg' % (prefix), item.koolitusaeg,
        ronly=not c.is_edit or not c.app_ekk)}</td>
      <td>${h.date_field('%s.kaskkirikpv' % (prefix), item.kaskkirikpv,
        ronly=not c.is_edit or not c.app_ekk)}</td>      
      <td>
        % if c.is_edit:
        ${h.grid_remove()}
        % endif
        ${h.hidden('%s.id' % prefix, item.id)}
      </td>
    </tr>
</%def>


<%def name="aine_disabled(item, baseprefix, cnt)">
## Ühe aine rida tabelis avalikus vaates, kus ei saa muuta
    <tr>
      <td>${item.aine_nimi}</td>
      <td>${item.kasutajagrupp.nimi}</td>
      <td>${item.keeletase_nimi}</td>
      % if c.app_ekk:
      <td>${h.fstr(item.rangus)}</td>
      <td>${h.fstr(item.halve)}</td>
      % endif
      <td>${h.str_from_date(item.koolitusaeg)}</td>
      <td>${h.str_from_date(item.kaskkirikpv)}</td>      
      <td></td>
    </tr>
</%def>

<%def name="labiviijatahised()">
<table class="table" >
  <caption>${_("Läbiviija tähised")}</caption>
  <col width="50px"/>
  <col/>
  <tbody>
    % for rcd in c.profiil.ainelabiviijad:
    <tr>
      <td>${rcd.tahis}</td>
      <td>${rcd.aine_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
</%def>
