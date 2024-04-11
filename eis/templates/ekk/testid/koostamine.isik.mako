${h.not_top()}
<%include file="/common/message.mako" />
${h.form_search(url=h.url('test_koostamine_isikud', test_id=c.test.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Isikukood"), 'isikukood')}
        ${h.text('isikukood', c.isikukood)}
      </div>
    </div>
    % if c.user.has_permission('testiroll', const.BT_CREATE, gtyyp=const.USER_TYPE_EKK):
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
    % endif
  </div>
  <div class="d-flex">
    <div class="flex-grow-1">
      ${h.radio('ametnik', 1, checked=not c.mitteametnik, label=_("Eksamikeskuse kasutaja rollid"))}
      ${h.radio('ametnik', 0, checked=c.mitteametnik, label=_("Testi korraldaja roll"))}          
    </div>
    <div>
      ${h.submit_dlg(_('Otsi'))}
    </div>
  </div>
</div>
${h.end_form()}

% if c.items != '' and not c.items:
  ${_("Otsingu tingimustele vastavaid isikuid ei leitud")}
% elif c.items:
${h.form(h.url('test_koostamine_isikud', test_id=c.test.id), method='put')}
<table border="0"  class="table table-borderless table-striped multipleselect tablesorter" id="table_isikud" width="100%">
        <col width="20px"/>
        <thead>
          <tr>
            <th sorter="false"></th>
            ${h.th_sort('nimi', _("Nimi"))}
            <th></th>
          </tr>
        </thead>
        <tbody>
          % for rcd in c.items:
          <tr>
            <td>
              ${h.checkbox('oigus', rcd.id, onclick="toggle_add()")}
            </td>
            <td>${rcd.nimi}</td>
            <td>${rcd.epost or ''}</td>
          </tr>
          % endfor
        </tbody>
      </table>

<script>
  $(function(){
     $('table#table_isikud').tablesorter();
  });
  function toggle_add()
  {
     var sel = $('input:checked[name="oigus"]'), visible = (sel.length > 0);
     $('table.add').toggle(visible);
  };
</script>

<div class="add d-flex flex-wrap" style="display:none">
  <div class="pr-3">
        <%
          opt_grupp = c.opt.testigrupp
          if c.mitteametnik:
             opt_grupp = [r for r in opt_grupp if r[0] == const.GRUPP_T_KORRALDAJA]
          else:
             opt_grupp = [r for r in opt_grupp if r[0] != const.GRUPP_T_KORRALDAJA]
        %>
        ${h.select('kasutajagrupp_id', '', opt_grupp)}
  </div>
  <div class="pr-3 nowrap">
    ${_("Kehtib kuni")} ${h.date_field('kehtib_kuni', '', wide=False)}
  </div>
  <div class="flex-grow-1 text-right">
      <span id="add_isik">
        ${h.submit_dlg()}
      </span>
  </div>
</div>
${h.end_form()}

% endif
