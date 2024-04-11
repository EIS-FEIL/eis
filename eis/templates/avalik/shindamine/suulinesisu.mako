<%
  c.sooritused = list(c.items)
  c.sooritajate_nimed = [(tos.id, tos.sooritaja.nimi) for tos in c.sooritused] # vt helivastus.mako
%>
${self.search_form()}
${self.save_form()}

<%def name="search_form()">
${h.form_search()}
<div class="question-status d-flex flex-wrap justify-content-between">
  <div class="item mr-5 mb-2">
    ${h.flb(_("Test"), 'test_nimi')}
    <div id="test_nimi">
      ${c.test.nimi}
      ${c.testiosa.tahis}
    </div>
  </div>
% if c.testiruum:
  <div class="item mr-5 mb-2">
    ${h.flb(_("Toimumise aeg"), 'ruum_algus')}
    <div id="ruum_algus">
      ${h.str_from_date(c.testiruum.algus)}
    </div>
  </div>
  <div class="item mr-5 mb-2">
    ${h.flb(_("Soorituskoht"), 'koht_nimi')}
    <div id="koht_nimi">
      ${c.testikoht.koht.nimi}
      ${c.testiruum.tahis}
    </div>
  </div>
% endif
  <div class="item mr-5 mb-2">
    <% label = len(c.sooritused) == 1 and _("Sooritaja") or _("Sooritajad") %>
    ${h.flb(label, 'sooritused')}
    <div id="sooritused">
      % for tos in c.sooritused:
      ${self.sooritaja(tos, False)}
      % endfor
    </div>
  </div>
  
  % if len(c.hindamiskogum_opt) > 0:
  <div class="item mr-5 mb-2">
    ${h.flb(_("Hindamiskogum"), 'hindamiskogum_id')}
    <div>
      % if len(c.hindamiskogum_opt)> 1:
      ${h.select('hindamiskogum_id', c.hindamiskogum_id,
      c.hindamiskogum_opt, wide=False, onchange='this.form.submit()')}
      % else:
      ${c.hindamiskogum_opt[0][1]}
      ${h.hidden('hindamiskogum_id', c.hindamiskogum_opt[0][0])}
      % endif
    </div>          
  </div>
  % endif
  
  <div class="item mr-5 mb-2">
    ${h.flb(_("Ülesandekomplekt"), 'komplekt_id')}
    <div>
      % if len(c.opt_komplektid) == 1:
      ${c.opt_komplektid[0][1]}
      ${h.hidden('komplekt_id', c.komplekt_id)}
      % else:
      ${h.select('komplekt_id', c.komplekt_id, c.opt_komplektid, wide=False, empty=len(c.opt_komplektid)>1, 
      onchange='this.form.submit()')}
      % endif
    </div>
  </div>
</div>
${h.end_form()}

<div>
  ## helivastused, mis on yles laaditud ilma ylesandeta
  ${self.helivastused(None)}
</div>
</%def>

<%def name="sooritaja(tos, on_teised)">
<%
  # ülesannete keeleks võtame ühe sooritaja keele
  c.lang = tos.sooritaja.lang
  holek = tos.get_hindamisolek(c.hindamiskogum)
  sooritaja = tos.sooritaja
%>
      <div class="d-flex flex-wrap">
        <div>
          % if on_teised:
          ${h.checkbox('sooritus_id', tos.id, label=f'{tos.tahised} {sooritaja.nimi}', class_='teised_id')}
          % else:
          ${tos.tahised} ${sooritaja.nimi}
          ${h.hidden('sooritus_id', tos.id)}
          % endif
        </div>

        <% erivajadused = tos.get_str_erivajadused() %>
        % if erivajadused:
        <div>
          <a onclick="$('#erivajadused_${tos.id}').toggle()" class="px-3">
            ${_("Eritingimused")}
          </a>
          <span id="erivajadused_${tos.id}" style="display:none">
            ${erivajadused}
          </span>
        </div>
        % endif

        <div class="px-2">
            % if holek:
            ${holek.staatus_nimi}
              % if holek.staatus == const.H_STAATUS_HINNATUD and holek.pallid is not None:
              ${h.fstr(holek.pallid)}p
              % endif
              % if holek.selgitus:
              (${holek.selgitus})
              % endif
            % endif

            % if c.ekspert_labiviija and c.hindamine:
              <% labivaatus = c.hindamine.get_labivaatus(c.ekspert_labiviija.id) %>
              % if labivaatus and labivaatus.staatus:
              - ${_("läbi vaadatud")}
              % else:
              - ${_("läbi vaatamata")}
              % endif
            % endif
            % if c.hindamine:
              <!--hindamine_id=${c.hindamine.id}-->
            % endif
        </div>
      </div>
</%def>

<%def name="save_form()">
${h.form_save(None)}

  % if c.app_eis and c.teised_helifailis:
  <div class="d-flex flex-wrap m-2 ml-3 ">
    ${h.flb(_("Vastanud koos"), 'koos', 'mr-3')}
    <div id="koos" class="d-flex flex-wrap">
      <div>
        % for tos2 in c.teised_helifailis:
        ${self.sooritaja(tos2, True)}
        % endfor
        <script>
          $('input.teised_id').click(function(){ $('#hindakoos').toggleClass('invisible', $('.teised_id:checked').length == 0 ); });
        </script>
      </div>
      <div>
        ${h.submit(_("Hindan koos"), level=2, id="hindakoos", class_="invisible")}
      </div>
    </div>
  </div>
  % endif

<div class="d-flex flex-wrap m-2 ml-3">
    ${h.flb(_("Intervjueerija"), 'intervjuu_labiviija_id', col="mr-2")}
    <div>
      <%
        testiruumid_id = [r.testiruum_id for r in c.sooritused]
        q = (model.SessionR.query(model.Labiviija.id, model.Kasutaja.nimi)
             .filter(model.Labiviija.testiruum_id.in_(testiruumid_id))
             .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_INTERVJUU)
             .join(model.Labiviija.kasutaja)
             .order_by(model.Kasutaja.nimi))
        intervjuu_opt = [(lv_id, k_nimi) for (lv_id, k_nimi) in q.all()]
      %>
            ${h.select('intervjuu_labiviija_id',
            c.intervjuu_labiviija_id, intervjuu_opt, wide=False)}
    </div>
  </div>


% if not c.komplekt:
${h.alert_notice(_("Palun vali ülesandekomplekt!"), False)}
% elif not c.hindamiskogum:
${h.alert_notice(_("Palun vali hindamiskogum!"), False)}
% elif not len(c.hindamiskogum.testiylesanded):
${h.alert_notice(_("Hindamiskogumis ei ole ülesandeid"), False)}
% else:
    ${self.punktitabel()}

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    % if not c.app_ekk:
    % if c.testiruum:
    ${h.btn_back(url=h.url('shindamine_vastajad', testiruum_id=c.testiruum.id))}
    % else:
    ${h.btn_back(url=h.url('khindamine_vastajad', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.labiviija.id))}
    % endif
    % endif
  </div>
  ${h.submit(clicked=True)}
  ${h.submit(_("Kinnita hindamine"), id='lopeta', clicked=True)}
</div>
% endif

${h.end_form()}
</%def>

<%def name="punktitabel()">
% for n_tos, tos in enumerate(c.sooritused):
##${h.hidden('sooritus_id', tos.id)}
${h.hidden('hmine-%d.sooritus_id' % n_tos, tos.id)}
% endfor
${h.hidden('komplekt_id', c.komplekt.id, id="pt_komplekt_id")}
${h.hidden('hindamiskogum_id', c.hindamiskogum.id, id="pt_hindamiskogum_id")}

<table width="100%" class="table table-align-top">       
  <col width="200px"/>
  % for ty in c.hindamiskogum.testiylesanded:
     % if ty.alatest and ty.alatest != c.alatest:
        <% c.alatest = ty.alatest %>
        <tr>
          <td colspan="5">
            <b>${_("Alatest")}: 
               ${c.alatest.tran(c.lang).nimi}
            </b>
          </td>
        </tr>
     % endif

     % if ty.testiplokk and ty.testiplokk != c.testiplokk:
        <% c.testiplokk = ty.testiplokk %>
        <tr>
          <td colspan="5">
            <b>${_("Plokk")}: 
            ${c.testiplokk.tran(c.lang).nimi}</b>
          </td>
        </tr>
     % endif

     ${self.row_testiylesanne(ty)}
  % endfor

</table>
</%def>


<%def name="row_testiylesanne(ty)">
             % if not ty.on_valikylesanne:
                <% vy = ty.get_valitudylesanne(c.komplekt) %>
                  ${self.row_ylesanne(ty,vy)}
             % else:
                % for seq in range(1, ty.valikute_arv+1):
                  <% vy = ty.get_valitudylesanne(c.komplekt, seq=seq) %>
                  ${self.row_ylesanne(ty,vy)}
                % endfor
             % endif
</%def>

<%def name="row_ylesanne(ty,vy)">
 <%
     nimi = _("Ülesanne") + ' %s %s' % (ty.seq, ty.tran(c.lang).nimi)
 %>
 % if not vy or not vy.ylesanne:
            ## komplekt valimata või ülesanne puudub komplektist
        <tr>
          <td class="field-header">
            ${nimi}
            <!--ty_id=${ty.id}-->
          </td>
        </tr>
 % else:
       <%
          ylesanne = vy.ylesanne
          ## testiylesannete loendur
          c.counter += 1 
       %>
        <tr>
          <td class="field-header">
            <%
              if c.app_ekk:
                 url_yl = h.url('hindamine_hindajavaade_edit_lahendamine', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, id=vy.ylesanne_id, lang=c.lang, indlg=True)
              else:
                 url_yl = h.url('khindamine_edit_lahendamine', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, id=vy.ylesanne_id, lang=c.lang, indlg=True)
            %>
            ${h.link_to_dlg(nimi, url_yl, title=nimi, size='lg')}
           (${h.fstr(ylesanne.max_pallid)})
         </td>

          % if len(ylesanne.hindamisaspektid) == 0:
         <td class="field-header">${_("Punktid")}</td>
          % else:
            % for ha in ylesanne.hindamisaspektid:
         <td class="field-header">
           ${ha.aspekt_nimi} (${h.fstr(ha.max_pallid)})
         </td>
            % endfor
          % endif
         <td class="field-header" rowspan="${len(c.sooritused)+1}">
           <div class="text-right">
             <%
               if c.app_ekk:
                  url_yl = h.url('hindamine_hindajavaade_hindamiskysimused', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, lang=c.lang, indlg=True)
               else:
                  url_yl = h.url('khindamine_hindamiskysimused', toimumisaeg_id=c.toimumisaeg.id, vy_id=vy.id, lang=c.lang, indlg=True)
             %>
             ${h.link_to_dlg(_("Küsimused hindamisjuhile"), url_yl, title=nimi, size='lg')}
             % if ylesanne and ylesanne.hindamisjuhist_muudetud():
            ${h.mdi_icon('mdi-flag', title=_("Ülesande hindamisjuhendit on hiljuti muudetud!"))}
             % endif
           </div>
           <!--ty_id=${ty.id} vy_id=${vy.id}-->

           <div class="pt-2">
             ${self.helivastused(ty.id)}
           </div>
         </td>
        </tr>

    % for n_tos, tos in enumerate(c.sooritused):
        ${self.tr_ylesanne_sooritus(ty, vy, ylesanne, n_tos, tos)}
    % endfor
 % endif
</%def>

<%def name="tr_ylesanne_sooritus(ty, vy, ylesanne, n_tos, tos)">        
        <% 
           holek = tos.get_hindamisolek(c.hindamiskogum)
           hindamine = holek.get_hindamine(c.labiviija.liik) 
           yhinne = hindamine and hindamine.get_vy_ylesandehinne(vy.id) or None
           prefix = 'hmine-%d.ty-%s' % (n_tos, c.counter)
        %>
        <tr>
          <td class="pl-4">
            ## kui on mitu samaaegset vastajat, siis kuvatakse siin 
            ## igaühe kohta rida, mille esimeses veerus on sooritaja nimi
            ## kui on ainult üks vastaja, siis on esimene veerg tühi
            % if len(c.items) > 1:
              ${tos.sooritaja.nimi}
            % endif
            ${h.hidden('%s.ty_id' % prefix, ty.id)}
            ${h.hidden('%s.vy_id' % prefix, vy.id)}
          % if len(ylesanne.hindamisaspektid) > 0:
            ## veateadete koht
            ${h.hidden('%s.toorpunktid' % prefix, '')}
          % endif
          </td>
          % if len(ylesanne.hindamisaspektid) == 0:
          <td nowrap>
            ${h.posfloat('%s.toorpunktid' % prefix, yhinne and yhinne.toorpunktid, maxvalue=ylesanne.max_pallid)}
            ${h.button('', mdicls=yhinne and yhinne.markus and 'mdi-comment-text' or 'mdi-comment-text-outline', class_='notes_btn mdibtn', name=prefix, level=2, title=_("Märkused"))} 
            ${h.hidden('%s.markus' % prefix, yhinne and yhinne.markus)}
          </td>
          % else:
            % for n_ha, ha in enumerate(ylesanne.hindamisaspektid):
          <td>
            <% 
               aspektihinne = yhinne and yhinne.get_aspektihinne(ha.id) or None
               ha_prefix = '%s.ha-%d' % (prefix, n_ha)
            %>
            ${h.posfloat('%s.toorpunktid' % ha_prefix, aspektihinne and aspektihinne.toorpunktid, maxvalue=ha.max_pallid)}
            ${h.button('', mdicls=aspektihinne and aspektihinne.markus and 'mdi-comment-text' or 'mdi-comment-text-outline', class_='notes_btn mdibtn', name=ha_prefix, level=2, title=_("Märkused"))}
            
            ${h.hidden('%s.markus' % ha_prefix, aspektihinne and aspektihinne.markus)}
            ${h.hidden('%s.a_kood' % ha_prefix, ha.aspekt_kood)}
          </td>
            % endfor
          % endif
        </tr>
</%def>

<%def name="helivastused(ty_id)">
% for hvf_id, in model.Helivastus.get_hvf_by_sooritus(c.sooritused_id, ty_id):
   <% c.helivastusfail = model.Helivastusfail.get(hvf_id) %>
   % if c.helivastusfail:
   <%include file="/avalik/svastamine/helivastus.mako"/>
   % endif
  % endfor
</%def>

<script>
var wnd_yl = null;
function popup_yl(url)
{
    wnd_yl = window.open(url, "wnd_yl", "toolbar=0,location=0,status=0,menubar=0,scrollbars=1");
}
function save_notes(name)
{
    var value = $('#notes_txt').val();
    $('input[name="'+name+'.markus"]').val(value);
    var mdi = $('button.notes_btn[name="'+name+'"]>i.mdi');
    if(value){
      mdi.removeClass('mdi-comment-text-outline').addClass('mdi-comment-text');
    } else {
      mdi.removeClass('mdi-comment-text').addClass('mdi-comment-text-outline');
    }
    close_notes();
}
function close_notes()
{
    $('#notes_bubble').remove();
}
function open_notes(event, name)
{
    close_notes();
    var buf = '<span>${_("Märkused")}<br/>'+
       '<textarea id="notes_txt" rows="5" cols="50"></textarea>'+
       '<br/>'+
       '<input type="button" class="btn btn-secondary" value="${_("Salvesta")}" onclick="save_notes(\''+ name+'\')"/>'+
       '<input type="button" class="btn btn-secondary" value="${_("Katkesta")}" onclick="close_notes()"/>'+
       '</span>'
% if c.ettepanek:
    var parent = $('div#dialog_div');
% else:
    var parent = null;
% endif
    var notes_bubble = bubble('notes_bubble', buf, -10, -10, true, parent);
    var field = $('input[name="'+name+'.markus"]');
    $('#notes_txt').val(field.val());
    pos_bubble(notes_bubble, event.pageX, event.pageY, 0, parent);
}
function show_notes(event, name)
{
    close_notes();
    var buf = '<span>${_("Märkused")}<br/>'+
       '<textarea id="notes_txt" rows="5" cols="50"></textarea>'+
       '<br/>'+
       '<input type="button" class="btn btn-secondary" value="${_("Katkesta")}" onclick="close_notes()"/>'+
       '</span>'
    
% if c.ettepanek:
    var parent = $('div#dialog_div');
% else:
    var parent = null;
% endif
    var notes_bubble = bubble('notes_bubble', buf, -10, -10, true, parent);
    var field = $('input[name="'+name+'.markus"]');
    $('#notes_txt').val(field.val());
    pos_bubble(notes_bubble, event.pageX, event.pageY, 0, parent);
}
$(function(){
  $('button.notes_btn').click(function(event){
     open_notes(event, $(this).attr('name'));
  });
});
</script>
