# -*- coding: utf-8 -*-
{
    'name': "warcraft",

    'summary': """
        Warcraft Orcs ans Humans""",

    'description': """
        This is a simple warcraft Orcs ans Humans based on the warcraft universe. 
    """,

    'author': "Carles Lagardera",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # añadir un fichero de vista personalizada para cada modelo. Ejemplo: views/hero.xml, views/player.xml
        'views/hero.xml',
        'views/player.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/battle.xml',
        'views/townhall.xml',
        'views/building.xml',
        'demo/buildings.xml',
        'crons/cron_warcraft.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
