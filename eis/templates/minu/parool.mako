## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Parooli muutmine")}
</%def>
${h.form(h.url('minu_parool'), method='post')}
<h1>${_("Parooli muutmine")}</h1>
<div class="m-4 form-wrapper">
        <% 
          kasutaja = c.user.get_kasutaja()
        %>
        % if c.user.has_pw:
        ## vana parooli kysida ainult parooliga sisse loginud kasutajalt
        <div class="form-group row">
          <div class="col col-md-6 text-md-right">
            ${h.flb(_("Vana parool"), 'parool_vana')}
          </div>
          <div class="col col-12 col-md-6">
            ${h.password('parool_vana', autocomplete='off')}
          </div>
        </div>
        % endif
        <div class="form-group row">
          <div class="col col-md-6 text-md-right">
            ${h.flb(_("Uus parool"), 'parool_uus')}
          </div>
          <div class="col col-12 col-md-6">
            ${h.password('parool_uus', autocomplete='off')}
          </div>
        </div>
        <div class="form-group row">
          <div class="col col-md-6 text-md-right">
            ${h.flb(_("Uus parool veelkord"), 'parool_uus2')}
          </div>
          <div class="col col-12 col-md-6">
            ${h.password('parool_uus2', autocomplete='off')}
          </div>
        </div>
        <div class="text-center">
	        ${h.submit(_("Muuda parool"))}
        </div>
</div>
${h.hidden('request_url', c.request_url, id="request_url_pw")}
${h.end_form()}


