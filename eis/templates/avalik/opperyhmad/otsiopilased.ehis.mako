<%include file="/common/message.mako"/>
${h.form_search(url=h.url_current('index', opperyhm_id=c.opperyhm.id))}
${h.hidden('sub', 'ehis')}

<div class="gray-legend p-3">
  <div class="row filter">
    <div class="col-12">
      ${h.flb(_("Õppeasutus"),'kool')}
      <div id="kool">${h.roxt(c.user.koht_nimi)}</div>
    </div>
    <div class="col-md-4">
      ${h.flb(_("Klass"), 'klass')}
      <% opt_kr = c.opt.opt_klassid_ryhmad(c.user.koht) %>
      ${h.select('klass', c.klass, opt_kr)}
    </div>
    <div class="col-md-4">
      ${h.flb(_("Paralleel"), 'paralleel')}
      ${h.text('paralleel', c.paralleel)}
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.submit_dlg(_('Otsi'))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<span id="progress"></span>

% if c.items:
${h.form(h.url_current('create', opperyhm_id=c.opperyhm.id), method='post', disablesubmit=True)}
<div id="listdiv_e">
      <table border="0" class="table table-borderless table-striped tablesorter" id="table_isikud" width="100%">
        <col width="20px"/>
        <col width="100px"/>
        <thead>
          <tr>
            <th sorter="false">${h.checkbox('all_id', 1, checked=True, title=_("Vali kõik"))}</th>
            ${h.th(_('Isikukood'))}
            ${h.th(_('Nimi'))}
          </tr>
        </thead>
        <tbody>
          % for rcd in c.items:
          <tr>
            <td>${h.checkbox('oigus', rcd.isikukood, checked=True, title=_("Vali rida {s}").format(s=rcd.isikukood))}</td>
            <td>${rcd.isikukood}</td>
            <td>
              ${rcd.eesnimi} ${rcd.perenimi}
            </td>
          </tr>
          % endfor
        </tbody>
      </table>

      <span id="add">
        ${h.submit(_('Salvesta'), id='add_isik')}
      </span>
</div>

${h.end_form()}

% endif

<script>
function toggle_add_e(){   
    var visible = ($('div#listdiv_e input:checked[name="oigus"]').length > 0);
    $('div#listdiv_e span#add').toggleClass('invisible', !visible);
}
$(function(){
  $('div#listdiv_e').on('click', 'input[name="oigus"]', toggle_add_e);
  $('div#listdiv_e').on('click', 'input[name="all_id"]', function(){
        $(this).closest('table').find('input[name="oigus"]').prop('checked', this.checked);
        toggle_add_e();
  });
});
</script>

