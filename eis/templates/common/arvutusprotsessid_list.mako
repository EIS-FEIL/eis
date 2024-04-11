% if c.arvutusprotsessid or not c.protsessid_no_empty:
% if not c.protsessid_no_pager:
${h.pager(c.arvutusprotsessid,
          listdiv=".listdiv-protsessid",
          list_url=h.url_current('index', sub='protsessid'),
          msg_not_found=_("Arvutusprotsesse pole käivitatud"),
          msg_found_one=_("Leiti üks protsess"),
          msg_found_many=_("Leiti {n} protsessi"),
          is_psize=False)}
% endif
% if c.arvutusprotsessid:
<table class="table table-borderless table-striped tablesorter">
  % if c.protsessid_caption:
  <caption>${c.protsessid_caption}</caption>
  % elif not c.protsessid_no_caption:
  <caption>${_("Taustaprotsessid")}</caption>
  % endif
% if len(c.arvutusprotsessid) == 0:
  <tr>
    <td>
      ${_("Arvutusprotsesse pole käivitatud")}
    </td>
  </tr>
% else:
  <tr>
    ${h.th(_("Kirjeldus"))}
    ${h.th(_("Käivitaja"))}
    ${h.th(_("Algus"))}
    ${h.th(_("Lõpp"))}
    ${h.th(_("Märkus"))}
    % if c.app_ekk:
    ${h.th(_("Server"))}
    % endif
  </tr>
  % for rcd in c.arvutusprotsessid:
  <tr>
    <td>${rcd.kirjeldus}</td>
    <td>${rcd.kasutaja.nimi}</td>
    <td>${h.str_from_datetime(rcd.algus, seconds=True)}</td>
    <td>
    % if rcd.lopp:
      ${h.str_from_datetime(rcd.lopp, seconds=True)}
      % if rcd.edenemisprotsent == 100 and c.protsessid_next:
      ${h.btn_to(_("Jätka"), c.protsessid_next(rcd.id), class_="ml-2")}
      % endif
    % else:
      <% c.pooleli += '&p_id=%s' % rcd.id %>
      ${h.progress(rcd.edenemisprotsent, _("Protsessi edenemisprotsent"), id='pb_%s' % rcd.id)}
    % endif
    </td>
    <td id="msg_${rcd.id}">
      ${h.html_nl(rcd.viga)}

      % if rcd.has_file:
      <%
        title = f'{rcd.filename} ({h.filesize(rcd.filesize)})'
        url = h.url('protsessifail', id=rcd.id, format=rcd.fileext)
      %>
        % if rcd.kasutaja_id == c.user.id or c.user.on_admin:
        ${h.link_to(title, url)}
        % else:
        ${title}
        % endif
      % endif
    </td>
    % if c.app_ekk:
    <td>${rcd.hostname}</td>
    % endif
  </tr>
  % endfor
% endif
</table>
<script>
  $(function(){
  % if c.pooleli:
  var interval = setInterval(function() { 
     $.getJSON("${c.url_refresh or h.url_current('index', sub='progress')}${c.pooleli}", function(data) {
             over = false;
             for(var i=0; i<data.protsessid.length; i++)
             {
                 var p_id = data.protsessid[i][0];
                 var percentage = data.protsessid[i][1];
                 set_progressbar_value('pb_'+p_id, percentage);
                 over = data.protsessid[i][2];
                 var msg = '<div>' + data.protsessid[i][3] + '</div>';
                 $('#msg_'+p_id).html(msg);
             }
             if(data.protsessid.length == 0 || over)
             {
                 clearInterval(interval);
                 location.reload(true);
                 return;
             }
         });
     }, 4500);
    $('a.paginate').click(function(){
       if(interval) { clearInterval(interval); }
    });
  % endif
  });
</script>
% endif
% endif
