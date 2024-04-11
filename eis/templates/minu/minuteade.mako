${h.not_top()}
<%include file="/common/message.mako" />
<div id="kiri">
<table width="100%"  class="table">
  <col width="160"/>
  <col/>
  % if c.kiri.teatekanal == const.TEATEKANAL_EPOST:
  <tr>
    <td class="fh">${_("Teema")}</td>
    <td id="kiri_teema">${c.kiri.teema}</td>
  </tr>
  % endif
  % if c.ks.epost or c.ks.isikukood:
  <tr>
    <td class="fh">${_("Saaja aadress")}</td>
    <td>
      % if c.ks.epost:
      &lt;${c.ks.epost}&gt;
      % elif c.ks.isikukood:
      ${c.ks.isikukood}
      % endif
    </td>
  </tr>
  % endif
  <tr>
  % if c.kiri.teatekanal in (const.TEATEKANAL_EPOST, const.TEATEKANAL_KALENDER, const.TEATEKANAL_STATEOS):
    <td class="fh">${_("Saatmise aeg")}</td>
  % else:
    <td class="fh">${_("Koostamise aeg")}</td>
  % endif
    <td>${h.str_from_datetime(c.kiri.created)}</td>
  </tr>
  <tr>
    <td colspan="2" class="mail-body" style="padding-top:18px">
      % if c.kiri.sisu and c.kiri.teatekanal == const.TEATEKANAL_STATEOS:
      ${c.kiri.sisu.replace('\n','<br/>\n')}
      % else:
      ${c.kiri.sisu}
      % endif

      % if c.kiri.teatekanal == const.TEATEKANAL_STATEOS and c.kiri.sisu_url:
      <div class="my-2">
        ${h.link_to(c.kiri.sisu_url, c.kiri.sisu_url)}
      </div>
      % endif
    </td>
  </tr>
  % if c.kiri.has_file:
  <tr>
    <td class="fh">${_("Manus")}</td>
    <td>
      ${h.link_to(c.kiri.filename, h.url_current('download', format=c.kiri.fileext))}
    </td>
  </tr>
  % endif
</table>
</div>

% if c.kiri.sisu:
<div class="d-flex flex-wrap mb-2" style="justify-content:flex-end">
  ${h.button(_("Trüki"), onclick='print_dlg()', level=2, class_="m-1")}
</div>

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
% if c.just_loeti:
<script>
  $('#ks_id_${c.ks.id}').closest('tr').removeClass('msg-new');
</script>
% endif
