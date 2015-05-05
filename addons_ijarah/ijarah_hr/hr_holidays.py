#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    Copyright (c) 2005-2006 Axelor SARL. (http://www.axelor.com)
#    and 2004-2010 Tiny SPRL (<http://tiny.be>).
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from datetime import datetime,time
from datetime import datetime
from lxml import etree    
import datetime

from datetime import datetime, timedelta
from openerp import netsvc
import time
DATES_FORMAT = "%Y-%m-%d"

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DTFORMAT
from openerp.tools.translate import _


class hr_holidays_status(osv.Model):

    _inherit = 'hr.holidays.status'

    _columns = {
        'ex_rest_days': fields.boolean('Exclude Rest Days',
                                       help="If enabled, the employee's day off is skipped in leave days calculation."),
        'ex_public_holidays': fields.boolean('Exclude Public Holidays',
                                             help="If enabled, public holidays are skipped in leave days calculation."),
    }


class hr_holidays(osv.osv):

    _name = 'hr.holidays'
    _inherit = ['hr.holidays', 'ir.needaction_mixin']

    _columns = {
        'real_days': fields.float('Total Days', digits=(16, 1)),
        'rest_days': fields.float('Weekend', digits=(16, 1)),
        'public_holiday_days': fields.float('Public Holidays', digits=(16, 1)),
        'real_days_int': fields.integer('Total Days'),
        'rest_days_int': fields.integer('Weekend'),
        'public_holiday_days_int': fields.integer('Public Holidays'),

        'date_from': fields.date('Start Date', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, select=True),
        'date_to': fields.date('End Date', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
	'no_of_days_temp_int':fields.integer("No of Days"),
        'employee_id': fields.many2one('hr.employee', "Employee", select=True, invisible=False, readonly=True,domain="[('activate','=',True)]", states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),        
    }
    
    #### cUSTOMIZE
    def create(self, cr, uid, vals, context=None):
        """ Override to avoid automatic logging of creation """
        if context is None:
            context = {}
        context = dict(context, mail_create_nolog=True)

        if 'name' in context:
            holiday_status_id = self.pool.get('hr.holidays.status').search(cr, uid, [('name','=',context['name'])])
            if len(holiday_status_id) > 0:
                holiday_status_id = holiday_status_id[0]
                dic = self.onchange_date_from(cr, uid, None, vals['date_to'], vals['date_from'], holiday_status_id,context=None)
                vals.update(dic)
                vals['real_days'] = dic['value']['real_days']
                vals['rest_days'] = dic['value']['rest_days']
                vals['public_holiday_days'] = dic['value']['public_holiday_days']
                vals['real_days_int'] = dic['value']['real_days_int']
                vals['rest_days_int'] = dic['value']['rest_days_int']
                vals['public_holiday_days_int'] = dic['value']['public_holiday_days_int']
                vals['number_of_days_temp'] = dic['value']['number_of_days_temp']
                vals['no_of_days_temp_int'] = dic['value']['no_of_days_temp_int']


        return super(hr_holidays, self).create(cr, uid, vals, context=context)
	
	# cUSTOMIZE
    '''	    
    def write(self, cr, uid, ids, vals, context=None):
	res={}
        check_fnct = self.pool.get('hr.holidays.status').check_access_rights
        for  holiday in self.browse(cr, uid, ids, context=context):
            if holiday.state in ('validate','validate1') and not check_fnct(cr, uid, 'write', raise_exception=False):
                raise osv.except_osv(_('Warning!'),_('You cannot modify a leave request that has been approved. Contact a human resource manager.'))


        try:
            holiday_status_id = vals['holiday_status_id']
        except:
            holiday_status_id = self.browse(cr, uid, ids[0], context=None).holiday_status_id.id
        if holiday_status_id:
            try:
                date_to = vals['date_to']
            except:
                date_to = self.browse(cr, uid, ids[0], context=None).date_to

            try:
                date_from = vals['date_from']
            except:
                date_from = self.browse(cr, uid, ids[0], context=None).date_from 

            dic = self.onchange_date_from(cr, uid, None, date_to, date_from, holiday_status_id,context=None)
            vals.update(dic)
            vals['real_days'] = dic['value']['real_days']
            vals['rest_days'] = dic['value']['rest_days']
            vals['public_holiday_days'] = dic['value']['public_holiday_days']
            vals['number_of_days_temp'] = dic['value']['number_of_days_temp']
	    res.update({'real_days': dic['value']['real_days'] , 
					'rest_days':dic['value']['rest_days'],			
					'public_holiday_days':dic['value']['public_holiday_days'],	
					'number_of_days_temp':dic['value']['number_of_days_temp']
					})		


        return super(hr_holidays, self).write(cr, uid, ids, vals, context=context)

    '''
    def _employee_get(self, cr, uid, context=None):

        if context == None:
            context = {}

        # If the user didn't enter from "My Leaves" don't pre-populate Employee
        # field
        import logging
        _l = logging.getLogger(__name__)
        _l.warning('context: %s', context)
        if not context.get('search_default_my_leaves', False):
            return False

        ids = self.pool.get('hr.employee').search(
            cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False

    def _days_get(self, cr, uid, context=None):

        if context == None:
            context = {}

        date_from = context.get('default_date_from')
        date_to = context.get('default_date_to')

        if date_from and date_to:    #date_to is with 00:00:00
            x=date_to.split(' ')
            date_to = x[0]
            delta = datetime.strptime(
                date_to, DATES_FORMAT) - datetime.strptime(date_from, DATES_FORMAT)
            return (delta.days and delta.days or 1)
        return False
    	
    _defaults = {
#        'holiday_status_id': 1,
        'employee_id': _employee_get,
        'number_of_days_temp': _days_get,
    }

    _order = 'date_from asc, type desc'    

    
    def _needaction_domain_get(self, cr, uid, context=None):
        emp_obj = self.pool.get('hr.employee')
        empids = emp_obj.search(cr, uid, [('parent_id.user_id', '=', uid)], context=context)
        dom = ['&', ('state', '=', 'confirm'), ('employee_id', 'in', empids)]
        # if this user is a hr.manager, he should do second validations
        if self.pool.get('res.users').has_group(cr, uid, 'base.group_hr_manager'):
            dom = ['|'] + dom + [('state', '=', 'validate1')]
        return dom
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        if context is None:
            context = {}
        default = default.copy()
        default['date_from'] = False
        default['date_to'] = False
        return super(hr_holidays, self).copy(cr, uid, id, default, context=context)

    def _create_resource_leave(self, cr, uid, leaves, context=None):
        '''This method will create entry in resource calendar leave object at the time of holidays validated '''
        obj_res_leave = self.pool.get('resource.calendar.leaves')
        for leave in leaves:
            vals = {
                'name': leave.name,
                'date_from': leave.date_from,

                'holiday_id': leave.id,
                'date_to': leave.date_to,
                'resource_id': leave.employee_id.resource_id.id,
                'calendar_id': leave.employee_id.resource_id.calendar_id.id
            }
            obj_res_leave.create(cr, uid, vals, context=context)
        return True
    def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
            result['value']['no_of_days_temp_int'] = round(math.floor(diff_day))+1

        else:
            result['value']['number_of_days_temp'] = 0
            result['value']['no_of_days_temp_int'] = 0

        return result
    
    def onchange_date_from(self, cr, uid, ids, date_to, date_from, holiday_status_id,context=None):
        # date_to has to be greater than date_from
        result = {'value': {}}
        
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        if date_from and not date_to:   #date_to = False
            date_to = date_from
            
        if not date_from and not date_to:
            return result
            
        no_days = 0
        if (date_to and date_from) and (date_from <= date_to):
            DATE_FORMAT = "%Y-%m-%d"
            from_dt = datetime.strptime(date_from, DATE_FORMAT)
            x=date_to.split(' ')
            date_to = x[0]            
            to_dt = datetime.strptime(date_to, DATE_FORMAT)
            timedeltaa = to_dt - from_dt
            no_days = int(timedeltaa.days)+1

        if holiday_status_id:
            hs_data = self.pool.get(
                'hr.holidays.status').read(cr, uid, holiday_status_id,
                                           ['ex_rest_days', 'ex_public_holidays'],
                                           context=context)
        else:
            hs_data = {}
        ex_rd = hs_data.get('ex_rest_days', False)
        ex_ph = hs_data.get('ex_public_holidays', False)

        holiday_obj = self.pool.get('hr.holidays.public')
        r = holiday_obj.get_rest_list(cr, uid, datetime.now().year , context=context) #[u'4',u'5']       
        rest_days = tuple([int(i) for i in r])   #(4,5)
        
        count_days = real_day = no_days        #if only date_from then its value is 1.0
        ph_days = 0
        r_days = 0
        next_dt = from_dt

        while count_days > 0:
            public_holiday = holiday_obj.is_public_holiday(
                cr, uid, next_dt.date(), context=context)                   #TRUE OR FALSE
            public_holiday = (public_holiday and ex_ph)

            rest_day = (next_dt.weekday() in rest_days and ex_rd)      # TRUE OR FALSE    #(FOR FRI & SAT RETURN VALUE TRUE)
            next_dt += timedelta(days=1)        # FROM DATE      next =NEXT DAY DATE

            if public_holiday or rest_day:      # TRUE OR FALSE
                if public_holiday:
                    ph_days += 1
                elif rest_day:
                    r_days += 1
                no_days -= 1
            count_days -= 1
        
        result['value'].update({'rest_days': r_days,
                                    'public_holiday_days': ph_days,
                                    'number_of_days_temp': no_days,
				    'no_of_days_temp_int':int(no_days),
                                    'rest_days_int':int(r_days),
                                    'real_days_int':int(real_day),
                                    'public_holiday_days_int':int(ph_days),					
                                    'real_days': real_day})
        return result

    
    def holidays_validate(self, cr, uid, ids, context=None):
        self.check_holidays(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'validate'})
        data_holiday = self.browse(cr, uid, ids)
        for record in data_holiday:
            if record.double_validation:
                self.write(cr, uid, [record.id], {'manager_id2': manager})
            else:
                self.write(cr, uid, [record.id], {'manager_id': manager})
            if record.holiday_type == 'employee' and record.type == 'remove':
                meeting_obj = self.pool.get('crm.meeting')
                meeting_vals = {
                    'name': record.name or _('Leave Request'),
                    'categ_ids': record.holiday_status_id.categ_id and [(6,0,[record.holiday_status_id.categ_id.id])] or [],
                    'duration': record.number_of_days_temp * 8,
                    'description': record.notes,
                    'user_id': record.user_id.id,
                    'date': record.date_from,
                    'end_date': record.date_to,
                    'date_deadline': record.date_to,
                    'state': 'open',            # to block that meeting date in the calendar
                }
                meeting_id = meeting_obj.create(cr, uid, meeting_vals)
                self._create_resource_leave(cr, uid, [record], context=context)
                self.write(cr, uid, ids, {'meeting_id': meeting_id})
            elif record.holiday_type == 'category':
                emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [record.category_id.id])])
                leave_ids = []
                for emp in obj_emp.browse(cr, uid, emp_ids):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'no_of_days_temp_int': record.no_of_days_temp_int,
                        'parent_id': record.id,
                        'employee_id': emp.id
                    }
                    leave_ids.append(self.create(cr, uid, vals, context=None))
                wf_service = netsvc.LocalService("workflow")
                for leave_id in leave_ids:
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        return True


#Added by Fareed  #Calculate remaining leaves w.r.t the date from
    def check_holidays(self, cr, uid, ids, context=None):
        holi_status_obj = self.pool.get('hr.holidays.status')
        for record in self.browse(cr, uid, ids):
            if record.holiday_type == 'employee' and record.type == 'remove':
                if record.employee_id and not record.holiday_status_id.limit:
                    leaves_rest = holi_status_obj.get_days( cr, uid, [record.holiday_status_id.id], record.employee_id.id, False)[record.holiday_status_id.id]['remaining_leaves']
                    if record.date_from and record.date_to:
                        cr.execute (''' select (EXTRACT(YEAR FROM (age(%s,now()))) * 12 + EXTRACT(MONTH FROM (age(%s, now())))) * 2.5 as leaves_balance''', (record.date_from,record.date_from,))   
                        data = cr.fetchone()
                        leaves_rest += data[0]
                    if leaves_rest < record.number_of_days_temp:
                        raise osv.except_osv(_('Warning!'), _('There are not enough %s allocated for employee %s; please create an allocation request for this leave type.') % (record.holiday_status_id.name, record.employee_id.name))
        return True


class hr_employee(osv.osv):
    _inherit="hr.employee"

    def create(self, cr, uid, vals, context=None):
        # don't pass the value of remaining leave if it's 0 at the creation time, otherwise it will trigger the inverse
        # function _set_remaining_days and the system may not be configured for. Note that we don't have this problem on
        # the write because the clients only send the fields that have been modified.
        if 'remaining_leaves' in vals and not vals['remaining_leaves']:
            del(vals['remaining_leaves'])
        return super(hr_employee, self).create(cr, uid, vals, context=context)

    def _set_remaining_days(self, cr, uid, empl_id, name, value, arg, context=None):
        employee = self.browse(cr, uid, empl_id, context=context)
        diff = value - employee.remaining_leaves
        type_obj = self.pool.get('hr.holidays.status')
        holiday_obj = self.pool.get('hr.holidays')
        # Find for holidays status
        status_ids = type_obj.search(cr, uid, [('limit', '=', False)], context=context)
        if len(status_ids) != 1 :
            raise osv.except_osv(_('Warning!'),_("The feature behind the field 'Remaining Legal Leaves' can only be used when there is only one leave type with the option 'Allow to Override Limit' unchecked. (%s Found). Otherwise, the update is ambiguous as we cannot decide on which leave type the update has to be done. \nYou may prefer to use the classic menus 'Leave Requests' and 'Allocation Requests' located in 'Human Resources \ Leaves' to manage the leave days of the employees if the configuration does not allow to use this field.") % (len(status_ids)))
        status_id = status_ids and status_ids[0] or False
        if not status_id:
            return False
        if diff > 0:
            leave_id = holiday_obj.create(cr, uid, {'name': _('Allocation for %s') % employee.name, 'employee_id': employee.id, 'holiday_status_id': status_id, 'type': 'add', 'holiday_type': 'employee', 'number_of_days_temp': diff}, context=context)
        elif diff < 0:
            leave_id = holiday_obj.create(cr, uid, {'name': _('Leave Request for %s') % employee.name, 'employee_id': employee.id, 'holiday_status_id': status_id, 'type': 'remove', 'holiday_type': 'employee', 'number_of_days_temp': abs(diff)}, context=context)
        else:
            return False
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
        wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
        wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        return True

    def _get_remaining_days(self, cr, uid, ids, name, args, context=None):
        cr.execute("""SELECT
                sum(h.number_of_days) as days,
                h.employee_id
            from
                hr_holidays h
                join hr_holidays_status s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                s.limit=False and
                h.employee_id in (%s)
            group by h.employee_id"""% (','.join(map(str,ids)),) )
        res = cr.dictfetchall()
        remaining = {}
        for r in res:
            remaining[r['employee_id']] = r['days']
        for employee_id in ids:
            if not remaining.get(employee_id):
                remaining[employee_id] = 0.0
        return remaining

    def _get_leave_status(self, cr, uid, ids, name, args, context=None):
        holidays_obj = self.pool.get('hr.holidays')
        holidays_id = holidays_obj.search(cr, uid,
           [('employee_id', 'in', ids), ('date_from','<=',time.strftime('%Y-%m-%d')),
           ('date_to','>=',time.strftime('%Y-%m-%d')),('type','=','remove'),('state','not in',('cancel','refuse'))],
           context=context)
        result = {}
        for id in ids:
            result[id] = {
                'current_leave_state': False,
                'current_leave_id': False,
                'leave_date_from':False,
                'leave_date_to':False,
            }
        for holiday in self.pool.get('hr.holidays').browse(cr, uid, holidays_id, context=context):
            result[holiday.employee_id.id]['leave_date_from'] = holiday.date_from
            result[holiday.employee_id.id]['leave_date_to'] = holiday.date_to
            result[holiday.employee_id.id]['current_leave_state'] = holiday.state
            result[holiday.employee_id.id]['current_leave_id'] = holiday.holiday_status_id.id
        return result

    _columns = {
        'remaining_leaves': fields.function(_get_remaining_days, string='Remaining Legal Leaves', fnct_inv=_set_remaining_days, type="float", help='Total number of legal leaves allocated to this employee, change this value to create allocation/leave request. Total based on all the leave types without overriding limit.'),
        'current_leave_state': fields.function(_get_leave_status, multi="leave_status", string="Current Leave Status", type="selection",
            selection=[('draft', 'New'), ('confirm', 'Waiting Approval'), ('refuse', 'Refused'),
            ('validate1', 'Waiting Second Approval'), ('validate', 'Approved'), ('cancel', 'Cancelled')]),
        'current_leave_id': fields.function(_get_leave_status, multi="leave_status", string="Current Leave Type",type='many2one', relation='hr.holidays.status'),
        'leave_date_from': fields.function(_get_leave_status, multi='leave_status', type='date', string='From Date'),
        'leave_date_to': fields.function(_get_leave_status, multi='leave_status', type='date', string='To Date'),
    }

hr_employee()
