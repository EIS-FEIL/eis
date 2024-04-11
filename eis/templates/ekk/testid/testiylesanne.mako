<%inherit file="/common/dlgpage.mako"/>
<%include file="translating.mako"/>
<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)}

% if c.test.diagnoosiv:
<div class="form-wrapper mb-2">
  <div class="form-group row">
    <div class="col">
      ${h.checkbox('f_on_jatk', c.item.on_jatk, checked=c.item.on_jatk, label=_("Jätkuülesanne"))}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Hindepallide arv"))}
    <div class="col">
      ${h.float5('f_max_pallid', c.item.max_pallid)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Toorpunktid"))}
    <div class="col">
      % for vy in c.item.valitudylesanded:
      % if vy.ylesanne_id:
      ${h.fstr(vy.ylesanne.max_pallid)}
      % endif
      % endfor
    </div>
  </div>
</div>
% else:
  ${h.hidden('f_alatest_id', c.item.alatest_id)}
  ${h.hidden('f_testiplokk_id', c.item.testiplokk_id)}
  <% aine = c.testiosa.test.aine_kood %>
${h.rqexp()}
<div class="form-wrapper mb-2">
  <div class="form-group row">
    <%
      span = f'<span class="jrk">{c.item.tahis or "-"}</span>'
      label = _("Testiülesanne nr {n}").format(n=span)
    %>
    ${h.flb3(label, rq=True)}
    <div class="col-md-2">
      % if c.is_tr:
      ${c.item.liik_nimi}
      % else:
      ${h.select('f_liik', c.item.liik, model.Testiylesanne.opt_liik)}
      <script>
        $('#f_liik').change(function(){
        $('input[name="f_kuvada_statistikas"]').prop('checked', $('#f_liik').val()=='Y');
        });
      </script>
      % endif
    </div>
    <div class="col">
      ${h.checkbox('f_kuvada_statistikas', 1,
      checked=c.item.kuvada_statistikas, label=_("Kuvatakse statistikas"), ronly=c.is_tr or not c.is_edit)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Testiülesande nimetus"))}
    <div class="col">
            % if c.lang:
              ${h.lang_orig(c.item.nimi)}<br/>
              ${h.lang_tag()}
              ${h.text('f_nimi', c.item.tran(c.lang).nimi, ronly=not c.is_tr)}
            % else:
              ${h.text('f_nimi', c.item.nimi, ronly=not c.is_tr and not c.is_edit)}
            % endif
    </div>
  </div>
  
  <%
    alatest = c.item.alatest or c.item.alatest_id and model.Alatest.get(c.item.alatest_id)
  %>
  % if alatest and alatest.kursus_kood:
  <div class="form-group row">
    ${h.flb3(_("Kood testide ühisosas"))}
    <div class="col">
      ${h.text('f_yhisosa_kood', c.item.yhisosa_kood, maxlength=10, size=10)}
    </div>
  </div>
  % endif

  <div class="form-group row">
    ${h.flb3(_("Hindepallide arv"))}
    <div class="col-md-2">
      ${h.float5('f_max_pallid', c.item.max_pallid)}
    </div>
    <div class="col">
      <div>
        ${h.checkbox('f_naita_max_p', 1, checked=c.item.naita_max_p, label=_("Hindepallid kuvatakse lahendajale"))}
      </div>
      <div>
        ${h.checkbox('f_on_markus_sooritajale', 1, checked=c.item.on_markus_sooritajale,
        label=_("Hindamisel saab jätta sooritajale märkusi"))}
      </div>
      <div class="d-flex flex-wrap">
        ${h.checkbox('on_valikylesanne', 1, checked=c.item.on_valikylesanne, label=_("Valikülesanne"))}
        <div class="ml-3">
            % if c.is_edit:
            ${h.int5('f_valikute_arv', c.item.valikute_arv, readonly=not c.item.on_valikylesanne)} ${_("valikute arv")}
            % else:
            ${c.item.valikute_arv or ''}
            % endif
        </div>
      </div>
      <div class="valik">
            % if c.is_edit:
            ${h.checkbox('f_valik_auto', 1, checked=c.item.valik_auto, label=_("Valikülesande valib arvuti"))}
            % elif c.item.valik_auto:
            ${_("Valikülesande valib arvuti")}
            % endif
      </div>
    </div>
  </div>

  % if not c.lang or c.item.on_valikylesanne:
  <div class="form-group row valik">
    ${h.flb3(_("Juhend"))}
    <div class="col">
            % if c.lang:
              ${h.lang_orig(c.item.sooritajajuhend)}<br/>
              ${h.lang_tag()}
              ${h.textarea('f_sooritajajuhend', c.item.tran(c.lang).sooritajajuhend, max=1024, rows=4, ronly=not c.is_tr)}
            % else:
              ${h.textarea('f_sooritajajuhend', c.item.sooritajajuhend, max=1024, rows=4, ronly=not c.is_tr and not c.is_edit)}
            % endif
    </div>
  </div>
  <div class="form-group row valik">
    ${h.flb3(_("Valikute pealkirjad"))}
    <div class="col td-pealkiri">
            <%
              pealkirjad = (c.item.pealkiri or '').split('\n')
              tran_pealkirjad = (c.item.tran(c.lang).pealkiri or '').split('\n')
            %>
            % for i in range(c.item.valikute_arv or 1):
            % if c.lang:
              ${h.lang_orig(i < len(pealkirjad) and pealkirjad[i] or _("VALIKÜLESANNE {n}").format(n=i+1))}<br/>
              ${h.lang_tag()}
              ${h.text('pealkiri-%d' % i, i < len(tran_pealkirjad) and tran_pealkirjad[i] or '', max=512, ronly=not c.is_tr)}
              <br/>
            % else:
              ${h.text('pealkiri-%d' % i, i < len(pealkirjad) and pealkirjad[i] or _("VALIKÜLESANNE {n}").format(n=i+1), max=512, ronly=not c.is_tr and not c.is_edit)}                
            % endif
            % endfor
    </div>
  </div>
  % endif

  <div class="form-group row">
    ${h.flb3(_("Hindamise liik"))}
    <div class="col-md-2">
            ${h.select('f_hindamine_kood', c.item.hindamine_kood,
            c.opt.klread_kood('HINDAMINE', empty=True, vaikimisi=c.item.hindamine_kood))}
    </div>
    <div class="col">
            ${h.checkbox('f_arvutihinnatav', 1, checked=c.item.arvutihinnatav, label=_("Arvutiga hinnatav"))}
            <script>
              $(function(){
                  $('#f_hindamine_kood').change(function(){
                      if($(this).val() == '${const.HINDAMINE_SUBJ}')
                      { 
                         $('input[name="f_arvutihinnatav"]').prop('checked', false);
                      }
                  });
                  $('input[name="f_arvutihinnatav"]').change(function(){
                      if($(this).val() == '1')
                      {
                         $('#f_hindamine_kood').val('${const.HINDAMINE_OBJ}');
                      }
                  });
              });
            </script>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Lahendamise piiraeg"))}
    <div class="col">
      <div>
        <div class="d-inline-block mr-3">
          max
          ${h.timedelta_sec('piiraeg', c.item.piiraeg, size=7, onchange="set_hoiatusaeg()", wide=False)}
        </div>
        <div class="d-inline-block">
          min
          ${h.timedelta_sec('min_aeg', c.item.min_aeg, size=7, wide=False)}
        </div>
      </div>
      <div>
        ${h.checkbox('f_piiraeg_sek', 1, checked=c.item.piiraeg_sek, label=_("Kuva sekundid"))}
      </div>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Hoiatus enne lõppu"))}
    <div class="col">
      ${h.posint5('hoiatusaeg', c.item.hoiatusaeg and c.item.hoiatusaeg/60)} ${_("minutit")}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Kooliaste"))}
    <div class="col">
      ${h.select('f_aste_kood', c.item.aste_kood,
      c.opt.astmed(aine), empty=True, vaikimisi=c.item.aste_kood)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Teema"))}
    <div class="col">
      ${h.select('f_teema_kood', c.item.teema_kood,
      c.opt.klread_kood('TEEMA', aine,bit=c.opt.aste_bit(c.item.aste_kood, aine),
      empty=True, vaikimisi=c.item.teema_kood), names=True)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Alateema"))}
    <div class="col">
            <%
               valdkond = model.Klrida.get_by_kood('TEEMA',
                             kood=c.item.teema_kood,
                             ylem_kood=aine)
               teema_id = valdkond and valdkond.id or None
            %>
            ${h.select('f_alateema_kood', c.item.alateema_kood,
            c.opt.klread_kood('TEEMA',ylem_id=teema_id,ylem_required=True,
                   bit=c.opt.aste_bit(c.item.aste_kood, aine),empty=True,
               vaikimisi=c.item.alateema_kood))}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Keeleoskuse tase"))}
    <div class="col">
      ${h.select('f_keeletase_kood', c.item.keeletase_kood,
      c.opt.klread_kood('KEELETASE', aine,
      empty=True, vaikimisi=c.item.keeletase_kood))}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Mõtlemistasand"))}
    <div class="col">
      ${h.select('f_mote_kood', c.item.mote_kood,
      c.opt.klread_kood('MOTE', empty=True, vaikimisi=c.item.mote_kood))}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Liik"))}
    <div class="col">
      ${h.select('f_tyyp', c.item.tyyp,c.opt.interaction_empty)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Kasutusmäär"))}
    <div class="col">
      ${h.float5('f_kasutusmaar', c.item.kasutusmaar)}
    </div>
  </div>
  <div class="form-group row">
    <div class="col">
      ${h.checkbox('f_ise_jargmisele', 1, checked=c.item.ise_jargmisele,
      label=_("Kohustusliku arvu vastuste andmisel minnakse automaatselt edasi"))}
    </div>
  </div>
</div>
<script>
      $(function(){
         % if not c.lang:
         $('select#f_aste_kood').change(
           callback_select("${h.url('pub_formatted_valikud', kood='TEEMA', format='json')}",
                           'aste',
                           $('select#f_teema_kood'),
                           {ylem_kood: '${aine}'},
                           $('select#f_alateema_kood'))
           );
         $('select#f_teema_kood').change(function(){
           var teema_id = $(this).find('option:selected').attr('name');
           if(teema_id)
           {
              var aste_kood = $('select#f_aste_kood').val();
              var url = "${h.url('pub_formatted_valikud', kood='ALATEEMA',format='json')}";
              var target = $('select#f_alateema_kood');
              var data = {ylem_id: teema_id, aste: aste_kood};
              update_options(null, url, null, target, data);
           }
         });

         $('input[name="on_valikylesanne"]').click(function(){
             $('#f_valikute_arv').attr('readonly',!this.checked);
             var n=$('#f_valikute_arv').val().trim();
             if(!this.checked)
                $('#f_valikute_arv').val('1');
             else if(n==''||n=='1')
                $('#f_valikute_arv').val('2');
             set_pealkirjad();
             $('.valik').toggle(this.checked);
         });
         $('.valik').toggle($('input[name="on_valikylesanne"]').prop('checked'));
         $('input#f_valikute_arv').change(function(){
             set_pealkirjad();
         });
         % endif
      });
      function set_pealkirjad()
      {
            var n;
            try {
              n = Math.max(1, parseInt($('input#f_valikute_arv').val()));
            } catch(e) {
              n = 1;
            }
            var pealkirjad = $('.td-pealkiri input[type="text"]');
            for(var i=pealkirjad.length; i<n; i++)
            {
               $('<input value="VALIKÜLESANNE '+(i+1)+'" class="datafield wide" id="pealkiri'+i+'" max="512" name="pealkiri-'+i+'" type="text">').appendTo('.td-pealkiri');
            }
            for(var i=pealkirjad.length; i>=n; i--)
            {
               pealkirjad.eq(i).remove();
            }
      }
      function set_hoiatusaeg()
      {
          var piiraeg = $('#piiraeg').val();
          if(piiraeg != '' && $('#hoiatusaeg').val() == '')
          {
             var li = piiraeg.split(':');
             var piiraeg_s = parseInt(li[0]);
             if(li.length > 1)
                piiraeg_s = piiraeg_s*60 + parseInt(li[1]);
             if(piiraeg_s > 300)
              $('#hoiatusaeg').val('5');
          }
      }
</script>
% endif

<div class="d-flex">
  % if c.is_edit or c.is_tr:
  <div class="flex-grow-1">
  % if not c.item.id:
    ${h.button(_("Lisa mitu ülesannet"), onclick="$('.howmany').show();$(this).hide();")}
    <div style="display:inline-table">
      <div class="howmany" style="display:none">
        <div class="d-flex">
          ${h.flb(_("Ülesannete arv"), 'mitu', 'pl-3 pr-1')}
          ${h.posint5('mitu', 1)}
        </div>
      </div>
    </div>
  % endif
  </div>
  <div>
    ${h.submit_dlg(clicked=True)} <span id="progress"></span>
  </div>
  % endif
</div>
      
${h.end_form()}
