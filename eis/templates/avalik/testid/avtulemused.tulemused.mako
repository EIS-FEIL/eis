<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>
<%def name="require()">
<%
c.includes['subtabs'] = True
c.includes['subtabs_label'] = True  
%>
</%def>
<%def name="page_title()">
${c.test.nimi or ''} | ${_("Tulemused")}
</%def>      
<%def name="breadcrumbs()">
% if c.test.on_jagatudtoo:
${h.crumb(_('Töölaud'), h.url('tookogumikud'))}
% endif
${h.crumb(c.test.nimi or _('Test'), h.url('testid_yldandmed', id=c.test_id, testiruum_id=c.testiruum_id))} 
${h.crumb(_('Tulemused'), h.url('test_avtulemused', test_id=c.test_id, testiruum_id=c.testiruum_id))}
</%def>

<%def name="draw_subtabs()">
<% c.tab2 = 'avtulemused' %>
<%include file="avtulemused.tabs.mako"/>
</%def>

<%def name="subtabs_label()">
<% c.testiosavalik_action = h.url_current('index') %>
  <%include file="testiosavalik.mako"/>
</%def>

% if len(c.sooritused) == 0:
${h.alert_notice(_("Sooritajaid pole lisatud"), False)}
% else:
<table class="table table-borderless table-striped tablesorter">
  <thead>
    <tr>
      % for h_sort, h_title in c.header:
      % if h_sort:
      ${h.th_sort(h_sort, h_title)}
      % else:
      ${h.th(h_title)}
      % endif
      % endfor
    </tr>
  </thead>
  <tbody>
  % for n, rcd in enumerate(c.sooritused):
      <%
        row = c.prepare_item(rcd, n)
        tos = rcd[0]
        if tos.staatus == const.S_STAATUS_TEHTUD:
           rcd_url = h.url('test_labiviimine_sooritusaknas', test_id=c.test_id, testiruum_id=c.testiruum_id, id=tos.id)
        else:
           rcd_url = None

        if c.on_kasitsi and tos.staatus == const.S_STAATUS_TEHTUD:
           h_url = h.url('test_sooritus_hindamised', test_id=c.test_id, testiruum_id=c.testiruum_id, sooritus_id=tos.id)
        else:
           h_url = None
      %>
  <tr>
    % for ind, value in enumerate(row):
    <td>
       % if ind == 0 and rcd_url:
         ${h.link_to(value, rcd_url, class_="sjalink pl-0")}
       % elif ind == c.ind_h and h_url:
         ${h.link_to(value, h_url)}
       % else:
         ${value}
       % endif
    </td>
    % endfor
  </tr>
  % endfor
  </tbody>
</table>

<script>
$(function(){
$('a.sjalink').click(function(){
$('#sja').remove();
open_dlg({dialog_id:'sja', title: $(this).text(), width: Math.min(window.innerWidth-20, 1400), iframe_url:this.href, autosize:true});
return false;
   });
});
</script>

${h.btn_to(_("CSV"), h.url_current('index', csv=1))}
% endif
