<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testsessioonid")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Testsessioonid"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%
c.can_update = c.user.has_permission('sessioonid', const.BT_UPDATE)
%>
<h1>${_("Testsessioonid")}</h1>
% if c.item:
${h.form_save(c.item.id)}
% endif
<div class="row">
  <div class="col-md-6">
    <div class="listdiv">
      <%include file="testsessioonid_list.mako"/>
    </div>
  </div>
  % if c.item:
  <div class="col-md-6">
    ${h.rqexp()}
    <% ch = h.colHelper('col-md-6','col-md-6') %>
    <div class="form-wrapper-lineborder mb-2">
      <div class="form-group row">
        ${ch.flb(_("Nimetus"), rq=True)}
        <div class="col">
          ${h.text('f_nimi', c.item.nimi, maxlength=100)}
        </div>
      </div>
      <div class="form-group row">
        ${ch.flb(_("Õppeaasta"), rq=True)}
        <div class="col">
          ${h.posint('f_oppeaasta', c.item.oppeaasta, size=5, maxlength=4)}
        </div>
      </div>
      <div class="form-group row">
        ${ch.flb(_("Testi liik"))}
        <div class="col">
          ${h.select('f_testiliik_kood', c.item.testiliik_kood,
          c.opt.testiliik, empty=True)}
        </div>
      </div>
      <div class="form-group row">
        ${ch.flb(_("Vaidlustamise tähtaeg"))}
        <div class="col">
          ${h.date_field('f_vaide_tahtaeg', c.item.vaide_tahtaeg, wide=False)}
        </div>
      </div>
      <div class="form-group row">
        ${ch.flb(_("Jrk nr"))}
        <div class="col">
          ${h.posint5('f_seq', c.item.seq)}
        </div>
      </div>
      <div class="form-group row">
        <div class="col">
          ${h.checkbox('f_vaikimisi', 1, checked=c.item.vaikimisi,
          label=_("Vaikimisi kasutatav sessioon uute testimiskordade loomisel"))}
        </div>
      </div>
    </div>
    <script>
      ## õppeaasta kopeerime vaikimisi jrk nr-ks
      $('#f_oppeaasta').change(function(){
        if($('#f_seq').val() == '') $('#f_seq').val(this.value);
      });
    </script>
    <div class="text-right">
        % if c.is_edit:
        ${h.submit(out_form=True)}
        % else:
        ${h.btn_to(_("Muuda"), h.url('admin_edit_testsessioon', id=c.item.id))}
        % endif
    </div>
  </div>
  
  % endif
</div>

    % if c.can_update:
      ${h.btn_to(_("Lisa"), h.url('admin_new_testsessioon'), level=2, mdicls='mdi-plus')}
    % endif

% if c.item:
${h.end_form()}      
% endif
