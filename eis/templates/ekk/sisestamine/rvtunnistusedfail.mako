<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Rahvusvahelise eksami tunnistuse sisestamine failist")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Rahvusvahelise eksami tunnistuse sisestamine'), h.url('sisestamine_rvtunnistused'))}
${h.crumb(_('Sisestamine failiga'), h.url('sisestamine_rvtunnistused_new_fail', rveksam_id=c.rveksam.id))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>

${h.form_save(None, multipart=True)}
<h2>
  ${c.rveksam.nimi}
</h2>
<table width="100%" class="table" cellpadding="4">
  <col width="160px%"/>
  <tr>
    <td valign="top" class="frh">${_("Test")}</td>
    <td>
      % if c.opt_testid:
      ${h.select('test_id', c.test_id, c.opt_testid, empty=True, wide=False)}
      <script>
       $(function(){
         $('select#test_id').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TESTIMISKORD', format='json')}", 
                           'test_id', $('select#testimiskord_id'),
                          ##function(){return {testiliik:"", sessioon_id:$('select#sessioon_id').val()}})
          ));
       });
      </script>
     
      % else:
      ${h.hidden('test_id', '')}
      ${h.hidden('testimiskord_id', '')}
      ${_("Rahvusvahelise eksamiga seotud testid puuduvad")}
      % endif
    </td>
  </tr>
  % if c.opt_testid:
  <tr>
    <td valign="top" class="frh">${_("Testimiskord")}</td>
    <td>
      ${h.select('testimiskord_id', c.testimiskord_id, model.Testimiskord.get_opt(test_id=c.test_id), empty=True, wide=False)}
    </td>
  </tr>
  % if c.rveksam.kantav_tulem:
  <tr>
    <td class="frh"></td>
    <td>
      ${h.checkbox('kanna', 1, checked=c.kanna, label=_("Kanna tunnistuse tulemused testisooritusele"))}
    </td>
  </tr>
  % endif
  % endif

  <tr>
    <td valign="top" class="frh">${_("Fail")}</td>
    <td>
      ${h.file('fail', value=_("Fail"))}
      ${h.submit(_('Laadi failist'))}
    </td>
  </tr>
</table>
${h.end_form()}
<p>
  ${_("CSV faili struktuur:")}<br/>
  <ol>
    % for f in c.fields:
    <li>${f}</li>
    % endfor
  </ol>
</p>
${h.link_to(_('Tunnistuste otsing'), h.url('otsing_rvtunnistused', rveksam_id=c.rveksam.id, sis_alates=h.str_from_date(model.date.today())))}

