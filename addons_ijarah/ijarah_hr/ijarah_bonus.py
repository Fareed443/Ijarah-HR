from openerp.osv import osv, fields
from datetime import datetime,time
from datetime import datetime
from dateutil import relativedelta
from lxml import etree    
import datetime
import time
import math
from openerp.tools.translate import _
from datetime import date, timedelta


class ijarah_hr_emp_bonus(osv.osv):

	def create(self, cr, uid, vals,context=None):		
		name = vals['name']
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
                vals['salary'] = this.contract_id.basic_salary # name.dbfieldname			
                vals['emp_name'] = this.name_related # name.dbfieldname			
                vals['job_id'] = this.job_id.id # name.dbfieldname			
#		vals['assign_name']= str(prod.designation.name)		
		return super(ijarah_hr_emp_bonus,self).create(cr, uid, vals, context)
	
	def write(self, cr, uid, ids, vals, context=None):						
		name = vals.get('name')
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
		res={}	
		if vals.get('name'):
			vals['salary'] = this.contract_id.basic_salary # name.dbfieldname			
			vals['emp_name'] = this.name_related # name.dbfieldname			
			vals['job_id'] = this.job_id.id # name.dbfieldname			
			res.update({'salary': this.contract_id.basic_salary , 'emp_name':this.name_related,			
				             'job_id':this.job_id.id ,		
					})		

		result = super(ijarah_hr_emp_bonus, self).write(cr, uid, ids, vals, context=context)	
		return result

	def _get_number_of_days(self, date_from,date_to):
	
		DATETIME_FORMAT = "%Y-%m-%d"		
		from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
		to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
		r = relativedelta.relativedelta(to_dt, from_dt)
		x = r.months
		return x

	_name = "ijarah.hr.emp.bonus"
	_columns = {
		'name'	: fields.many2one("hr.employee","Employee No",required=True,domain="[('activate','=',True)]",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'emp_name':fields.char("Employee Name",readonly=True,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'job_id':fields.many2one("hr.job","Job Title",readonly=True,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'salary':fields.float("Salary",readonly=True,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'note':fields.text("Note",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'date_from':fields.date("From Date",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'date_to':fields.date("End Date",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'state': fields.selection([('Draft', 'Draft'),('Open', 'Open'),('Done', 'Done')],'Status',  readonly=True,),
		'bonus_amount':fields.float("Bonus Amount",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'paid':fields.boolean("Paid",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'repeat_bonus':fields.boolean("Repeat Bonus"),
		'nom':fields.float("No of Months",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'lines':fields.one2many('ijarah.hr.emp.bonus.child','bonus_ids',ondelete="cascade"),

	}
	_defaults = {			
		'state'  : lambda * a :'Draft',
        	'date_from': lambda *a: time.strftime('%Y-%m-01'),
#		'date_to': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
		'paid': False,	
	}
	
	def unlink(self, cr, uid, ids, context=None):
		bonus = self.pool.get('ijarah.hr.emp.bonus').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in bonus:
		    if x['state'] in ('Draft'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete Bonus which are already Opened or Done state !'))
#		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
#		return True
		return super(ijarah_hr_emp_bonus, self).unlink(cr, uid, ids, context=context)        	

	def validate_state(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'Open'}, context=context)
		return True
		         		    	
	def onchange_empno(self, cr, uid,ids,name,for_month,month_end_date,context=None):
		if name:		 
			this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
			contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
			value ={'salary':this.contract_id.basic_salary,'emp_name':this.name_related,'job_id':this.job_id.id}
			return {'value': value}

	def onchange_date(self, cr, uid,ids,date_from,date_to,context=None):
		result = {'value': {}}
		if (date_from and date_to) and (date_from <= date_to):
			diff_day = self._get_number_of_days(date_from, date_to)
			result['value']['nom'] = round(math.floor(diff_day))
		else:
			result['value']['nom'] = 1
		return result

	def fetch_data(self, cr, uid, ids, context=None):	 	
	 	for gp in self.browse(cr, uid, ids, context=context):
			DATETIME_FORMAT = "%Y-%m-%d"
			a = int(gp.nom)
			if not gp.lines:
				for x in range(a):        
					ds = datetime.datetime.strptime(gp.date_from,DATETIME_FORMAT)
					cr.execute("""INSERT INTO ijarah_hr_emp_bonus_child(bonus_ids,name,month,status,paid)
					  	 	SELECT ijarah_hr_emp_bonus.id,ijarah_hr_emp_bonus.bonus_amount, %s,%s,%s
							From ijarah_hr_emp_bonus
							WHERE ijarah_hr_emp_bonus.id = %s """,(ds+relativedelta.relativedelta(months=x+1),True,False,ids[0],))
ijarah_hr_emp_bonus()

class ijarah_hr_emp_bonus_child(osv.osv):
        
		_name = "ijarah.hr.emp.bonus.child"
		_columns = {
			'bonus_ids' : fields.many2one("ijarah.hr.emp.bonus","Bonus ID",hidden=True,ondelete='cascade'),
			'name':fields.float("Amount",readonly=True),
			'paid' :fields.boolean("Paid",readonly=True),
			'month' : fields.date("Month",readonly=True),
			'status':fields.boolean("Active"),
		}                
		_order = "month"                    
		_defaults = {
			'status' : True,
			'paid':False,	
		}
ijarah_hr_emp_bonus_child()        

