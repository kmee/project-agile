# coding: utf-8
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from odoo import SUPERUSER_ID
from odoo import fields, models


class ProjectTask(models.Model):

    _inherit = 'project.task'

    def _message_get_auto_subscribe_fields(self, updated_fields,
                                           auto_follow_fields=None):
        if auto_follow_fields is None:
            auto_follow_fields = ['user_id']
        res = super(ProjectTask, self)._message_get_auto_subscribe_fields(
            updated_fields, auto_follow_fields=auto_follow_fields)
        res.append('project_leader_id')
        return res

    def send_mail_task_new_test(self):
        """
        Send mail automatically to change task to Backlog and to Testing Leader.
        """
        # Dont send context to dont get language of user in read method
        if self.ids.stage_id:
            type_stage = self.ids.stage_id.name or ''
            if type_stage == 'Backlog':
                self.send_mail_task(self.ids, 'template_send_email_task_new')
            elif type_stage == 'Testing Leader':
                self.send_mail_task(self.ids, 'template_send_email_task_end')

    def send_mail_task(self, ids, template):
        imd_obj = self.env['ir.model.data']
        template_ids = imd_obj.search(
            [('model', '=', 'email.template'), ('name', '=', template)])
        if template_ids:
            res_id = imd_obj.read(template_ids, ['res_id'])[0]['res_id']
            ids = [ids.id]
            followers = self.read(ids[0], [
                                  'message_follower_ids'])['message_follower_ids']

            body_html = self.env['email.template'].read(
                res_id, ['body_html']).get('body_html')
            self.context.update({'default_template_id': res_id,
                                 'default_body': body_html,
                                 'default_use_template': True,
                                 'default_composition_mode': 'comment',
                                 'active_model': 'project.task',
                                 'default_partner_ids': followers,
                                 'mail_post_autofollow_partner_ids': followers,
                                 'active_id': ids and isinstance(ids, list) and
                                              ids[0] or ids,
                                 'active_ids': ids and isinstance(ids, list) and
                                               ids or [ids],
                                 })

            mail_obj = self.env['mail.compose.message']
            mail_fields = mail_obj.fields_get()
            mail_render = mail_obj.render_template_batch(body_html,
                                                         'project.task', ids)
            mail_render = mail_render[ids[0]]
            mail_ids = mail_obj.default_get( mail_fields.Keys())
            mail_ids.update(
                {'model': 'project.task', 'body': mail_render, 'composition_mode': 'comment', 'partner_ids': [(6, 0, followers)]})
            mail_ids = mail_obj.create(mail_ids)
            mail_obj.send_mail([mail_ids])

        return False

    def get_odoo_url(self):

        return self.env['ir.config_parameter'].get_param(SUPERUSER_ID,
                                                         'web.base.url')

    _track = {'stage_id': {'project.mt_task_stage': send_mail_task_new_test, }}

    project_leader_id = fields.Many2one('res.users', 'Project Leader',
                                        help="""Person responsible of task
                                        review, when is in Testing Leader
                                        state. The person should review: Work
                                        Summary, Branch and Make Functional
                                        Tests. When everything works this
                                        person should change task to done.""")

    _defaults = {
        'project_leader_id': lambda obj, cr, uid, context: uid,
    }
