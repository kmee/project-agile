# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'User Story Kanban',
    'summary': """
        User Story Kanban""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'www.kmee.com.br',
    'depends': [
	    'user_story_scrum',
    ],
    'data': [
        'views/user_story_priority.xml',
        'views/user_story.xml',
        'views/user_story_type_view.xml',
        'data/user_story_type_data.xml',
    ],
    'demo': [
    ],
}
