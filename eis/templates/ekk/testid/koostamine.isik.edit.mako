
<%include file="/common/message.mako" />
% if c.item.id:
${h.form_save(c.item.id)}
<% k = c.item.kasutaja %>
${k.nimi}
<% ch = h.colHelper('col-md-6','col-md-6') %>
<div class="form-wrapper-lineborder">
  <div class="form-group row">
    ${ch.flb(_("Kasutajaroll"))}
    <div class="col">
      <%
        on_avalik = c.test.testityyp == const.TESTITYYP_AVALIK
        opt_grupp = c.opt.opt_testigrupp(on_avalik)
        
        pedagoog_grupid = (const.GRUPP_T_KORRALDAJA,)
        if c.item.kasutajagrupp_id in pedagoog_grupid:
           opt_grupp = [r for r in opt_grupp if r[0] in pedagoog_grupid]
        else:
           opt_grupp = [r for r in opt_grupp if r[0] not in pedagoog_grupid]
      %>
      ${h.select('kasutajagrupp_id', c.item.kasutajagrupp_id, opt_grupp)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Kehtib kuni"))}
    <div class="col">
      ${h.date_field('kehtib_kuni', c.item.kehtib_kuni_ui, wide=False)}
    </div>
  </div>
</div>
<div class="d-flex">
${h.btn_to(_("Kustuta"), h.url('test_koostamine_delete_isik', id=c.item.id, test_id=c.test.id),
method='post', confirm=_("Kas oled kindel, et soovid kustutada?"), level=2)}
<div class="flex-grow-1 text-right">
  ${h.submit_dlg()}
</div>
</div>
${h.end_form()}
% endif
