<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>

<%def name="block_edit()">
<% kysimus = c.block.kysimus %>
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row mb-1">
  <% name = 'l.max_pikkus' %>
  ${ch.flb(_("Vastuse max pikkus"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.max_pikkus', kysimus.max_pikkus)}
  </div>

  <% name = 'l.pikkus' %>
  ${ch.flb(_("Rea pikkus"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.pikkus', kysimus.pikkus)}
  </div>
  <% name = "l.ridu" %>
  ${ch.flb(_("Ridade arv"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.ridu', kysimus.ridu)}
  </div>
</div>
<div class="row mb-1">
  <% name = 'l.reakorgus' %>
  ${ch.flb(_("Reakõrgus"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.float5('l.reakorgus', kysimus.reakorgus or 1.6)}
  </div>

  <% name = 'l.mask' %>
  ${ch.flb(_("Mask"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.text('l.mask', kysimus.mask)}
  </div>
</div>
<div class="row mb-1">  
  <% name = "l.vihje" %>
  ${ch.flb(_("Vihje"), name)}
  <div class="col-md-3 col-xl-4">
      % if c.lang:
        ${h.lang_orig(kysimus.vihje)}
       <div class="linebreak"></div>
        ${h.lang_tag()}
        ${h.text('l.vihje', kysimus.tran(c.lang).vihje, maxlength=256, ronly=not c.is_tr)}
      % else:
        ${h.text('l.vihje', kysimus.vihje, maxlength=256, ronly=not c.is_tr and not c.is_edit)}
      % endif
  </div>

  <% name = 'l.max_vastus' %>
  ${ch.flb(_("Vastuste arv"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.max_vastus', kysimus.max_vastus or 1)}
  </div>
  <% name = 'l.min_vastus' %>
  ${ch.flb(_("Minimaalne vastuste arv"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.min_vastus', kysimus.min_vastus)}
  </div>

  <div class="col-md-4 col-xl-3">
    ## sisuploki lisamisel vaikimisi sõnade arv sees
    <% if not kysimus.id: kysimus.sonadearv = True %>
    ${h.checkbox('l.sonadearv', 1, checked=kysimus.sonadearv, label=_("Kuvada sõnade arv vastuses"), disabled=not c.is_edit or c.lang)}
  </div>
  <div class="col-md-4 col-xl-3">
    ${h.checkbox('l.tekstianalyys', 1, checked=kysimus.tekstianalyys, label=_("Tekstianalüüs"), disabled=not c.is_edit or c.lang)}
  </div>
  <div class="col-md-4 col-xl-3">
    ${h.checkbox('l.hindaja_markused', 1, checked=kysimus.hindaja_markused, label=_("Hindaja saab tekstis vigu märkida"))}
  </div>
  <div class="col-md-4 col-xl-3">
    ${h.checkbox('l.vastus_taisekraan', 1, checked=kysimus.vastus_taisekraan, label=_("Vastust saab vaadata täisekraanil"))}
  </div>
  <div class="col-md-4 col-xl-3">
    ${h.checkbox('l.algvaartus', 1, checked=kysimus.algvaartus, label=_("Vihje jääb vastuse algväärtuseks"))}
  </div>

  <div class="col-md-4 col-xl-3">
      <% f_toggle_ckeditor = None %>
      % if c.is_edit and not c.lang:
      <script>
        var sp_toggle_ckeditor = function(){
          var ck_attr = {toolbar:'supsub',
                         language:'${request.localizer.locale_name}',
                         enterMode:$('#lrtf_enter:checked').val()
                        };
          toggle_ckeditor('am1hm1', true, null, ck_attr, 'am1_mapping1', 'l.rtf', 'am1.valem');        
        };
      </script>
      <% f_toggle_ckeditor = 'sp_toggle_ckeditor()' %>
      
      ${h.checkbox('l.rtf', 1, checked=kysimus.rtf, label=_("Kirev tekst"), onclick="%s;$('.is-rtf').toggle(this.checked);" % (f_toggle_ckeditor))} 
        % else:
          ${h.checkbox('l.rtf', 1, checked=kysimus.rtf, label=_("Kirev tekst"), disabled=True)}
      % endif
      <script>
        $(function(){
          $('.is-rtf').toggle(${kysimus.rtf and 'true' or 'false'});
        });
      </script>
  </div>
  <div class="col-md-4 col-xl-3 is-rtf">
    ${h.checkbox('l.rtf_notshared', 1, checked=kysimus.rtf_notshared, label=_("Nupuriba lahtri sees"), disabled=not c.is_edit or c.lang)}
  </div>
  <div class="col-md-8 col-xl-6 is-rtf">  
    ${h.radio('l.rtf_enter', const.RTF_ENTER_P, checkedif=kysimus.rtf_enter, label=_("Reavahetus alustab uut lõiku"))}
    ${h.radio('l.rtf_enter', const.RTF_ENTER_BR, checkedif=kysimus.rtf_enter or const.RTF_ENTER_BR, label=_("Reavahetus alustab uut rida"))}
  </div>
  <div class="col-md-3 col-xl-2">
      ${choiceutils.joondus(kysimus)}
  </div>
</div>

${choiceutils.hindamismaatriks(kysimus, basetype_opt=c.opt.tulemus_baseType, naidis=True, naidis_naha=True, heading1=_("Vastus"), can_rtf=True, f_toggle_ckeditor=f_toggle_ckeditor)}
</%def>


<%def name="block_preview()">
  % for n in range(c.block.kysimus.max_vastus or 1):
  ${h.textarea('input', '', cols=c.block.kysimus.pikkus,
    rows=c.block.kysimus.ridu, pattern=c.block.kysimus.mask, datafield=False, wide=False)}
    <br/>
  % endfor
</%def>


<%def name="block_print()">
    % if c.block.naide:
       % for n, entry in enumerate(c.block.kysimus.best_entries()):
          <b>${entry.tran(c.lang).kood1}</b>
       % endfor
    % else:
       % for n in range(c.block.kysimus.max_vastus or 1):
          ${h.print_input(c.block.kysimus.pikkus,c.block.kysimus.ridu)} <br/>
       % endfor
    % endif
</%def>

<%def name="block_view()">
  <% 
     responded = [] 
     kvskannid = []
     kysimus = c.block.kysimus
     max_vastus = kysimus.max_vastus
     if c.block.naide or c.block_correct:
        ## õige vastuse näitamine
        responses = c.correct_responses
     else:
        ## kasutaja vastuse näitamine
        responses = c.responses
     kv = responses.get(kysimus.kood) 
     kvsisud = kv and list(kv.kvsisud) or []
     kvskannid = kv and list(kv.kvskannid) or []
  %>
  ${h.qcode(kysimus, nl=True)}
  <div id="block_${c.block_prefix}" class="asblock ${c.block.kleepekeeld and 'nopaste' or ''}">
  % for n in range(max_vastus or 1):
    <%
       name = kysimus.result
       field_id = f'{name}_{n}_'
       ks = len(kvsisud) > n and kvsisud[n] or None
       value = ks and ks.sisu or ''
       if not c.is_edit and value:
          if not kysimus.rtf:
	     value = h.escape_tags(value)
          else:
             value = h.escape_script(value)

       if not ks and kysimus.algvaartus:
          value = kysimus.tran(c.lang).vihje
       elif value and ks and not (c.block.naide or c.block_correct or c.is_edit):
          value = c.ks_sisu_ksmarkustega(kv, ks.seq, value, c.on_hindamine, c.hindamine) or ''

       sonade_arv = ks and ks.sonade_arv or ''
       skann = len(kvskannid) > n and kvskannid[n]
    %>
    % if kysimus.sonadearv:
    <div class="ks-wordcounter px-3">${_("{s} sõna").format(s='<span class="wordcount" id="wordcount_%s">%d</span>' % (field_id, sonade_arv or 0))}</div>
    % endif

    <div class="ks-outer" data-kood="${kysimus.kood}_${n}" id="ks_outer_${kysimus.kood}_${n}">
      <div>
      % if max_vastus and max_vastus > 1:
      ${n+1}.
      % endif
      % if not c.is_edit and kysimus.vastus_taisekraan:
       <div class="float-right">
         <img title="${_("Maksimeerimine")}" class="ks-fullscreen p-2 mr-2" src="/static/images/maximize.png" style="float:right" border="0"/>
       </div>
      % endif
      </div>
    % if skann:
          <div ${c.on_hindamine and 'class="hinnatavlynk"' or ''}>
            ${h.image(h.url('tulemus_kvskann', sooritus_id=c.sooritus.id, id=skann.id),
            width=skann.laius_orig and skann.laius_orig/4)}
          </div>
    % else:
    <%
       if kysimus.rtf:
          ronly = False
       else:
          ronly = None
       # ronly - kuvatakse tavaline tekst
       # readonly - kuvatakse readonly sisestusväli
      
       vihje = kysimus.tran(c.lang).vihje
       classes = []
       if c.on_hindamine and kv and not kv.arvutihinnatud:
          classes.append('hinnatavlynk')
          if kysimus.hindaja_markused:
             classes.append('mcommentable')
          if kysimus.tekstianalyys:
             classes.append('textanalyzed')
       elif not c.is_edit:
          classes.append('vaadatavlynk')
          if kysimus.hindaja_markused:
             classes.append('mcommentable')
          if kysimus.tekstianalyys:
             classes.append('textanalyzed')
       if kysimus.rtf:
          classes.append('noexample')
       if kysimus.sonadearv:
          classes.append(kysimus.rtf and 'ck-wordcounting' or 'wordcounting')
      
       tulemus = kysimus.tulemus
       if tulemus.baastyyp == const.BASETYPE_INTEGER:
          classes.append('integer')
       elif tulemus.baastyyp == const.BASETYPE_FLOAT:      
          classes.append('float')
       style = ''
       if not kysimus.rtf and kysimus.reakorgus:
          style += "line-height: %s;" % str(kysimus.reakorgus)
    %>
    % if not c.is_edit or kysimus.muutmatu:
    <%
      classes.append('marginright30')
      if kysimus.joondus in const.JUSTIFIES:
         classes.append('text-align-%s' % kysimus.joondus)
      if (c.prepare_correct or c.on_hindamine and kv and kv.arvutihinnatud) and ks and ks.on_hinnatud and not c.block.varvimata:
         classes.append(model.ks_correct_cls(responses, kysimus.tulemus, kv, ks, False, not c.block_correct) or '')

      ro_classes = 'readonly ' + ' '.join(classes)  
      if kysimus.rtf or kysimus.hindaja_markused or kysimus.tekstianalyys:
          ro_value = h.literal(value)
      else:
          ro_value = h.html_nl(value)
      # mcomment jaoks ei tohi olla liigseid tyhikuid!
      if kysimus.pikkus:
          style = "width:%sem" % (kysimus.pikkus/2)
      else:
          style = ''  
      %>
      ## vastuse divi sisu ette ei tohi panna reavahetust ega tyhikuid, muidu mcomment ei tööta!
      <div data-k_id="${kysimus.id}" data-ksseq="${n}" class="${ro_classes}" style="${style}">${ro_value}</div>
      % if c.is_edit and kysimus.muutmatu:
      ${h.hidden(name, value)}
      % endif
    % else:
      ${h.textarea(name, value,
                   id=field_id,
                   cols=kysimus.pikkus, rows=kysimus.ridu, 
                   maxlength=kysimus.max_pikkus or None,
                 pattern=kysimus.mask,
                 readonly=not c.is_edit or c.block.read_only or None,
                 ronly=ronly,
                 datafield=False, wide=False,
                 title=vihje or None,
                 justify=kysimus.joondus,
                 style=style,
                 data_kood=kysimus.kood,
                 spellcheck=c.ylesanne.spellcheck,
                 class_=' '.join(classes) or None)}
    % endif
    % endif
   </div>
  % endfor
</div>
</%def>

<%def name="block_view_js()">
<% kysimus = c.block.kysimus %>
$(function(){
% for n in range(kysimus.max_vastus or 1):
    <%
       name = kysimus.result
       field_id = f'{name}_{n}_'
       classes = []
       if c.on_hindamine:
          classes.append('hinnatavlynk')
       if kysimus.rtf:
          classes.append('noexample')
       style = ''
       if kysimus.reakorgus:
          style += "body {line-height: %s;}" % str(kysimus.reakorgus)      
    %>
  % if c.is_edit:  
    % if kysimus.rtf:
    <%
      icons = c.ylesanne.get_ckeditor_icons()
      shared = not kysimus.rtf_notshared and 'Maximize' not in icons and 'y' or None
    %>
        ${h.ckeditor_js(field_id, 'custom', rows=kysimus.ridu, cols=kysimus.pikkus,
                 ronly=False,
                 disabled=not c.is_edit or c.block.read_only,
                 shared=shared,
                 justify=kysimus.joondus,
                 placeholder=kysimus.tran(c.lang).vihje,
                 icons=icons,
                 css=style,
                 entermode=kysimus.rtf_enter,
                 spellcheck=c.ylesanne.spellcheck,
                 maxlength=kysimus.max_pikkus or None,
                 class_=' '.join(classes) or None)}
         if(typeof resized === "function")
         CKEDITOR.instances['${field_id}'].on('instanceReady', function(ev){
                resized();
            % if not c.read_only:
                var field = $('textarea#${field_id}');
                input_set_finished(field);
            % endif
         });
         CKEDITOR.instances['${field_id}'].on('instanceReady', function(ev) {  
                ev.editor.on('maximize', function(evt) {
                  is_y_fullscreen = (evt.data == 1); 
                  if(typeof resized === "function") resized();
                  var body = ev.editor.document.getBody();
                  if(is_y_fullscreen)
                  {
                      body.addClass('maximized-A4').setStyle('padding','1.5cm 2.0cm 1.5cm 2.0cm');
                  }
                  else
                  {
                      body.removeClass('maximized-A4').setStyle('padding','0');
                  }
                });
         });

         CKEDITOR.instances['${field_id}'].on('change', function(){
            var field = $('textarea#${field_id}');
         % if not c.read_only:
            var hasvalue = this.getData() != '';
            field.toggleClass('hasvalue', hasvalue);
            if(!hasvalue) field.val('');
            input_set_finished(field);
        % endif
            ## muutus märgitakse kõigile sama kysimuse vastustele
            response_changed($('textarea[name="${name}"]'));
         });

         % if kysimus.rtf and 'mathck' in icons:
         var matheditor_buttons = ${model.json.dumps(c.ylesanne.get_math_icons())};  
         % endif

% if shared:
         CKEDITOR.instances['${field_id}'].on('focus', function(e){
         $('#y_ckeditor_ttop').show().position({
                my: 'left bottom',
                at: 'left top',
                of: $(this.element.$.parentElement)});
         });
         CKEDITOR.instances['${field_id}'].on('blur', function(e){
            $('#y_ckeditor_ttop').hide();
         });
% endif

    % elif c.block.read_only:
       ## ei saa vastust muuta
       $('textarea#${field_id}').prop('readonly',true);
    % endif

    % if not c.block.read_only:    
    % if not kysimus.rtf:
     $('textarea#${field_id}').keyup(function(){
        set_finished_${c.block.id}();
     }).change(function(){
        ## muutus märgitakse kõigile sama kysimuse vastustele
        response_changed($('textarea[name="${name}"]'));
     });
     k_check_finished["${kysimus.kood}"] = set_finished_${c.block.id};    
     set_finished_${c.block.id}();   
    % endif
    % endif
  % endif  
% endfor
% if c.is_edit:
    % if kysimus.sonadearv and not c.is_sp_analysis:
      % if kysimus.rtf:
       $(".asblock#block_${c.block_prefix} textarea.ck-wordcounting").each(function(){
          var field_id = this.id, editor = CKEDITOR.instances[field_id],
              counter = $('#wordcount_' + field_id);
          count_words(counter, editor.getData(), true);
          editor.on('change', function(){count_words(counter, this.getData(), true);});
       });
      % else:
       $(".asblock#block_${c.block_prefix} textarea.wordcounting").each(function(){
          var field_id = this.id, fld = $(this),
              counter = $('#wordcount_' + field_id);    
          count_words(counter, fld.val(), false);
          fld.keyup(function(){count_words(counter, fld.val(), false);});        
       });
      % endif
    % endif
% elif not c.is_edit and kysimus.vastus_taisekraan:
    $(".asblock#block_${c.block_prefix} .ks-fullscreen").click(function(){toggle_fullscreen($(this).closest('.ks-outer'));});
% endif
% if kysimus.rtf:
    if(typeof resized === "function")
       resized();
% endif
  is_response_dirty = false;
});
function set_finished_${c.block.id}()
{
    var block = $('div#block_${c.block_prefix}');    
    input_set_finished(block.find('textarea[name="${kysimus.result}"]'), ${kysimus.min_vastus or 0});
}
</%def>
