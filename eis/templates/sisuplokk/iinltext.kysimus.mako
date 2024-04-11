## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>
<%def name="block_edit()">
<% f_toggle_ckeditor = None %>
<div class="row">
  <div class="col-lg-6">

    <div class="form-group row">
      <% name = 'l.pikkus' %>
      ${h.flb3(_("Lünga pikkus"), name, 'col-md-6 text-md-right')}
      <div class="col-md-6">
        % if c.lang:
        ${h.lang_orig(c.kysimus.pikkus)}
        <div>${h.lang_tag()}${h.posint5('l.pikkus', c.kysimus.tran(c.lang).pikkus, ronly=not c.is_tr)}</div>
        % else:
        ${h.posint5('l.pikkus', c.kysimus.pikkus, ronly=not c.is_tr and not c.is_edit)}
        % endif
      </div>
    </div>

    <div class="form-group row">
      <% name = 'l.max_pikkus' %>
      ${h.flb3(_("Vastuse max pikkus"), name, 'col-md-6 text-md-right')}
      <div class="col-md-6">
        % if c.lang:
        ${h.lang_orig(c.kysimus.max_pikkus)}
        <div>${h.lang_tag()}${h.posint5('l.max_pikkus', c.kysimus.tran(c.lang).max_pikkus, ronly=not c.is_tr)}</div>
        % else:
        ${h.posint5('l.max_pikkus', c.kysimus.max_pikkus, ronly=not c.is_tr and not c.is_edit)}
        % endif
      </div>
    </div>

    % if c.tulemus.baastyyp == const.BASETYPE_MATH:
    <div class="form-group row">
      <% name = 'l.min_vastus' %>
      ${h.flb3(_("Minimaalne vastuste arv"), name, 'col-md-6 text-md-right')}
      <div class="col-md-6">
        ${h.select('l.min_vastus', c.kysimus.min_vastus, ('0','1'), wide=False)}
        ${h.hidden('l.max_vastus', 1)}
      </div>
    </div>
    % else:

    <div class="form-group row">
      <% name = 'l.mask' %>
      ${h.flb3(_("Mask"), name, 'col-md-6 text-md-right')}
      <div class="col-md-6">
        % if c.lang:
        ${h.lang_orig(c.kysimus.mask)}
        <div>${h.lang_tag()}${h.text('l.mask', c.kysimus.tran(c.lang).mask, maxlength=256, ronly=not c.is_tr)}</div>
        % else:
        ${h.text('l.mask', c.kysimus.mask, maxlength=256, ronly=not c.is_tr and not c.is_edit)}
        % endif
      </div>
    </div>

    <div class="form-group row">
      <% name = 'l.vihje' %>
      ${h.flb3(_("Vihje"), name, 'col-md-6 text-md-right')}
      <div class="col-md-6">
        % if c.lang:
        ${h.lang_orig(c.kysimus.vihje)}
        <div>${h.lang_tag()}${h.text('l.vihje', c.kysimus.tran(c.lang).vihje, maxlength=256, ronly=not c.is_tr)}</div>
        % else:
        ${h.text('l.vihje', c.kysimus.vihje, maxlength=256, ronly=not c.is_tr and not c.is_edit)}
        % endif
      </div>
      <div class="col-md-6"></div>
      <div class="col-md-6">
        ${h.checkbox('l.algvaartus', 1, checked=c.kysimus.algvaartus, label=_("Vihje jääb vastuse algväärtuseks"))}
      </div>
    </div>

    % endif

  </div>
  <div class="col-lg-6 pl-3">
    
    % if c.tulemus.baastyyp == const.BASETYPE_MATH:
    
    <div class="form-group row">
      <% name = 'l.n_asend' %>
      ${h.flb3(_("Nupurea asend"), name, 'text-md-right')}
      <div class="col-md-9">
        ${h.radio('l.n_asend', 1, checked=c.kysimus.n_asend==1 or c.kysimus.n_asend is None, label=_("all"))}
      ${h.radio('l.n_asend', 0, checkedif=c.kysimus.n_asend, label=_("paremal"))}
      </div>
    </div>
    <div class="form-group row">
      <% name = 'l.vihje' %>
      ${h.flb3(_("Vihje"), name, 'text-md-right')}
      <div class="col-md-9">
        % if c.lang:
        ${h.lang_orig(c.kysimus.vihje)}
        <div>${h.lang_tag()}${h.text('l.vihje', c.kysimus.tran(c.lang).vihje, maxlength=256, ronly=not c.is_tr)}</div>
        % else:
        ${h.text('l.vihje', c.kysimus.vihje, maxlength=256, ronly=not c.is_tr and not c.is_edit)}
        % endif
      </div>
    </div>
    % else:
    
    <div class="form-group row">
      <% name = 'l.laad' %>
      ${h.flb3(_("Laad"), name, 'text-md-right')}
      <div class="col-md-9">
        % if c.lang or not c.is_edit:
        ${h.hidden('l.laad', c.kysimus.laad)}
        ${h.roxt(c.kysimus.laad)}
        % else:
        ${h.text('l.laad', c.kysimus.laad, maxlength=256)}
        % endif
      </div>
    </div>
    <div class="form-group row">
      <div class="col-md-3">
        ${choiceutils.joondus(c.kysimus)}
      </div>
      <div class="col-md-9">
      % if c.is_edit and not c.lang:
       <script>
        var sp_toggle_ckeditor = function(){
          toggle_ckeditor('am1hm1', true, null, {toolbar:'supsub', language:'${request.localizer.locale_name}'}, 'am1_mapping1', 'l.rtf', 'am1.valem');
        };
        </script>
         <% f_toggle_ckeditor = 'sp_toggle_ckeditor()' %>
##          ${h.checkbox('l.rtf', 1, checked=c.kysimus.rtf, label=_("Kirev tekst"), onclick="sp_toggle_ckeditor();$('td.rtf').toggle(this.checked)")}
         ${h.checkbox('l.rtf', 1, checked=c.kysimus.rtf, label=_("Kirev tekst"), onclick="$(this).closest('td').find('.needsave').show()")}
          <div class="needsave brown" style="display:none">${_("Muudatus rakendub peale salvestamist")}</div>         
        % else:
          ${h.checkbox('l.rtf', 1, checked=c.kysimus.rtf, label=_("Kirev tekst"), disabled=True)}
        % endif
          <br/>
          ${h.checkbox('l.sonadearv', 1, checked=c.kysimus.sonadearv, label=_("Kuvada sõnade arv vastuses"), disabled=not c.is_edit or c.lang)}
          <br/>
          ${h.checkbox('l.vastus_taisekraan', 1, checked=c.kysimus.vastus_taisekraan, label=_("Vastust saab vaadata täisekraanil"))}
      </div>
    </div>
    <div class="form-group row rtf" style="${not c.kysimus.rtf and 'display:none' or ''}">
      <% name = 'l.ridu' %>
      ${h.flb3(_("Ridade arv"), name, 'text-md-right')}
      <div class="col-md-9">
        % if c.lang:
        ${h.lang_orig(c.kysimus.ridu)}
        <div>${h.lang_tag()}${h.posint5('l.ridu', c.kysimus.tran(c.lang).ridu or c.kysimus.ridu, ronly=not c.is_tr)}</div>
        % else:
        ${h.posint5('l.ridu', c.kysimus.ridu, ronly=not c.is_tr and not c.is_edit)}
        % endif
      </div>
    </div>
    % endif   
  </div>
</div>

% if c.tulemus.baastyyp == const.BASETYPE_MATH:
${choiceutils.hindamismaatriks(c.kysimus, basetype=const.BASETYPE_MATH, tulemus=c.tulemus, heading1=_("Vastus"), matheditor=True, naidis=True, naidis_all=True)}
% if not c.is_tr:
<div class="icons-custom" style="display:${c.kysimus.matriba and 'block' or 'none'};">
  ${h.button(_("Kasuta ülesande vaikimisi nupuriba"), onclick="toggle_mathsetting(false)", class_="float-right")}    
  <%include file="/ekk/ylesanded/mathsetting.sisu.mako"/>
</div>
% endif
    
<script>
  ## toolbar hindamismaatriksi sisestamiseks
  var matheditor_buttons_${c.kysimus.kood} = ${model.json.dumps(c.ylesanne.get_math_icons(c.kysimus.matriba))};
  function toggle_mathsetting(is_custom)
  {
    $('.icons-default').toggle(!is_custom);
    $('.icons-custom').toggle(is_custom);
    $('#on_matriba').val(is_custom ? 1 : '');
  }
</script>
${h.hidden('on_matriba', c.kysimus.matriba and 1 or '')}
% else:
${choiceutils.hindamismaatriks(c.kysimus, basetype_opt=c.opt.tulemus_baseType, tulemus=c.tulemus, heading1=_("Vastus"), can_rtf=True, naidis_all=True, naidis_naha=False, f_toggle_ckeditor=f_toggle_ckeditor)}
% endif
</%def>
