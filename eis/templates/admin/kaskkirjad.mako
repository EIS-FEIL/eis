<%inherit file="/common/pagenw.mako"/>
<%def name="page_title()">
${_("Kasutajad")} | ${_("Käskkirja laadimine")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Kasutajad"), h.url('admin_kasutajad'))} 
${h.crumb(_("Käskkirja laadimine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>


${h.form_save(None, h.url('admin_kaskkirjad'), multipart=True)}
${h.hidden('testiliik', c.testiliik)}

<div class="p-2 mb-4">
  <div class="form-group row">
    ${h.flb3(_("Roll"))}
    <div class="col">
      <%
         opt_grupp = c.opt.labiviijagrupp
      %>
      ${h.select('kasutajagrupp_id', c.kasutajagrupp_id, opt_grupp, 
      onchange="onchange_grupp()")}
    </div>      
  </div>
  <div class="form-group row aine">
    ${h.flb3(_("Õppeaine"))}
    <div class="col">
      ${h.select('aine_kood', c.aine_kood,  c.opt.klread_kood('AINE'),  onchange="onchange_aine()")}
    </div>
  </div>
  <div class="form-group row aine keeletase">
    ${h.flb3(_("Keeleoskuse tase"))}
    <div class="col">
      <%
        keeletasemed = {r.kood: r.ctran.nimi for r in model.Klassifikaator.getR('KEELETASE').read if not r.ylem_id and r.kehtib}
        ainekeeletasemed = [r for r in model.Klassifikaator.getR('KEELETASE').read if r.kehtib and r.ylem_id]
      %>
      % for r in sorted(ainekeeletasemed, key=lambda r: r.kood):
      <span class="keeletase aine_${r.ylem.kood}">
        ${h.checkbox('keeletase', r.kood, checkedif=c.keeletase,
        label=keeletasemed.get(r.kood))}
      </span>
      % endfor
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Käskkirja kuupäev"))}
    <div class="col">
      ${h.date_field('kaskkirikpv', c.kaskkirikpv, wide=False)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Faili veerud"))}
    <div class="col-md-9">
      ${h.checkbox('col', 'isikukood', checked=True, disabled=True, label=_("isikukood"))}
      ${h.checkbox('col', 'epost', label=_("e-posti aadress"))}
      ${h.checkbox('col', 'telefon', label=_("telefon"))}
      <script>$('input[name="col"][value="isikukood"]').prop('checked', true);</script>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Käskkirja andmete fail"))}
    <div class="col">
      ${h.file('fail', value=_("Fail"))}
    </div>
  </div>
</div>
<div class="d-flex">
  <div class="flex-grow-1">
    ${h.btn_to(_("Tagasi"), h.url('admin_kasutajad'), level=2)}
    </div>
  ${h.submit(_("Laadi"))}
</div>
${h.end_form()}

<script>
function onchange_aine()
{
  var aine = $('select#aine_kood').val();
  $('span.keeletase').hide();
  $('span.keeletase.aine_'+aine).show();   
}
function onchange_grupp()
{
    var grupp_id = $('#kasutajagrupp_id').val();
    $('.aine').toggle(grupp_id != "${const.GRUPP_VAATLEJA}");
}
$(document).ready(onchange_aine);
$(document).ready(onchange_grupp);
</script>
