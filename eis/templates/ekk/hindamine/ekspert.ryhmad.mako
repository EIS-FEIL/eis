<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
  c.includes['subtabs'] = True
  c.includes['subtabs_label'] = True
  c.includes['sortablejs'] = True
%>
</%def>
<%def name="page_title()">
${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal} | ${_("Ekspertrühmad")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Eksperthindamine"), h.url('hindamine_eksperttood', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(_("Ekspertrühm"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'ekspert' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="ekspert.tabs.mako"/>
</%def>

<%def name="subtabs_label()">
  ${h.flb(_("Hindamise liik"), 'hliik')}
  <span class="brown ml-1" id="hliik">
    % if c.toimumisaeg.tulemus_kinnitatud:
    ${_("Vaide korral hindamine")}
    % else:
    ${_("IV hindamine")}
    % endif
  </span>
</%def>

<% n=0 %>
${h.form_save(None)}
<div class="row m-2">
  <div class="col-12 col-md-6 p-2">
    <h2>${_("Vaiete ekspertrühm")}</h2>
    <div id="ryhmaliikmed" class="rounded border p-2" style="min-height:100px">
    % for lv in c.ryhmaliikmed:
    <div class="draggable border-draggable" id="k_${lv.kasutaja_id}">
      ${h.mdi_icon('mdi-drag-vertical')}
      ${lv.kasutaja.nimi}
      ${h.hidden('k-%d.lv_id' % n, lv.id)}
      ${h.hidden('k-%d.kasutaja_id' % n, lv.kasutaja_id)}
      <% n += 1 %>
    </div>
    % endfor
    </div>
  </div>
  <div class="col-12 col-md-6 p-2">
    <h2>${_("Ekspertrühma määramata eksperdid")}</h2>
    <div id="rmaaramata" class="rounded border p-2" style="min-height:100px">
      % for k in c.eksperdid:
      <div class="draggable border-draggable" id="k_${k.id}">
        ${h.mdi_icon('mdi-drag-vertical')}
        ${k.nimi}
        ${h.hidden('k-%d.lv_id' % n, '')}
        ${h.hidden('k-%d.kasutaja_id' % n, k.id)}
        <% n += 1 %>
      </div>
      % endfor
    </div>
  </div>
</div>

<script>
$(function(){
var r1 = $('#ryhmaliikmed'), r2 = $('#rmaaramata');
new Sortable(r1[0], {
    animation: 150,
    group: 'shared',
    onChange: function(evt){
      r1.find('[id$="lv_id"]').val('1');
      dirty = true;
    }
});
new Sortable(r2[0], {
    animation: 150,
    group: 'shared',
    onChange: function(evt){
      r1.find('[id$="lv_id"]').val('');
      dirty = true;
    }
});
});
</script>

${h.submit()}
${h.end_form()}
