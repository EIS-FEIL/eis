<%
  is_open = c.open_tk_id == c.item.id
  cls = is_open and 'open' or ''
%>
<div class="tkogumik rounded border p-2 ${cls}">
  <div class="d-flex flex-wrap">
    <div class="tkogumik-header btn btn-link flex-grow-1"
         data-contents="tkogumik_${c.item.id}"
         data-href="${h.url_current('edit', id=c.item.id)}">
        <span class="mr-2">
          ${h.mdi_icon('mdi-folder-open-outline')}
          ${h.mdi_icon('mdi-folder-outline')}
        </span>
        <span class="tk-name">
          ${c.item.nimi}
        </span>
    </div>   
    <div>
      <div class="tkogumik-btns">
      ${h.button('', mdicls='mdi-folder-edit-outline', level=0, class_="tk-edit", title=_("Muuda töökogumiku nimetus"))}
      ${h.button('', mdicls='mdi-folder-remove-outline', level=0, class_="tk-remove", title=_("Kustuta töökogumik"),
      href=h.url_current('delete', id=c.item.id))}
      </div>
    </div>
  </div>
  <div class="tk-edit-name" style="display:none">
    <div class="d-flex">
      <div class="flex-grow-1">
        ${h.text('nimi', c.item.nimi)}
      </div>
      ${h.button('', mdicls='mdi-check', level=0, class_="tk-check-name", title=_("Muuda nimetus"))}
    </div>
    <div class="error tk-edit-error" style="display:none"></div>
  </div>
  <div id="tkogumik_${c.item.id}">
    % if is_open:
    <%include file="tookogumik.sisu.mako"/>
    % endif
  </div>
</div>
