<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Isikuandmed")}
</%def>
<%def name="breadcrumbs()">
</%def>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>
${h.form_save(None)}

<div class="form-wrapper-lineborder mb-1">
  <div class="form-group row">
    ${h.flb3(_("Isikukood ja nimi"))}
    <div class="col-md-3">
      ${c.kasutaja.isikukood}
      ${c.kasutaja.nimi}
    </div>
    <div class="col-md-6">
      % if request.is_ext():
      ${h.submit(_("Päri andmed Rahvastikuregistrist"), id='rr', level=2)}
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Aadress"))}
    <div class="col-md-9">
      <%
         c.aadress = c.kasutaja.aadress
         c.aadress_obj = c.kasutaja
      %>
      <%include file="/admin/aadressivalik.mako"/>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Postiindeks"),'k_postiindeks')}
    <div class="col-md-3">
      ${h.posint('k_postiindeks', c.kasutaja.postiindeks, maxlength=5)}
    </div>
    ${h.flb3(_("Telefon"),'k_telefon', 'text-md-right')}
    <div class="col-md-3">
      ${h.text('k_telefon', c.kasutaja.telefon)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("E-post"),'k_epost')}
    <div class="col-md-3 err-parent">
      ${h.text('k_epost', c.kasutaja.epost)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Arveldusarve"))}
    <div class="col-md-9">
      ${h.text('p_arveldusarve', c.profiil.arveldusarve, maxlength=20)}
    </div>
  </div>
  <div class="form-group row">
    <div class="col">
      ${h.checkbox('p_on_psammas', 1, checked=c.profiil.on_psammas, 
      label=_("Olen liitunud pensionikindlustuse II sambaga"))}
      <span id="psammas">
        ${h.radio('p_psammas_protsent', 2, checkedif=c.profiil.psammas_protsent, label='2%')}
        ${h.radio('p_psammas_protsent', 3, checkedif=c.profiil.psammas_protsent, label='3%')}        
      </span>
      <script>
        $(function(){
          $('input#p_on_psammas').change(function(){
             $('span#psammas').toggle($('input#p_on_psammas:checked').length > 0);
          });
          $('span#psammas').toggle($('input#p_on_psammas:checked').length > 0);
        });
      </script>
    </div>
  </div>
  <div class="form-group row">
    <div class="col">
      ${h.checkbox('p_on_pensionar', 1, checked=c.profiil.on_pensionar, 
      label=_("Olen vanaduspensionär"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col">  
      ${h.checkbox('p_on_ravikindlustus', 1, checked=c.profiil.on_ravikindlustus, 
      label=_("Kehtiv ravikindlustusleping"))}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Märkused"))}
    <div class="col-md-9">
      ${h.textarea('p_oma_markus', c.profiil.oma_markus)}
    </div>
  </div>
</div>

<div class="text-right">
  ${h.submit()}
</div>
<%include file="labiviijalepingud.mako"/>
<div class="text-right">
  ${h.submit(_('Kinnita leping'), id='kinnita', style="display:none;")}
</div>
${h.end_form()}
