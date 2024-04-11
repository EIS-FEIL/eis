<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.ylesandekogu = c.item %>
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.item.nimi or _("E-kogu")} 
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("E-kogud"), h.url('ylesandekogud'))}
${h.crumb(c.item.nimi or _("E-kogu"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

<%def name="page_headers()">
<style>
  ## eemaldame valiku ymbert raami ja taustavärvi, lisame alljoone
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice {
  background-color: #fff;
  overflow:hidden;
  border: none;
  border-radius:0;
  border-bottom: .5px solid #afafaf;
  }
  ## proovime eemaldada alljont viimaselt valikult
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice:last-child {
  border-bottom: none;
  }
  ## teeme valikud kogu rea pikkuseks
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice {
    float:none;
  }
  ## ristike veidi suuremaks (muidu on 75%)
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice__remove {
  font-size:150%;
  }
  ## valiku tekst ristikesega samale reale kogu rea laiuses
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice div.row{
  width:99%;
  float:right;
  }
</style>
</%def>
<%
c.can_update = c.user.has_permission('ylesandekogud', const.BT_UPDATE,c.item)
%>
${h.form_save(c.item.id, multipart=True)}
${h.rqexp()}
<div class="form-wrapper mb-2">
  <div class="form-group row">
    ${h.flb3(_("ID"))}
    <div class="col-md-3">
      ${c.item.id or ''}
    </div>
    ${h.flb3(_("Olek"), 'f_staatus', 'text-md-right')}
    <div class="col">
      <%
        opt_st = [(st, c.opt.YK_STAATUS.get(st)) for st in (const.YK_STAATUS_MITTEAVALIK, const.YK_STAATUS_TESTIMISEL, const.YK_STAATUS_AVALIK, const.YK_STAATUS_ARHIIV)]
        if not c.user.has_permission('sisuavaldamine', const.BT_UPDATE):
            ignore = [const.YK_STAATUS_AVALIK]
            opt_st = [r for r in opt_st if (c.item.staatus == r[0]) or (r[0] not in ignore)]        
      %>
      ${h.select('f_staatus', c.item.staatus, opt_st, wide=False)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Nimetus"), rq=True)}
    <div class="col">
      ${h.text('f_nimi', c.item.nimi)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Õppeaine"), rq=True)}
    <div class="col">
      <% aine_opt = c.opt.klread_kood('AINE', vaikimisi=c.item.aine_kood) %>
      ${h.select('f_aine_kood', c.item.aine_kood, aine_opt, empty=True, wide=False)}
    </div>
  </div>
  <% style = c.item.aine_kood != const.AINE_YLD and 'display:none' or '' %>
  <div class="form-group row seotud" style="${style}">
    ${h.flb3(_("Seotud õppeained"))}
    <div class="col">
      ${h.select2('f_seotud_ained', c.item.seotud_ained, aine_opt, multiple=True)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Ainevaldkond"))}
    <div class="col">
      <span class="ainevald_nimi">${c.item.ainevald_nimi}</span>
      ${h.hidden('f_ainevald_kood', c.item.ainevald_kood)}    
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Kooliaste"), rq=True)}
    <div class="col-md-3 astmed">
      <% aste_opt = c.opt.astmed() %>
      ${h.select('f_aste_kood', c.item.aste_kood, aste_opt, empty=True, wide=False)}
    </div>
    <div class="col-md-6">
      <div style="float:left">${_("Sobilik ka:")}</div>
      <div style="float:left">
        ${h.select_checkbox('kooliastmed', c.item.kooliastmed, aste_opt)}
      </div>
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Klass"))}
    <div class="col">
    <%
      opt_klass = c.opt.KLASS_A
    %>
      ${h.select('f_klass', c.item.klass, opt_klass, empty=True, wide=False, names=True)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Teema"))}
    <div class="col div-teemad">
      <% opt_teemad = c.opt.teemad2(c.item.aine_kood, c.item.aste_kood) %>
      ${h.select2('teemad2', c.item.teemad2, [], data=opt_teemad, multiple=True, multilevel=True, template_selection='template_selection2')}
    </div>
  </div>

  <% style = c.item.ainevald_kood != const.AINEVALD_VRK and 'display:none' or '' %>  
  <div class="form-group row oskus" style="${style}">
    ${h.flb3(_("Oskus"))}
    <div class="col">
      ${h.select('f_oskus_kood', c.item.oskus_kood,
      c.opt.klread_kood('OSKUS', c.item.aine_kood,
      ylem_required=True,empty=True, vaikimisi=c.item.oskus_kood), wide=False)}
    </div>
  </div>
  
  <% style = c.item.ainevald_kood != const.AINEVALD_VRK and c.item.aine_kood not in (const.AINE_ET,const.AINE_EE,const.AINE_W) and 'display:none' or '' %>    
  <div class="form-group row keeletase" style="${style}">
    ${h.flb3(_("Keeleoskuse tase"))}
    <div class="col">
      ${h.select('f_keeletase_kood', c.item.keeletase_kood,
      c.opt.klread_kood('KEELETASE', c.item.aine_kood, vaikimisi=c.item.keeletase_kood), empty=True, wide=False)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Eristuskiri"))}
    <div class="col">
      <% ek = c.item.kogufail %>
      ${h.textarea('ek_sisu', ek and ek.sisu or '', rows=8)}

      <div class="d-flex flex-wrap">
        <div>
          % if ek and ek.has_file:
          <span class="efile" style="padding-right:18px">
            ${h.btn_to(_("Laadi alla"), h.url_current('download', format=ek.fileext, id=c.item.id))}
            ${ek.filename}
            ${h.grid_s_remove('.efile', confirm=True)}
            ${h.hidden('is_efile', 1)}
          </span>
          ${h.hidden('was_efile', 1)}
          % endif
        </div>
        <div>
          % if c.is_edit:
          ${h.file('ek_filedata', value=_("Vali fail"))}
          % endif
        </div>
      </div>

    </div> 
  </div>
  
  % if c.item.id:
  <div class="form-group row">
    ${h.flb3(_("Punktid"))}
    <div class="col">
      ${h.fstr(c.item.max_pallid) or 0} p
    </div>
  </div>
  % endif
</div>

<div class="d-flex flex-wrap">
  ${h.btn_back(url=h.url('ylesandekogud'))}
  % if c.item.id and c.can_update:
  ${h.btn_remove()}
  % endif

  <div class="flex-grow-1 text-right">
    % if c.is_edit:
    ${h.submit()}
    % elif c.can_update:
    ${h.btn_to(_("Muuda"), h.url('edit_ylesandekogu', id=c.item.id), method='get')}
    % endif
  </div>
</div>
${h.end_form()}

% if c.is_edit:
<script>
  <%include file="ylesandekogu.js"/>
</script>
% endif

