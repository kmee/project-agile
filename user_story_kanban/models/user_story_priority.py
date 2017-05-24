# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class UserStoryPriority(models.Model):

    _inherit = 'user.story.priority'

    _order = 'sequence'
    sequence = fields.Integer(
        string=u'Sequence',
        default=0)
