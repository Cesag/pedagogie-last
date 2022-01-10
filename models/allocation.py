# -*- coding: utf-8 -*-

from openerp import models, fields, tools, api, _
import time
import openerp.addons.decimal_precision as dp
from time import gmtime, strftime
from openerp.exceptions import Warning, ValidationError
from datetime import datetime
from openerp.tools.translate import _


STATES_REQ = [('draft','Brouillon'),('cancel','Annulée'),('progress','Directeur / Chef de parcours'),('done','Validée'),('reject','Rejetée')]

STATES_TEACHER = [('done','Validée'),('reject','Rejetée')]

STATES_ALLOCATION = [('draft','Brouillon'),('cancel','Annulée'),('progress','Chef de parcours'),('progress_formation','Directeur formation'),('done','Validée'),('reject','Rejetée')]

class CesagAllocationEnseignant(models.Model):
    _name = 'cesag.allocation.enseignant'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Allocation des enseignants'
    _rec_name='classroom_id'

    @api.model
    def create(self, vals):
        if vals:
            vals.update({
                'name': self.env['ir.sequence'].get('ALLOC-')
            })
        return super(CesagAllocationEnseignant, self).create(vals)

    @api.multi
    def _get_datetime(self):
        date_now = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
        return date_now

    @api.multi
    def action_button_confirm(self):
        for o in self:
            if not o.module_ids:
                raise UserError("Vous ne pouvez pas confimer une allocation sans module")
        self.state = 'progress'
        return True

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'
        return True

    @api.multi
    def action_button_valid_dir_chef_service(self):
        self.state = 'progress_formation'
        return True

    @api.multi
    def action_button_valid_dir_formation(self):
        self.state = 'done'
        self.date_recept = time.strftime('%Y-%m-%d')
        return True

    @api.multi
    def action_reject_two(self):
        return self.env['warning'].info(title='Motif de rejet', message="Donner un motif de rejet",
                                        request_id=self.ids[0])

    # @api.onchange('year_id')
    # def onchange_year_id(self):
    #     for rec in self:
    #         return {'domain': {'level_id': [('program_id', '=', rec.program_id.id)]}}



    @api.model
    def _get_current_user(self):
        return self.env['res.users'].browse(self.env.uid)

    @api.model
    def _get_dept_user(self):
        current_user = self.env['res.users'].browse(self.env.uid)
        current_emp = self.env['hr.employee'].search([('user_id', '=', current_user.id)])
        for emp in current_emp:
            if emp.id:
                return self.env['hr.department'].browse(emp.department_id.id)

    @api.model
    def _get_manager_dept(self):
        current_user = self.env['res.users'].browse(self.env.uid)
        obj_emp = self.env['hr.employee'].search([('user_id', '=', current_user.id)])
        for emp in obj_emp:
            if emp.id:
                return self.env['hr.employee'].browse(emp.parent_id.id)

    @api.model
    def _company_get(self):
        company_id = self.env['res.company']._company_default_get(self._name)
        return self.env['res.company'].browse(company_id)

    @api.multi
    def send_teacher_mail(self):
        user = self.env.user
        template = self.sudo().env.ref('school_mgmt.allocations_by_mails')
        ctx = self.env.context.copy()
        res = template.with_context(ctx).send_mail(self.id)
        return res

    @api.one
    @api.constrains('module_ids.teacher_id')
    def check_total_cours(self):
        for rec in self:
            for line in rec.module_ids.teacher_id.id:
                if line > 1:
                    raise UserError("Le total de cours par classe ne doit pas dépassé 3")

    @api.multi
    def action_create_teacher_history(self):
        for obj in self:
            line_ids = []
            for mod in obj.module_ids:
                if mod.state == 'done':
                    faculty = self.env['sm.faculty'].search([('id', '=', mod.teacher_id.id)])
                    # print faculty.name
                    for teacher in faculty:
                        teacher.write({'history_ids': [(0, 0, {'year_id': obj.year_id and obj.year_id.id or False,
                                                               'program_id': obj.program_id and obj.program_id.id or False,
                                                               'classroom_id': obj.classroom_id and obj.classroom_id.id or False,
                                                               'level_id': obj.level_id and obj.level_id.id or False,
                                                               'module_id': mod.module_id and mod.module_id.id or False,
                                                               'hours': mod.tpe and mod.tpe or False,
                                                               'date_from': mod.date_start and mod.date_start or False,
                                                               'date_to': mod.date_end and mod.date_end or False,
                                                               })]})
                        teacher.write({'contract_ids': [(0, 0, {'program_id': obj.program_id and obj.program_id.id or False,
                                                               'classroom_id': obj.classroom_id and obj.classroom_id.id or False,
                                                               # 'level_id': obj.level_id and obj.level_id.id or False,
                                                               'module_id': mod.module_id and mod.module_id.id or False,
                                                               'hours': mod.tpe and mod.tpe or False,
                                                               'date_from': mod.date_start and mod.date_start or False,
                                                               'date_to': mod.date_end and mod.date_end or False,
                                                               })]})
        return True

    # @api.multi
    # def send_teacher_mail(self):
    #     for rec in self:
    #         if rec.module_ids:
    #             for mod in rec.module_ids:
    #                 if mod:
    #                     template_id = self.env.ref('school_mgmt.allocations_by_mails').id
    #                     template = self.env['email.template'].browse(template_id)
    #                     template.send_mail(mod.id, force_send=True, raise_exception=False)
    #         else:
    #             raise userError(
    #                 "Aucune fiche de paie envoyée\nCe lot doit en avoir au minimum une")

    date = fields.Date(string=u"Date", default=_get_datetime, readonly=True, track_visibility='onchange')
    date_recept = fields.Date(string="Date Réception Demande",
                                      track_visibility='onchange')
    email = fields.Char(string=u"Email")
    email_to = fields.Char(string=u"Email a")
    name = fields.Char(string=u"Reference", track_visibility='onchange', store=True, readonly=True)
    request_user_id = fields.Many2one('res.users', string=u"Demandeur", default=_get_current_user, required=True)
    request_department_id = fields.Many2one('hr.department', string=u"Département", default=_get_dept_user,
                                            required=True)
    manager_dept = fields.Many2one('hr.employee', string=u"Responsable du département", default=_get_manager_dept,
                                   track_visibility='onchange', readonly=False)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=_company_get,
                                 track_visibility='onchange')
    classroom_id = fields.Many2one(string=u"Classe", comodel_name='sm.classroom', required=True)
    level_id = fields.Many2one(string=u"Niveau", comodel_name='sm.level', required=True)
    year_id = fields.Many2one(string=u"Année Académique", comodel_name='sm.year', required=True)
    program_id = fields.Many2one(comodel_name='sm.program', string=u"Programme", required=True)
    class_capacity = fields.Integer(string=u"Capacité", compute='classroom_information', readonly=True, store=True)
    module_ids = fields.One2many(comodel_name='classroom.allocation.module', inverse_name='classroom_allocation_id', copy=True)
    avenant_ids = fields.One2many(comodel_name='enseigant.avenant', inverse_name='enseignant_avenant_id', copy=True)
    state = fields.Selection(STATES_ALLOCATION, string=u'Statut allocation', required=True, readonly=True,
                             default='draft', track_visibility='onchange')
    color = fields.Integer('Color Index', default=0)
    

    @api.multi
    def action_button_confirm(self):
        self.state = 'progress'
        return True

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'
        return True

    @api.multi
    def action_button_valid_dir_chef_service(self):
        self.state = 'progress_formation'
        # self.date_recept_request = time.strftime('%Y-%m-%d')
        return True

    @api.multi
    def action_button_valid_dir_formation(self):
        self.state = 'done'
        return True


    @api.multi
    @api.onchange("classroom_id")
    def onchange_module_by_class(self):
        list = []
        for rec in self:
            if rec.classroom_id:
                classroom = self.env['sm.classroom']
                classroom = classroom.search([('id', '=', rec.classroom_id.id)])
                if classroom:
                    for c in classroom.module_ids:
                        if c:
                            list.append({
                               'module_id': c.module_id.id,
                               'domain_id': c.domain_id.id,
                               'tpe': c.tpe,
                                })
        rec.module_ids = list

    # @api.multi
    # @api.onchange("classroom_id")
    # def onchange_teacher_by_domain(self):
    #     list = []
    #     res = {}
    #     for rec in self:
    #         if rec.classroom_id:
    #             classroom = self.env['sm.classroom']
    #             classroom = classroom.search([('id', '=', rec.classroom_id.id)])
    #             if classroom:
    #                 for c in classroom.module_ids.domain_id:
    #                     teacher = self.env['sm.faculty']
    #                     teacher = teacher.search([('domain.id', '=', c.id)])
                    #     if c:
                    #         list.append({
                    #             'module_id': c.id,
                    #             'domain_id': c.domain_id.id,
                    #             'tpe': c.tpe,
                    #         })
                    # rec.module_ids = list

    @api.multi
    @api.onchange("classroom_id")
    def onchange_teacher(self):
        for rec in self:
            list_partner = []
            if rec.classroom_id:
                classroom = self.env['sm.classroom']
                classroom = classroom.search([('id', '=', rec.classroom_id.id)])
                if classroom:
                    for c in classroom.module_ids:
                        if c:
                            for obj_line_fiche in c:
                                list_partner.append(obj_line_fiche.domain_id.id)
                            res = {}
                            res['domain'] = {'teacher_id': [('id', 'in', list_partner)]}
                            return res


    @api.depends("classroom_id")
    def classroom_information(self):
        for rec in self:
            if rec.classroom_id:
                search_element = self.env['sm.classroom']
                search_element = search_element.search([('id', '=', rec.classroom_id.id)])
                if search_element.id:
                    rec.class_capacity = search_element.class_capacity
    
    @api.onchange('level_id')
    def onchange_classroom_id(self):
        for rec in self:
            return {'domain': {'module_ids.semestre_id': [('level_id', '=', rec.level_id.id)]}}
    
   


class ClassroomModule(models.Model):

    _name = 'classroom.allocation.module'
    _rec_name= 'module_id'

    classroom_allocation_id = fields.Many2one(comodel_name='cesag.allocation.enseignant', copy=True, ondelete="cascade")
    module_id = fields.Many2one(comodel_name='sm.module', string='Module', copy=True)
    tpe = fields.Integer(string=u"Quantum horaire", readonly=True, store=True, copy=True)
    domain_id = fields.Many2one(comodel_name='sm.domaine', string='Domaine', store=True, copy=True)
    teacher_id = fields.Many2one(comodel_name='sm.faculty', string='Professeur', copy=True)
    date_start = fields.Date(string=u'Date de début', copy=True)
    date_end = fields.Date(string=u'Date de fin', copy=True)
    year_id = fields.Char( 'Année Académique')
    classroom_id = fields.Char( 'Classe')
    state = fields.Selection(STATES_TEACHER, string=u'Etat',
                             default='done', track_visibility='onchange')
    semestre_id = fields.Many2one(comodel_name='sm.semester', string='Semestre', copy=True)
                             
    @api.onchange("year_id")
    def _compute_year(self):
        for obj in self:
           # career_university_names = ""
            if obj.classroom_allocation_id.year_id:
                year_id = obj.classroom_allocation_id.year_id.name
                obj.year_id = year_id
                
    @api.onchange("year_id")
    def _compute_class(self):
        for obj in self:
           # career_university_names = ""
            if obj.classroom_allocation_id.classroom_id:
                classroom_id = obj.classroom_allocation_id.classroom_id.name
                obj.classroom_id = classroom_id
    
   

    
    
            

class AvenantEnseigant(models.Model):

    _name = 'enseigant.avenant'

    enseignant_avenant_id = fields.Many2one(comodel_name='cesag.allocation.enseignant', copy=True, ondelete="cascade")
    # cout_total = fields.Float(string=u"Coût total de l'avenant", digits=(12, 0))
    date = fields.Date(string="Date de l'avenant")
    observation = fields.Char(string="Observation")
    motif = fields.Char(string="Motif de l'avenant")

class QuantumHoraire(models.Model):

    _name = 'quantum.horaire'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.multi
    def _get_datetime(self):
        date_now = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
        return date_now

    date = fields.Date(string=u"Date", default=_get_datetime, readonly=True, track_visibility='onchange')
    quantum = fields.Integer(string=u"Quantum horaire maximum", required=True)
    year_id = fields.Many2one(string=u"Année Académique", comodel_name='sm.year', required=True)

class VaccationAsk(models.Model):

    _name = 'vaccation.ask'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.model
    def create(self, vals):
        if vals:
            vals.update({
                'name': self.env['ir.sequence'].get('VACC-')
            })
        return super(VaccationAsk, self).create(vals)

    @api.multi
    def _get_datetime(self):
        date_now = datetime.strftime(datetime.today(), "%Y-%m-%d %H:%M:%S")
        return date_now

    @api.multi
    def action_button_confirm(self):
        self.state = 'progress'
        return True

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'
        return True

    @api.multi
    def action_button_valid_dir_chef_service(self):
        self.state = 'done'
        self.date_recept_request = time.strftime('%Y-%m-%d')
        return True

    @api.multi
    def action_reject_two(self):
        return self.env['warning'].info(title='Motif de rejet', message="Donner un motif de rejet",
                                        request_id=self.ids[0])

    @api.one
    def attr_create(self):
        """
        Method to open create customer invoice form
        """
        view_ref = self.env['ir.model.data'].get_object_reference('school_mgmt', 'sm_faculty_view_form')
        view_id = view_ref[1] if view_ref else False
        project_obj = self.env['sm.faculty']
        vals_project = {}
        vals_project['name'] = self.firstname
        vals_project['lastname'] = self.lastname
        vals_project['faculty_grade_id'] = self.faculty_grade_id.id
        vals_project['faculty_type'] = self.faculty_type
        vals_project['faculty_quality'] = '2'
        vals_project['diplome_id'] = self.diplome_id.id
        vals_project['sigle_diplome'] = self.sigle_diplome
        # raise UserError(vals_project)
        project_id = project_obj.create(vals_project)
        res = {
            'type': 'ir.actions.act_window',
            'name': ('Création du vaccataire'),
            'res_model': 'sm.faculty',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current'
        }
        self.test_click = True
        return res

    test_click = fields.Boolean(string='test click', track_visibility='always', default=False)
    request_id = fields.Many2one('vaccation.ask', string=u"Référence de la demande", 
                                 ondelete='cascade', select=True, readonly=True)
    # year_id = fields.Many2one(string=u"Année Académique", comodel_name='sm.year', required=True)
    date = fields.Date(string=u"Date", default=_get_datetime, readonly=True, track_visibility='onchange')
    name = fields.Char(string=u"Reference", track_visibility='onchange', store=True, readonly=True)
    firstname = fields.Char(string=u"Nom", required=True)
    lastname = fields.Char(string=u"Prénom", required=True)
    # birthday = fields.Date(string=u"Date de naissance")
    email = fields.Char(string=u"Email", track_visibility='onchange')
    street = fields.Char(string=u"Adresse", track_visibility='onchange')
    birth_date = fields.Date(string=u"Date de naissance", track_visibility='onchange')
    origin_country_id = fields.Many2one('res.country', 'Provenance', track_visibility='onchange')
    faculty_grade_id = fields.Many2one('sm.faculty.grade', 'Grade', track_visibility='onchange', required=True)
    diplome_id = fields.Many2one(string=u"Diplome obtenue", comodel_name='diplome.teacher', required=True, track_visibility='onchange')
    sigle_diplome = fields.Char(string=u"Sigle diplome", required=True, track_visibility='onchange')
    tel = fields.Char(string=u"Telephone")
    date_recept_request = fields.Date(string="Date Réception Demande",
                                      track_visibility='onchange')
    rate = fields.Float(string=u"Taux horaire", compute="onchange_grade", readonly=True, store=True)
    faculty_type = fields.Selection([
        ('1', u'Madame'),
        ('2', u'Monsieur'),
        ('3', u'Professeur'),
        ('4', u'Docteur'),
    ], string=u'Titre', track_visibility='onchange', required=True)

    civility = fields.Selection([
        ('1', u'Madame'),
        ('2', u'Monsieur'),
    ], string=u'Civilité', track_visibility='onchange', required=True)


    state = fields.Selection(STATES_REQ, string=u'Statut demande vaccation', required=True, readonly=True,
                             default='draft', track_visibility='onchange')


    @api.onchange("diplome_id")
    def onchange_sigle(self):
        for rec in self:
            if rec.diplome_id:
                search_element = self.env['diplome.teacher']
                search_element = search_element.search([('id', '=', rec.diplome_id.id)])
                if search_element.id:
                    rec.sigle_diplome = search_element.sigle

    @api.depends("faculty_grade_id")
    def onchange_grade(self):
        for rec in self:
            if rec.faculty_grade_id:
                search_element = self.env['sm.faculty.grade']
                search_element = search_element.search([('id', '=', rec.faculty_grade_id.id)])
                if search_element.id:
                    rec.rate = search_element.rate

class DiplomeTeacher(models.Model):
    _name = 'diplome.teacher'

    name = fields.Char(string=u"Intitulé", required=True)
    sigle = fields.Char(string=u"Sigle", required=True)