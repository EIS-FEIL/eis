<table width="100%"  class="table table-borderless table-striped tablesorter">
  <tr>
    ${h.th(_("Kirjeldus"))}
    ${h.th(_("Käivitaja"))}
    ${h.th(_("Algus"))}
    ${h.th(_("Lõpp"))}
    ${h.th(_("Viga"))}
    % if c.is_debug:
    ${h.th(_("Server"))}
    % endif
  </tr>
  % for rcd in c.arvutusprotsessid:
  <tr>
    <td>${rcd.kirjeldus}</td>
    <td>${rcd.kasutaja.nimi}</td>
    <td>${h.str_from_datetime(rcd.algus)}</td>
    <td>
    % if rcd.lopp:
      ${h.str_from_datetime(rcd.lopp)}
    % else:
      <% c.pooleli += '&p_id=%s' % rcd.id %>
      ${h.progress(rcd.edenemisprotsent, _("Protsessi edenemisprotsent"), 'pb_%s' % rcd.id)}
    % endif
    </td>
    <td>
      ${rcd.viga}
    </td>
    % if c.is_debug:
    <td>${rcd.hostname}</td>
    % endif
  </tr>
  % endfor
</table>
<br/>
<script>
  $(document).ready(function(){
  % if c.pooleli:
  var interval = setInterval(function() { 

     $.getJSON("${c.url_refresh}${c.pooleli}", function(data) {
             over = false;
             for(var i=0; i<data.protsessid.length; i++)
             {
                 var p_id = data.protsessid[i][0];
                 var percentage = data.protsessid[i][1];
                 over = data.protsessid[i][2];
                 set_progressbar_value('pb_'+p_id, percentage);
             }
             if(data.protsessid.length == 0 || over)
             {
                 clearInterval(interval);
                 location.reload(true);
                 return;
             }
         });
     }, 4500);
  % endif
  });
</script>
