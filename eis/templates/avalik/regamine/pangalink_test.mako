## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>

<%def name="page_title()">
${_("Pangalingi testimine")}
</%def>      

<%include file="avaldus.tasumine.mako"/>

% if c.is_devel:
<form action="http://eisdev:5000/admin/pangalinktest/seb/return" method="post" target="local">
<%
  data = [
  ('EMKNO','15725'),
  ('VK_SERVICE','1111'),
  ('VK_VERSION','008'),
  ('VK_SND_ID','EYP'),
  ('VK_REC_ID','testvpos'),
  ('VK_STAMP','T8jHCmoUVgbB0LM4FdW9'),
  ('VK_T_NO','15725'),
  ('VK_AMOUNT','.01'),
  ('VK_CURR','EUR'),
  ('VK_REC_ACC','EE411010002050618003'),
  ('VK_REC_NAME','Keupmees Test'),
  ('VK_SND_ACC','EE541010010046155012'),
  ('VK_SND_NAME','TIIGER LEOPOLDÃµ'),
  ('VK_REF','3500081539'),
  ('VK_MSG','Pangalingi testimine'),
  ('VK_T_DATETIME','2019-08-26T07:15:44+0300'),
  ('VK_MAC','IO/Qf9aff9ebWRkrXrjq0hp4IMwMg2fGE03eTPeV2XPdLZKFui4sWSO8eC+p8+lIYJcnxwxRm5DwPipyNfEuBG5dIfTzC54TlXUvK+P6A9Q735ORAGiCN4dp+rqorAVOKzMmNxKUIcXLAFFuiWoh9yRuvEiPRt2x9EJrJ5Ib53Y='),
  ('VK_LANG','EST'),
  ('VK_RETURN','http://localhost:6545/admin/pangalinktest/seb/return'),
  ('VK_AUTO','N'),
  ('VK_ENCODING','UTF-8'),
  ]
%>
% for key, val in data:
${h.hidden(key, val)}
% endfor
${h.submit('Post response')}
% endif
</form>
