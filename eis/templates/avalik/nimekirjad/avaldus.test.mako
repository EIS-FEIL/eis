<%
   c.testimiskord = c.sooritaja.testimiskord
   c.test = c.sooritaja.test
   c.kasutaja = c.sooritaja.kasutaja
   c.opilane = c.kasutaja.opilane
%>
${h.form_save(c.sooritaja.id, h.url('nimekirjad_avaldus_update_test',
id=c.kasutaja.id, sooritaja_id=c.sooritaja.id))}

<div>
  <%
    c.tsuffix = ''
    c.reg_kool = True
  %>
  <%include file="/avalik/regamine/avaldus.testiseaded.mako"/>  
  ## selles failis seatakse c.voib_muuta
</div>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to_dlg(_("Määra tugiisik"), h.url('nimekirjad_avaldus_tugiisikud', kasutaja_id=c.kasutaja.id, sooritaja_id=c.sooritaja.id), level=2, title=_("Määra tugiisik"), size='md')}    
  </div>
  <div>
    % if c.voib_muuta:
    ${h.submit_dlg()}
    % endif
  </div>
</div>
${h.end_form()}
