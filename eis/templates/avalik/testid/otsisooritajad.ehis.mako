<%include file="/common/message.mako"/>
${h.form_search(url=h.url('test_nimekiri_otsisooritajad', test_id=c.test_id, nimekiri_id=c.nimekiri_id))}
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
${h.form(h.url('test_nimekiri_sooritajad', test_id=c.test_id, nimekiri_id=c.nimekiri_id), method='post', disablesubmit=True)}
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
            <% c.keel = c.keel or rcd.lang %>
          <tr>
            <td>${h.checkbox('oigus', rcd.isikukood, checked=True, title=_("Vali rida {s}").format(s=rcd.isikukood))}</td>
            <td>${rcd.isikukood}</td>
            <td>${rcd.eesnimi} ${rcd.perenimi}</td>
          </tr>
          % endfor
        </tbody>
      </table>

<div id="add" class="d-flex flex-wrap mt-3">
    <% opt_keeled = c.testimiskord and c.testimiskord.opt_keeled or c.test.opt_keeled %>
    % if len(opt_keeled) > 0:
    <div class="mr-4">
    ${_("Soorituskeel:")}
      % if len(opt_keeled) > 1:
      ${h.select('keel', c.keel, opt_keeled, wide=False)}    
      % else:
      ${opt_keeled[0][1]}
      ${h.hidden('keel', opt_keeled[0][0])}
    % endif
    </div>
    % endif

    <% opt_kursused = c.test.opt_kursused %>
    % if len(opt_kursused):
    <div class="mr-4">
   ${_("Kursus:")}  ${h.select('kursus', None, opt_kursused, wide=False)}    
    </div>
   % endif

    % if c.test.testiliik_kood in (const.TESTILIIK_KOOLIPSYH, const.TESTILIIK_LOGOPEED):
    <div class="mr-4">
    ${h.checkbox('vanem_nous', 1, label=_('Vanema nõusolek'))}
    </div>
    % endif

    ${h.submit(_('Salvesta'), id='add_isik')}
</div>
</div>

${h.end_form()}

% endif

<script>
function toggle_add_e(){   
    var visible = ($('div#listdiv_e input:checked[name="oigus"]').length > 0);
    $('div#listdiv_e #add').toggleClass('invisible', !visible);
}
$(function(){
  $('div#listdiv_e').on('click', 'input[name="oigus"]', toggle_add_e);
  $('div#listdiv_e').on('click', 'input[name="all_id"]', function(){
        $(this).closest('table').find('input[name="oigus"]').prop('checked', this.checked);
        toggle_add_e();
  });
});
</script>

