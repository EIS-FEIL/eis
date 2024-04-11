<%include file="/common/message.mako" />

% if c.is_edit:
${h.form_save(c.item.id)}
${h.hidden('k_id', c.kasutaja and c.kasutaja.id)}
<div class="d-flex flex-wrap mb-2" style="justify-content:flex-end">
  ${h.button(_("Trüki"), onclick='print_dlg()', level=2, class_="m-1")}
  % if c.item.teatekanal == const.TEATEKANAL_EPOST:
  ${h.submit_dlg(_("Saada"), class_="m-1")}
  <div class="m-1">
    ${h.flb('%s:' % _("Saaja"), 'epost')}
    <span class="err-parent">
      % if c.item.teatekanal == const.TEATEKANAL_STATEOS:
      ${h.text('isikukood', c.kasutaja and c.kasutaja.isikukood, size=11)}
      % else:
      ${h.text('epost', c.kasutaja and c.kasutaja.epost, size=40)}
      % endif
    </span>
  </div>
  % endif
</div>
${h.end_form()}

<script>
function print_dlg() 
{
   var wnd=window.open("about:blank", "_blank"); 
   wnd.document.open(); 
   wnd.document.write('<html><head><title>' + $('#kiri_teema').text() + '</title>');
   wnd.document.write('</head><body>');
   wnd.document.write($('div#dialog_div div#kiri').html());
 ## debug_toolbar!
   wnd.document.write('</' + 'body></html>');
   wnd.document.close(); 
   wnd.print();
   wnd.close();
}
</script>
% endif

<div id="kiri">
<table width="100%"  class="table">
  <col width="160"/>
  <col/>
  % if c.item.teatekanal == const.TEATEKANAL_EPOST:
  <tr>
    <td class="fh">${_("Teema")}</td>
    <td id="kiri_teema">${c.item.teema}</td>
  </tr>
  % endif
  % for r in c.item.kirjasaajad:
  <tr>
    <td class="fh">${_("Saaja")}</td>
    <td>
      % if r.kasutaja_id:
      ${r.kasutaja.nimi}
      % elif r.koht_id:
      ${r.koht.nimi}
      % endif
      % if r.epost:
      &lt;${r.epost}&gt;
      % elif r.isikukood:
      ${r.isikukood}
      % endif
    </td>
  </tr>
  % endfor
  <tr>
  % if c.item.teatekanal in (const.TEATEKANAL_EPOST, const.TEATEKANAL_KALENDER, const.TEATEKANAL_STATEOS):
    <td class="fh">${_("Saatmise aeg")}</td>
  % else:
    <td class="fh">${_("Koostamise aeg")}</td>
  % endif
    <td>${h.str_from_datetime(c.item.created, True)}</td>
  </tr>
  <tr>
    <td colspan="2" class="mail-body" style="padding-top:18px">
      % if c.item.sisu and c.item.teatekanal == const.TEATEKANAL_STATEOS:
      ${c.item.sisu.replace('\n','<br/>\n')}
      % else:
      ${c.item.sisu}
      % endif

      % if c.item.teatekanal == const.TEATEKANAL_STATEOS and c.item.sisu_url:
      <div class="my-2">
        ${h.link_to(c.item.sisu_url, c.item.sisu_url)}
      </div>
      % endif
    </td>
  </tr>
  % if c.item.has_file:
  <tr>
    <td class="fh">${_("Manus")}</td>
    <td>
      ${h.link_to(c.item.filename, h.url_current('download', format=c.item.fileext))}
    </td>
  </tr>
  % endif
</table>
</div>
