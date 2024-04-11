% if c.items:
${h.pager(c.items, msg_not_found=_("Sooritajaid ei ole"), msg_found_one=_("Leiti 1 sooritaja"), msg_found_many=_("Leiti {n} sooritajat"))}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <col width="20px"/>
  <thead>
    <tr>
      ${h.th('', sorter='false')}
      ${h.th_sort('sooritus.tahis', _("Tähis"))}
      ${h.th_sort('kasutaja.nimi', _("Sooritaja"))}
      ${h.th_sort('sooritus.staatus', _("Vastamise olek"))}
      ${h.th_sort('sooritus.kavaaeg', _("Kavandatud algus"))}
      ${h.th_sort('sooritus.algus', _("Tegelik algus"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       tos, sooritaja, k = rcd
    %>
    <tr data-vst="${tos.staatus}">
      <td>
        ${h.checkbox('sooritus_id', tos.id, checked=False, ronly=False, class_="nosave sooritus")}
      </td>
      <td>${tos.tahis}</td>
      <td>
        <%
          label = f'{k.isikukood} {sooritaja.nimi}'
          url = None
          if c.testiosa.vastvorm_kood == const.VASTVORM_I:
             if tos.staatus in (const.S_STAATUS_REGATUD, const.S_STAATUS_ALUSTAMATA):
                url = h.url('sooritamine_alusta_osa', test_id=c.test.id, testiosa_id=tos.testiosa_id, id=tos.id)
             elif tos.staatus in (const.S_STAATUS_POOLELI, const.S_STAATUS_KATKESTATUD):
                url = h.url('sooritamine_jatka_osa', test_id=c.test.id, testiosa_id=tos.testiosa_id, id=tos.id)
        %>
        % if url:
        ${h.link_to(label, url, method='post', class_="pl-0")}
        % else:
        ${label}
        % endif
      </td>
      <td>
        ${tos.staatus_nimi}
      </td>
      <td>
        % if tos.kavaaeg:
        ${h.str_from_datetime(tos.kavaaeg, hour0=False)}
        % endif
      </td>
      <td>
        % if tos.algus:
        ${h.str_from_datetime(tos.algus)}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
  
% endif

<script>
function change_status(status)
{
  $('input#staatus').val(status);
  $('form#form_save').submit();
}
function toggle_valikuline()
{
  var flds = $('input.sooritus:checked');
  $('.valikuline').hide();                     
  if(flds.length > 0)
  {
      var clist = '.vst-all';
      for(var i=0; i<flds.length; i++)
      {
          var tr = flds.eq(i).closest('tr');
          var cls = '.vst-' + tr.attr('data-vst');
          if(clist.indexOf(cls) == -1)
             clist = clist + ',' + cls;
      }
      $('.valikuline').filter(clist).show();
  }
}
$(function(){
##  $('.listdiv').on('click', 'input.sooritus', toggle_valikuline);
  $('input.sooritus').click(toggle_valikuline);                                  
  toggle_valikuline();
});
</script>
