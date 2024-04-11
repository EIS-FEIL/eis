<%inherit file="/common/dlgpage.mako"/>
<% 
   c.kasutaja = c.item 
   c.profiil = c.item.give_profiil()
   c.is_edit = True
   c.can_update_profiil = True
%>

${h.form_save(c.item.id)}
## läbiviija otsinguväljad
${h.hidden('labiviija_id', c.labiviija_id)}
${h.hidden('grupp_id', c.grupp_id)}

<%include file="/common/message.mako"/>
<div class="gray-legend p-3 d-flex flex-wrap">
  <div class="item mr-5">
    ${h.flb(_("Isikukood"), 'isikukood')}
    <div id="isikukood">${c.item.isikukood}</div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Eesnimi"),'eesnimi')}
    <div id="eesnimi">${c.item.eesnimi}</div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Perekonnanimi"),'perenimi')}
    <div id="perenimi">${c.item.perenimi}</div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("E-post"),'epost')}
    <div class="err-parent" id="epost">
      % if c.item.epost:
      ${c.item.epost}
      % else:
      ${h.text('k_epost', c.item.epost, size=40)}
      % endif
    </div>
  </div>
  % if c.profiil.markus:
  <div class="item mr-5">
    ${h.flb(_("Märkus"),'markus')}
    <div id="markus">
      ${c.profiil.markus}
    </div>
  </div>
  % endif
</div>
<%include file="/admin/kasutaja.profiilisisu.mako"/>

<div class="d-flex flex-wrap">
<div class="flex-grow-1"> </div>
<% grupp = model.Kasutajagrupp.get(c.grupp_id) %>
${h.btn_to_dlg(_("Katkesta"), h.url_current('index', grupp_id=c.grupp_id, labiviija_id=c.labiviija_id, isikukood=c.kasutaja.isikukood), method='get', title=grupp.nimi, width=700, level=2, size='lg')}
${h.submit_dlg()}
</div>

${h.end_form()}
