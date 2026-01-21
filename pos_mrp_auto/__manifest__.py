{
    'name': 'POS Manufacturing Automation',
    'version': '1.0',
    'summary': 'Automatically create Manufacturing Orders from POS',
    'depends': ['base'],
    'category': 'Manufacturing',
    'author': 'Shatah',
    'depends': [
        'point_of_sale',
        'mrp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,

}
