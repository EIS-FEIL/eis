## -*- coding: utf-8 -*- 
## Oma testidele registreerimiseks testimiskordade otsimine
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testile registreerimise nimekirjad")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Registreerimisnimekirjad"))}
</%def>
${h.form_search(url=h.url('nimekirjad_testid'))}
<table width="100%" class="field" >
  <tr>
    <td valign="top" class="field_body" width="50%">
      <table width="100%"  class="search">
        <tr>
          <td class="fh" nowrap>${_("Testi ID")}</td>
          <td width="80%">${h.int10('test_id', c.test_id)}</td>
        </tr>
        <tr>
          <td class="fh" nowrap>${_("Testi nimetus")}</td>
          <td>${h.text('nimi', c.nimi)}</td>
        </tr>
        <tr>
          ${h.td_field(_("Õppeaine"), h.select('aine', c.aine, c.opt.klread_kood('AINE', empty=True)))}
        </tr>
      </table>
    </td>
    
    <td valign="top" class="field_body" width="50%">
      <table width="100%"  class="search">
        <tr>
          <td class="fh">${_("Kasutamisviis")}</td>
          <td width="80%">
            <%
               if c.user.on_pedagoog:
                  opt_tase = c.opt.opt_avalik[2:]
               else:
                  opt_tase = [(const.AVALIK_MAARATUD, _("Sooritajate nimistu")),
                              (const.AVALIK_SOORITAJAD, _("Kõigile vabalt lahendamiseks"))]
            %>
            ${h.select('avaldamistase', c.avaldamistase, opt_tase)}
          </td>
        </tr>
        ##% endif
        <tr>
          <td class="fh" nowrap>${_("Nimekirja looja")}</td>
          ##<td>${h.text('esitaja', c.esitaja)}</td>
          <td>
            <%
               if c.user.on_pedagoog:
                  opt_esitajad = model.Nimekiri.get_esitajad_opt(c.user.koht_id)
               else:
                  opt_esitajad = [(c.user.id, c.user.fullname)]
            %>
            ${h.select('esitaja_id', c.esitaja_id, opt_esitajad, empty=True)}
          </td>
        </tr>
        <tr>
          <td class="field-header" colspan="2">${h.btn_search()}</td>
        </tr>
      </table>
    </td>
  </tr>
</table>

${h.end_form()}

<div class="listdiv">
<%include file="testid_list.mako"/>
</div>
