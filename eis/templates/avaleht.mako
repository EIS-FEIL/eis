<%inherit file="/common/pagenw.mako"/>
<%def name="require()">
% if c.app_plank:
<meta name="description" content="Plankide moodul"/>
% else:
<meta name="description" content="Ülesanded ja testid õppuritele ja õpetajatele, harjutamiseks ja eksamineerimiseks"/>
% endif
</%def>

<%def name="page_main()">
<main class="page-content flex-grow-1">
  ${self.requirenw()}
  <div class="container ${c.pagenw and 'container-nw' or c.pagexl and 'container-lg' or ''}">
    <%include file="/common/message.mako" />
    <div class="page ${c.pagenw and 'container-nw' or ''}" id="${h.page_id(self)}">
      <span id="maincontent"></span>
% if c.app_ekk and request.is_ext() and c.test_data:
      <div id="trace"></div>
      <%include file="admin.info.mako"/>
% else:
      ${self.home()}
% endif
      ${self.jscript()}
    </div>
  </div>
</main>
</%def>

<%def name="textbanner()">
## avalehe lisabanner autentimata kasutajatele
% if c.app_eis and not c.user.is_authenticated:
    <nav class="navbar navbar-expand-lg navbar-textbanner">
      <div class="container d-flex">
        <div class="textbanner flex-grow-1">
          <div class="textbanner-text">
           % if c.inst_name == 'clone':
            <div class="textbanner-title pl-3">
              ${_("Kõrgkoolide sisseastumistestide ja kutseeksamite sooritamise keskkond")}
            </div>
            <div class="pl-2">
              ${h.link_to(_("Tutvu lähemalt meie võimalustega"), 'https://projektid.edu.ee/pages/viewpage.action?pageId=51642534', target="_blank", rel="noopener")}
            </div>
          % else:
            <div class="textbanner-title pl-3">
              ${_("Eksamite ja testide loomise ning lahendamise keskkond")}
            </div>
            <div class="pl-2">
              ${h.link_to(_("Tutvu lähemalt meie võimalustega"), 'https://projektid.edu.ee/display/EKAV/Keskkonna+tutvustus', target="_blank", rel="noopener")}
            </div>
          % endif
          </div>
        </div>
      </div>
    </nav>
% endif
</%def>

<%def name="praegused_testid()">
% if c.praegu:
        <div class="col-12 p-3">
            % for sooritaja_id, test_id, t_nimi, algus in c.praegu:
            <%
            s_algus = h.str_time_from_datetime(algus)
            url = h.url('sooritamine_alustamine', test_id=test_id, sooritaja_id=sooritaja_id)
            lnk = h.link_to(_("Mine sooritama!"), url=url)
            if algus < model.datetime.now():
                buf = _("{test} on alanud!").format(test=t_nimi) + ' ' + lnk
                cls = 'alert-danger'       
            else:       
                buf = _("{test} on algamas!").format(test=t_nimi) + ' ' + lnk
                cls = 'alert-primary'
            %>
              ##${h._alert(cls + ' py-6', buf, False, mdicls='mdi-clock-alert')}
              ${h._alert(cls, buf, False, mdicls='mdi-clock-alert')}              
            % endfor
        </div>
% endif
</%def>            

<%def name="home()">      
      <%
        on_teade = c.user.is_authenticated
        pilt = (not on_teade or not c.di_info) and model.Avalehepilt.get_kehtiv()
      %>
      % if c.user.is_authenticated:
      <h1>${_("Tere, {nimi}!").format(nimi=c.user.eesnimi)}</h1>
      % endif
      <div class="row">
        ${self.praegused_testid()}
        % if on_teade:
        <% cls = not c.di_info and 'col-lg-7' or 'col-lg-6' %>
        <div class="${cls} p-3">
          % if c.info_test or c.info_tulemus or c.info_reg or c.user.cnt_new_msg:
          <h2>${_("Sulle suunatud!")}</h2>

          <div class="mb-5">
          % if c.info_test:
          ${h.alert_info(h.link_to(c.info_test + '.', url=h.url('sooritamised', avaldamistase=const.AVALIK_POLE)), False, mdicls='mdi-puzzle')}
          % endif
          % if c.info_tulemus:
          ${h.alert_success(c.info_tulemus, False, mdicls='mdi-poll')}
          % endif
          % if c.info_reg:
          ${h.alert_notice(h.link_to(c.info_reg, url=h.url('regamised')), False, mdicls='mdi-application')}
          % endif
          % if c.user.cnt_new_msg:
          ${h.alert_notice(h.link_to(_("Sul on {n} uut teadet.").format(n=c.user.cnt_new_msg), url=h.url('minu_teated')), False, mdicls='mdi-email-multiple')}
          % endif
          </div>
          % endif
          
          <h2>${_("EISi moodulid")}</h2>
          ${self.moodulid()}
        </div>
        % endif
        % if c.di_info:
        <% cls = not on_teade and 'col-lg-7 pl-6 py-3' or 'col-lg-6 p-3' %>        
        <div class="${cls}">
          <% c.lnk_arh = True %>
          ${self.listinfo(model.Avaleheinfo.KELLELE_ADMIN, _("Koolijuhtidele"))}
          ${self.listinfo(model.Avaleheinfo.KELLELE_PEDAGOOG, _("Pedagoogidele"))}
          ${self.listinfo(model.Avaleheinfo.KELLELE_OPILANE, _("Õpilastele"))}
          ${self.listinfo(model.Avaleheinfo.KELLELE_SOORITAJA, _("Testide sooritajatele"))}          
          ${self.listinfo(model.Avaleheinfo.KELLELE_X, _("Üldised teated"))}          
        </div>
        % endif
        % if pilt:
        <% cls = (on_teade or c.di_info) and 'col-lg-5' or 'col-lg-8' %>
        <div class="${cls} p-3">
          ${self.img_licensed(pilt)}
        </div>
        % endif
      </div>
</%def>

<%def name="listinfo(kellele, title)">
 <% li_info = c.di_info.get(kellele) %>
 % if li_info:
          <div class="d-flex flex-wrap">
            <h2 class="flex-grow-1">${title}</h2>
            % if c.lnk_arh:
            % if not c.arh:
            ${h.link_to_container(_("Vanad teated"), h.url('avaleht', arh=1), mdicls='mdi-archive')}
            % else:
            ${h.link_to_container(_("Peida vanad teated"), h.url('avaleht'), mdicls='mdi-archive')}
            % endif
            <% c.lnk_arh = False %>
            % endif
          </div>
          % for rcd in li_info:
          ${self.infobox(rcd)}
          % endfor
 % endif
</%def>

<%def name="moodulid()">
<%
  on_plank = c.user.id and not c.app_plank and not c.user.testpw_id and c.user.has_permission('plangid', const.BT_SHOW)
  on_ekk = c.user.id and not c.app_ekk and not c.user.testpw_id and c.user.has_ekk()
%>
          % if not c.app_eis:
          <div>
            ${h.link_to(_("Avalik vaade"), '/eis', mdicls='mdi-home')}
          </div>
          % endif
          % if on_plank:
          <div>
            ${h.link_to(_("Plankide moodul"), '/plank', mdicls='mdi-clipboard-text')}
          </div>
          % endif
          % if on_ekk:
          <div>
            ${h.link_to(_("Siseveeb"), '/ekk', mdicls='mdi-home-account')}
          </div>
          % endif

          % if c.inst_name == 'clone':
          <div>
            ${h.link_to(_("Eksamite infosüsteem"), 'https://eis.ekk.edu.ee/eis', mdicls='mdi-forward')}
          </div>
          % elif c.inst_name == 'test' or c.inst_name == 'prelive':
          <div>
            ${h.link_to(_("Eksamite infosüsteem (live)"), 'https://eis.ekk.edu.ee/eis', mdicls='mdi-forward')}
          </div>
          % endif

          % if c.inst_name != 'clone':
          <div>
            ${h.link_to(_("Kutseeksamid"), 'https://testid.edu.ee/eis', mdicls='mdi-worker')}
          </div>
          % endif
</%def>          
      
<%def name="infobox(rcd)">
  <%
  map_tyyp = {model.Avaleheinfo.TYYP_HOIATUS: 'info-red',
              model.Avaleheinfo.TYYP_TULEMUS: 'info-green',
              model.Avaleheinfo.TYYP_INFO: 'info-blue',
              }  
  %>    
  <div class="infobox my-3">
    <div class="${map_tyyp.get(rcd.tyyp)}">
      <h6>${rcd.pealkiri}</h6>
      % if c.arh and rcd.kuni < model.date.today():
      <div><i><small>${_("Kuvatud")} ${h.str_from_date(rcd.alates)} - ${h.str_from_date(rcd.kuni)}</small></i></div>
      % endif
      <div>
        ${rcd.sisu}
        % if rcd.lisasisu:
        <div class="moreinfo">
          <button type="button" class="morebtn btn btn-link">${h.mdi_icon('mdi-menu-down')} ${_("Rohkem infot")}</button>
          <div class="morebody pl-3" style="display:none">
            ${rcd.lisasisu}
          </div>
        </div>
        % endif
      </div>
    </div>
  </div>
</%def>

<%def name="img_licensed(item)">
<%
  license = ''
  if item.autor:
     license += _("Autor") + ': ' + item.autor
  if item.allikas:
     license += (license and '<br/>' or '') + item.allikas
%>
<div class="text-right">
${h.image(h.url('avalehepilt', format=item.fileext, id=item.id, v=item.fileversion), class_=f"avimg-{item.id}", width="100%")}
% if license:
<button class="btn iconbtn img-license" data-toggle="tooltip" data-placement="bottom" title="${h.hm_str2(license)}">${h.mdi_icon('mdi-license')}</button>
% endif
</div>
</%def>

<%def name="jscript()">
<script>
  ## rohkema info kuvamine ja peitmine
  $('.moreinfo .morebtn').click(function(){
  $(this).find('.mdi').toggleClass('mdi-menu-down').toggleClass('mdi-menu-up');
  $(this).closest('.moreinfo').find('.morebody').toggle();
  });

  ## pildi autor ja allikas kuvatakse tooltipina
  $('.img-license').tooltip({html: true});
</script>
</%def>
