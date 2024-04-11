## Testi kõigile testiosadel tugiisikute määramine
<%include file="/common/message.mako"/>
${h.alert_notice(_("Tugiisik määratakse juhul, kui sooritaja ei ole võimeline ise testi vastuseid sisestama ja vajab selleks tugiisiku abi."),False)}

% if c.sooritus:
## yhele testiosale tugiisiku määramine
${self.tos_tugiisik(0, c.sooritus, c.sooritus.testiosa, False)}
% else:
## kõigile testiosadele tugiisiku määramine
<%
  testiosad = list(c.test.testiosad)
  show_osa = len(testiosad) > 1
%>
% for ind, testiosa in enumerate(testiosad):
<% tos = c.sooritaja and c.sooritaja.get_sooritus(testiosa.id) or None %>
${self.tos_tugiisik(ind, tos, testiosa, show_osa)}
% endfor
% endif

<%def name="tos_tugiisik(ind, tos, testiosa, show_osa)">
<% tugik = tos and tos.tugiisik_kasutaja or None %>
<div class="rounded border p-2 mb-2 tugiosa">
  % if show_osa:
  <b>${testiosa.nimi}</b>
  % endif
  <div>
    ${h.radio('tkid_%s' % testiosa.id, '',
    checked=not tugik, class_="tkid-off", label=_("Tugiisikut ei kasuta"))}
  </div>
  <div class="d-flex flex-wrap">
    ${h.radio('tkid_%s' % testiosa.id, tugik and tugik.id or '',
    checked=tugik is not None, class_="tkid-on", label=_("Kasutab tugiisikut, tugiisiku isikukood:"))}
      % if request.is_ext():
      ${h.posint('isikukood', tugik and tugik.isikukood or '', size=12, maxlength=11, class_="isikukood mr-3")}
      % else:
      ${h.text('isikukood', tugik and tugik.isikukood or '', size=16, maxlength=25, class_="isikukood mr-3")}
      % endif
    ${h.button(_("Otsi"), class_="mr-2 ikotsi", style="display:none")}
    <span class="tnimi">${tugik and tugik.nimi or ''}</span>
  </div>
  <div class="errpos"></div>
</div>
</%def>

<script>
  ## dialoogi salvestamise nupp on siis, kui kõigile testiosadele, kus soovitakse tugiisikut, on tugiisiku päring tehtud
  function toggle_btsave(){
     $('.btsave').toggle($('.tkid-on:checked[value=""]').length == 0);
  }
  $('input.tkid-on,input.tkid-off').click(toggle_btsave);

  ## nupp, kuhu kasutaja saab vajutada peale isikukoodi sisestamist (otsingu käivitab tegelikult change)
  $('.isikukood').keyup(function(){
     $('.ikotsi').toggle($(this).val().trim().length == 11);
  });
  ## isikukoodi järgi tugiisiku otsimine
  $('.isikukood').change(function(){
       var tr = $(this).closest('.tugiosa'), ik = tr.find('.isikukood').val(), tnimi = tr.find('.tnimi'), errpos = tr.find('.errpos');
       ## märgime, et kasutab tugiisikut, aga tugiisiku isikut ei ole teada
       tr.find('.tkid-on').prop('checked', true).prop('value', '');         
       $('.btsave').hide();
       tnimi.text(''); errpos.text('');
  % if request.is_ext():
       if(ik.trim().length == 11)
  % else:
       if(ik.trim() != '')
  % endif
       {
          set_spinner(tnimi);
          $.ajax({type: 'get',
               url: "${h.url_current('index', sub='tik')}",
               data:  'isikukood='+ik,
               success: function(data){
                  if(data.error) {
                      tnimi.text('');
                      alert_error(errpos, data.error);
                  } else {
                      tnimi.text(data.nimi);
                      tr.find('.tkid-on').prop('value', data.tkid); 
                      toggle_btsave();
                  }
               },
               error: function(data){
                  tnimi.text('');
                  alert_error(errpos, eis_textjs.smth_wrong);
               }
          });
       }
  });
</script>  
