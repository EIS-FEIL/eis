## värv keskkonna eristamiseks
% if c.style:
<%
  st_bgcolor = c.style.get('bgcolor') or '#e4882a'
  st_bghover = c.style.get('bghover') or '#ba5915'
  st_outline = c.style.get('outline') or '#f7a047'
  st_link = c.style.get('link') or '#dd7f26'
  st_fheader = c.style.get('fheader') or '#ffd6ad'
%>
<style>
nav.navbar,nav.navbar .dropdown-menu{ background: ${st_bgcolor};}
nav.navbar ul.nav a:hover { background: ${st_bghover};}
div.table-header > div {background: ${st_outline};}
:input.active { border:3px solid ${st_link}}
A:link, A:visited { color: ${st_link}}
.act {background: ${st_bghover};}
.bgcolor {background: ${st_bgcolor};}   
.bgcolor-color {color: ${st_bgcolor};}   
.menu2, a:link.menu2, a:visited.menu2 {	color: ${st_bghover};}
div.xclose { float:right;color: ${st_bghover};}
.glyphicon {color: ${st_bghover};}
.dropdownmenutbl{ padding:8px;background: ${st_bgcolor};}
.dropdown:hover .dropdown-menu { background: ${st_bgcolor};}
input.btn, INPUT.button1, button.button1, a.button1, a.button1:visited, a.button1:link { background: ${st_bgcolor};}
INPUT.button150, button.button150{background: ${st_bgcolor};}
.field {background: ${st_bgcolor};}
.search1 {border: .5px solid ${st_bgcolor};}
.search {background: ${st_bgcolor};}
.search td.field-header, .field-header,
table.form-border td.field-header, table.form td.field-header  {background: ${st_fheader};}
table.form-border {border:1px ${st_bgcolor} solid;}
table.grid td { border:1px ${st_bgcolor} solid;}
table.list, div.table.list {background: ${st_bgcolor};}
td.rightborder, th.rightborder { border-right:3px solid ${st_bgcolor};}
table.inborder{ background: ${st_bgcolor};}
table.inborder>tbody>tr>td.bgcolor { background: ${st_bgcolor};}
.border { border: 1px ${st_bgcolor} solid;}
tr.firstrow td {border-top:2px ${st_bgcolor} solid;}
div.menubg { background-color:${st_bgcolor};}
button:hover,
a.button:hover,input[type="button"]:hover,input[type="submit"]:hover {
color: ${st_bgcolor}; border: 1px solid ${st_bgcolor}; background: #eeeeee;}
div.bubble-frame { border: 1px solid ${st_bgcolor};}
table.iline>tbody>tr>td { border-top: .5px ${st_bgcolor} solid; }
.search td,th,.field_title, .search td.fh, .search td.frh { background: ${st_outline};}
caption {background: ${st_outline};}
button:focus,input[type="button"]:focus,input[type="submit"]:focus{
outline: 1px outset ${st_outline};}
.togglebutton:hover{ background-color:${st_outline};}
a.paginate { background-image:none; background-color: ${st_bgcolor};}
h1,h2,h3 {color: ${st_link};}
</style>
% endif
