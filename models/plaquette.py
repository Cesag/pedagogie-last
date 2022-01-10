# -*- coding: utf-8 -*-

from datetime import datetime
import base64
import re
import time
import itertools
from lxml import etree
# 2 :  imports of openerp
import openerp
from openerp import api, fields, models 
from openerp.tools.safe_eval import safe_eval as eval
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

############################################################################################################

class Smplaquette(models.Model):

    _name = 'sm.plaquette'
    # _description = u'plaquette'

    _inherit = ['mail.thread']
    
    year_id=fields.Many2one("sm.year" ,'Année academique')
    level_id = fields.Many2one('sm.level',string=u'Niveau', required=True)
    program_id= fields.Many2one('sm.program',string=u'Programme', required=True)
    credit = fields.Integer(string=u'Crédit Total',compute='_compute_credit', store=True)
    cm = fields.Integer(string=u'CM',compute='_compute_cm', store=True)
    tdtp = fields.Integer(string=u'TD/TP',compute='_compute_tdtp', store=True)
    total = fields.Integer(string=u'Total(CM/(Td/Tp)',compute='_compute_ttl', store=True)
    tpe = fields.Integer(string=u'TPE',compute='_compute_tpe', store=True)
    # Pog_id = fields.One2many('sm.plaquette_line','plaquette_id',string=u'Enseignements')
    # semestre_id = fields.Many2many('sm.semester','sm_plaquette_semestre_rel', 'semestre_id', 'plaquette_id',string=u'Semestre')
    color = fields.Integer('Color Index', default=0)
    state = fields.Selection([('draft', u'Draft'),('finish', u'Terminer'), ('dup', u'Dupliquer')], u'Statut')
    date_plaquette = fields.Date(u'Date ',default=datetime.now().strftime('%Y-%m-%d'), readonly=True)
    # unit_id = fields.Many2many('sm.unit','sm_plaquette_lev_rel','plaquette_id', string=u'UE')
    # module_id = fields.Many2many('sm.module','sm_plaquette_module_rel', 'module_id', 'plaquette_id',string=u'Modules')
    semestre_id = fields.One2many('sm.plaquette.smstre', 'plaquette_sms',string=u'Semestre')
    unit_id = fields.One2many('sm.palaquette.unit','plaquette_uni', string=u'UE')
    module_id = fields.One2many('sm.plaquette.module',  'plaquette_md',string=u'Modules')

    
    

    @api.multi
    def set_terminate(self):
        self.write({'state': 'finish'})
        return True

    @api.multi
    def set_dublicatat(self):
        self.write({'state': 'dup'})
        return True

    @api.depends('cm','semestre_id.cm')
    def _compute_cm(self):
        for obj in self:
            obj.cm = sum(obj.semestre_id.mapped('cm'))

    @api.depends('tdtp','semestre_id.tdtp')
    def _compute_tdtp(self):
        for obj in self:
            obj.tdtp = sum(obj.semestre_id.mapped('tdtp'))
    
    @api.depends('tpe','semestre_id.tpe')
    def _compute_tpe(self):
        for obj in self:
            obj.tpe = sum(obj.semestre_id.mapped('tpe'))


    @api.depends('cm','total','tdtp')
    def _compute_ttl(self):
        for obj in self:
            obj.total = obj.cm + obj.tdtp
   

    @api.depends('credit','semestre_id.credit')
    def _compute_credit(self):
        for obj in self:
            obj.credit = sum(obj.semestre_id.mapped('credit'))
    


    @api.multi
    @api.onchange('level_id')
    def onchange_sms_level(self):
        '''Method to get student roll no'''
        stud_list = []
        stud_obj = self.env['sm.semester']
        for rec in self:
            if rec.level_id:
                stud_list = [{ 'name': stu.name,
                               'credit': stu.credit,
                               'cm': stu.cm,
                               'tdtp': stu.tdtp,
                               'total': stu.total,
                               'tpe': stu.tpe}
                             for stu in stud_obj.search([('level_id', '=',
                                                          rec.level_id.id)
                                                        ])]
            rec.semestre_id = stud_list



    @api.multi
    @api.onchange('level_id')
    def onchange_uni_level(self):
        '''Method to get student roll no'''
        stud_list = []
        stud_obj = self.env['sm.unit']
        for rec in self:
            if rec.level_id:
                stud_list = [{ 'name': stu.name,
                               'code': stu.code,
                               'credit': stu.credit,
                               'cm': stu.cm,
                               'tdtp': stu.tdtp,
                               'total': stu.total,
                               'tpe': stu.tpe}
                             for stu in stud_obj.search([('level_id', '=',
                                                          rec.level_id.id)
                                                        ])]
            rec.unit_id = stud_list
    

    @api.multi
    @api.onchange("level_id")
    def onchange_mod_level(self):
        list_partner = []
        res = {}
        for rec in self:
            if rec.level_id:
                level = self.env['sm.unit']
                level = level.search([('level_id', '=', rec.level_id.id)])
                for o in level:
                    for unit in o.module_ids:
                        list_partner.append({
                            'name': unit.name,
                               'nom': unit.nom,
                               'cm': unit.cm,
                               'tdtp': unit.tdtp,
                               'total': unit.total,
                               'tpe': unit.tpe
                        })
        rec.module_id = list_partner

class Smplaquettesms(models.Model):

    _name = 'sm.plaquette.smstre'
    # _description = u'plaquette'

    _inherit = ['mail.thread']
    
    plaquette_sms=fields.Many2one('sm.plaquette','plaquette')
    smestre_ids=fields.Many2one('sm.semestre','nom')
    name=fields.Char(string=u'nom')
    credit = fields.Integer(string=u'Crédit Total')
    cm = fields.Integer(string=u'CM')
    tdtp = fields.Integer(string=u'TD/TP')
    total = fields.Integer(string=u'Total(CM/(Td/Tp)' )
    tpe = fields.Integer(string=u'TPE')


class Smplaquetteunit(models.Model):

    _name = 'sm.palaquette.unit'
    # _description = u'plaquette'

    _inherit = ['mail.thread']
    
    plaquette_uni=fields.Many2one('sm.plaquette','plaquette')
    name = fields.Char(string=u'Nom UE')
    code= fields.Char(string=u'Code')
    credit = fields.Integer(string=u'Crédit')
    cm = fields.Integer(string=u'CM')
    tdtp = fields.Integer(string=u'TD/TP')
    total = fields.Integer(string=u'Total(CM/(Td/Tp)')
    tpe = fields.Integer(string=u'TPE')

class Smplaquettemodule(models.Model):

    _name = 'sm.plaquette.module'
    # _description = u'plaquette'

    _inherit = ['mail.thread']
    
    plaquette_md=fields.Many2one('sm.plaquette','plaquette')
    nom = fields.Char(string=u'Nom')
    domaine=fields.Many2one('sm.domaine','domaine')
    name=fields.Char('Code ')
    cm = fields.Integer(string=u'CM')
    tdtp = fields.Integer(string=u'TP/TD')
    total = fields.Integer(string=u'totale(CM/(TP/TP)')
    tpe = fields.Integer(string=u'TPE')
