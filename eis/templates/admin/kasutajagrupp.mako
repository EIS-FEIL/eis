<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Kasutajagrupid")} | ${c.item.nimi or _("Uus kasutajagrupp")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Kasutajagrupid"), h.url('admin_kasutajagrupid'))} 
${h.crumb(c.item.nimi or _("Uus kasutajagrupp"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
${h.form_save(c.item.id)}
${h.rqexp()}
<div class="form-wrapper mb-2">
  <div class="form-group row">
    ${h.flb3(_("Nimi"), 'f_nimi', rq=True)}
    <div class="col">
      ${h.text('f_nimi', c.item.nimi, maxlength=30)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Liik"), 'f_tyyp', rq=True)}
    <div class="col">
      <% disabled = c.item.id and True or False %>
      % if disabled:
      ${h.hidden('f_tyyp', c.item.tyyp)}
      % endif
      ${h.radio('f_tyyp', const.USER_TYPE_EKK, checked=(c.item.tyyp == const.USER_TYPE_EKK),
      label=_("Eksamikeskuse ametnike grupp"), disabled=disabled)}
      <br/>
      ${h.radio('f_tyyp', const.USER_TYPE_AV, checked=(c.item.tyyp == const.USER_TYPE_AV),
      label=_("EKK vaate avalike kasutajate grupp"), disabled=disabled)}
      <br/>
      ${h.radio('f_tyyp', const.USER_TYPE_Y, checked=(c.item.tyyp == const.USER_TYPE_Y),
      label=_("Ülesandega seotud ametnike grupp"), disabled=disabled)}
      <br/>
      ${h.radio('f_tyyp', const.USER_TYPE_T, checked=(c.item.tyyp == const.USER_TYPE_T),
      label=_("Testiga seotud ametnike grupp"), disabled=disabled)}
      <br/>
      ${h.radio('f_tyyp', const.USER_TYPE_KOOL, checked=(c.item.tyyp == const.USER_TYPE_KOOL),
      label=_("Soorituskoha kasutajate grupp"), disabled=disabled)}
    </div>
  </div>
% if c.item.id not in (const.GRUPP_OPILANE, const.GRUPP_LOPETANU):
  <div>
        <table class="table table-borderless table-striped tablesorter">
          <caption>${_("Õigused")}</caption>
          <thead>
            <tr>
              ${h.th(_("Nimi"))}
              ${h.th(_("Loetelu"))}
              ${h.th(_("Vaatamine"))}
              ${h.th(_("Lisamine"))}
              ${h.th(_("Muutmine"))}
              ${h.th(_("Kirjeldus"))}
            </tr>
          </thead>
          <tbody>
            <% 
               g_oigused = dict()
               for kgo in c.item.kasutajagrupp_oigused:
                   g_oigused[kgo.kasutajaoigus_id] = kgo
            %>
            % for cnt,o in enumerate(model.Kasutajaoigus.all()):
               <%
                  prefix = 'o-%d' % cnt
                  kgo = g_oigused.get(o.id)
                  bitimask = kgo and kgo.bitimask or 0
                  b_index = bitimask & const.BT_INDEX == const.BT_INDEX
                  b_show = bitimask & const.BT_SHOW == const.BT_SHOW
                  b_create = bitimask & const.BT_CREATE == const.BT_CREATE
                  b_update = bitimask & const.BT_ALL == const.BT_ALL                 
               %>
            % if c.is_edit or kgo:
            <tr>
              <td>${o.nimi}
                ${h.hidden('%s.oigus_id' % prefix, o.id)}
              </td>
              <td>
                <span class="d-none">${b_index}</span>
                ${h.checkbox('%s.b_index' % prefix, const.BT_INDEX, checked=b_index)}
              </td>
              <td>
                <span class="d-none">${b_show}</span>
                ${h.checkbox('%s.b_show' % prefix, const.BT_SHOW, checked=b_show)}
              </td>
              <td>
                <span class="d-none">${b_create}</span>
                ${h.checkbox('%s.b_create' % prefix, const.BT_CREATE, checked=b_create)}
              </td>
              <td>
                <span class="d-none">${b_update}</span>
                ${h.checkbox('%s.b_update' % prefix, const.BT_ALL, checked=b_update, class_="b-update")}
              </td>
              <td>${o.kirjeldus}</td>
            </tr>
            % endif
            % endfor
          </tbody>
        </table>
  </div>
% endif

</div>
<script>
  $(function(){
  $('.b-update').click(function(){
    if(this.checked) $(this).closest('tr').find('input[type="checkbox"]').prop('checked', true);
  })
  });
</script>

<div class="d-flex flex-wrap">
${h.btn_back(url=h.url('admin_kasutajagrupid'))}
% if c.is_edit:
%   if c.item.id:
${h.btn_to(_("Vaata"), h.url('admin_kasutajagrupp', id=c.item.id), method='get', level=2)}
%   endif
<div class="flex-grow-1 text-right">
  ${h.submit()}
</div>
% else:
${h.btn_to(_("Muuda"), h.url('admin_edit_kasutajagrupp', id=c.item.id), method='get')}
% endif
</div>

${h.end_form()}
