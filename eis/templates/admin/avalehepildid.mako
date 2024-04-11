<div container_sel="#div_avalehepildid">
<div class="d-flex flex-wrap my-1">
  <h1 class="flex-grow-1">${_("Pilt")}</h1>
  <div>
    <%
      if c.item:
          url = h.url('admin_edit_avalehepilt', id=c.item.id, v=c.item.fileversion)
      else:
          url = h.url('admin_edit_avalehepilt', id=model.Avalehepilt.DEFAULT_ID)
    %>
    ${h.btn_to_dlg(_("Muuda"), url, title=_("Pildi vahetamine"), size='md')}
  </div>
</div>
<%include file="/common/message.mako"/>
% if c.item and c.item.has_file:
% if c.item.id != c.item.DEFAULT_ID:
<div class="bg-white p-2">
  <b>${_("Kuvamise aeg")}:</b> ${h.str_from_date(c.item.alates)} - ${h.str_from_date(c.item.kuni_ui)}
</div>  
% endif
${self.img_licensed(c.item)}
% endif

<div class="d-flex flex-wrap my-1">
  % for rcd in c.items:
  <div class="mr-3 my-2">
    <div class="bg-white p-2">
      ${h.str_from_date(rcd.alates)} - ${h.str_from_date(rcd.kuni_ui)}
      ${h.dlg_edit(h.url_current('edit', id=rcd.id), title=_("Pildi vahetamine"), size='md')}
    </div>
    ${h.image(h.url('avalehepilt', format=c.item.fileext, id=rcd.id, v=rcd.fileversion), class_=f"avimg-{rcd.id}", width=200)}
  </div>
  % endfor
</div>

<script>
  $('.img-license').tooltip({html: true});
</script>

<%def name="img_licensed(item)">
<%
  license = ''
  if item.autor:
     license += _("Autor") + ': ' + item.autor
  if item.allikas:
     license += (license and '<br/>' or '') + item.allikas
%>
<div class="text-right">
${h.image(h.url('avalehepilt', format=item.fileext, id=item.id, v=item.fileversion), class_=f"avimg-{item.id}", width="100%")}
% if license:
<button class="btn iconbtn img-license" data-toggle="tooltip" data-placement="bottom" title="${h.hm_str2(license)}">${h.mdi_icon('mdi-license')}</button>
% endif
</div>
</%def>
