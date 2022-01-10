# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) Rachid IBIZZI (<https://ma.linkedin.com/in/rachidibizzi>).
#
##############################################################################

# 1 : imports of python lib


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
from datetime import date, datetime, timedelta



class Projecteherite(models.Model):

    _inherit = 'sm.alumni.projet'
    _description = u'project '
    
    finance_id=fields.One2many('sm.alumni.financement','project_id')
    descript=fields.Html('Description du projet')
   
    

class Cotiseherite(models.Model):

    _inherit = 'sm.alumni.cotisation'
    _description = u'Cotisation '
    
    excepfine=fields.Float(string=' Montant Exceptionnelle')
    year_id = fields.Many2one('sm.cotiseyear', 'Année Académique', states={'draft': [('readonly', False)]})
    amount = fields.Float(u'Montant', compute='amounte_comp')
    cotise_type=fields.Many2many('cotise.type','cotise_type_sm_alumni_cotisation_rel','cotise_type','cotise_id',string='Type de Cotisation')

    
    @api.multi
    @api.depends('year_id')
    def amounte_comp(self):
        if self.year_id:
            self.amount = self.year_id.amount_year
            
            
class financeherite(models.Model):

    _inherit = 'sm.alumni.financement'
    
    project_amount = fields.Float(u'Montant Projet', readonly=True,compute="amounte_comp")
    cotise_type=fields.Many2many('cotise.type','cotise_type_sm_alumni_cotisation_rel','cotise_type','cotise_id',string='Type de Financement')
    descript=fields.Html('Déscription du projet',compute="amounte_comp")
    descript_fine=fields.Html('Veuillez specifier vos type de financement')

    
    @api.multi
    @api.depends('project_id')
    def amounte_comp(self):
        if self.project_id:
            self.project_amount = self.project_id.amount
            self.descript = self.project_id.descript
            

class SmAlumniCotisationtype(models.Model):

    _name = 'cotise.type'
    _rec_name= 'cotise_id'
    
    cotise_id=fields.Char('Type de cotisation')


class SmAlumniCotisatyeartype(models.Model):

    _name = 'sm.cotiseyear'
    _rec_name='year'
    
    year=fields.Char('Anné Académique')
    amount_year=fields.Char('Cotisation Annuelle')

class SmAlumnicible(models.Model):

    _name = 'sm.cible'
    _rec_name= 'cible_id'
    
    cible_id=fields.Char('Cibles')

class SmAlumnicible(models.Model):

    _name = 'sm.oppotype'
    _rec_name= 'opportype_id'
    
    opportype_id=fields.Char('Cibles')
   


    
    
    
        

    
############################################################################################################

class Smpromotion(models.Model):

    _inherit = 'sm.promotion'
    _rec_name= 'program_id'
    
    
class Progherite(models.Model):

    _inherit = 'sm.program'
    _description = u'Programme '

    year_id = fields.Many2one('sm.year', string=u"Année", store=True)
    nomcourt = fields.Char(u'Nom Court')
    public = fields.Char(u'Public Cible')
    condition = fields.Text(u'''Condition d'entrée''')
    libelle = fields.Char(u'Libellé')
    
    semestre_id = fields.Many2many('sm.semester', 'sm_program_semestre_rel', 'program_id', 'semestre_id',string=u'Semestre')
    unit_id = fields.Many2many('sm.unit', 'sm_program_unit_rel', 'program_id', 'unit_id',string=u'UE')
    level_id = fields.Many2many('sm.level', 'sm_program_level_rel', 'program_id', 'user_id',string=u'Niveau')
    module_id = fields.Many2many('sm.module', 'sm_program_module_rel', 'program_id', 'module_id',string=u'Modules')


    @api.multi
    def action_ue_count(self):
        action = self.env.ref('school_mgmt.sm_unit_action')
        action_dict = action.read()[0]
        action_dict['name'] = "UE"
        action_dict['domain'] = [('program_id','=',self.id)]
        return action_dict
    
    @api.multi
    def action_semestre_count(self):
        action = self.env.ref('school_mgmt.sm_semester_action')
        action_dict = action.read()[0]
        action_dict['name'] = "Semestre"
        action_dict['domain'] = [('program_id','=',self.id)]
        return action_dict
    
    @api.multi
    def action_level_count(self):
        action = self.env.ref('school_mgmt.sm_level_action')
        action_dict = action.read()[0]
        action_dict['name'] = "Niveau"
        action_dict['domain'] = [('program_id','=',self.id)]
        return action_dict
    
    @api.multi
    def action_classe_count(self):
        action = self.env.ref('school_mgmt.sm_classroom_action')
        action_dict = action.read()[0]
        action_dict['name'] = "Classe"
        action_dict['domain'] = [('program_id','=',self.id)]
        return action_dict




# Level herite :::::::::::::::::::::::::::



class SmLevelherite(models.Model):

    _inherit = 'sm.level'
    _description = u'Niveau'


    # name = fields.Many2one('sm.level_standard',string=u'Nom', required=True)
    # program_id= fields.Many2one('sm.program',string=u'Programme')
    credit = fields.Integer(string=u'Crédit Total',compute='_compute_credit', store=True)
    cm = fields.Integer(string=u'CM',compute='_compute_cm', store=True)
    tdtp = fields.Integer(string=u'TD/TP',compute='_compute_tdtp', store=True)
    total = fields.Integer(string=u'Total(CM/(Td/Tp)',compute='_compute_ttl', store=True)
    tpe = fields.Integer(string=u'TPE',compute='_compute_tpe', store=True)
    semestre_id=fields.One2many('sm.semester','level_id','Enseignements',store=True)
    student_id=fields.One2many('sm.student',  'level_id', string=u"Classes",store=True)
    classe_id=fields.One2many('sm.classroom',  'level_id', string=u"Classes",store=True)
    classe_count = fields.Integer(compute='_classe_count', string='Classe', required=True)
    smester_count= fields.Integer(compute='_semester_count',string=u'semestre')
    student_count= fields.Integer(compute='_student_count',string=u'Etudiant')
    unit_id=fields.One2many('sm.unit','level_id','UE')
    color = fields.Integer('Color Index', default=0)
   


    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "Le Nom Niveau doit être unique"),
    ]

    


    @api.multi
    def _student_count(self):
        student_pool = self.env['sm.student']
        for obj in self:
            domain = [
                ('level_id','=',obj.id),
            ]
            student_count = student_pool.search_count(domain)
            obj.student_count = student_count
    

    @api.multi
    def action_student_count(self):
        action = self.env.ref('school_mgmt.sm_student_action')
        action_dict = action.read()[0]
        action_dict['name'] = "Étudiants"
        action_dict['domain'] = [('level_id','=',self.id)]
        return action_dict


    @api.multi
    def _classe_count(self):
        classe_pool = self.env['sm.classroom']
        for obj in self:
            domain = [
                ('level_id','=',obj.id),
            ]
            classe_count = classe_pool.search_count(domain)
            obj.classe_count = classe_count
    
    @api.multi
    def action_classe_count(self):
        action = self.env.ref('school_mgmt.sm_classroom_action')
        action_dict = action.read()[0]
        action_dict['name'] = "Classe"
        action_dict['domain'] = [('level_id','=',self.id)]
        return action_dict
    
    @api.multi
    def _semester_count(self):
        semester_pool = self.env['sm.semester']
        for obj in self:
            domain = [
                ('level_id','=',obj.id),
            ]
            smester_count = semester_pool.search_count(domain)
            obj.smester_count = smester_count
    
    @api.multi
    def action_smester_count(self):
        action = self.env.ref('school_mgmt.sm_semester_action')
        action_dict = action.read()[0]
        action_dict['name'] = "Semestre"
        action_dict['domain'] = [('level_id','=',self.id)]
        return action_dict



    
    

   
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


class Smlevelstandard(models.Model):

    _name = 'sm.level_standard'

    
    name=fields.Char('Niveau')






# ::Semestre herite :::::::::::://////////
class SmSmster(models.Model):

    _name = 'sm.smster'
    _description = u'Semestre'

    name=fields.Char('Semestre')

class SmSemesterherite(models.Model):

    _inherit = 'sm.semester'
    _description = u'Semestre'



    name = fields.Selection(selection_add=[('7', u'Semestre-7'),('8', u'Semestre-8'),('9', u'Semestre-9'),('10', u'Semestre-10'),('11', u'Semestre-11'),
                                            ('12', u'Semestre-12'),('13', u'Semestre-13'),('14', u'Semestre-14'),('15', u'Semestre-15'),('16', u'Semestre-16')],
                                      string='Nom', required=True,
                                      inivisible=False)
    # semestre_id = fields.Many2one('sm.smster', u'Semestre', required=True)
    code=fields.Char(string=u'code')
    credit = fields.Integer(string=u'Crédit Total',compute='_compute_credit', store=True)
    cm = fields.Integer(string=u'CM',compute='_compute_cm', store=True)
    tdtp = fields.Integer(string=u'TD/TP',compute='_compute_tdtp', store=True)
    total = fields.Integer(string=u'Total(CM/(Td/Tp)',compute='_compute_ttl', store=True)
    tpe = fields.Integer(string=u'TPE',compute='_compute_tpe', store=True)
    # credit = fields.Integer(string=u'Crédit Total', compute='_compute_credit', store=True)
    unit_ids = fields.Many2many('sm.unit', 'sm_semester_unit_rel', 'semester_id', 'unit_id', string=u"Unités")
    # program_year_id = fields.Many2one('sm.program.year', string=u"Année Programme")
    program_id = fields.Many2one('sm.program', string=u"Programme de Formation", store=True)
    level_id = fields.Many2one('sm.level', string=u"Niveau", store=True)
    year_id = fields.Many2one('sm.year', string=u"Année",  store=True)
    color = fields.Integer('Color Index', default=0)
    

    
   

    @api.depends('cm','unit_ids.cm')
    def _compute_cm(self):
        for obj in self:
            obj.cm = sum(obj.unit_ids.mapped('cm'))

    @api.depends('tdtp','unit_ids.tdtp')
    def _compute_tdtp(self):
        for obj in self:
            obj.tdtp = sum(obj.unit_ids.mapped('tdtp'))
    
    @api.depends('tpe','unit_ids.tpe')
    def _compute_tpe(self):
        for obj in self:
            obj.tpe = sum(obj.unit_ids.mapped('tpe'))


    @api.depends('cm','total','tdtp')
    def _compute_ttl(self):
        for obj in self:
            obj.total = obj.cm + obj.tdtp

    @api.multi
    def name_get(self):
        result = []
        for obj in self:
            result.append((obj.id, "%s: [%s]" % (  obj.name,obj.program_id.name)))
            # result.append((obj.id, "%s" % (dict(self.env['sm.semester']._columns['name'].selection)[obj.name])))
        return result

    
    @api.depends('credit','unit_ids.credit')
    def _compute_credit(self):
        for obj in self:
            obj.credit = sum(obj.unit_ids.mapped('credit'))
    
    # @api.one
    # @api.depends("program_year_id", "program_year_id.program_id", "program_year_id.level_id", "program_year_id.year_id")
    # def _compute_data(self):
    #     self.program_id = self.program_year_id.program_id.id
    #     self.level_id = self.program_year_id.level_id.id
    #     self.year_id = self.program_year_id.year_id.id


# Unit :::::::::::::::::::::::::::::::::::::::::


class SmUnitherite(models.Model):

    _inherit = 'sm.unit'
    _description = u'Unité'


    name = fields.Char(string=u'Nom UE', required=True)

    program_id_h = fields.Many2one('sm.program', string=u"Programme de Formation",   store=True)
    level_id_h = fields.Many2one('sm.level', string=u"Niveau",   store=True)
    
    color = fields.Integer('Color Index', default=0)
    code= fields.Char(string=u'Code', required=True)
    credit = fields.Integer(string=u'Crédit',compute='_compute_credmodule')
    cm = fields.Integer(string=u'CM',compute='_compute_cm', store=True)
    tdtp = fields.Integer(string=u'TD/TP',compute='_compute_tdtp', store=True)
    total = fields.Integer(string=u'Total(CM/(Td/Tp)',compute='_compute_ttl', store=True)
    tpe = fields.Integer(string=u'TPE',compute='_compute_tpe', store=True)
    

    module_ids = fields.Many2many('sm.module', 'sm_unit_module_rel', 'unit_id', 'module_id', string=u"Modules")
  



    @api.depends('cm','module_ids.cm')
    def _compute_cm(self):
        for obj in self:
            obj.cm = sum(obj.module_ids.mapped('cm'))

    @api.depends('tdtp','module_ids.tdtp')
    def _compute_tdtp(self):
        for obj in self:
            obj.tdtp = sum(obj.module_ids.mapped('tdtp'))
    
    @api.depends('tpe','module_ids.tpe')
    def _compute_tpe(self):
        for obj in self:
            obj.tpe = sum(obj.module_ids.mapped('tpe'))


    @api.depends('cm','total','tdtp')
    def _compute_ttl(self):
        for obj in self:
            obj.total = obj.cm + obj.tdtp
    
    @api.depends('credit','module_ids.modulecredi')
    def _compute_credmodule(self):
        for obj in self:
            obj.credit = sum(obj.module_ids.mapped('modulecredi'))
    
   

# Module :::::::::::::::::


class Smdomaine(models.Model):

    _name = 'sm.domaine'
    _description = u'Domaine'


    name = fields.Char(string=u'Nom Domaine', required=True)

    code=fields.Char('Code', required=True)

   


class SmModule(models.Model):

    _inherit= 'sm.module'
    _description = u'Module'
    _rec_name= "nom"


    nom = fields.Char(string=u'Nom', required=True)
    domaine=fields.Many2one('sm.domaine','domaine')
    code=fields.Char('Code ')
    cm = fields.Integer(string=u'CM', store=True)
    tdtp = fields.Integer(string=u'TP/TD', store=True)
    total = fields.Integer(string=u'totale(CM/(TP/TP)',compute='_compute_ttl', store=True)
    tpe = fields.Integer(string=u'TPE', store=True)
    tpe = fields.Integer(string=u'TPE', store=True)
    modulecredi = fields.Integer('Credit')
    color = fields.Integer('Color Index', default=0)
    sm_classroom_id=fields.Many2one('sm.classroom','domaine')
    
    

   
    @api.depends('cm','total','tdtp')
    def _compute_ttl(self):
        for obj in self:
            obj.total = obj.cm + obj.tdtp
    

 



# Enseignat////////////////////////////


############################################################################################################




class SmFaculty(models.Model):

    _inherit = 'sm.faculty'
    _description = u'Enseignement'
    
    # _inherits = {"res.partner": "partner_id"}

    # @api.onchange('firstname')
    # def _get_firstname(self):
    #     for rec in self:
    #         rec.name = rec.firstname

    @api.one
    @api.constrains('total_point')
    def check_total_point(self):
        for rec in self:
            search_element = self.env['quantum.horaire']
            # search_element = search_element.search([('quantum')])
            if search_element:
                if rec.total_point >= rec.search_element.quantum:
                    raise UserError("Le total d'heure ne peut pas dépassé " + rec.search_element.quantum)

    @api.multi
    @api.depends('contract_ids.hours')
    def total_point_all(self):
        for order in self:
            total_point = 0.0
            for line in order.contract_ids:
                total_point += line.hours
            order.update({'total_point': total_point})

    @api.multi
    def _get_datetime(self):
        date_now = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
        return date_now

    @api.onchange("diplome_id")
    def onchange_sigle(self):
        for rec in self:
            if rec.diplome_id:
                search_element = self.env['diplome.teacher']
                search_element = search_element.search([('id', '=', rec.diplome_id.id)])
                if search_element.id:
                    rec.sigle_diplome = search_element.sigle

    date = fields.Date(string=u"Date", default=_get_datetime, readonly=True, track_visibility='onchange')
    # name = fields.Char('Nom', track_visibility='onchange', required=True)
    # lastname=fields.Char('Prenom', track_visibility='onchange', required=True)
    total_point = fields.Float(string=u"TOTAL HEURES DE COURS", compute='total_point_all')
    # name = fields.Char('Nom')

    # partner_id = fields.Many2one('res.partner', 'Partner', ondelete="cascade", track_visibility='onchange') #TODO
   
   
    # email = fields.Char(string=u"Email", track_visibility='onchange')
    # street = fields.Char(string=u"Adresse", track_visibility='onchange')
    # birth_date = fields.Date(string=u"Date de naissance", track_visibility='onchange')
   
    diplome_id = fields.Many2one(string=u"Diplome obtenue", comodel_name='diplome.teacher', required=True, track_visibility='onchange')
    sigle_diplome = fields.Char(string=u"Sigle diplome", required=True, track_visibility='onchange')
    # tel = fields.Char(string=u"Telephone")

    contract_ids = fields.One2many(comodel_name='teacher.contract', inverse_name='teacher_id')
    history_ids = fields.One2many(comodel_name='teacher.historisation', inverse_name='teacher_id')
    attachment_id = fields.Many2many('ir.attachment', 'doc_warning_rel', 'doc_id', 'attach_id4',
                                     string="Pieces jointes")
    # domain_id = fields.Many2many(comodel_name='sm.domaine', string=u"Domaine", required=True)


  
   

class TeacherHistorisation(models.Model):

    _name = 'teacher.historisation'

    teacher_id = fields.Many2one(comodel_name='sm.faculty')
    year_id = fields.Many2one(comodel_name='sm.year', string=u"Année")
    program_id = fields.Many2one(comodel_name='sm.program', string=u"Parcours")
    classroom_id = fields.Many2one(comodel_name='sm.classroom', string=u"Classes")
    level_id = fields.Many2one(comodel_name='sm.level', string=u"Niveau")
    hours = fields.Integer(string=u"Heures")
    module_id = fields.Many2one(string=u"Cours", comodel_name='sm.module')
    date_from = fields.Date(string=u"Date Début")
    date_to = fields.Date(string=u"Date Fin")


class TeacherContract(models.Model):

    _name = 'teacher.contract'

    teacher_id = fields.Many2one(comodel_name='sm.faculty')
    program_id = fields.Many2one(comodel_name='sm.program', string=u"Parcours")
    classroom_id = fields.Many2one(comodel_name='sm.classroom', string=u"Classes")
    hours = fields.Float(string=u"Heures")
    module_id = fields.Many2one(string=u"Cours", comodel_name='sm.module')
    date_from = fields.Date(string=u"Date Début")
    date_to = fields.Date(string=u"Date Fin")



# Inherite Classroum/////////////


class SMclass(models.Model):

    _name = 'sm.class'
    _description = u'Classe'

    _inherit = ['mail.thread']

    name = fields.Char(string=u'Nom', required=True)


class SMclassroom(models.Model):

    _inherit = 'sm.classroom'
    _description = u'Classe'


   
    module_ids = fields.One2many(comodel_name='classroom.module', inverse_name='sm_classroom_id', copy=True)
    # name = fields.Many2one('sm.class',string=u'Nom', required=True, copy=True)
    student_ids=fields.One2many('sm.student','classroom_id',"Etudents")
    plaquette_sms=fields.Many2one('sm.plaquette')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name,year_id)',
         "Le Nom Classe doit être unique"),
    ]

   
    # @api.multi
    # def name_get(self):
    #     result = []
    #     for obj in self:
    #         result.append((obj.id, "%s | %s" % (obj.name.name, obj.level_id.name and obj.program_id.name or '')))
    #     return result
    
    @api.multi
    def do_product_revision(self):
        record = self.copy()
        view_ref = self.env['ir.model.data'].get_object_reference('school_mgmt', 'sm_classroom_view_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dupliquer Classe',
            'res_model': 'sm.classroom',
            'res_id': record[0].id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }
    


   


    @api.multi
    @api.onchange("level_id")
    def onchange_module_by_level(self):
        list_partner = []
        res = {}
        for rec in self:
            if rec.level_id:
                level = self.env['sm.unit']
                level = level.search([('level_id', '=', rec.level_id.id)])
                for o in level:
                    for unit in o.module_ids:
                        list_partner.append({
                            'module_id': unit.id,
                            'domain_id': unit.domaine.id,
                            'tpe': unit.cm,
                        })
        rec.module_ids = list_partner
    
   
    @api.one
    def copy(self, default=None):
        for rec in self:
            default = dict(default or {})
            self.ensure_one()
            default.update({
                'name': rec.name + " " + 'Duplicata',
                'year_id': rec.year_id.id,
                # 'mon_fin': rec.mon_fin,
                'class_capacity': rec.class_capacity,
                'class_type': rec.class_type,
                'program_id': rec.program_id.id,
                'level_id': rec.level_id.id,
            })
        return super(SMclassroom, self).copy(default)
    

    
    @api.multi
    def action_timetable_count(self):
        action = self.env.ref('school_mgmt.action_timetable_regular')
        action_dict = action.read()[0]
        action_dict['name'] = "Emploi du temps"
        action_dict['domain'] = [('standard_id','=',self.id)]
        return action_dict
    



class ClassroomModule(models.Model):

    _name = 'classroom.module'

    sm_classroom_id = fields.Many2one(comodel_name='sm.classroom', copy=True)
    module_id = fields.Many2one(comodel_name='sm.module', string='Module',  copy=True)
    domain_id = fields.Many2one(comodel_name='sm.domaine', string='Domaine',   store=True, copy=True)
    tpe = fields.Integer(string=u"Quantum horaire", readonly=True, store=True, copy=True)






