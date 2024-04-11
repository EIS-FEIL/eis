<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Ametnikud")} | ${_("Kasutajate laadimine")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Ametnikud"), h.url('admin_ametnikud'))} 
${h.crumb(_("Kasutajate laadimine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

${h.form_save(None, h.url('admin_ametnikulaadimine'), multipart=True)}

<table  class="table" width="100%">
  <col width="150"/>
  <tr>
    <td class="fh">${_("Läbiviija roll")}</td>
    <td>
      <%
        grupid_id = (const.GRUPP_AINETOORYHM, const.GRUPP_SISESTAJA, const.GRUPP_P_KORRALDUS, const.GRUPP_REGAJA, const.GRUPP_VAIDEKOM, const.GRUPP_VAIDEKOM_ESIMEES)
        opt_grupp = [(0, _("Ilma rollita"))] + [(g_id, c.opt.grupp_nimi(g_id)) for g_id in grupid_id]
      %>
      ${h.select('kasutajagrupp_id', c.kasutajagrupp_id, opt_grupp, 
      onchange="grupp_changed()")}
    </td>      
  </tr>
  <tr class="d-none r_aine">
    <td class="fh">${_("Õppeaine")}</td>
    <td>${h.select('aine_kood', c.aine_kood, 
      c.opt.klread_kood('AINE', vaikimisi=c.aine_kood))}</td>
  </tr>
  <tr class="d-none r_testiliik">
    <td class="fh">${_("Testiliik")}</td>
    <td>${h.select('testiliik_kood', c.testiliik_kood, c.opt.testiliik, empty=True)}</td>
  </tr>
  <tr class="d-none r_piirkond">
    <td class="fh">${_("Piirkond")}</td>
    <td>
      <%
         c.piirkond_field = 'piirkond_id'
      %>
      <%include file="/admin/piirkonnavalik.mako"/>
    </td>
  </tr>

  <tr>
    <td class="fh">${_("Andmefail")}</td>
    <td>
      ${h.file('fail', value=_("Fail"))}
      <small>
        ${_("Faili kõik read peavad olema kujul <i>isikukood; eesnimi; perekonnanimi; e-posti aadress; rolli lõppkuupäev; Harno kasutajakonto lõppkuupäev</i>")}
      </small>
    </td>
  </tr>
  <tr>
    <td>
      <div class="d-flex">
        <b class="flex-grow-1">${_("JIRA pilet")}</b>
        <span>EJ-</span>
      </div>
    </td>
    <td>
      ${h.posint5('jira_nr', '')}
    </td>
  </tr>
  <tr>
    <td colspan="2">
      <b>${_("Selgitus")}</b>
      ${h.textarea('selgitus', '', rows=5)}
    </td>
  </tr>
</table>
${h.submit(_("Laadi"), onclick="$('.alert-danger').remove()")}
${h.btn_to(_("Tagasi"), h.url('admin_ametnikud'))}
${h.end_form()}

<script>
  $(function(){
    grupp_changed();
    $('input#r_kehtib_kuni').datepicker();
  });
  function grupp_changed()
  {
     var grupp_id = $('#kasutajagrupp_id').val();
     var b = (grupp_id == '${const.GRUPP_AINETOORYHM}');
     $('tr.r_aine').toggleClass('d-none', !b);

     var b = (grupp_id == '${const.GRUPP_SISESTAJA}' ||
          grupp_id == '${const.GRUPP_REGAJA}' ||
          grupp_id == '${const.GRUPP_P_KORRALDUS}' ||
          grupp_id == '${const.GRUPP_VAIDEKOM_ESIMEES}' ||
          grupp_id == '${const.GRUPP_VAIDEKOM}'); 
     $('tr.r_testiliik').toggleClass('d-none', !b);

     b = (grupp_id == '${const.GRUPP_P_KORRALDUS}');
     $('tr.r_piirkond').toggleClass('d-none', !b);
  }
</script>
              
