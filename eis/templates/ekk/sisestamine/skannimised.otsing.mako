<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Skannitud vastuste laadimine")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>

<h1>${_("Skannitud vastuste laadimine")}</h1>
${h.form_search(url=h.url('sisestamine_skannimised'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-3 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Sisesta toimumisaja tähis"),'ta_tahised')}
        ${h.text('ta_tahised', c.ta_tahised, onclick="clear_ta();this.form.submit();")}
      </div>
    </div>
  </div>
  <div class="row filter">
    <div class="col-12 col-md-3 col-lg-3">
      <div class="form-group">
        ${h.flb(_("või vali testsessioon"),'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id,
        c.opt.testsessioon, empty=True, onchange='clear_ta();this.form.submit()')}
      </div>
    </div>
    <div class="col-12 col-md-3 col-lg-3">
      <div class="form-group">
        ${h.flb(_("ja toimumisaeg"),'toimumisaeg_id')}
        ${h.select('toimumisaeg_id', c.toimumisaeg_id,
          c.opt_toimumisaeg, empty=True, onchange='clear_sk();this.form.submit()')}
      </div>
    </div>
    <div class="col-12 col-md-3 col-lg-3">
      <div class="form-group">
        ${h.flb(_("sisestuskogum"),'sisestuskogum_id')}
        ${h.select('sisestuskogum_id', c.sisestuskogum_id, c.opt_sisestuskogum or [], empty=True,
        onchange='this.form.submit();')}
      </div>
    </div>
    <div class="col d-flex align-items-end">
      <div class="form-group">
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>

      <script>
        function clear_ta()
        {
        $('#toimumisaeg_id').val('');
        clear_sk();
        }
        function clear_sk()
        {
        $('#sisestuskogum_id').val('');
        $('#sooritus_id').val('');
        }
      </script>
% if c.toimumisaeg and c.sisestuskogum_id:
      <div class="border row">
        ${h.flb3(_("Sisendkataloog (serveris)"), 'kataloog')}
        <div class="col-md-6">
          ${h.text('kataloog', c.kataloog)}
        </div>
        <div class="col-md-3">
          ${h.submit(_('Laadi'), id='laadi')}
        </div>
      </div>
% endif

${h.end_form()}
