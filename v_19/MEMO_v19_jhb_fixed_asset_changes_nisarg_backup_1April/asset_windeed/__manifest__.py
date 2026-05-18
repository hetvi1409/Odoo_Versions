{
    'name': 'Building Windeed Extension',
    'version': '19.0.1.0.0',
    'summary': 'Adds Windeed details to the Building model',
    'description': """
        This module extends the Building model by adding a new Windeed tab 
        containing Property Details, Ownership, Endorsements, and History of Documents sections.
    """,
    'category': 'Real Estate',
    'author': 'Nated Systems',
    'company': 'Nated Systems',
    'maintainer': 'Nated Systems',
    'website': 'https://natedsystems.co.za/',
    'depends': ['itsys_real_estate'],  # 'your_existing_module' is the module that contains the building model
    'data': [
        'views/building_views.xml',  # Path to the form view extension XML file
    ],
    'qweb': [],
    'images': [],
    'license': 'OEEL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
