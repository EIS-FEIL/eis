# -*- coding: utf-8 -*-

from eis.lib.base import *
_ = i18n._

def get_charttypes(handler, request):
    return [
        {'name': 'AreaChart',
         'title': 'Area',
         'cols': [{'title': _("X-telg"), 'datatype': 'string', 'roles':['annotation','annotationText']},
                  {'title': _("Andmehulga {n} väärtused"), 'datatype': 'number', 'multi':True, 'roles':['annotation','annotationText','certainty','emphasis','interval','scope','style','tooltip']},
                  ],
         'package': 'corechart',
         },
        {'name': 'BarChart',
         'title': 'Bar',
         'cols': [{'title': _("Y-telg"), 'datatype': 'string'},
                  {'title': _("Andmehulga {n} väärtused"), 'datatype': 'number', 'multi':True, 'roles':['annotation','certainty','interval','scope','style','tooltip']},
                  ],
         'package': 'corechart',
         },
        {'name': 'BubbleChart',
         'title': 'Bubble',
         'cols': [{'title': _("ID"), 'datatype': 'string'},
                  {'title': _("X koordinaat"), 'datatype': 'number'},
                  {'title': _("Y koordinaat"), 'datatype': 'number'},
                  {'title': _("Sarja ID"), 'datatype': 'string', 'optional':True},
                  {'title': _("Suurus"), 'datatype': 'number', 'optional':True},
                  ],
         'package': 'corechart',
         },
        {'name': 'CandlestickChart',
         'title': 'Candlestick',
         'cols': [{'title': _("X-telg"), 'datatype': 'string'},
                  {'title': _("Min väärtus"), 'datatype': 'number'},
                  {'title': _("Algväärtus"), 'datatype': 'number'},
                  {'title': _("Lõppväärtus"), 'datatype': 'number'},
                  {'title': _("Max väärtus"), 'datatype': 'number'},
                  {'title': _("Laad"), 'datatype': 'rolesonly', 'roles':['tooltip', 'style']},
                  ],
         'package': 'corechart',
         },
        {'name': 'ColumnChart',
         'title': 'Column',
         'cols': [{'title': _("X-telg"), 'datatype': 'string'},
                  {'title': _("Andmehulga {n} väärtused"), 'datatype': 'number', 'multi':True, 'roles':['annotation','certainty','interval','scope','style','tooltip']},
                  ],
       'package': 'corechart',
         },
        {'name': 'ComboChart',
         'title': 'Combo',
         'cols': [{'title': _("X-telg"), 'datatype': 'string', 'roles':['annotation','annotationText']},
                  {'title': _("Andmehulga {n} väärtused"), 'datatype': 'number', 'multi':True, 'roles':['annotation','annotationText','certainty','emphasis','interval','scope','style','tooltip']},
                  ],
         'package': 'corechart',
         },
        {'name': 'GeoChart',
         'title': 'GeoChart',
         'cols': [{'title': _("Asukoht"), 'datatype': 'string'},
                  {'title': _("Värv"), 'datatype': 'number', 'optional':True},
                  {'title': _("Suurus"), 'datatype': 'number', 'optional':True},
                  ],
         'package': 'geochart',
         },       
        {'name': 'Histogram',
         'title': _("Histogram (üks andmehulk)"),
         'cols': [{'title': _("Nimi"), 'datatype': 'string'},
                  {'title': _("Väärtus"), 'datatype': 'number'},
                  ],                    
         'package': 'corechart',
         },
        {'name': 'Histogram.N',
         'title': _("Histogram (mitu andmehulka)"),
         'cols': [{'title': _("Nimi {n}"), 'datatype': 'number', 'multi':True},
                  ],
         'package': 'corechart',
         },
        {'name': 'LineChart',
         'title': 'Line',
         'cols': [{'title': _("X-telg"), 'datatype': 'string', 'roles':['annotation','annotationText']},
                  {'title': _("Andmehulga {n} väärtused"), 'datatype': 'number', 'multi':True, 'roles':['annotation','annotationText','certainty','emphasis','interval','scope','style','tooltip']},
                  ],
         'package': 'corechart',
         },
        # {'name': 'Map.l',
        #  'title': _(u"Map (lat-long)"),
        #  'cols': [{'title': _(u"Latitude"), 'datatype': 'number'},
        #           {'title': _(u"Longitude"), 'datatype': 'number'},
        #           {'title': _(u"Location description"), 'datatype': 'string', 'optional':True},
        #           ],
        #  'package': 'map',
        #  },
        # {'name': 'Map.a',
        #  'title': _(u"Map (string address)"),
        #  'cols': [{'title': _(u"Aadress"), 'datatype': 'string'},
        #           {'title': _(u"Location description"), 'datatype': 'string', 'optional':True},
        #           ],
        #  'package': 'map',
        #  },
        {'name': 'PieChart',
         'title': 'Pie',
         'cols': [{'title': _("Sektori nimetus"), 'datatype': 'string'},
                  {'title': _("Sektori väärtused"), 'datatype': 'number', 'roles': ['tooltip']},
                  ],
         'package': 'corechart',
         },
        {'name': 'ScatterChart',
         'title': 'Scatter',
         'cols': [{'title': _("Punkti X väärtus"), 'datatype': 'number'},
                  {'title': _("Andmehulga {n} Y väärtused"), 'datatype': 'number', 'multi':True, 'roles':['certainty','emphasis','scope','tooltip']},
                ],
         'package': 'corechart',
         },
        {'name': 'SteppedAreaChart',
         'title': 'SteppedArea',
         'cols': [{'title': _("X-telg"), 'datatype': 'string'},
                  {'title': _("Andmehulga {n} väärtused"), 'datatype': 'number', 'multi':True, 'roles':['certainty','interval','scope','style','tooltip']},
                  ],
         'package': 'corechart',
         },
        ]
    
    