## -*- coding: utf-8 -*-
## Teadete kuvamine
<% 
   messages = request.session.pop_flash('success')
%>

% for message in messages:
  ${h.alert_success(message, False)}
% endfor

<% 
   messages = request.session.pop_flash('error')
%>
% for message in messages:
${h.alert_error(message, False)}
% endfor

<% 
   messages = request.session.pop_flash('notice')
%>
% for message in messages:
${h.alert_notice(message, False)}
% endfor

<% 
   messages = request.session.pop_flash('beep')
%>
% if len(messages):
<audio autoplay="autoplay">
  <source src="/static/images/beep.mp3"/>
  <source src="/static/images/beep.wav"/>
  <embed src="/static/images/beep.mp3" autostart="true" hidden="true" width="0" height="0" id="beep"></embed>
</audio> 
% endif

## lisame abiinfo sisestamise lingid, kui kasutajal on selline õigus
% if c.user.helpmaster:
<script>
if(window.jQuery) { $(function(){ add_help_edit(); });}
</script>	 
% endif

