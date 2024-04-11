<div container_sel="#div_avaleheteated">
${h.not_top()}
<div class="d-flex flex-wrap my-1">
  <h1 class="flex-grow-1">${_("Teated")}</h1>
  <div>
    ${h.link_to_container(_("Muudatuste logi"), h.url('admin_avaleheteatelogid'), mdicls='mdi-archive')}
    % if c.user.on_admin:
    ${h.btn_to_dlg(_("Erakorraline teade"), h.url('admin_edit_avaleheteade', id=model.Avaleheinfo.ID_EMERGENCY), title=_("Erakorraline teade"), size='md', level=2)}
    % endif
  </div>
  <div>
    ${h.btn_to_dlg(_("Uus teade"), h.url('admin_new_avaleheteade'), title=_("Uus teade"), size='md')}
    
  </div>
</div>
<%include file="/common/message.mako"/>

${h.form_search()}
<div class="gray-legend p-3 filter-w">

  <div class="row">
    <div class="col-12 col-md-5">
      <div class="form-group">
        ${h.flb(_("Sisu"),'sisu')}
        ${h.text('sisu', c.sisu)}
      </div>
    </div>
    <div class="col-12 col-md-5 d-flex align-items-end">
      <div class="form-group">
        ${h.checkbox1('kehtetu', '1', checkedif=c.kehtetu, label=_("Näita ka kehtetuid teateid"))}
      </div>
    </div>

    <div class="col d-flex flex-wrap justify-content-end align-items-end">
      <div>
        ${h.submit_dlg(_("Otsi"), "$('#div_avaleheteated')")}
      </div>
    </div>
    </div>
  </div>
</div>  

${h.end_form()}

<div class="listdiv">
  <%include file="avaleheteated_list.mako"/>
</div>
</div>
