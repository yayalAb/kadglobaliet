{
    'name': 'Delivery Port',
    'summary': 'Manage the list of delivery ports used for export/import shipments',
    'description': 'A module to maintain a master list of delivery ports (name, code, country) configurable from Sales.',
    'author': 'Niyat Consultancy.',
    'category': 'Sales',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/delivery_port_data.xml',
        'views/delivery_port_views.xml',
    ],
    'installable': True,
    'application': False,
}
