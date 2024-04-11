<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Minu andmed")}
</%def>      

${h.form_save(None)}
<h1>${_("Minu andmed")}</h1>
<%include file="isikuandmed.mako"/>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_('Päri andmed Rahvastikuregistrist'), h.url('minu_edit_anne', id='rr'), level=2)}
  </div>
  <div>
    ${h.submit()}
  </div>
</div>

${h.end_form()} 
