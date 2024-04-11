## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Tõlked")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Kasutajaliidese tõlkimine"), h.url('potext'))}
</%def>
<h1>${_("Kasutajaliidese tõlkimine")}</h1>
<%
available_languages = request.registry.settings.get('available_languages').split()
languages = [r for r in c.opt.klread_kood('SOORKEEL') if r[0] in available_languages and r[0] != const.LANG_ET]
%>

${h.form_search()}
<table>
  <col width="120px"/>
  <tr>
  </tr>
</table>
<script>
  $(function(){
  $('select#lang').change(function(){
  $('form#form_search').submit();
  });
  });
</script>

<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Tõlke keel"),'lang')}
        ${h.select('lang', c.lang, languages)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Otsing"),'msgstr')}
        ${h.text('msgstr', c.msgstr)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.checkbox('tolketa', 1, checked=c.tolketa, label=_('Ainult tõlkimata tekstid'))}
        ${h.checkbox('tapne', 1, checked=c.tapne, label=_('Täpne otsing'))}
      </div>
    </div>
    <div class="col-12 col-md-12 col-lg-3">
      <div class="form-group d-flex justify-content-end align-items-end">    
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

${h.form_save(None)}
${h.hidden('lang', c.lang)}
<div class="listdiv">
<%include file="potext_list.mako"/>
</div>
${h.submit('Salvesta')}
${h.end_form()}
