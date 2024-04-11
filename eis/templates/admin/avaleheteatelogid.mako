<div container_sel="#div_avaleheteated">
${h.not_top()}
<div class="d-flex flex-wrap my-1">
  <h1 class="flex-grow-1">${_("Muudatuste logi")}</h1>
  <div>
    ${h.link_to_container(_("Teated"), h.url('admin_avaleheteated'))}
  </div>
</div>

${h.form_search()}
${h.end_form()}

<div class="listdiv">
  <%include file="avaleheteated_list.mako"/>
</div>
</div>
