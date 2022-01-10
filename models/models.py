# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning as UserError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    teacher = fields.Boolean(string='Enseignant permanent')

    @api.multi
    def attr_create(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sm.faculty',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_name': self.name, 'default_email': self.work_email, 'default_street': self.address_home_id.street,
                        'default_bank_account_number': self.bank_account_id.acc_number, 'default_bank_account_id': self.bank_account_id.bank_name,
                        'default_origin_country_id': self.country_id.id, 'default_birth_date' : self.birthday, 'default_permanent' : self.teacher, 'default_faculty_quality' : '1'}
        }

class SmFaculty(models.Model):
    _inherit = 'sm.faculty'

    domain = fields.Many2many('sm.domaine'
                                  , string=u"Domaine de compétence")

    permanent = fields.Boolean(string='Professeur permanent', default=False, readonly=True, store=True)

    other_quality = fields.Boolean(string=u'Enseignant encadrant', default=False)

    @api.onchange("faculty_quality")
    def onchange_quality(self):
        for rec in self:
            if rec.faculty_quality == '1':
                rec.permanent = True
            else:
                rec.permanent = False


class SmClassroomCesag(models.Model):

    _inherit = 'sm.classroom'

    test = fields.Char("TEST")

    # @api.onchange("level_id")
    # def onchange_test(self):
    #     for rec in self:
    #         if rec.level_id:
    #             rec.test = "True"
#
    @api.multi
    @api.onchange("level_id")
    def onchange_module_by_level(self):
        list_partner = []
        res = {}
        for rec in self:
            if rec.level_id:
                level = self.env['sm.unit']
                level = level.search([('level_id', '=', rec.level_id)])
                if level:
                    for unit in level.module_ids:
                        if unit:
                            list_partner.append({
                               'module_id': unit.id,
                               'domain_id': unit.domaine.id,
                               'tpe': unit.tpe,
                                })
                    rec.module_ids = list_partner







    