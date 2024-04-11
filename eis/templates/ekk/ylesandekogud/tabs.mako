<%namespace name="tab" file='/common/tab.mako'/>
% if c.ylesandekogu.id:
${tab.draw('ylesandekogud', h.url('edit_ylesandekogu', id=c.ylesandekogu.id), _("E-kogu"))}
${tab.draw('kogusisu', h.url('ylesandekogu_kogusisu', kogu_id=c.ylesandekogu.id), _("Testid ja ülesanded"))}
${tab.draw('muutjad', h.url('ylesandekogu_muutjad', id=c.ylesandekogu.id), _("Koostamise ajalugu"))}
% else:
${tab.draw('ylesandekogud', None, _("E-kogu"))}
${tab.draw('kogusisu', None, _("Testid ja ülesanded"))}
${tab.draw('muutjad', None, _("Koostamise ajalugu"))}
% endif

