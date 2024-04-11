<%
  c.grupid = [(yg, [gy.valitudylesanne.testiylesanne_id for gy in yg.grupiylesanded]) for yg in c.testiosa.ylesandegrupid]
  c.joutud_ylesanded = set()
%>
% if c.grupid:
Võimalike kombinatsioonide rohkuse tõttu ei pruugi gruppide tagasiside olla puus esitatud täpselt õigetes kohtades
% endif
<table  class="table table-borderless table-striped" style="margin:5px 0">
  <tbody>
    % for ty in c.testiosa.testiylesanded:
    % if not ty.on_jatk:
    % for vy in ty.valitudylesanded:
    % if vy.ylesanne_id:
    <tr>
      <td><b>${_("Ülesanne")} ${vy.ylesanne_id}</b> - ${vy.ylesanne.nimi}
        <% c.kobara_ylesanded = set() %>
        ${self.edasi(ty, [], 0)}
        <% c.joutud_ylesanded = c.joutud_ylesanded.union(c.kobara_ylesanded) %>
      </td>
    </tr>
    % endif
    % endfor
    % endif
    % endfor
  </tbody>
</table>

% for ty in c.testiosa.testiylesanded:
% if ty.on_jatk and ty.id not in c.joutud_ylesanded:
% for vy in ty.valitudylesanded:
% if vy.ylesanne_id:
% endif
<div class="error">
  ${_("Pole võimalik jõuda ülesandeni:")} ${vy.ylesanne_id} - ${vy.ylesanne.nimi}
</div>
% endfor
% endif
% endfor

<%def name="edasi(ty, ahel, level)">
<%
  is_cycle = False
  if ty.id in ahel:
       is_cycle = True
%>
% if level > 50:
<span class="error">etc</span>
% elif is_cycle:
<span class="error">kordus</span>
% else:
<%
  model.log.info('edasi %s %s' % (level, ty.id))
  uued_grupid = []
  for (yg, liikmed) in c.grupid:
     if ty.id in liikmed:
        # vaatame läbi grupid, kuhu see ylesanne kuulub
        muud_ylesanded = [ty_id for ty_id in liikmed if ty_id != ty.id]
        tehtud = c.joutud_ylesanded.union(ahel)
        if ty.id not in tehtud and tehtud.issuperset(muud_ylesanded):
             # loeme, et grupp sai läbitud
             # see ei ole päris täpne, kuna kõik c.joutud_ylesanded sees olevad ylesanded ei pruugi olla yhes ahelas
             uued_grupid.append(yg)
             break

  c.kobara_ylesanded.add(ty.id)
  ahel.append(ty.id)
%>
<table>
  <tbody>
    % for np in ty.normipunktid:
    <tr>
      <td>${np.nimi}</td>
      <td>
        ${self.nptagasisided(np, ahel, level)}
      </td>
    </tr>
    % endfor
    % for grupp in uued_grupid:
    % for np in grupp.normipunktid:
    <tr>
      <td>Grupp ${grupp.nimi} ${np.nimi}</td>
      <td>
        ${self.nptagasisided(np, ahel, level)}
      </td>
    </tr>
    % endfor
    % endfor
  </tbody>
</table>
% endif
</%def>

<%def name="nptagasisided(np, ahel, level)">
<table class="iline">
  <tbody>
    % for ns in np.nptagasisided:
    <%
      ahelas = not ns.ahel_testiylesanne_id
      if not ahelas:
            if ns.ahel_testiylesanne_id in ahel:
               ahelas = True
    %>
    % if ahelas:
    <tr>
      <td>
        ${np.kysimus_kood or _("Tulemus")}
        ${ns.tingimus_tehe_ch}
        ${ns.tingimus_valik or h.fstr(ns.tingimus_vaartus)}
        % if np.normityyp == const.NORMITYYP_PROTSENT:
        ${'%'}
        % endif
      </td>
      <td class="leftborder">
        % if ns.tagasiside:
        ${ns.tran(c.lang).tagasiside}<br/>
        % endif
        <% ty = ns.uus_testiylesanne %>
        % if ty:
        % for vy in ty.valitudylesanded:
        % if vy.ylesanne_id:
        <b>${_("Ülesanne")} ${vy.ylesanne_id}</b> - ${vy.ylesanne.nimi}
        ${self.edasi(ty, list(ahel), level+1)}
        % endif
        % endfor
        % endif
      </td>
    </tr>
    % endif
    % endfor
  </tbody>
</table>
</%def>
