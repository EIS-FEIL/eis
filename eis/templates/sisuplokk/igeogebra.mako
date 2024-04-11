## -*- coding: utf-8 -*- 
## GeoGebra
## https://wiki.geogebra.org/en/Reference:GeoGebra_Apps_Embedding

<%inherit file="baasplokk.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
<%
  mo = c.block.meediaobjekt
  k = c.block.kysimus
  tulemus = k.tulemus or c.new_item(kood=k.kood)
  if not mo.laius:
     mo.laius = 900
  if not mo.korgus:
     mo.korgus = 700
  di_data = c.block.get_json_sisu()
  c.ggbdata = c.new_item.create_from_dict(di_data) or c.new_item()
  ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') 
%>
${h.hidden('am1.kysimus_id', k.id)}
<div class="row mb-1">
  <% name = 'mo.laius' %>
  ${ch.flb(_("Laius"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.int5('mo.laius', mo.laius, maxvalue=1500)}
  </div>

  <% name = 'mo.korgus' %>
  ${ch.flb(_("Kõrgus"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.int5('mo.korgus', mo.korgus)}
  </div>
</div>
<div class="form-group row">
  <div class="col-md-12 d-flex flex-wrap">
      ${h.checkbox('ggb.showtoolbar', 1, checked=c.ggbdata.showtoolbar, label=_("Kuva tööriistariba"))}
      ## menyyd ei või lahendajale kuvada GeoGebra vea tõttu, mis "Tööriistad" valimisel käivitab vormi submiti (ES-1944)
      ##${h.checkbox('ggb.showmenubar', 1, checked=c.ggbdata.showmenubar, label=_("Kuva menüüriba"))}
      ${h.checkbox('ggb.showalgebrainput', 1, checked=c.ggbdata.showalgebrainput, label=_("Kuva algebra sisendi rida"))}
      ${h.checkbox('ggb.allowstylebar', 1, checked=c.ggbdata.allowstylebar, label=_("Luba stiiliriba"))}
  </div>
</div>

% if c.is_edit:
${self.block_edit_import()}
% endif

${h.hidden('ggb_filedata_b64', '')}
${h.hidden('ggb_png_b64', '')}
<%
  if mo.laius and mo.korgus:
     width = '%dpx' % mo.laius
     height = '%dpx' % (mo.korgus + 70)
  else:
     width = '100%'
     height = '%dpx' % ((mo.korgus or 700) + 70)
%>
<div style="width:${width};height:${height}" id="applet_contpos_${c.block.id}"> 
  <div id="applet_container_${c.block.id}" class="applet-container"> </div>
</div>
<script>
  ${self.create_applet_js(True)}
  $(window).resize(resize_${c.block_prefix});
  $('form#form_save').submit(function(){
    ## vormi salvestamisel ekspordime geogebra faili
    $('input[name="ggb_filedata_b64"]').val(ggbApplet_${c.block.id}.getBase64());
    $('input[name="ggb_png_b64"]').val(ggbApplet_${c.block.id}.getPNGBase64(1,true, 72));
  });
</script>

<div class="gbox hmtable overflow-auto d-flex flex-wrap pt-3">
  <div class="bg-gray-50 p-3">      
    ${choiceutils.tulemus(k, tulemus, 'am1.', maatriks=False)}
  </div>
  <div class="flex-grow-1 p-3">
    ${choiceutils.naidisvastus(k, tulemus, 'am1.', rows=3, naha=False)}
  </div>
</div>

</%def>

<%def name="block_edit_import()">
<div style="text-align:right">
${h.button(_("Impordi failist..."), onclick="open_import_dlg($('div#import_f'));")}
${h.button(_("Impordi ID järgi..."), onclick="open_import_dlg($('div#import_id'));")}
</div>

<script>
## avame dialoogiakna materjali importimise andmete sisestamiseks
  function open_import_dlg(container)
  {
    open_dialog({'contents_elem': container, 'title': 'GeoGebra'});
    if(container.closest('form').length == 0)
    {
      var form = $('<form method="POST" multipart="true"></form>');
      container.wrap(form);
    }
  }
## dialoogiakna andmeväljad kopeeritakse suurde vormi ja submititakse
  function submit_in_parent(child_form)
  {
    var parent_form = $('form#form_save');
    ## kopeerime dialoogivormi väljad suure akna vormile
    $.each(child_form.find('input[type="text"],input[type="file"]'),
      function(i, field)
      {
        var clone = $(field).clone();
        $(field).after(clone).appendTo(parent_form);
      });
    parent_form.submit();
  }
</script>

<div style="display:none">
  <div id="import_f">
    <table>
      <col width="80"/>
      <tr>
        <td>${_("Fail")}</td>
        <td>${h.file('mo.filedata', value=_("Fail"))}</td>
      </tr>
    </table>
    ${h.button(_("Impordi"), onclick="submit_in_parent($(this.form))")}
  </div>
  
  <div id="import_id">
    <table>
      <col width="120"/>
      <tr>
        <td>${_("GeoGebra ID")}</td>
        <td>${h.text('mo.kood', '', size=10)}</td>
      </tr>
    </table>
    ${h.button(_("Impordi"), onclick="submit_in_parent($(this.form))")}
  </div>
</div>
</%def>

<%def name="block_view()">
<%
  kysimus = c.block.kysimus
  mo = c.block.meediaobjekt

  if c.block.naide or c.block_correct:
     responses = c.correct_responses
  else:
     responses = c.responses
  kv = responses.get(kysimus.kood)

  value = ''
  if kv and len(kv.kvsisud):
     ks = kv.kvsisud[0]
  else:
     ks = None
  if ks and ks.has_file:
     from eis.s3file import s3file_get
     filedata = s3file_get('kvsisu', ks)
     if filedata:
        value = h.b64encode2s(filedata)

  if not c.ggbdata or c.ggbdata_id != c.block.id:
     di_data = c.block.get_json_sisu()
     c.ggbdata = c.new_item.create_from_dict(di_data) or c.new_item()
     c.ggbdata_id = c.block.id
  width = mo.laius and '%dpx' % mo.laius or '100%'
  height = mo.korgus
  if height and c.ggbdata.showmenubar:
     # menyyriba korral on vaja 47 px juurde lisada
     height += 47
  height = '%dpx' % (height or 700)
  
  if c.prepare_correct and ks and ks.on_hinnatud and not c.block.varvimata:
     corr_cls = model.ks_correct_cls(responses, kysimus.tulemus, kv, ks, False) or ''
  else:
     corr_cls = ''
%>
${h.qcode(kysimus, nl=True)}
<div style="width:${width};height:${height};" id="applet_contpos_${c.block.id}"> 
  <div id="applet_container_${c.block.id}" class="${corr_cls}">  </div>
</div>
${h.hidden(kysimus.result, value)}
<% 
if c.on_copy_resp_prefixes == '':
   c.on_copy_resp_prefixes = []
c.on_copy_resp_prefixes.append((c.y_prefix, c.block_prefix))

if c.resize_prefixes == '':
  c.resize_prefixes = []
c.resize_prefixes.append((c.y_prefix, c.block_prefix))
%>

</%def>

<%def name="block_view_js()">
<% kysimus = c.block.kysimus %>
${self.create_applet_js(False)}
$(function(){
is_response_dirty = false;
});
function on_copy_resp_${c.block_prefix}()
{
  var res = $('input[name="${kysimus.result}"]'),
      newval = ggbApplet_${c.block.id}.getBase64();
  ## ei saa kindlaks teha, kas vastus on muutunud, salvestame alati
  res.val(newval);
  response_changed(res);
}
</%def>

<%def name="create_applet_js(editing)">
<%
  mo = c.block.meediaobjekt
  k = c.block.kysimus
  if not c.ggbdata or c.ggbdata_id != c.block.id:
     di_data = c.block.get_json_sisu()
     c.ggbdata = c.new_item.create_from_dict(di_data) or c.new_item()
     c.ggbdata_id = c.block.id
%>
function resize_${c.block_prefix}()
{
$('#applet_container_${c.block.id}').position({my: 'left top', at: 'left top', of: $('#applet_contpos_${c.block.id}')});
}

$(function(){
var params = {
% if mo.filename:
filename: "${mo.get_url(no_sp=c.url_no_sp)}",
% elif mo.kood:
material_id: "${mo.kood}",
% endif
## ggbBase64: "",
% if mo.laius:
width: ${mo.laius},
% endif
% if mo.korgus:
height: ${mo.korgus},
% endif
##showMenuBar: ${editing and 'true' or 'false'},
showMenuBar: ${(c.ggbdata.showmenubar or editing) and 'true' or 'false'},
showToolBar: ${(c.ggbdata.showtoolbar or editing) and 'true' or 'false'},
showToolBarHelp: true,
showAlgebraInput: ${(c.ggbdata.showalgebrainput or editing) and 'true' or 'false'},
showResetIcon: true,
allowStyleBar: ${(c.ggbdata.allowstylebar or editing) and 'true' or 'false'},
language: "${c.lang or request.localizer.locale_name}",
fixed: true,
##appletOnLoad: function(){ window.scrollTo(0,0); },
id: "ggbApplet_${c.block.id}"};

  var data = $('input[name="${k.result}"]').val();
  if((data!='') && (typeof data === 'string'))
     {
        params['ggbBase64'] = data.replace(/[\r\n]/g,'');
     }
  
  var applet_${c.block.id} = new GGBApplet(params, true);
  ##applet_${c.block.id}.setHTML5Codebase('/static/GeoGebra/HTML5/5.0/web3d/');

    function show_hidden_parents(fld)
    {
        var hidden_parents = fld.parents('.eis-sphidden');
        if(hidden_parents.length)
            hidden_parents.removeClass('eis-sphidden');
        return hidden_parents;
    }
    function hide_hidden_parents(hidden_parents)
    {
        if(hidden_parents.length)
            hidden_parents.addClass('eis-sphidden');        
    }
    var cont = $('#applet_container_${c.block.id}'), contpos = cont.parent(), frm = contpos.closest('form');
    var hp = show_hidden_parents(cont);
    applet_${c.block.id}.inject('applet_container_${c.block.id}', 'preferHTML5');
    hide_hidden_parents(hp);
    if(frm.length)
    {
      ## vastamise ajal tõstame geogebra vormist välja (kui on vormi sees, siis menyy "Tööriistad" või Undo klikk postitab vormi), ES-1944, ES-2464
<%
  cls = 'eis-sp-%s' % (c.block.tahis or c.block.seq)
  if c.is_sp_view_js and not c.on_hindamine and not c.hindamine and not c.block_correct and c.block.staatus==const.B_STAATUS_NAHTAMATU:
     cls += ' eis-sphidden'
%>
      var outform = $('<div class="outform-sp ${cls}"><div class="eis-spbody"></div></div>');
      frm.after(outform);
      outform.find('.eis-spbody').append(cont);
      cont.css('position','absolute');
      resize_${c.block_prefix}();
   }
   ## kui geogebra on algul nähtamatu, siis nihkub aken ära
   window.scrollTo(0,0);
});

</%def>

<%def name="block_print()">
  <% obj = c.block.taustobjekt  %>
  % if obj:
     <image src="images_${c.block.ylesanne_id}_${c.block.id}_${c.lang or ''}/${obj.filename}"
            alt="${_("Pilt")}" ${h.width(obj)} ${h.height(obj)} 
            title="${obj.tran(c.lang).tiitel}"/>
  % endif
</%def>

<%def name="block_entry()">
<div class="td-sis-value2">${_("Faili ei sisestata")}</div>
</%def>
