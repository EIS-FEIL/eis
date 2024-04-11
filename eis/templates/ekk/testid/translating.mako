## Kui on testi tõlkimine või toimetamine, siis muudetakse c.is_edit ja c.is_tr
<%
if c.is_edit:
    if c.lang and c.user.has_permission('ekk-testid-tolkimine', const.BT_UPDATE,c.test):
        # tõlkimise ajal on ainult tõlkeväljad kirjutatavad
        c.is_edit = False
        c.is_tr = True
    elif not c.lang and \
            not c.user.has_permission('ekk-testid',const.BT_UPDATE, c.test) and \
            c.user.has_permission('ekk-testid-toimetamine', const.BT_UPDATE,c.test):
        # toimetaja tohib ainult tekstivälju kirjutada
        c.is_edit = False
        c.is_tr = True
%>
