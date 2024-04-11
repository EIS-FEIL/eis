"Eksamistatistika raporti diagrammid"

import io
import math
import plotly.graph_objects as go
from svglib.svglib import svg2rlg
from .pdfutils import Image, Spacer, mm

def gen_dgm_confidence(data, total_avg, is_portrait):
    """Tulemuste tulpdiagramm usalduspiiriga:
    x-teljel protsendid
    y-teljel maakonnad või koolid
    """

    story = []

    # data = [["Harju maakond", 30.354838709677395, 9.246320492585934],
    #         ["Ida-Viru maakond", 81.8, 39.10164345216007],
    #         ["Pärnu maakond", 18.3, 34.492930643700692],
    #         ["Tartu maakond", 24.9375, 7.315222900220341],
    #         ["5st väiksema eksaminandide arvuga maakonnad kokku", 19.0, 11.269731310598718]
    #         ]
    # avg = 25.48

    def multiline(title):
        MAX_LINE = 33
        buf = ''
        nl_cnt = 0
        len_buf = 0
        for w in title.split(' '):
            len_w = len(w)
            if len_buf + len_w >= MAX_LINE and len_w < MAX_LINE and nl_cnt == 0:
                # ei mahu reale
                nl_cnt += 1
                buf += '<br>' + w
                len_buf = len_w
            else:
                buf += ' ' + w
                len_buf += 1 + len_w
        return buf
    
    elem_cnt = len(data)
    # kuvame ühe või mitu horisontaalset diagrammi, mis mahuvad lehele
    if is_portrait:
        page_size = 21
    else:
        page_size = 12
    for ind in range(0, elem_cnt, page_size):
        labels = []
        values = []
        errors = []
        min_res = max_res = total_avg
        n_labels = []
        annotations = []
        max_label = 0
        # lehele mahtuv osa
        chunk = reversed(data[ind: ind + page_size])
        for n, r in enumerate(chunk):
            title, value, error = r
            # y väärtuseks on nimed, aga sama nimi võib esineda mitu korda
            # seetõttu eristame lisaks y väärtused ka indeksiga
            n_labels.append(n)
            # maakondade/koolide nimed
            label = multiline(title)
            labels.append(label)

            # keskmine tulemuse protsent
            values.append(value)
            # usalduspiir
            errors.append(error)
            # tekst peal
            annot = dict(xref='x',
                         yref='y',
                         x=values[n]+3,
                         y=n+.2,
                         font=dict(size=11),
                         text=f'{round(values[n],1)}%',
                         showarrow=False)
            annotations.append(annot)
            min_res = min(value - error, min_res)
            max_res = max(value + error, max_res)

        # tulemuse skaala (x-telg)
        min_res = max(0, math.floor(min_res/10) * 10)
        max_res = min(100, math.ceil(max_res/10) * 10)
        tickvals = [i for i in range(0, 101, 10) \
                    if min_res <= i <= max_res]
        ticktext = [f'{x}%' for x in tickvals]

        # Tulpdiagrammid maakondade/koolide kaupa
        fig = go.Figure(go.Bar(
            x=values,
            y=n_labels,
            error_x=dict(type='data',
                         array=errors),
            orientation='h'))

        # Eesti keskmise joon
        max_y = len(n_labels)
        fig.add_trace(go.Scatter(
            x=[total_avg, total_avg],
            y=[-1, max_y],
            mode='lines',
            line=dict(dash='dot')
            ))
        # Eesti keskmise pealdis
        annot = dict(xref='x1',
                     yref='y1',
                     x=total_avg,
                     y=max_y-1,
                     text=f"Eesti keskmine {round(total_avg)}%",
                     font=dict(color='red'),
                     showarrow=True)
        annotations.append(annot)
        
        fig.update_layout(font_family="Times New Roman",
                          font_color="black",
                          xaxis=dict(tickvals=tickvals,
                                     ticktext=ticktext,
                                     range=[min_res, max_res]
                                     ),
                          yaxis=dict(tickvals=n_labels,
                                     ticktext=labels,
                                     range=[-.5, max_y-.5]
                                     ),                          
                          margin=dict(l=5, r=5, t=10*mm, b=6*mm),
                          annotations=annotations,
                          showlegend=False,
                          )
        
        row_cnt = len(values)
        height = row_cnt * 11 + 15
        width = is_portrait and 180 or 270
        fdata = fig.to_image(format='svg',
                             height=height * mm,
                             width=width * mm)
        img = svg2rlg(io.BytesIO(fdata))
        story.append(img)

    return story

def gen_dgm_jaotus(items, max_pallid):
    "Testitulemuse jaotusdiagramm"
    y_max = max(items.values())

    x_values = []
    y_values = []
    for pallid in range(int(math.ceil(max_pallid)) + 1):
        # pallid
        x_values.append(pallid)
        # sooritajate arv
        y_values.append(items.get(pallid) or 0)
    
    # Tulpdiagrammid
    fig = go.Figure(go.Bar(x=x_values, y=y_values))
    fig.update_layout(font_family="Times New Roman",
                          font_color="black",
                          xaxis=dict(range=[0, max_pallid+1],
                                     title='Punktid'),
                          yaxis=dict(range=[0, y_max],
                                     title='Sagedus'),
                          margin=dict(l=5, r=5, t=5*mm, b=5*mm),
                          showlegend=False,
                          )
    fdata = fig.to_image(format='svg',
                         height=140*mm,
                         width=260*mm)
    img = svg2rlg(io.BytesIO(fdata))
    return img

def gen_dgm_sugu(data_m, data_n, x_tickvals, x_ticktext):
    "Tulemused sooti"
    fig = go.Figure()

    # Poisid
    fig.add_trace(go.Bar(x=[r[0] for r in data_m],
                         y=[r[1] for r in data_m],
                         name="Poisid"))
    # Tüdrukud
    fig.add_trace(go.Bar(x=[r[0] for r in data_n],
                         y=[r[1] for r in data_n],
                         name="Tüdrukud"))

    fig.update_layout(font_family="Times New Roman",
                      font_color="black",
                      xaxis=dict(tickvals=x_tickvals,
                                 ticktext=x_ticktext),
                      yaxis=dict(range=[0, 101],
                                 title="Protsent"),
                      margin=dict(l=5, r=5, t=5*mm, b=5*mm),
                      showlegend=True
                      )
    fdata = fig.to_image(format='svg',
                         height=140*mm,
                         width=260*mm)
    img = svg2rlg(io.BytesIO(fdata))
    return img

def gen_dgm_ylesanded(x_tickvals, x_ticktext, y_values):
    "Ülesannete tulpdiagramm"

    fig = go.Figure()
    fig.add_trace(go.Bar(x=x_tickvals, y=y_values))

    fig.update_layout(font_family="Times New Roman",
                      font_color="black",
                      xaxis=dict(tickvals=x_tickvals,
                                 ticktext=x_ticktext),
                      yaxis=dict(range=[0, 101],
                                 title="Protsent"),
                      margin=dict(l=5, r=5, t=5*mm, b=5*mm)
                      )
    fdata = fig.to_image(format='svg',
                         height=140*mm,
                         width=260*mm)
    img = svg2rlg(io.BytesIO(fdata))
    return img
