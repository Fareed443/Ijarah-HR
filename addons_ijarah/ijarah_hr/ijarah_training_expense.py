from openerp.osv import osv, fields
from datetime import datetime,time
from openerp.addons import jasper_reports
from lxml import etree    
import datetime
import time
import math
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
from datetime import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

class ijarah_hr_emp_train_exp(osv.osv):

	def create(self, cr, uid, vals,context=None):		
		name = vals['name']
		date_start = vals['date_start']
		date_end= vals['date_end']
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
                vals['emp_name'] = this.name_related # name.dbfieldname
		if (date_start and date_end) and (date_start <= date_end):
			diff_day = self._get_number_of_days(date_start, date_end)
			vals['days'] = round(math.floor(diff_day))
		else:
			vals['days'] = 1

		return super(ijarah_hr_emp_train_exp,self).create(cr, uid, vals, context)
	
	def write(self, cr, uid, ids, vals, context=None):						
		name = vals.get('name')
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		res={}	
		if vals.get('name'):
			vals['emp_name'] = this.name_related # name.dbfieldname			
			res.update({'emp_name':this.name_related,})
		result = super(ijarah_hr_emp_train_exp, self).write(cr, uid, ids, vals, context=context)	
		return result

	def _get_number_of_days(self, date_start, date_end):
	
		DATETIME_FORMAT = "%Y-%m-%d"		
		from_dt = datetime.strptime(date_start, DATETIME_FORMAT)
		to_dt = datetime.strptime(date_end, DATETIME_FORMAT)
		timedelta = to_dt - from_dt
		diff_day = timedelta.days + float(timedelta.seconds) / 86400
		return diff_day		

	_name = "ijarah.hr.emp.train.exp"
	_columns = {
		'name'	: fields.many2one("hr.employee","Employee No",required=True,domain="[('activate','=',True)]",states={'Done':[('readonly',True)]}),
		'emp_name':fields.char("Employee Name",readonly=True,states={'Done':[('readonly',True)]}),
		'note':fields.text("Description",states={'Done':[('readonly',True)],'Done':[('readonly',True)]}),
		'date_start':fields.date("Start Date",states={'Done':[('readonly',True)]},required=True),
		'date_end':fields.date("End Date",states={'Done':[('readonly',True)]},required=True),
		'days':fields.integer("Days",readonly=True),
		'amount':fields.float('Amount',states={'Done':[('readonly',True)]},required=True),
		'no_of_hours':fields.float("No of Hours",required=True),
		'course_name':fields.char("Course Name",required=True,states={'Done':[('readonly',True)]}),
		'train_type': fields.selection([('Internal', 'Internal'),('External', 'External')],'Type of Training',required=True),
		'state': fields.selection([('Draft', 'Draft'),('Done', 'Done')],'Status',  readonly=True,),

	}
	_defaults = {			
		'state'  : lambda * a :'Draft',
#        	'date_start': lambda *a: time.strftime('%Y-%m-01'),
#		'date_end': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
	}
	
	def unlink(self, cr, uid, ids, context=None):
		ded = self.pool.get('ijarah.hr.emp.deduct').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in ded:
		    if x['state'] in ('Draft'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete Enties which are already Opened or Done state !'))
#		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
#		return True
		return super(ijarah_hr_emp_train_exp, self).unlink(cr, uid, ids, context=context) 
            		
	def validate_state(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'Done'}, context=context)
		return True
		         		    	
	def onchange_empno(self, cr, uid,ids,name,context=None):
		if name:		 
			this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
			value ={'emp_name':this.name_related}
			return {'value': value}

	def onchange_date_start(self, cr, uid,ids,date_start,date_end,context=None):
		value = {}
		if date_start > date_end:
			return { 'Warning':{'title':'warning','message':'Put valid From Date'},'value' :{'date_end':''}}
		return True

	def onchange_date(self, cr, uid,ids,date_start,date_end,context=None):
		result = {'value': {}}
		if date_start > date_end:
			return { 'Warning':{'title':'warning','message':'Put valid From Date'},'value' :{'date_end':''}}
			
		if (date_start and date_end) and (date_start <= date_end):
			diff_day = self._get_number_of_days(date_start, date_end)
			result['value']['days'] = round(math.floor(diff_day))
		else:
			result['value']['days'] = 1
		return result

ijarah_hr_emp_train_exp()
