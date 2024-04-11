# -*- coding: utf-8 -*- 
"PDF lehekyljemallide dynaamiline importimine"

import os
import re
import logging

# mallide staatiline laadimine
from . import pages

log = logging.getLogger(__name__)
pages_templates = {}

def load_pages(pages_mod, pages_templates, refresh=False):
    "Imporditakse kõik moodulid kataloogist pages"
    if pages_templates and not refresh:
        return pages_templates
    
    pages_templates = {}

    for template in pages_mod.__all__:
        name = template.__name__.split('.')[-1]
        m = re.match(r'^(.+)_([^_]+)$', name)
        if m:
            t_type, t_name = m.groups()
            if t_type not in pages_templates:
                pages_templates[t_type] = []
            pages_templates[t_type].append((t_name, template))        
        else:
            log.error('PDF malli nimi "%s" ei liigitu' % name)

    return pages_templates

def get_templates_opt_dict():
    global pages_templates
    pages_templates = load_pages(pages, pages_templates)
    di = {}
    for t_type in list(pages_templates.keys()):
        di[t_type] = get_templates_opt(t_type)
    return di

def get_templates_opt(t_type):
    global pages_templates
    pages_templates = load_pages(pages, pages_templates)
    options = []
    for (t_name, t_module) in pages_templates.get(t_type) or []:
        title = t_module.__doc__ or t_name
        options.append((t_name, title))
    return options

def get_template(t_type, t_name):
    global pages_templates
    pages_templates = load_pages(pages, pages_templates)
    t_templates = pages_templates.get(t_type)
    if t_templates:
        for rcd in t_templates:
            if rcd[0] == t_name:
                return rcd[1]

