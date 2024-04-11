<%inherit file="/common/pagenw.mako"/>
<%def name="page_title()">
${_("Kasutajad")} | ${_("Koolituste laadimine")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Kasutajad"), h.url('admin_kasutajad'))} 
${h.crumb(_("Koolituste laadimine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>


${h.form_save(None, h.url('admin_koolitused'), multipart=True)}
${h.hidden('testiliik', c.testiliik)}

<div class="p-2 mb-4">
  <div class="form-group row">
    ${h.flb3(_("Läbiviija roll"))}
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
      % for keeletase, ained in c.opt.aine_keeletasemed:
      <% ained_cls = ' '.join(['aine_%s' % aine for aine in ained]) %>
      <span class="keeletase ${ained_cls}">
        ${h.checkbox('keeletase', keeletase, checkedif=c.keeletase,
        label=keeletase)}
      </span>
      % endfor
    </div>
  </div>
  <div class="form-group row keeled">
    ${h.flb3(_("Keeled"))}
    <div class="col">
      % for lang in const.LANG_ORDER:
      ${h.checkbox('lang', value=lang, checkedif=c.lang, label=model.Klrida.get_lang_nimi(lang))}
      % endfor
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Koolituse kuupäev"))}
    <div class="col">${h.date_field('koolitusaeg', c.koolitusaeg, wide=False)}</div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Koolitusandmete fail"))}
    <div class="col">
      ${h.file('fail', value=_("Fail"))}
      <small>
        ${_("Faili kõik read peavad olema kujul <i>isikukood;e-post;telefon</i>")}
      </small>
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
    $('div.aine').toggle(grupp_id != "${const.GRUPP_VAATLEJA}");
    $('div.keeled').toggle(grupp_id == "${const.GRUPP_INTERVJUU}" || grupp_id == "${const.GRUPP_VAATLEJA}" || grupp_id == "${const.GRUPP_HINDAJA_S}" || grupp_id == "${const.GRUPP_HINDAJA_K}");
}
$(document).ready(onchange_aine);
$(document).ready(onchange_grupp);
</script>
