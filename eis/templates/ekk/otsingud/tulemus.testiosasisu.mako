<%inherit file="/avalik/sooritamine/testiosasisu.mako"/>
<%def name="set_responded_files(vf)">
<%
   for vf in ylesandevastus.vastusfailid:
       vf.url = h.url('sooritamine_vastusfail', test_id=c.test.id, sooritus_id=c.sooritus.id,id='%s.file' % vf.id)
   c.responded_files[vf.nimi] = vf
%>
</%def>
