${h.form_search(url=h.url_current('index'))}
${h.rqexp(True, _("Palun sisesta vähemalt isikukood või perekonnanimi"))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Isikukood"), 'isikukood')}
        ${h.text('isikukood', c.isikukood)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Eesnimi"), 'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>      
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Perekonnanimi"), 'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>      
    <div class="col d-flex justify-content-end align-items-end">  
      <div class="form-group">
        ${h.submit_dlg(_('Otsi'))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<span id="progress"></span>

<div class="listdiv">
<%include file="/common/message.mako"/>
% if not c.items and c.items != '':
${_("Kasutajaid ei leitud")}
% endif
% if c.items:
${h.form(h.url_current('create'), method='post')}
<table border="0" class="table table-borderless table-striped tablesorter" id="table_isikud" width="100%">
        <thead>
          <tr>
            <th sorter="false">${h.checkbox('all_id', 1, title=_("Vali kõik"))}</th>
            ${h.th_sort('isikukood', _('Isikukood'))}
            ${h.th_sort('eesnimi,perenimi', _('Nimi'))}
          </tr>
        </thead>
        <tbody>
          % for rcd in c.items:
          <tr>
            % if rcd.id:
            ## olemasolev kasutaja
            <td>${h.checkbox('oigus', 'K%s' % rcd.id, onclick="toggle_add()", title=_("Vali rida {s}").format(s=rcd.isikukood))}</td>
            <td>${rcd.isikukood_hide}</td>
            <td>
              ${rcd.eesnimi} ${rcd.perenimi}
            </td>
            % else:
            ## RRist saadud andmed
            <td>${h.checkbox('oigus', rcd.isikukood, onclick="toggle_add()")}</td>
            <td>${rcd.isikukood}</td>
            <td>
              ${rcd.eesnimi} ${rcd.perenimi}
              ${h.hidden('i%s_eesnimi' % rcd.isikukood, rcd.eesnimi)}
              ${h.hidden('i%s_perenimi' % rcd.isikukood, rcd.perenimi)}
            </td>           
            % endif
          </tr>
          % endfor
        </tbody>
      </table>

<script>
function toggle_add(){   
    var visible = ($('div.listdiv input:checked[name="oigus"]').length > 0);
    $('div.listdiv span#add').toggleClass('invisible', !visible);
}
$(function(){
  $('div.listdiv').on('click', 'input[name="oigus"]', toggle_add);
  $('div.listdiv').on('click', 'input[name="all_id"]', function(){
        $(this).closest('table').find('input[name="oigus"]').prop('checked', this.checked);
        toggle_add();
  });
});
</script>
<span id="add" class="invisible">
  ${h.submit('Salvesta', id='add_isik')}
</span>
${h.end_form()}
% endif
</div>
