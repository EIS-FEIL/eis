<%include file="/common/message.mako"/>
${h.form_save(c.roll.id)}
<% sub = c.params.get('sub') %>
${h.hidden('sub', sub)}

    <%
       piirkond_id = c.roll.koht and c.roll.koht.piirkond_id
       aadress = c.roll.koht and c.roll.koht.aadress
       maakond = aadress and aadress.maakond
       vald = aadress and aadress.vald

       if c._arrayindexes != '':
          if c.params.get('maakond_kood'):
             maakond = model.Aadresskomponent.get_by_tase_kood(1, c.params.get('maakond_kood'))
          if c.params.get('vald_kood'):
             vald = model.Aadresskomponent.get_by_tase_kood(2, c.params.get('vald_kood'))
    %>

${h.rqexp(None, _("Palun vali kas piirkond või maakond ja vald/linn"))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4">
      ${h.flb(_("Piirkond"), 'piirkond_id')}
      <div>
      <%
         c.piirkond_id = c.piirkond_id
         c.piirkond_field = 'piirkond_id'
         c.piirkond_on_change = 'change_by_piirkond();'
      %>
      <%include file="/admin/piirkonnavalik.mako"/>
      </div>
    </div>
    <div class="col-12 col-md-4">
      ${h.flb(_("Maakond"),'maakond_kood')}
      <div>
        ${h.select('maakond_kood', maakond and maakond.kood,
        model.Aadresskomponent.get_opt(None),
        empty=True,onchange="change_vald()")}
      </div>
    </div>
    <div class="col-12 col-md-4">    
      ${h.flb(_("Vald/linn"),'vald_kood')}
      <div>
        ${h.select('vald_kood', vald and vald.kood,
        maakond and maakond.get_opt_alamad(2) or [], empty=True,
        onchange="change_koht()")}
      </div>
    </div>
  </div>
</div>

${h.rqexp()}
<div class="form-wrapper-lineborder mb-2">
  <div class="form-group row">
    ${h.flb3(_("Soorituskoht"), rq=True)}
    <div class="col">
      ${h.select('koht_id', c.roll.koht_id,
      vald and vald.get_koht_opt() or [])}
    </div>
  </div>

% if sub == 'roll':
  <div class="form-group row">
    ${h.flb3(_("Roll"), rq=True)}
    <div class="col">
      ${h.select('kasutajagrupp_id', c.item and c.item.kasutajagrupp_id, c.opt.get_antav_kooligrupp(c.app_ekk), onchange='grupp_changed()')}
    </div>
  </div>
  <div class="form-group row invisible" id="r_aine">
    ${h.flb3(_("Õppeaine"))}
    <div class="col">
      ${h.select('aine_kood', c.item and c.item.aine_kood, 
      c.opt.klread_kood('AINE', vaikimisi=c.item and c.item.aine_kood or None))} 
    </div>
  </div>
% endif
  <div class="form-group row">
    ${h.flb3(_("Kehtib kuni"))}
    <div class="col">
      ${h.date_field('kehtib_kuni', c.roll.kehtib_kuni_ui, wide=False)}
    </div>
  </div>
</div>

<script>
        function change_by_piirkond()
        {
           var url = "${h.url('pub_formatted_valikud', kood='PIIRKONNAKOHT', format='json')}";
           var ylem_id = $('#piirkond_id').val();
           if(ylem_id != '')
           {
              var data = {ylem_id: ylem_id};
              var target = $('select#koht_id');
              $('select#vald_kood').val('');
              $('select#maakond_kood').val('');
              update_options(null, url, null, target, data, null, true);
           }
        }
        function change_vald()
        {
           var url = "${h.url('pub_formatted_valikud', kood='ADRKOMP',format='json')}";
           $('select#prk_id').val('');
           var data = {ylem_tasekood: $('select#maakond_kood').val()};
           var target = $('select#vald_kood');
           var subtarget = $('select#koht_id');
           update_options(null, url, null, target, data, subtarget, true);
        }
        function change_koht()
        {
           var vald_kood = $('select#vald_kood').val();
           if(vald_kood)
           {
              $('select#prk_id').val('');
              var url = "${h.url('pub_formatted_valikud', kood='KOHT', format='json')}";
              var data = {ylem_tasekood: vald_kood};
              var target = $('select#koht_id');
              update_options(null, url, null, target, data);
           }
        }
% if sub == 'roll':
  function grupp_changed()
  {
     var grupp_id = $('select#kasutajagrupp_id').val();
     var b = (grupp_id == '${const.GRUPP_AINEOPETAJA}');
     $('tr#r_aine').toggleClass('invisible', !b);
  }
  $(document).ready(function(){
    $('input#kehtib_kuni').datepicker();
    grupp_changed();
  });
% endif
</script>
<div class="text-right">
  ${h.submit_dlg()}
</div>
${h.end_form()}

