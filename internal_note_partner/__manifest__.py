{
    'name': 'Internal Note',
    'description': "Ajouter Liste des commentaires de type note internes Dans la vue de Tree de partner "
                   "Ajout de l'option show or hide pour tous les champs "
                   "afficher dans le tableau qui affiche tous les clients"
                   "[1] Add smart button in partner view to display list of comments based on active_id"
                   "[2] Display last comment added for a client in list tree of all clients"
                   "[3] Add optional hide or show for all fields in tree of res.partner",
    'author': "Mejri Takwa",
    'maintainer': 'DIGIMOOV',
    'category': 'Partner',
    'sequence': 15,
    'summary': '[1] Add smart button in partner view to display list of comments based on active_id,'
               '[2] Display last comment added for a client in list tree of all clients'
               '[3] Add optional hide or show for all fields in tree of res.partner',
    'depends': [
        'base',
        'mail',
        'contacts',
    ],
    'data': [
        'views/inherit_res_partner.xml',
    ],
    'qweb': [],
    'images': [],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
