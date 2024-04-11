<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${c.item.nimi}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_('Rahvusvaheliste eksamite tunnistused'), h.url('admin_rveksamid'))} 
${h.crumb(c.item.nimi)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

${h.form_save(c.item.id)}

<h3>${_("Rahvusvahelise eksami tunnistus")}</h3>

${h.rqexp()}
<div class="form-wrapper mb-2">
  <div class="form-group row">
    ${h.flb3(_("Eksami nimetus"),rq=True)}
    <div class="col">
      ${h.text('f_nimi', c.item.nimi)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Eksami nimetus määruses"))}
    <div class="col">
      ${h.select('f_rveksam_kood', c.item.rveksam_kood, c.opt.RVEKSAM, empty=True)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Õppeaine"), rq=True)}
    <div class="col">
      ${h.select('f_aine_kood', c.item.aine_kood, c.opt.AINE)}
      <script>
        $(function(){
         $('select#f_aine_kood').change(
           callback_select("${h.url('pub_formatted_valikud', kood='KEELETASE', format='json')}", 
                           'ylem_kood', 
                           'select.keeletase')
           );
        });
        function upd_tase()
        {
           var target = $('table#choicetbl_t>tbody>tr select.keeletase:last');
           var source = $('select#f_keeletase_kood');
           target.empty();
           $.each(source.find('option'), function(i, option) {
               target.append($(option).clone());
           });
        }
      </script>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Tase"))}
    <div class="col">
      ${h.select('f_keeletase_kood', c.item.keeletase_kood,
      c.opt.klread_kood('KEELETASE', c.item.aine_kood, empty=True, ylem_required=True,
      vaikimisi=c.item.keeletase_kood), wide=False, class_='keeletase')}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Tase1"))}
    <div class="col">
      <% 
         if c.item.vastab_tasemele is None:
            n_vastab = None
         elif c.item.vastab_tasemele:
            n_vastab = '1'
         else:
            n_vastab = '0'
         opt_vastab = (('1', u'Vastab tasemele'), ('0', u'Võrreldav tasemega'))
      %>
      ${h.select('f_vastab_tasemele', n_vastab, opt_vastab, wide=False, empty=True)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Tulemuse esitamine"), rq=True)}
    <div class="col">
      <div class="my-3">
      % for value, label in model.Rveksam.opt_tulemusviis:
      ${h.radio('f_tulemusviis', value, checkedif=c.item.tulemusviis, label=label)}
      <br/>
      % endfor
      </div>

      ${h.checkbox('f_on_tase_tunnistusel', checkedif=c.item.on_tase_tunnistusel and '1')}
      ${_("Tunnistusel on märgitud saavutatud kogutulemus EN skaalal")}
      <br/>
      ${h.checkbox('f_on_tulemus_tunnistusel', checkedif=c.item.on_tulemus_tunnistusel and '1')}
      ${_("Kogutulemus on märgitud tunnistusele")}
      <br/>
      ${h.checkbox('f_on_tulemus_sooritusteatel', checkedif=c.item.on_tulemus_sooritusteatel and '1')}
      ${_("Kogutulemus on märgitud sooritusteatele")}
      <br/>
      ${h.checkbox('f_on_osaoskused_tunnistusel', checkedif=c.item.on_osaoskused_tunnistusel and '1')}
      ${_("Osaoskused on märgitud tunnistusele")}
      <br/>
      ${h.checkbox('f_on_osaoskused_sooritusteatel', checkedif=c.item.on_osaoskused_sooritusteatel and '1')}
      ${_("Osaoskused on märgitud sooritusteatele")}
      <br/>
      ${h.checkbox('f_on_osaoskused_jahei', checkedif=c.item.on_osaoskused_jahei and '1')}
      ${_("Osaoskuste vastavus tasemele märgitakse jah/ei")}
      <br/>
      ${h.checkbox('f_on_kehtivusaeg', checkedif=c.item.on_kehtivusaeg and '1')}
      ${_("Kehtivusaeg")}
      <br/>
      ${h.checkbox('f_on_tunnistusenr', checkedif=c.item.on_tunnistusenr and '1')}
      ${_("Tunnistuse number")}
      <br/>
      ${h.checkbox('f_kantav_tulem', checkedif=c.item.kantav_tulem and '1')}
      ${_("Tulemuste testisooritusele kandmise võimalus (failist laadimisel)")}
    </div>
  </div>
</div>

<h3>${_("Kogutulemus")}</h3>
<div class="form-wrapper pb-1 mb-2">
  <div class="form-group row">
    ${h.flb3(_("Alates"))}
    <div class="col">
      ${h.posint5('f_alates', c.item.alates)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Kuni"))}
    <div class="col">
      ${h.posint5('f_kuni', c.item.kuni)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Tulemuste vahemikud"))}
    <div class="col">
      ${self.kogutulemus()}
    </div>
  </div>
</div>

<%def name="row_osaoskus(n, r)">
    <% prefix = 'osa-%d' % (n) %>
    <tr>
      <td>
        <div class="d-flex">

          <div class="flex-grow-1">
            <div class="form-group row">
              ${h.flb3(_("Nimetus"), rq=True)}
              <div class="col">
                ${h.text('%s.nimi' % prefix, r.nimi, maxlength=30)}
                ${h.hidden('%s.id' % prefix, r.id)}
              </div>
            </div>
            <div class="form-group row">
              ${h.flb3(_("Alates"))}
              <div class="col">
                ${h.posint5('%s.alates' % prefix, r.alates)}
              </div>
            </div>
            <div class="form-group row">
              ${h.flb3(_("Kuni"))}
              <div class="col">
                ${h.posint5('%s.kuni' % prefix, r.kuni)}
              </div>
            </div>
            <div class="form-group row">
              ${h.flb3(_("Tulemuste vahemikud"))}
              <div class="col">
                ${self.osavahemikud(prefix, n, r)}
              </div>
            </div>
          </div>

          % if c.is_edit:
          <div>
            % if not r.in_use:
            ${h.grid_remove(title=_("Eemalda osaoskus"))}
            % endif
          </div>
          % endif
        </div>
      </td>
    </tr>
</%def>

<h3>${_("Osaoskused")}</h3>

<table class="table pl-4">
  <col width="150px"/>  
  <tbody>
    <% 
       on_osaoskusi = False 
       n = -1
    %>
  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for n in c._arrayindexes.get('osa') or []:
        <% on_osaoskusi = True %>
        ${self.row_osaoskus(n, c.new_item())}
  %   endfor
  % else:
## tavaline kuva
    % for n,r in enumerate(c.item.rvosaoskused):
    <% on_osaoskusi = True %>
    ${self.row_osaoskus(n, r)}
    % endfor

    % if c.lisaosaoskus:
    <% 
       on_osaoskusi = True 
       r = c.new_item()
       if len(c.item.rvosaoskused):
          prev = c.item.rvosaoskused[-1]
          r.rvosatulemused = [c.new_item(tahis=x.tahis, alates=x.alates, kuni=x.kuni) \
                             for x in prev.rvosatulemused]
    %>
    ${self.row_osaoskus(n+1, r)}
    % endif
  % endif

    % if not on_osaoskusi:
    <tr>
      <td colspan="2">${_("Osaoskusi pole kirjeldatud")}</td>
    </tr>
    % endif
  </tbody>
  % if c.is_edit:
  <tfoot>
    <tr>
      <td colspan="3">
        ${h.submit(u'Lisa osaoskus', id='lisaosaoskus')}
      </td>
    </tr>
  </tfoot>
  % endif
</table>

<div class="form-wrapper pb-1 mb-2">
  <div class="form-group row">
    ${h.flb3(_("Märkused"))}
    <div class="col">
      ${h.textarea('f_markus', c.item.markus)}
    </div>
  </div>
</div>

<div class="d-flex flex-wrap">
${h.btn_back(url=h.url('admin_rveksamid'))}
% if c.item.id and c.is_debug:
${h.btn_to(_("Ekspordi"), h.url_current('download', format='raw', id=c.item.id), level=2)}
% endif
% if c.is_edit and c.item.id:
${h.btn_to(_('Vaata'), h.url('admin_rveksam', id=c.item.id), method='get', level=2)}
% endif

<div class="flex-grow-1 text-right">
  % if c.is_edit:
  ${h.submit()}
  % elif c.user.has_permission('rveksamid', const.BT_UPDATE):
  ${h.btn_to(_('Muuda'), h.url('admin_edit_rveksam', id=c.item.id), method='get')}
  % endif
</div>

</div>

${h.end_form()}

<%def name="kogutulemus()">
      <table class="table" id="choicetbl_t">
        <col width="250"/>
        <col width="90"/>
        <col width="90"/>
        <col width="90"/>
        <col width="40"/>
        <thead>
          <tr>
            <th>${_("Tähis")}</th>
            <th>${_("Alates")}</th>
            <th>${_("Kuni")}</th>
            <th>${_("Tase")}</th>
          </tr>
        </thead>
        <tbody>

  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get('tulemus') or []:
        ${self.row_koguvahemik('tulemus-%s' % (cnt), c.new_item())}
  %   endfor
  % else:
## tavaline kuva
    % for n,r in enumerate(c.item.rveksamitulemused):
    ${self.row_koguvahemik('tulemus-%d' % (n), r)}
    % endfor
  % endif
        </tbody>
        % if c.is_edit:
        <tfoot>
          <tr>
            <td colspan="3">
              ${h.button(_("Lisa"), onclick="grid_addrow('choicetbl_t');upd_tase();",
              level=2, mdicls='mdi-plus')}
              <div id="sample_choicetbl_t" class="invisible">
                <!--
                    ${self.row_koguvahemik('tulemus__cnt__', c.new_item())}
                  -->
              </div>
            </td>
          </tr>
        </tfoot>
        % endif
      </table>
</%def>

<%def name="row_koguvahemik(prefix, r)">
          <tr>
            <td>
              ${h.text('%s.tahis' % prefix, r.tahis, maxlength=30)}
              ${h.hidden('%s.id' % prefix, r.id)}
            </td>
            <td>
              ${h.posfloat('%s.alates' % prefix, r.alates)} 
            </td>
            <td>
              ${h.posfloat('%s.kuni' % prefix, r.kuni)}
            </td>
            <td>
              ${h.select('%s.keeletase_kood' % prefix, r.keeletase_kood,
              c.opt.klread_kood('KEELETASE', c.item.aine_kood, empty=True, ylem_required=True,
              vaikimisi=c.item.keeletase_kood), class_='keeletase')}
            </td>
            % if c.is_edit:
            <td>
              % if not r.in_use:
              ${h.grid_remove()}
              % endif
            </td>
            % endif
          </tr>
</%def>

<%def name="osavahemikud(prefix, n_osaoskus, osaoskus)">
      <table class="table" id="choicetbl_osa${n_osaoskus}t">
        <thead>
          <tr>
            ${h.th(_("Tähis"))}
            ${h.th(_("Alates"))}
            ${h.th(_("Kuni"))}
            <th></th>
          </tr>
        </thead>
        <tbody>

  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get('%s.tulemus' % prefix) or []:
        ${self.row_osavahemik('%s.tulemus-%s' % (prefix, cnt), c.new_item())}
  %   endfor
  % else:
## tavaline kuva
    % for n,r in enumerate(osaoskus.rvosatulemused):
    ${self.row_osavahemik('%s.tulemus-%d' % (prefix, n), r)}
    % endfor
  % endif
        </tbody>
        % if c.is_edit:
        <tfoot>
          <tr>
            <td colspan="3">
              ${h.button(_("Lisa"), onclick=f"grid_addrow('choicetbl_osa{n_osaoskus}t');",
              level=2, mdicls='mdi-plus')}
              <div id="sample_choicetbl_osa${n_osaoskus}t" class="invisible">
                <!--
                    ${self.row_osavahemik('%s.tulemus__cnt__' % prefix, c.new_item())}
                  -->
              </div>
            </td>
          </tr>
        </tfoot>
        % endif
      </table>
</%def>

<%def name="row_osavahemik(prefix, r)">
          <tr>
            <td>
              ${h.text('%s.tahis' % prefix, r.tahis, maxlength=30)}
              ${h.hidden('%s.id' % prefix, r.id)}
            </td>
            <td>
              ${h.posfloat('%s.alates' % prefix, r.alates)} 
            </td>
            <td>
              ${h.posfloat('%s.kuni' % prefix, r.kuni)}
            </td>
            % if c.is_edit:
            <td>
              % if not r.in_use:
              ${h.grid_remove()}
              % endif
            </td>
            % endif
          </tr>
</%def>


