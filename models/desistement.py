# -*- coding: utf-8 -*-

from openerp import models, fields, tools, api, _
import time
import openerp.addons.decimal_precision as dp
from time import gmtime, strftime
from openerp.exceptions import Warning, ValidationError
from datetime import datetime
from openerp.tools.translate import _
# from openerp.exceptions import Warning as UserError

STATES_TEACHER = [('done','Validée'),('reject','Rejetée')]
STATES_CONSOLIDATION = [('draft','Brouillon'),('done','Validée'),('cancel','Annulée')]

class CesagDesistement(models.Model):
    _name = 'cesag.desistement'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Desistement'

    @api.model
    def create(self, vals):
        if vals:
            vals.update({
                'name': self.env['ir.sequence'].get('DES-')
            })
        return super(CesagDesistement, self).create(vals)

    @api.multi
    def _get_datetime(self):
        date_now = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
        return date_now

    @api.multi
    @api.onchange("teacher_id")
    def onchange_teacher_by_allocation(self):
        list = []
        res = {}
        for rec in self:
            if rec.teacher_id:
                teacher = self.env['consolidation.teacher.lines']
                teacher = teacher.search([('teacher_id.id', '=', rec.teacher_id.id)])
                if teacher:
                    for c in teacher:
                        if c.state == 'done':
                            list.append({
                                'module_id': c.module_id.id,
                                'tpe': c.tpe,
                                'domain_id': c.domain_id.id,
                                'date_start': c.date_start,
                                'date_end': c.date_end,
                            })
                    rec.module_ids = list

    @api.depends("teacher_id")
    def teacher_information(self):
        for rec in self:
            if rec.teacher_id:
                search_element = self.env['sm.faculty']
                search_element = search_element.search([('id', '=', rec.teacher_id.id)])
                if search_element.id:
                    rec.number_hours = search_element.total_point
                    rec.faculty_quality = search_element.faculty_quality
                    rec.faculty_grade_id = search_element.faculty_grade_id.id
                    rec.rate = search_element.faculty_grade_id.rate
                    rec.diplome_id = search_element.diplome_id.id
                    rec.sigle_diplome = search_element.sigle_diplome
                    rec.faculty_type = search_element.faculty_type

    # @api.onchange('year_id')
    # def onchange_level_id(self):
    #     for rec in self:
    #         return {'domain': {'teacher_id': [('year_id', '=', rec.year_id.id)]}}

    @api.multi
    @api.onchange("year_id")
    def onchange_teacher_by_year_id(self):
        for rec in self:
            list_partner = []
            if rec.name:
                com_anuel = rec.env['cesag.consolidation']
                com_anuel = com_anuel.search([('year_id.id', '=', rec.year_id.id)])
                for obj_line_fiche in com_anuel:
                    list_partner.append(obj_line_fiche.teacher_ids.teacher_id.id)
                res = {}
                res['domain'] = {'teacher_id': [('id', 'in', list_partner)]}
                return res

    name = fields.Char(string=u"Reference", track_visibility='onchange', store=True, readonly=True)
    date = fields.Date(string=u"Date", default=_get_datetime, readonly=True, track_visibility='onchange')
    year_id = fields.Many2one(string=u"Année Académique", comodel_name='sm.year', required=True)
    teacher_id = fields.Many2one(comodel_name='sm.faculty', string=u"Enseignant", required=True)
    renoncement_date = fields.Date(string=u"Date de renoncement")
    new_teacher_id = fields.Many2one(comodel_name='sm.faculty', string=u"Professeur choisie")
    number_hours = fields.Float(string=u"Total heure alloué (heure)", store=True, readonly=True, compute='teacher_information')
    faculty_quality = fields.Selection([
        ('1', u'Permanent'),
        ('2', u'Vacataire'),
        ('3', u'Encadrant'),
    ], string=u'Qualité', track_visibility='onchange', required=True, compute='teacher_information')
    faculty_grade_id = fields.Many2one('sm.faculty.grade', 'Grade', track_visibility='onchange', required=True, compute='teacher_information')
    rate = fields.Float(string=u"Taux horaire", compute='teacher_information')
    diplome_id = fields.Many2one(string=u"Diplome obtenue", comodel_name='diplome.teacher', required=True,
                                 track_visibility='onchange', compute='teacher_information')
    sigle_diplome = fields.Char(string=u"Sigle diplome", required=True, track_visibility='onchange', compute='teacher_information')
    faculty_type = fields.Selection([
        ('1', u'Madame'),
        ('2', u'Monsieur'),
        ('3', u'Professeur'),
        ('4', u'Docteur'),
    ], string=u'Titre', track_visibility='onchange', required=True, compute='teacher_information')
    module_ids = fields.One2many(comodel_name='desistement.module.lines', inverse_name='desistement_id')
    module_id = fields.Many2one(comodel_name='sm.module', string='Module', required=True, copy=True)
    state = fields.Selection(STATES_CONSOLIDATION, required=True, readonly=True,
                             default='draft', track_visibility='onchange')


class CesagDesistementLine(models.Model):
    _name = 'desistement.module.lines'

    desistement_id = fields.Many2one(comodel_name='cesag.consolidation', ondelete="cascade")
    module_id = fields.Many2one(comodel_name='sm.module', string='Module', required=True, copy=True)
    tpe = fields.Integer(string=u"Quantum horaire", required=True, readonly=True, store=True, copy=True)
    domain_id = fields.Many2one(comodel_name='sm.domaine', string='Domaine', required=True, readonly=True, store=True,
                                copy=True)
    # teacher_id = fields.Many2one(comodel_name='sm.faculty', string='Enseignant', required=True, copy=True)
    date_start = fields.Date(string=u'Date de début', copy=True)
    date_end = fields.Date(string=u'Date de fin', copy=True)
    state = fields.Selection(STATES_TEACHER, string=u'Etat', track_visibility='onchange')




