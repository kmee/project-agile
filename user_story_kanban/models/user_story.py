# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, fields, models, _


class UserStory(models.Model):

    _inherit = 'user.story'
    _order = "priority desc, sequence, date, name, id"
   
    sequence = fields.Integer('Sequence', select=True, help="Gives the sequence order when displaying a list of tasks.")
    
    #stage_id = fields.Many2one('project.task.type', string='Stage', track_visibility='onchange', index=True,
    #    default=_get_default_stage_id, group_expand='_read_group_stage_ids',
    #    domain="[('project_ids', '=', project_id)]", copy=False)
    color = fields.Integer(string='Color Index')
    priority = fields.Integer(
        string=u'Sequence', related='priority_level.sequence', store=True)   
 
    state = fields.Selection(selection_add=[
        ('20af',u'Análise Funcional'),
        ('21at',u'Análise Técnica'),
        ('22backlog',u'Backlog'),
        ('23sprint',u'Sprint Backlog'),
    ])    

    @api.model
    def _avaliable_transition(self, old_state, new_state):
        return True
        allowed = [
            ('draft', 'open'),
            ('open', 'paid'),
            ('open', 'cancel'),
        ]
        return (old_state, new_state) in allowed

    @api.multi
    def change_state(self, new_state):
        for record in self:
            if record._avaliable_transition(record.state, new_state):
                record.state = new_state
            else:
                raise UserError(_("This state transition is not allowed"))

    @api.multi
    def do_af(self):
        for record in self:
            record.change_state('20af')

    @api.multi
    def do_at(self):
        for record in self:
            record.change_state('21at')

    @api.multi
    def do_backlog(self):
        for record in self:
            record.change_state('22backlog')

    @api.multi
    def do_sprint(self):
        for record in self:
            record.change_state('23sprint')

