# -*- coding: utf-8 -*-

from openerp import models, fields, tools, api, _
import time
import openerp.addons.decimal_precision as dp
from time import gmtime, strftime
from openerp.exceptions import Warning, ValidationError
from datetime import datetime
from openerp.tools.translate import _
# from openerp.exceptions import Warning as UserError


class CesagContractTeacher(models.Model):
    _name = 'cesag.contract.teacher'
    _description = 'Description'

    @api.multi
    def _get_datetime(self):
        date_now = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
        return date_now

    @api.model
    def create(self, vals):
        if vals:
            vals.update({
                'name': self.env['ir.sequence'].get('CONTRACT-')
            })
        return super(CesagContractTeacher, self).create(vals)

    @api.multi
    @api.onchange("consolidation_id")
    def onchange_teacher_by_consolidation(self):
        list = []
        res = {}
        for rec in self:
            if rec.consolidation_id:
                consolidation = self.env['cesag.consolidation']
                consolidation = consolidation.search([('id', '=', rec.consolidation_id.id)])
                if consolidation:
                    for c in consolidation:
                        for o in c.teacher_ids:
                            if o.state == 'done':
                                list.append({
                                    'teacher_id': o.teacher_id.id,
                                })
                        rec.contract_line_ids = list

    name = fields.Char(string=u"Reference", track_visibility='onchange', store=True, readonly=True, copy=True)
    year_id = fields.Many2one(comodel_name='sm.year', string=u"Année académique", required=True)
    date = fields.Date(string=u"Date", default=_get_datetime, readonly=True, track_visibility='onchange', copy=True)
    consolidation_id = fields.Many2one(comodel_name='cesag.consolidation', required=True, string=u"Reference consolidation")
    contract_line_ids = fields.One2many(comodel_name='contract.teacher.lines', inverse_name='contract_id')

class CesagContractLine(models.Model):
    _name = 'contract.teacher.lines'

    contract_id = fields.Many2one(comodel_name='cesag.contract.teacher', copy=False, ondelete="cascade")
    teacher_id = fields.Many2one(comodel_name='sm.faculty', string='Enseignant', required=True, copy=True)
    number_hours = fields.Float(string=u"Total heure alloué (heure)", store=True, readonly=True)
    # state = fields.Selection(STATES_TEACHER, string=u'Etat', track_visibility='onchange', copy=True)

