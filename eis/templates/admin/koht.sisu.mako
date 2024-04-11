${h.form_save(c.item.id)}

${h.rqexp()}
<div class="form-wrapper mb-2">
  <div class="form-group row">
    ${h.flb3(_("Kehtivus"))}
    <div class="col">
      ${h.checkbox('on_soorituskoht', 1, disabled=not c.app_ekk, 
      checked=c.item.on_soorituskoht, label=_("Kasutusel EISis"))}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Haldusõigus"), 'haldusoigus')}
    <div class="col">
      ${h.checkbox('haldusoigus', value=1, disabled=not c.app_ekk,
      checked=c.item.haldusoigus, label=_("Soorituskoht võib ise oma andmeid hallata"))}
    </div>
  </div>
  % if c.item.kool_regnr:
  <div class="form-group row">
    ${h.flb3(_("Reg nr"))}
    <div class="col">
      ${c.item.kool_regnr}
    </div>
  </div>
  % endif
  % if c.item.kool_id:
  <div class="form-group row">
    ${h.flb3(_("EHIS ID"), 'kool_id')}
    <div class="col" id="kool_id">
      ${c.item.kool_id}
    </div>
  </div>
  % endif
  <div class="form-group row">
    ${h.flb3(_("Nimi"), 'f_nimi', rq=True)}
    <div class="col">
      ${h.text('f_nimi', c.item.nimi)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Liik"))}
    <div class="col">
      % if c.item.valitsus_tasekood:
        % if c.item.valitsus_aadresskomponent.tase == 1:
      ${_("Maavalitsus")}
        % else:
        ${_("Omavalitsus")}
        % endif
       (${c.item.valitsus_aadresskomponent.nimetus})
      % else:
      ${h.select('f_koolityyp_kood', c.item.koolityyp_kood,
        c.opt.klread_kood('KOOLITYYP', vaikimisi=c.item.koolityyp_kood), empty=True)}
      % endif
    </div>
  </div>

  % if len(c.item.koolinimed) > 1:
  <div class="form-group row">
    ${h.flb3(_("Varasemad nimed"))}
    <div class="col">
      % for r in c.item.koolinimed:
        % if r.nimi != c.item.nimi:
        ${r.nimi}<br/>
        % endif
      % endfor
    </div>
  </div>
  % endif

  % if not c.item.valitsus_tasekood:
  <div class="form-group row">
    ${h.flb3(_("Omandivorm"))}
    <div class="col">
      ${h.select('f_omandivorm_kood', c.item.omandivorm_kood,
      c.opt.klread_kood('OMANDIVORM', vaikimisi=c.item.omandivorm_kood), empty=True)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Alamliik"))}
    <div class="col">
      ${h.select('f_alamliik_kood', c.item.alamliik_kood,
        c.opt.klread_kood('ALAMLIIK', vaikimisi=c.item.alamliik_kood), empty=True)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Klassikomplektide arv"))}
    <div class="col">
      ${h.posint('f_klassi_kompl_arv', c.item.klassi_kompl_arv)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Õpilaste arv"))}
    <div class="col">
      ${h.posint('f_opilased_arv', c.item.opilased_arv)}
    </div>
  </div>
  % endif
  <div class="form-group row">
    ${h.flb3(_("Piirkond"))}
    <div class="col">
      <%
         c.piirkond_id = c.item.piirkond_id
         c.piirkond_field = 'f_piirkond_id'
      %>
      <%include file="/admin/piirkonnavalik.mako"/>
    </div>
  </div>
  % if not request.is_ext():
  <div class="form-group row">
    ${h.flb3(_("Riik"))}
    <div class="col">
      ${h.select('f_riik_kood', c.item.riik_kood,
      c.opt.klread_kood('RIIK', vaikimisi=c.item.riik_kood), empty=True)}
      <script>
        $(document).ready(function(){
        $('select#f_riik_kood').change(function(){
           $('div.eestiaadress').toggle($(this).val()=='EST');
        });
        $('div.eestiaadress').toggle($('select#f_riik_kood').val()=='EST');
        });
      </script>
    </div>
  </div>
  % endif
  <div class="form-group row">
    ${h.flb3(_("Aadress"))}
    <div class="col">
      <%
         c.aadress = c.item.aadress
         c.aadress_obj = c.item
      %>
      <%include file="/admin/aadressivalik.mako"/>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Postiindeks"))}
    <div class="col">
      ${h.text('f_postiindeks', c.item.postiindeks, size=5)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Telefon"))}
    <div class="col">
      ${h.text('f_telefon', c.item.telefon)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("E-post"))}
    <div class="col err-parent">
      ${h.text('f_epost', c.item.epost)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Varustus"))}
    <div class="col">
      ${h.textarea('f_varustus', c.item.varustus)}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-12">
      ${h.flb(_("Õppetasemed ja õppekavajärgsed haridustasemed"))}
    </div>
    <div class="col-12" id="div_oppekavad">
      <%include file="koht.oppekavad.mako"/>
    </div>
  </div>
</div>

<div class="d-flex flex-wrap">
  ${h.btn_back(url=h.url('admin_kohad'))}
  % if c.app_ekk and c.user.has_permission('kohteelvaade', const.BT_SHOW):
  ${h.btn_to(_("Soorituskoha administraatori eelvaade"), '/eis/kohteelvaade/%s' % c.item.id, target='_blank', level=2)}
  % endif

  <div class="flex-grow-1 text-right">
  % if c.is_edit:
%   if c.item.id:
${h.btn_to(_("Vaata"), h.url('admin_koht', id=c.item.id), method='get')}
  %   endif
    ${h.submit()}
% elif c.can_edit:
${h.btn_to(_("Muuda"), h.url('admin_edit_koht', id=c.item.id), method='get')}
% endif
  </div>
</div>

${h.end_form()}
