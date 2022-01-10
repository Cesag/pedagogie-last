# -*- encoding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
import time
from calendar import monthrange
from datetime import datetime








class DailyAttendance(models.Model):
    '''Defining Daily Attendance Information.'''

    _description = 'Daily Attendance'
    _name = 'daily.attendance'
    

    @api.depends('student_ids')
    def _compute_total(self):
        '''Method to compute total student'''
        for rec in self:
            rec.total_student = len(rec.student_ids and
                                    rec.student_ids.ids or [])
    

    @api.depends('student_ids')
    def _compute_present(self):
        '''Method to count present students.'''
        for rec in self:
            count = 0
            for att in rec.student_ids:
                if att.is_present:
                    count += 1
            rec.total_presence = count

    @api.depends('student_ids')
    def _compute_absent(self):
        '''Method to count absent students'''
        for rec in self:
            count_fail = 0
            if rec.student_ids:
                for att in rec.student_ids:
                    if att.is_absent:
                        count_fail += 1
                rec.total_absent = count_fail

  
    

    @api.multi
    @api.onchange('classroom_id')
    def onchange_class_info(self):
        '''Method to get student roll no'''
        stud_list = []
        stud_obj = self.env['sm.student']
        for rec in self:
            if rec.classroom_id:
                stud_list = [{ 'name': stu.firstname,
                               'prenom': stu.lastname}
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
  
    classroom_id = fields.Many2one('cesag.allocation.enseignant',string=u'Classe',)
                                  
    student_ids = fields.One2many('daily.attendance.line', 'classroom_id',
                                  'Students'
                                 )

    module_id=fields.Many2one('classroom.allocation.module','Module')
    
    program_id = fields.Many2one('sm.program', string=u"Programme de Formation", required=True)

    level_id = fields.Many2one('sm.level', string=u"Niveau")

    year_id = fields.Many2one('sm.year', 'Année academique', 
                              help="Anné academique")

    semestre_id= fields.Many2one('sm.semester', 'Semestre', 
                              )

    teacher_id = fields.Many2one('sm.faculty', 'Professeur'
                              )
   
    total_student = fields.Integer(compute="_compute_total",
                                   store=True,
                                   help="Total Etudiant",
                                   string='Total Etudiant')
    total_presence = fields.Integer(compute="_compute_present",
                                    store=True, string='Present Students',
                                    help="Present ")
    total_absent = fields.Integer(compute="_compute_absent",
                                  store=True,
                                  string='Absent ',
                                  )
    
    cahier_ids=fields.One2many('cahier.line','absence_id', 'Cahier de texte')
    color = fields.Integer('Color Index', default=0)
    
    starttime = fields.Datetime('Heure de debut')
    endtime = fields.Datetime('Heure de fin')
    decs=fields.Text('Description du cours ')
    
    @api.onchange("module_id")
    def module_inf(self):
        for rec in self:
            if rec.module_id:
                search_element = self.env['classroom.allocation.module']
                search_element = search_element.search([('id', '=', rec.module_id.id)])
                if search_element.id:
                    rec.teacher_id = search_element.teacher_id.id
    



   

   

   


class DailyAttendanceLine(models.Model):
    '''Defining Daily Attendance Sheet Line Information.'''

    _description = 'Daily Attendance Line'
    _name = 'daily.attendance.line'
    # _order = 'roll_no'
    # _rec_name = 'roll_no'

    # roll_no = fields.Integer('Roll No.', help='Roll Number')
    prenom = fields.Char('Prenom.', help='Roll Number')
    name = fields.Char('Nom.', help='Roll Number')
    classroom_id = fields.Many2one('daily.attendance', 'Classe')
    stud_id = fields.Many2one('sm.student', 'Etudiants')
    is_present = fields.Boolean('Present',default=True, help="Check if student is present")
    is_absent = fields.Boolean('Absent', help="Check if student is absent")
    present_absentcheck = fields.Boolean('Present/Absent Boolean')
    late_time = fields.Datetime('Heure de retard')
    is_late = fields.Boolean('Retard',default=False)


    @api.onchange('is_present')
    def onchange_attendance(self):
        '''Method to make absent false when student is present.'''
        if self.is_present:
            self.is_absent = False
            self.present_absentcheck = True

    @api.onchange('is_absent')
    def onchange_absent(self):
        '''Method to make present false when student is absent.'''
        if self.is_absent:
            self.is_present = False
            self.present_absentcheck = True
    
    @api.onchange('is_late')
    def onchange_late(self):
        '''Method to make present false when student is absent.'''
        if self.is_late:
            self.is_absent = False
            self.present_absentcheck = True
    
    @api.onchange('is_late')
    def onchange_late_present(self):
        '''Method to make present false when student is absent.'''
        if self.is_late:
            self.is_present = False
            self.present_absentcheck = True


    @api.constrains('is_present', 'is_absent')
    def check_present_absent(self):
        '''Method to check present or absent.'''
        for rec in self:
            if not rec.is_present and not rec.is_absent:
                raise ValidationError(_('Check Present or Absent!'))


class Cahierdetexte(models.Model):

    _description = 'Cahier de texte'
    _name = 'cahier.line'



    starttime = fields.Datetime('Heure de debut')
    endtime = fields.Datetime('Heure de fin')
    decs=fields.Text('Description ')
    absence_id=fields.Many2one('daily.attendance')
