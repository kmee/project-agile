# -*- coding: utf-8 -*-
# Copyright 2016 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'User Story Timesheet Task',
    'summary': """
        Fix user_story link when timesheet_task is instaled""",
    'version': '8.0.0.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'www.kmee.com.br',
    'depends': [
        'user_story',
        'timesheet_task',
    ],
    'data': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': True,
}
