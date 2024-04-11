% for r in c.ylesanne.vahendid:
<% 
   vahend = r.abivahend
   t_vahend = vahend.tran(request.locale_name)
   nimi = t_vahend.nimi
   cls = 'toolbtn m-1'
   if vahend.kood == const.VAHEND_MALL:
       onclick = "return toggle_tool(this, 'mall', '/static/abivahendid/mall.png')"
   elif vahend.kood == const.VAHEND_JOONLAUD:
       onclick = "return toggle_tool(this, 'joonlaud', '/static/abivahendid/joonlaud.png')"
   elif vahend.kood == const.VAHEND_JOONLAUD2:
       onclick = "return toggle_tool(this, 'liner2', '/static/abivahendid/joonlaud2.gif')"
   elif vahend.kirjeldus or vahend.pais:
       onclick = "open_dlg({dialog_id:'vahend_%s', title:'%s',iframe_url:'%s', width:%s, height:%s, below:$(this).closest('.tools')}).addClass('dlgtool')" % (r.vahend_kood, nimi, 
         h.url_current('showtool', task_id=c.ylesanne.id, vahend=r.vahend_kood), vahend.laius or 600, vahend.korgus or 400)
   else:
       onclick = None 
   ikoon = vahend.ikoon_url or '/static/abivahendid/muu_ikoon.png'
%>
% if onclick:
${h.image(src=ikoon, onclick=onclick, alt=nimi, title=nimi, height=38, class_=cls)}
% endif
% endfor
