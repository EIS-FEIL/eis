## -*- coding: utf-8 -*- 
## $Id: markused.mako 544 2016-04-01 09:07:15Z ahti $         

<%def name="show(items, url_to_new, url_to_delete=None)">
% for rcd in items:
<div>
  ## kui dialoogiaken on varem lahti olnud, siis on kuskil mujal sama nimega div veel olemas, seepärast on vaja .each
    <a id="demo" onclick="$(this).siblings('#markus').toggle();return false;" class="menu1">
      <b>${rcd.kasutaja.nimi}</b>
      <span style="font-size:70%">${h.str_from_datetime(rcd.aeg)}</span>
      <i>${rcd.teema}</i>
      <% alamate_arv = rcd.alamate_arv %>
      % if alamate_arv:
        (${alamate_arv})
      % endif
    </a>
    &nbsp;
    % if url_to_new:
    ${h.btn_to_dlg(_("Lisa märge"), url_to_new(rcd), title=u'Märkus', width=600)}
    % endif

    % if url_to_delete and len(rcd.alamad) == 0 and rcd.kasutaja.id==c.user.id:
    ${h.btn_to_dlg(_("Kustuta"), url_to_delete(rcd), method='post',
    title=_("Märkus"), width=600, confirm=_("Kas oled kindel, et soovid kustutada?"))}
    % endif

    <% display = len(items) == 1 and 'block' or 'none' %>
    <div id="markus" style="display:${display}">
      <div class="view">${rcd.sisu}</div>
      % if rcd.alamad:
      <table width="100%">
        <tr>
          <td width="30px"></td>
          <td>
            ${self.show(rcd.alamad, url_to_new, url_to_delete)}
          </td>
        </tr>
      </table>
      % endif
    </div>
</div>
% endfor

</%def>
