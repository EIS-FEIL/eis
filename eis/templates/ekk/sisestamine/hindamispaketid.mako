<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Kirjalike testitööde ümbrike hindajatele väljastamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Kirjalike testitööde ümbrike hindajatele väljastamine'), 
h.url('sisestamine_valjastamine', sessioon_id=c.toimumisaeg.testimiskord.testsessioon_id))}
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>


<%include file="valjastamine.before_tabs.mako"/>

${h.form_search(url=h.url('sisestamine_valjastamine_hindamispaketid', toimumisaeg_id=c.toimumisaeg.id))}
<table width="100%" class="field">
  <tr>
    <td class="field_body" width="33%">
      <table width="100%" class="search2">
        <tr>
          <td class="fh">${_("Hindaja")}</td>
          <td>${h.select('hindaja_id', c.hindaja_id, c.hindajad_opt, empty=True)}
          </td>
          <td class="frh">${_("Hindamiskogum")}</td>
          <td>${h.select('hindamiskogum_id', c.hindamiskogum_id, c.hindamiskogumid_opt, empty=True)}
          </td>
          <td>
            ${h.btn_search()}
            ${h.submit(_('Kleebised'), id='kleeps')}
            ${h.submit(_('Kleebised ühekaupa'), id='kleeps1')}
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
${h.end_form()}
<br/>

<div class="listdiv">
<%include file="hindamispaketid_list.mako"/>
</div>
<br/>
