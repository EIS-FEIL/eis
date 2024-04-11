<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
${h.hidden('sub', 'lisa')}
<table class="form psisuplokk-new" >
  <col width="160"/>
  <col width="180"/>
  <tbody>
    <tr>
      <td class="fh">${_("Sisuploki tüüp")}</td>
      <td>
        <%
          opt_ptyyp = ((const.INTER_CHOICE, _("Valikvastusega küsimus")),
                       (const.INTER_EXT_TEXT, _("Avatud vastusega küsimus")))
          opt_vkoodid = (('A', 'A, B, C, ...'),
                         ('1', '1, 2, 3, ...'),
                         ('1A', '1 (A), 2 (B), 3 (C), ...'),
                        )
        %>
        ${h.select('tyyp', '', opt_ptyyp, class_="ptyyp")}
      </td>
    </tr>
    <tr>
      <td class="fh">${_("Küsimuste arv")}</td>
      <td>
        ${h.posint5('karv', 1)}
      </td>
    </tr>
    <tr>
      <td class="fh">${_("Max punktide arv")}</td>
      <td>
        ${h.posfloat('max_pallid', 1)}
      </td>
    </tr>
    <tr class="pchoice">
      <td class="fh">${_("Valikute arv")}</td>
      <td>${h.posint5('varv', 2)}</td>
    </tr>
    <tr class="pchoice">
      <td class="fh">${_("Valikud")}</td>
      <td>${h.select('koodid', '', opt_vkoodid)}</td>
    </tr>
    <tr class="pchoice">
      <td class="fh">${_("Max vastuste arv")}</td>
      <td>${h.posint5('max_vastus', 1)}</td>
    </tr>
    <tr class="pchoice">
      <td class="fh">${_("Õige vastuse punktide arv")}</td>
      <td>${h.posfloat('oige_pallid', 1)}</td>
    </tr>
    <tr class="pexttext" style="display:none">
      <td class="fh">${_("Punktide intervall")}</td>
      <td>${h.posfloat('pintervall', 1)}</td>
    </tr>
  </tbody>
</table>

${h.submit_dlg(_("Lisa"))}
${h.end_form()}

<script>
  ## väljade valik sõltuvalt sisuplokityybist
  $('.psisuplokk-new .ptyyp').change(function(){
    var is_choice = $(this).val() == '${const.INTER_CHOICE}';
    $('.psisuplokk-new .pexttext').toggle(!is_choice);
    $('.psisuplokk-new .pchoice').toggle(is_choice);
  });
</script>
