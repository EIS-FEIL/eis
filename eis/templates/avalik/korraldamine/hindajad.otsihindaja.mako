<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>
${h.form_save(None, form_name='form_otsihindaja')}
${h.hidden('sub','otsihindaja')}
% for hindamiskogum_id in c.hk_id:
${h.hidden('hk_id', hindamiskogum_id)}
% endfor
${h.hidden('lang', c.lang)}
${h.hidden('valimis', c.valimis and '1' or '')}
<script>
  dirty = false; 
  function change_aind(arg)
  {
    var fld = arg.currentTarget || arg;
    if($(fld).val() != '')
    {
       var others = $(fld).closest('.row-aind').find('.aind').filter(function(){
         return (this.id != fld.id);
       });
       others.val('').trigger('change');
    }
    $('#salvesta').hide();
  }
</script>

## Kõigepealt valik hindajad, kus kuvatakse kõik oma kooli hindajad, kellel on juba vastav profiil olemas.
## Järgmine valik on oma kooli õpetajad, kellel vastavat hindaja rolli pole
## ja siis isikukood juhuks, kui kool soovib määrata hindajat, kes ei ole tema kooli pedagoog.

<div class="gray-legend p-3">

% if c.paarishindamine:
<div class="rounded border m-2 p-2">
  ${self.search_i(1)}
</div>

<div class="rounded border m-2 p-2">
  ${self.search_i(2)}
</div>

% else:
  ${self.search_i(1)}
% endif

<div class="text-right">
  ${h.button(value=_("Otsi"), id="otsi")}
</div>
</div>

% if c.kasutaja1 and not c.error1 and (not c.paarishindamine or c.kasutaja2) and not c.error2:
<div class="mt-2 p-2" id="salvesta">
  ${self.hsettings()}
</div>
% endif

${h.end_form()}

<%def name="search_i(ind)">
<%
  if ind == 2:
     hkasutaja_id = c.hkasutaja2_id
     opetaja_id = c.opetaja2_id
     kasutaja = c.kasutaja2
     isikukood = c.isikukood2
     error = c.error2
     muuda_profiil = c.muuda_profiil2
  else:
     hkasutaja_id = c.hkasutaja1_id
     opetaja_id = c.opetaja1_id
     kasutaja = c.kasutaja1
     isikukood = c.isikukood1
     error = c.error1
     muuda_profiil = c.muuda_profiil1
%>
  % if error:
  <div>
      ${h.alert_error(error)}
  </div>
  % endif
  <div class="p-2">
    <div class="d-flex">
      <div class="flex-grow-1">
        <h4>
      % if c.paarishindamine:
        <b>
          ${ind == 1 and _("I hindaja") or _("II hindaja")}
        </b>
      % endif
      % if kasutaja:
        ${kasutaja.nimi}
        % endif
        </h4>
      </div>
      % if error and kasutaja and muuda_profiil:
      <div class="pl-2">
        ${h.hidden(f'isik{ind}_id', kasutaja.id)}
        ${h.button(value=_("Muuda isiku profiil sobivaks"), id=f"sobita{ind}")}
      </div>
      % endif
    </div>
  </div>
  
  <div class="row row-aind">
    % if len(c.opt_kasutaja):
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Hindajad"), f'hkasutaja{ind}_id')}
        ${h.select2(f'hkasutaja{ind}_id', hkasutaja_id, c.opt_kasutaja, empty=True, class_="aind", allowClear=True, on_select="change_aind")}
      </div>
    </div>
    % endif
    % if len(c.opt_opetaja):
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Minu kooli õpetajad"), f'opetaja{ind}_id')}
        ${h.select2(f'opetaja{ind}_id', opetaja_id, c.opt_opetaja, empty=True, class_="aind", allowClear=True, on_select="change_aind")}
      </div>
    </div>
    % endif
    <div class="col-12 col-md-4">
      <div class="form-group">    
          ${h.flb(_("Hindaja isikukood"), f'isikukood{ind}')}
          ${h.text(f'isikukood{ind}',isikukood, class_="aind", onchange="change_aind(this)")}
          ${h.hidden(f'kasutaja{ind}_id', kasutaja and not error and kasutaja.id or '')}
      </div>
    </div>
  </div>
</%def>

<%def name="hsettings()">
  <div class="form-group row">
    ${h.flb3(_("Keel"), 'flang')}
    <div id="flang" class="col">
      ${model.Klrida.get_lang_nimi(c.lang)}
    </div>
  </div>
  
  % if c.sooritajate_arv != '':
  <div class="brown my-2">${_("Kokku {n} hinnatavat tööd").format(n=c.sooritajate_arv)}
    % if c.testimiskord.sisaldab_valimit:
    % if c.valimis:
    (${_("valimi hindamine")})
    % else:
    (${_("mitte-valimi hindamine")})
    % endif
    % endif
  </div>
  % endif

  % if len(c.klassid) > 1:
  <div class="form-group row">
    ${h.flb3(_("Klass"), 'klassid')}
    <div id="klassid" class="col">
    % for klass, paralleel, cnt in c.klassid:
    <%
      value = '%s-%s' % (klass, paralleel)
      label = not klass and _("määramata") or f"{klass} {paralleel}"
    %>
    ${h.checkbox('klass', value, checked=True, label=f'{label} ({cnt})')}
    % endfor
    ${h.hidden('klassid_arv', len(c.klassid))}
    </div>
  </div>
  % endif
  
  <div class="form-group row">
    ${h.flb3(_("Max tööde arv"), 'planeeritud_toode_arv', 'pr-3')}
    <div class="col">
      ${h.posint5('planeeritud_toode_arv', '')}
    </div>
  </div>
  
  % if c.vali1v2:
  ${h.submit(_("Vali I hindaja"), name="vali1")}
  ${h.submit(_("Vali II hindaja"), name="vali2")}
  % else:
  ${h.submit(name='vali')}
  % endif
</%def>

<script>
  $('button#otsi').click(function(){
      var url = "${h.url_current(otsi=True)}";
      dialog_load(url, $(this.form).serialize(),'get', $(this.form).parent());
  });
% if c.kasutaja1:
  $('button#sobita1').click(function(){
      var url = "${h.url_current(sobita=c.kasutaja1.id)}";
      dialog_load(url, $(this.form).serialize(),'post', $(this.form).parent());
  });
% endif
% if c.kasutaja2:  
  $('button#sobita2').click(function(){
      var url = "${h.url_current(sobita=c.kasutaja2.id)}";
      dialog_load(url, $(this.form).serialize(),'post', $(this.form).parent());
  });
% endif
</script>
