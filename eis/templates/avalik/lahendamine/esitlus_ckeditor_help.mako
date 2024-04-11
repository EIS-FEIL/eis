## -*- coding: utf-8 -*- 
<%
    help = {}
    if c.lang == const.LANG_RU:
        help['Superscript'] = """      
<p>
  Для использования кнопки [icon]:
  <ol>
    <li>введи число, которое хочешь возвести в степень;</li>
    <li>на панели кнопок щелкни мышкой на иконку [icon];</li>
    <li>запиши нужный показатель степени;</li>
    <li>на панели кнопок снова щелкни на [icon] и продолжи.</li>
  </ol>
</p>
"""
    else:
        help['Superscript'] = """      
  <p>
    Nupu [icon] kasutamiseks:
    <ol>
      <li>kirjuta arv, mida soovid astendada;</li>
      <li>klõpsa nupureal pildil [icon];</li>
      <li>kirjuta astendajaks sobiv arv;</li>
      <li>klõpsa uuesti nupureal pildil [icon] ja jätka.</li>
    </ol>
  </p>
  """

    c.ckeditor_help = ""
    for icon in c.ylesanne.get_ckeditor_icons():
        icon_help = help.get(icon)
        if icon_help:
            icon_img = c.opt.get_ckeditor_icon_img(icon)
            c.ckeditor_help += icon_help.replace('[icon]', icon_img)
%>
