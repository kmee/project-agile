# coding: utf-8
import threading

from odoo import SUPERUSER_ID
from odoo.models.orm import except_orm
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestUserStory(TransactionCase):

    def setUp(self):
        super(TestUserStory, self).setUp()
        self.story = self.registry('user.story')
        self.criterial = self.registry('acceptability.criteria')
        self.project = self.registry('project.project')
        self.user = self.registry('res.users')
        self.data = self.registry('ir.model.data')
        self.message = self.registry('mail.message')
        self.context = {'tracking_disable': True}

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.models.orm')
    def test_create_method(self):
        cr, uid = self.cr, self.uid
        # Search groups that allow manage user story
        us_manager_group = self.data.get_object(
            cr, uid, 'user_story', 'group_user_story_manager')
        # Creating user to try the create method
        user_test_id = self.user.create({
            'name': 'User Test',
            'login': 'test_create_user'
        })
        # Creating project set it in the new user stories creted
        project_id = self.project.create({
            'name': 'Project Test',
            'use_tasks': True,
        })
        # Try that a user without user story group cannot create an user story
        self.assertRaises(except_orm, self.story.create, cr, user_test_id, {
            'name': 'User Story Test',
            'owner_id': user_test_id,
            'project_id': project_id,
            # Adding user story group to the user created
            # previously
            'accep_crit_ids': [
                (0, 0, {
                    'name': 'Criterial Test 1',
                    'scenario': 'Test 1',
                    'sequence_ac': 1}),
                (0, 0, {
                    'name': 'Criterial Test 2',
                    'scenario': 'Test 2',
                    'sequence_ac': 2}),
                (0, 0, {
                    'name': 'Criterial Test 3',
                    'scenario': 'Test 3',
                    'sequence_ac': 3}),
            ]})
        # Adding user story group to the user created previously
        self.user.write([user_test_id], {
            'groups_id': [(4, us_manager_group.id)]
        })
        # Try that a user with user story group can create a user story,  this
        # group must allow create user story without problems
        us_create = self.story.create({
            'name': 'User Story Test',
            'owner_id': user_test_id,
            'project_id': project_id,
            'accep_crit_ids': [
                (0, 0, {
                    'name': 'Criterial Test 1',
                    'scenario': 'Test 1',
                    'sequence_ac': 1}),
                (0, 0, {
                    'name': 'Criterial Test 2',
                    'scenario': 'Test 2',
                    'sequence_ac': 2}),
                (0, 0, {
                    'name': 'Criterial Test 3',
                    'scenario': 'Test 3',
                    'sequence_ac': 3}),
            ]
        }, self.context)
        self.assertTrue(
            us_create,
            "An user with user story group manager cannot create an"
            " user story")
        # Test sequence acceptability criteria
        # You create the context manually
        context_ac = self.context.copy()
        us_ac_ids = self.story.browse(us_create)
        ac_l_v = [[us_create, ac.id, False] for ac in us_ac_ids.accep_crit_ids]
        context_ac.update({'accep_crit_ids': ac_l_v})
        seq_ac = self.criterial._get_default_sequence(cr,
                                                      user_test_id,
                                                      context_ac)
        self.assertEqual(seq_ac, 4, 'Sequence should be equal 4')

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.models.orm')
    def test_write_method(self):
        cr, uid = self.cr, self.uid
        # Search groups that allow manage user story
        us_manager_group = self.data.get_object('user_story',
                                                'group_user_story_manager')
        # Creating user to try the create method
        user_test_id = self.user.create({
            'name': 'User Test',
            'login': 'test_create_user'
        })
        # Creating project set it in the new user stories creted
        project_id = self.project.create({
            'name': 'Project Test',
            'use_tasks': True,
        })
        # Creating an user story for try modify
        story_id = self.story.create({
            'name': 'User Story Test',
            'owner_id': user_test_id,
            'project_id': project_id,
            'accep_crit_ids': [
                (0, 0, {
                    'name': 'Criterial Test 1',
                    'scenario': 'Test 1',
                    'sequence_ac': 1}),
                (0, 0, {
                    'name': 'Criterial Test 2',
                    'scenario': 'Test 2',
                    'sequence_ac': 2}),
                (0, 0, {
                    'name': 'Criterial Test 3',
                    'scenario': 'Test 3',
                    'sequence_ac': 3}),
            ]})
        # Try that a user without user story group cannot write an user story
        self.assertRaises(except_orm, self.story.write, cr,
                          user_test_id, [story_id],
                          {
                              'name': 'User Story Test Changed',
                          })
        # Adding user story group to the user created previously
        self.user.write([user_test_id], {
            'groups_id': [(4, us_manager_group.id)]
        })
        # Try that a user with user story group can write a user story,  this
        # group must allow create user story without problems
        self.assertTrue(
            self.story.write([story_id], {
                'name': 'User Story Test Changed',
                }, self.context),
            "An user with user story group manager cannot write an user story")

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.models.orm')
    def test_unlink_method(self):
        cr, uid = self.cr, self.uid
        # Search groups that allow manage user story
        us_manager_group = self.data.get_object('user_story',
                                                'group_user_story_manager')
        # Creating user to try the create method
        user_test_id = self.user.create({
            'name': 'User Test',
            'login': 'test_create_user'
        })
        # Creating project set it in the new user stories creted
        project_id = self.project.create({
            'name': 'Project Test',
            'use_tasks': True,
        })
        # Creating an user story for try modify
        story_id = self.story.create({
            'name': 'User Story Test',
            'owner_id': user_test_id,
            'project_id': project_id,
            'accep_crit_ids': [
                (0, 0, {
                    'name': 'Criterial Test 1',
                    'scenario': 'Test 1',
                    'sequence_ac': 1}),
                (0, 0, {
                    'name': 'Criterial Test 2',
                    'scenario': 'Test 2',
                    'sequence_ac': 2}),
                (0, 0, {
                    'name': 'Criterial Test 3',
                    'scenario': 'Test 3',
                    'sequence_ac': 3}),
            ]})
        # Try that a user without user story group cannot remove an user story
        self.assertRaises(except_orm, self.story.unlink,
                          cr, user_test_id, [story_id])
        # Adding user story group to the user created previously
        self.user.write([user_test_id], {
            'groups_id': [(4, us_manager_group.id)]
        })
        # Try that a user with user story group can remove a user story,  this
        # group must allow create user story without problems
        self.assertTrue(self.story.unlink([story_id]),
                        "An user with user story group manager cannot remove "
                        "an user story")

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.models.orm')
    def test_copy_method(self):
        cr, uid = self.cr, self.uid
        # Search groups that allow manage user story
        us_manager_group = self.data.get_object('user_story',
                                                'group_user_story_manager')
        # Creating user to try the create method
        user_test_id = self.user.create({
            'name': 'User Test',
            'login': 'test_create_user'
        })
        # Creating project set it in the new user stories creted
        project_id = self.project.create({
            'name': 'Project Test',
            'use_tasks': True,
        })
        # Creating an user story for try modify
        story_id = self.story.create({
            'name': 'User Story Test',
            'owner_id': user_test_id,
            'project_id': project_id,
            'accep_crit_ids': [
                (0, 0, {
                    'name': 'Criterial Test 1',
                    'scenario': 'Test 1',
                    'sequence_ac': 1}),
                (0, 0, {
                    'name': 'Criterial Test 2',
                    'scenario': 'Test 2',
                    'sequence_ac': 2}),
                (0, 0, {
                    'name': 'Criterial Test 3',
                    'scenario': 'Test 3',
                    'sequence_ac': 3}),
            ]})
        # Try that a user without user story group cannot copy an user story
        self.assertRaises(except_orm, self.story.copy, cr,
                          user_test_id, story_id)
        # Adding user story group to the user created previously
        self.user.write([user_test_id], {
            'groups_id': [(4, us_manager_group.id)]
        })
        # Try that a user with user story group can copy a user story,  this
        # group must allow create user story without problems
        self.assertTrue(
            self.story.copy(story_id),
            "An user with user story group manager cannot remove an"
            " user story")

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.models.orm')
    def test_acceptability_criterial_buttons(self):
        cr, uid = self.cr, self.uid
        self.test_create_method()
        threading.currentThread().testing = True
        # Search the user and the user story to change the criterials
        user_id = self.user.search([('name', '=', 'User Test')])
        story_id = self.story.search(cr, uid,
                                     [('name', '=', 'User Story Test')])
        user_brw = user_id and self.user.browse(user_id[0])
        if not user_brw.email:
            user_brw.write({'email': 'admin@test.com'})
        story_brw = story_id and self.story.browse(story_id[0])

        # Test approve an acceptability criteria with a specific user and chack
        # that the generated message is send by the user who approve.
        approve_user_id = self.user.create({
            'name': 'Approver User', 'login': 'user_approver',
            'email': 'approver@test.com',
        })
        self.assertTrue(approve_user_id)
        user_brw = self.user.browse(approve_user_id)
        # Adding user story group to the user created previously
        us_manager_group = self.data.get_object(
            cr, uid, 'user_story', 'group_user_story_manager')
        self.user.write([approve_user_id], {
            'groups_id': [(4, us_manager_group.id)]})

        i = 0
        for criterial in user_brw and story_brw and story_brw.accep_crit_ids:
            if i == 0:
                mes = ('The acceptability criterion %{criteria}%'
                       ' has been accepted by %').format(
                           criteria=criterial.name)
                self.assertFalse(criterial.accepted)
                self.criterial.approve([criterial.id])
                self.assertTrue(criterial.accepted)
                m_id = self.message.search(cr, uid,
                                           [('res_id', '=', story_brw.id),
                                            ('body', 'ilike', mes)])
                self.assertTrue(m_id, "The message was not created")
                msg_data = self.message.read(m_id, [
                    'model', 'author_id', 'create_uid', 'write_uid',
                    'email_from', 'notified_partner_ids', 'partner_ids',
                ])[0]
                self.partner = self.registry('res.partner')
                author_id = msg_data.get('author_id')[0]
                approver_partner = self.user.browse(
                    cr, uid, approve_user_id).partner_id.id
                self.assertEqual(approver_partner, author_id)
                cri_brw = self.criterial.browse(criterial.id)
                self.assertTrue(cri_brw.accepted,
                                "The criterial was not accepted")

            elif i == 1:
                mes = 'Please Review%{0}'.format(criterial.name)
                self.criterial.ask_review([criterial.id])
                m_id = self.message.search(cr, uid,
                                           [('res_id', '=', story_brw.id),
                                            ('body', 'ilike', mes)])
                self.assertTrue(m_id, "The message was not created")
            i += 1

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.models.orm')
    def test_approve_button(self):
        cr, uid = self.cr, self.uid
        self.test_create_method()
        threading.currentThread().testing = True
        # Search the user and the user story to change the criterials
        user_id = self.user.search([('name', '=', 'User Test')])
        story_id = self.story.search(cr, uid,
                                     [('name', '=', 'User Story Test')])
        user_brw = user_id and self.user.browse(user_id[0])
        if not user_brw.email:
            user_brw.write({'email': 'admin@test.com'})
        self.story.do_approval(story_id)
