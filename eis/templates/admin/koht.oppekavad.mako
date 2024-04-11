<div container_sel="#div_oppekavad">
  <%include file="/common/message.mako"/>
  <div class="d-flex flex-wrap">
    <div class="flex-grow-1">
            % for r in c.item.koolioppekavad:
            <div>
            ${r.oppetase_nimi} ${r.kavatase_nimi}
            % if c.is_edit and not r.on_ehisest:
            ${h.ajax_remove(h.url('admin_koht_delete_oppekava', koht_id=c.item.id, id=r.id), "#div_oppekavad")}
            % endif
            </div>
            % endfor
    </div>
    % if c.is_edit and c.item.id:
    <div>
            ${h.btn_to_dlg(_("Lisa haridustase käsitsi"), 
            h.url('admin_koht_new_oppekava', koht_id=c.item.id),
            title=_("Õppeasutusele uue haridustaseme lisamine"), level=2)} 
    </div>
    % endif
  </div>
</div>
