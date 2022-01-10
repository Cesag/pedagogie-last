# -*- encoding: utf-8 -*-


# from typing_extensions import Required
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import time
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
from calendar import monthrange
from datetime import datetime






STATES_REQ = [('draft','Brouillon'),('valider','Valider Notes'),('cancel','Rectifier'),('exam','Note Examan'),('done','Valider examan'),('cancelexam','Rectifier'),('cloturer','Cloturer')]


class Notecontrole(models.Model):
   

    _description = 'Note de controle'
    _name = 'note.controle'
    _rec_name = 'module_id'
    

    @api.multi
    @api.onchange('classroom_id')
    def onchange_class_info(self):
        '''Method to get student roll no'''
        stud_list = []
        stud_obj = self.env['sm.student']
        for rec in self:
            if rec.classroom_id:
                stud_list = [{ 'name': stu.firstname,
                               'prenom': stu.lastname,
                               'pcent': 0.4,}
                             for stu in stud_obj.search([('classroom_id', '=',
                                                          rec.classroom_id.classroom_id.id)
                                                        ])]
            rec.student_ids = stud_list
    

    
    @api.model
    def check_user(self):
        '''Method to get default value of logged in Student'''
        return self.env['res.partner'].search([(' partner_user_id', '=',
                                                    self._uid)]).id

    date = fields.Date("Date", help="Current Date",
                       default=lambda *a: time.strftime('%Y-%m-%d'))
    
    date_control = fields.Date("Date du controlle",required=True
                       )
  
    classroom_id = fields.Many2one('cesag.allocation.enseignant', 'Classe',
                                  )
    student_ids = fields.One2many('note.controle.line', 'classroom_id',
                                  'Students'
                                 )

    module_id=fields.Many2one('classroom.allocation.module','Module')
    
    program_id = fields.Many2one('sm.program', string=u"Programme de Formation", required=True)

    level_id = fields.Many2one('sm.level', string=u"Niveau")

    year_id = fields.Many2one('sm.year', 'Année academique', 
                              help="Anné academique")

    semestre_id= fields.Many2one('sm.semester', 'Semestre', 
                              )

    teacher_id = fields.Many2one('sm.faculty', 'Professeur')

    color = fields.Integer('Color Index', default=0)
    
    
    @api.onchange('classroom_id')
    def onchange_program_id(self):
        for rec in self:
            return {'domain': {'module_id': [('classroom_allocation_id.classroom_id.id', '=', rec.classroom_id.classroom_id.id)]}}
    
    
    @api.onchange("module_id")
    def module_inf(self):
        for rec in self:
            if rec.module_id:
                search_element = self.env['classroom.allocation.module']
                search_element = search_element.search([('id', '=', rec.module_id.id)])
                if search_element.id:
                    rec.teacher_id = search_element.teacher_id.id
    
    
    

    # state = fields.Selection(STATES_REQ, string=u'Statut demande vaccation', required=True, readonly=True,
    #                          default='draft', track_visibility='onchange')


   
 
   

class Notecontroleline(models.Model):


    _name = 'note.controle.line'
   
    prenom = fields.Char('Prenom.')
    name = fields.Char('Nom.')
    classroom_id = fields.Many2one('note.controle', 'Classe')
    note1 = fields.Float(string='Note 1')
    note2 = fields.Float(string='Note 2')
    moyenne = fields.Float(string='Moyenne Controle',compute='com_moy')
    pcent=fields.Float('Pourcentage')
    notecontrole = fields.Float('Note finale Controle',compute='com_final')
    
    @api.depends('note1','note2')
    def com_moy(self):
        '''Method to count present students.'''
        for rec in self:
            rec.moyenne = (rec.note1 + rec.note2)/2

    @api.depends('moyenne','pcent')
    def com_final(self):
        '''Method to count present students.'''
        for rec in self:
            rec.notecontrole = rec.pcent*rec.moyenne
    
    
    @api.constrains('note1')
    def note1_contrains(self):
        for rec in self:
            if rec.note1 > 20 :
                raise ValidationError("La note doit être comprise entre 0 et 20")
    
    @api.constrains('note2')
    def note2_contrains(self):
        for rec in self:
            if rec.note2 > 20 :
                raise ValidationError("La note doit être comprise entre 0 et 20")






class Noteexam(models.Model):
   

    _description = 'Note de controle'
    _name = 'note.exam'


    @api.multi
    @api.onchange("module_id")
    def onchange_mod_level(self):
        list_partner = []
        res = {}
        for rec in self:
            if rec.module_id:
                module = self.env['note.controle']
                module = module.search([('id', '=', rec.module_id.id)])
                for o in module:
                    for note in o.student_ids:
                        list_partner.append({
                            'nom': note.name,
                               'prenom': note.prenom,
                               'notecontrole': note.notecontrole,
                               'pcent': 0.6,
                        })
        rec.student_ids = list_partner
    
    
    @api.onchange('classroom_id')
    def onchange_program_id(self):
        for rec in self:
            return {'domain': {'module_id': [('classroom_id.classroom_id', '=', rec.classroom_id.classroom_id.id)]}}
    
    
    
    @api.onchange("module_id")
    def classroom_information(self):
        for rec in self:
            if rec.module_id:
                search_element = self.env['classroom.allocation.module']
                search_element = search_element.search([('module_id.module_id.id', '=', rec.module_id.module_id.id)])
                if search_element.id:
                    rec.teacher_id = search_element.teacher_id.id

    
   


    @api.model
    def check_user(self):
        '''Method to get default value of logged in Student'''
        return self.env['res.partner'].search([(' partner_user_id', '=',
                                                    self._uid)]).id

    date = fields.Date("Date", help="Current Date",
                       default=lambda *a: time.strftime('%Y-%m-%d'))
    
    date_exam = fields.Date("Date de l'éxamen",required=True
                       )
  
    classroom_id = fields.Many2one('cesag.allocation.enseignant', 'Classe',
                                  )
    student_ids = fields.One2many('note.exam.line', 'classroom_id')
    

    module_id=fields.Many2one('note.controle','Module')
    
    program_id = fields.Many2one('sm.program', string=u"Programme de Formation", required=True)

    level_id = fields.Many2one('sm.level', string=u"Niveau")

    year_id = fields.Many2one('sm.year', 'Année academique', 
                              help="Anné academique")

    semestre_id= fields.Many2one('sm.semester', 'Semestre', 
                              )

    teacher_id = fields.Many2one('sm.faculty', 'Professeur')

    color = fields.Integer('Color Index', default=0)
    session = fields.Selection([('premier','Premiére session'),('deuxiéme','Deuxiéme Session')],'Session')
    
   
   
 
   

class Noteexamline(models.Model):


    _name = 'note.exam.line'
   
    prenom = fields.Char('Prenom.')
    nom = fields.Char('Nom.')
    name = fields.Char('Nom Prenom.')
    classroom_id = fields.Many2one('note.exam', 'Classe')
    pcent=fields.Float('Pourcentage')
    notecontrole = fields.Float('Note finale Controle')
    notexam=fields.Float('Note Examan')
    notefinal=fields.Float('Note Finale',compute='com_final')
    val_id=fields.Selection([('valide','validée'),('nonvalide','Non Valider'),('elimine','Eliminatoire')],'Apreciation',compute='com_moy')
    
    @api.one
    @api.depends("prenom", "nom")
    def _compute_name(self):
        self.name = "%s %s" %(self.nom.strip().upper(), self.prenom.strip().title())
         
    
   
    @api.depends('notefinal','val_id')
    def com_moy(self):
        for rec in self:
            if rec.notefinal > 0 and rec.notefinal < 7 :
                rec.val_id= 'elimine'
            if rec.notefinal > 6 and rec.notefinal < 10:
                rec.val_id= 'nonvalide'
            if rec.notefinal > 9 and rec.notefinal < 21:
                rec.val_id= 'valide'

    @api.constrains('notexam')
    def exam_contrains(self):
        for rec in self:
            if rec.notexam > 20 :
                raise ValidationError("La note doit être comprise entre 0 et 20")

    
    
    @api.depends('notexam','pcent','notefinal','notecontrole')
    def com_final(self):
        for rec in self:
            rec.notefinal = rec.notecontrole + (rec.pcent*rec.notexam)
    
    



class Deliberationfinal(models.Model):
   

    _description = 'Deliberation finale'
    _name = 'delibration.finale'


    
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
                            'nom': unit.nom,
                            'credit': unit.credit,
                            
                        })
        rec.student_ids = list_partner
    
   
   

    @api.model
    def check_user(self):
        '''Method to get default value of logged in Student'''
        return self.env['res.partner'].search([(' partner_user_id', '=',
                                                    self._uid)]).id

    date = fields.Date("Date", help="Current Date",
                       default=lambda *a: time.strftime('%Y-%m-%d'))
                       
  
    classroom_id = fields.Many2one('sm.classroom', 'Classe',
                                  )
    student_ids = fields.One2many('note.deliberation.line', 'classroom_id',
                                  'Students'
                                 )
    
    etudiant = fields.Many2one('sm.student','Etudiant')
    
    absence = fields.Float("Nombre d'abcence")
    
    program_id = fields.Many2one('sm.program', string=u"Programme de Formation", required=True)

    level_id = fields.Many2one('sm.level', string=u"Niveau")

    year_id = fields.Many2one('sm.year', 'Année academique', 
                              help="Anné academique")

    semestre_id= fields.Many2one('sm.semester', 'Semestre', 
                              )

    teacher_id = fields.Many2one('sm.faculty', 'Professeur')
    
    moyenne = fields.Float('Moyenne')
    
    total = fields.Float('Total')

    color = fields.Integer('Color Index', default=0)
    
    result=fields.Selection([('valide','validée'),('nonvalide','Non Valider')],'Resultat')
    session = fields.Selection([('premier','Premiére session'),('deuxiéme','Deuxiéme Session')],'Session')
    
    
    

class Notedeliberationline(models.Model):


    _name = 'note.deliberation.line'
   
   
    classroom_id = fields.Many2one('delibration.finale', 'Classe')
    
    notexam=fields.Float('Note Contrôle et Examan')
    notefinal=fields.Float('Note Finale')
    val_id=fields.Selection([('valide','validée'),('nonvalide','Non Valider'),('elimine','Note éliminatiore')],'Apreciation')
    nom=fields.Char('Module')
    credit=fields.Integer('Crédit')
    
   
