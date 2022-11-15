# -*- coding: utf-8 -*-
{
    'name': "MCM_Academy_MOOCIT",

    'summary': " Ce module permet d'ajouter une interface qui comporte toutes "
               "les statistiques sur OpenEdx pour chaque client. "
               "Ce module nous permet aussi "
               "d'ajouter i-Ones automatiquement sur Moocit via un api oopenedx, "
               "de supprimer i-Ones automatiquement après le passage d'examen.",

    'description': """
        Open Academy module for managing trainings:
            - training courses
            - training sessions
            - attendees registration
    """,

    'author': "Khouloudachour",
    'website': "https://www.mcm-academy.fr/",

    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'mail',
                'board',
                'mcm_session',
                'calendly_api_integration'],

    'qweb': [
        'static/src/xml/btn.xml',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        "views/partner.xml",
        "views/calendly.xml",
        "views/event_calendly.xml",
        "views/en_attentee.xml",
        "views/gerer_user_ir_cron.xml",
        "views/statestique.xml",
        "views/hide.xml",
        "views/jotform.xml",
        "views/form_sub.xml",
        "views/session.xml",
        "views/coach.xml",
        "views/cma_resultat.xml",
        "views/rapport.xml",
        "views/actif_inactif.xml",
        "views/assets.xml",
        'data/mail_data.xml',
        'data/automation_action_add_evalbox.xml',
        'views/dashboard.xml',


    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True

}
