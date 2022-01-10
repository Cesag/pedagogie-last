# -*- coding: utf-8 -*-

from openerp import models, fields, tools, api, _
import time
import openerp.addons.decimal_precision as dp
from time import gmtime, strftime
from openerp.exceptions import Warning, ValidationError
from datetime import datetime
from openerp.tools.translate import _
# from openerp.exceptions import Warning, UserError

STATES_CONSOLIDATION = [('draft','Brouillon'),('done','Validée'),('cancel','Annulée')]
STATES_TEACHER = [('done','Validée'),('reject','Rejetée')]


class CesagConsolidation(models.Model):
    _name = 'cesag.consolidation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Consolidation'

    @api.model
    def create(self, vals):
        if vals:
            vals.update({
                'name': self.env['ir.sequence'].get('CONS-')
            })
        return super(CesagConsolidation, self).create(vals)

    @api.multi
    def _get_datetime(self):
        date_now = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
        return date_now

    @api.multi
    @api.onchange("year_id")
    def onchange_verify_year_conslidation(self):
        list = []
        res = {}
        for rec in self:
            if rec.year_id:
                selects = self.env['cesag.consolidation'].search([('year_id.id', '=', rec.year_id.id)])
                for y in selects:
                    if y:
                        raise ValidationError("Vous ne pouvez pas faire deux consolidations pour la même année académique")


    @api.multi
    @api.onchange("year_id")
    def onchange_teacher_by_allocation(self):
        list = []
        res = {}
        for rec in self:
            if rec.year_id:
                year = self.env['cesag.allocation.enseignant']
                year = year.search([('year_id.id', '=', rec.year_id.id)])
                if year:
                    for c in year:
                        for o in c.module_ids:
                            if o.state == 'done':
                                list.append({
                                    'teacher_id': o.teacher_id.id,
                                    'tpe': o.tpe,
                                    'domain_id': o.domain_id.id,
                                    'module_id': o.module_id.id,
                                    'date_start': o.date_start,
                                    'date_end': o.date_end,
                                    'number_hours': o.teacher_id.total_point,
                                    'state': o.state,
                                })
                        rec.teacher_ids = list

    @api.multi
    def do_product_revision(self):
        record = self.copy()
        view_ref = self.env['ir.model.data'].get_object_reference('school_mgmt', 'cesag_consolidation_form_view')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': "Dupliquer la consolidation",
            'res_model': 'cesag.consolidation',
            'res_id': record[0].id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    @api.one
    def copy(self, default=None):
        for rec in self:
            default = dict(default or {})
            self.ensure_one()
            default.update({
                'date_cons': rec.date_cons,
            })
        return super(CesagConsolidation, self).copy(default)


    # @api.multi
    # def action_button_confirm(self):
    #     for o in self:
    #         if not o.teacher_ids:
    #             raise UserError("Vous ne pouvez pas confimer une consolidation sans enseignants")
    #     self.state = 'done'
    #     return True

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'
        return True

    @api.multi
    def action_button_done(self):
        for o in self:
            if not o.teacher_ids:
                raise UserError("Vous ne pouvez pas confimer une consolidation sans enseignants")
        self.state = 'done'
        self.date_cons = time.strftime('%Y-%m-%d')
        return True

    name = fields.Char(string=u"Reference", track_visibility='onchange', store=True, readonly=True, copy=True)
    date = fields.Date(string=u"Date", default=_get_datetime, readonly=True, track_visibility='onchange', copy=True)
    date_cons = fields.Date(string=u"Date de consolidation", readonly=True, track_visibility='onchange', copy=True)
    year_id = fields.Many2one(string=u"Année Académique", comodel_name='sm.year', required=True, copy=True)
    teacher_ids = fields.One2many(comodel_name='consolidation.teacher.lines', inverse_name='consolidation_id', copy=True)
    state = fields.Selection(STATES_CONSOLIDATION, required=True, readonly=True,
                             default='draft', track_visibility='onchange')

class CesagConsolidationLine(models.Model):
    _name = 'consolidation.teacher.lines'

    consolidation_id = fields.Many2one(comodel_name='cesag.consolidation', copy=False, ondelete="cascade")
    module_id = fields.Many2one(comodel_name='sm.module', string='Module', required=True, copy=True)
    tpe = fields.Integer(string=u"Quantum horaire", required=True, readonly=True, store=True, copy=True)
    domain_id = fields.Many2one(comodel_name='sm.domaine', string='Domaine', required=True, readonly=True, store=True,
                                copy=True)
    teacher_id = fields.Many2one(comodel_name='sm.faculty', string='Enseignant', required=True, copy=True)
    date_start = fields.Date(string=u'Date de début', copy=True)
    date_end = fields.Date(string=u'Date de fin', copy=True)
    number_hours = fields.Float(string=u"Total heure alloué (heure)", store=True, readonly=True)
    state = fields.Selection(STATES_TEACHER, string=u'Etat', track_visibility='onchange', copy=True)

