## Ettepaneku kirjutamisel ühe kirjaliku ülesande sisu
<%inherit file="ekspert.hindamine.ylesanne.mako"/>
<% c.is_ettepanek = True %>

<%def name="ylesanded()">   
% if not c.vy:
## ylesanneteta_tulemus
 ${h.alert_notice(_("Tulemused ainult protokollil"), False)}
% else:
  ## ei ole vaja sakke
 ${self.ty_form()}
% endif
</%def>

<%def name="footer_buttons()">
% if c.hindamine and c.is_edit:
${h.button(_("Salvesta"), id='peata', class_='hbsave')}

<script>
  $('button.hbsave').click(function(){
    if(is_dblclick($(this)))
      return;
    var form = $('form#form_save_h');
    var container = form.parent();
    var iframe = $('iframe.hylesanne');
    copy_valuation_from_iframe(iframe, form);  
    var data = form.serialize() + '&op=' + this.id;
    dialog_load(form.attr('action'), data, 'post', container);
  });
</script>
% endif
</%def>

