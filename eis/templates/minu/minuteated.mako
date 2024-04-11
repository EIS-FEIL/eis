<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Minu teated")}
</%def>

<%def name="page_headers()">
<style>
  tr.msg-new td, tr.msg-new td .btn-link:not(:disabled) { font-weight: 800 !important; }
  tr.msg-arch td { background-color: #ccd9e0; }
</style>
</%def>

<h1>${_("Minu teated")}</h1>
${h.form_search(url=h.url('minu_teated'))}

<div class="gray-legend p-3 filter-w">

  <div class="row">
    <div class="col-12 col-md-6">
      <div class="form-group">
        ${h.checkbox('staatus', const.KIRI_UUS, checkedif=c.staatus, label=_("Uued teated"))}
        ${h.checkbox('staatus', const.KIRI_LOETUD, checkedif=c.staatus, label=_("Loetud teated"))}
        ${h.checkbox('staatus', const.KIRI_ARHIIV, checkedif=c.staatus, label=_("Arhiveeritud teated"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Edastuskanal"),'teatekanal')}
        <%
          kanalid = c.opt.TEATEKANAL
          opt_kanal = [(k, kanalid.get(k)) for k in (const.TEATEKANAL_EPOST, const.TEATEKANAL_POST, const.TEATEKANAL_STATEOS, const.TEATEKANAL_EIS)]
        %>
        ${h.select('teatekanal', c.teatekanal, opt_kanal, empty=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
        ${h.btn_search()}
    </div>
  </div>
</div>
${h.end_form()}

${h.form_save(None)}
<div class="listdiv">
<%include file="minuteated_list.mako"/>
</div>

${h.submit(_("Märgi loetuks"), id="loetuks", style="display:none")}
${h.submit(_("Märgi uueks"), id="uueks", style="display:none")}
${h.submit(_("Arhiveeri"), id="arhiivi", style="display:none")}
${h.submit(_("Võta arhiivist välja"), id="arhiivist", style="display:none")}
${h.end_form()}
