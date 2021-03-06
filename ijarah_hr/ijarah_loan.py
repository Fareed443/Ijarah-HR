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


class ijarah_hr_emp_loan(osv.osv):

	def create(self, cr, uid, vals,context=None):		
		name = vals['name']
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
                vals['salary'] = this.contract_id.basic_salary # name.dbfieldname			
                vals['emp_name'] = this.name_related # name.dbfieldname			
                vals['job_id'] = this.job_id.id # name.dbfieldname			
#		vals['assign_name']= str(prod.designation.name)		
		return super(ijarah_hr_emp_loan,self).create(cr, uid, vals, context)
	
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
				             'job_id':this.job_id.id , 	})		

		result = super(ijarah_hr_emp_loan, self).write(cr, uid, ids, vals, context=context)	
		return result

	def _get_number_of_days(self, from_date, to_date):
	
		DATETIME_FORMAT = "%Y-%m-%d"		
		from_dt = datetime.datetime.strptime(from_date, DATETIME_FORMAT)
		to_dt = datetime.datetime.strptime(to_date, DATETIME_FORMAT)
#		r = relativedelta.relativedelta(to_dt, from_dt)
#		x = r.months
#		return x	
		diff_month = (12*to_dt.year + to_dt.month) - (12*from_dt.year + from_dt.month)	
		return diff_month

	_name = "ijarah.hr.emp.loan"
	_columns = {
		'name'	: fields.many2one("hr.employee","Employee No",required=True,domain="[('activate','=',True)]",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'emp_name':fields.char("Employee Name",readonly="True",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'job_id':fields.many2one("hr.job","Job Title",readonly="True",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'salary':fields.float("Salary",readonly="True",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'note':fields.text("Note",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'req_amount':fields.float("Requested Amount",states={'Open':[('readonly',True)],'Done':[('readonly',True)]},required=True),
#		'apprv_by':fields.char("Approved By",size=64,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'apprv_by':fields.many2one("res.users","Approved By",readonly=True,select=True),
		'from_date': fields.date("From Date",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'to_date':fields.date("To Date",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'nom':fields.float("No of Months",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'deduct_amount':fields.float('Deduction Amount'),
		'per_month':fields.float("Installment/Month",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'total_install':fields.float("Total Installmment",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'net_amount':fields.float("Net Amount",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'state': fields.selection([('Draft', 'Draft'),('Open', 'Open'),('Done', 'Done')],'Status',  readonly=True,),
		'loan_type': fields.selection([
			('Employee Loan', 'Employee Loan'),('Iqama', 'Iqama'),('Labour Office', 'Labour Office'),
			('Transfer Sponsorship', 'Transfer Sponsorship')
		],'Loan Type',states={'Open':[('readonly',True)],'Done':[('readonly',True)]},required=True),
		'deduct_type': fields.selection([('Deductable', 'Deductable'),('Non-Deductable', 'Non-Deductable')],'Deduct Type',required=True,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'state': fields.selection([('Draft', 'Draft'),('Open', 'Open'),('Done', 'Done')],'Status',  readonly=True,),
		'lines':fields.one2many('ijarah.hr.emp.loan.child','loan_ids',ondelete="cascade"),

	}
	_defaults = {			
		'state'  : lambda * a :'Draft',
	}
	
	def check_installment(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
		cr.execute("""SELECT id,net_amount, total_install , req_amount  
				FROM ijarah_hr_emp_loan WHERE state = 'Open' AND total_install = req_amount AND net_amount = 0.00 """)	
		for x in cr.fetchall():
			cr.execute("""UPDATE ijarah_hr_emp_loan SET state = 'Done' where id = %s """,(x[0],))
	
	def unlink(self, cr, uid, ids, context=None):
		loans = self.pool.get('ijarah.hr.emp.loan').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in loans:
		    if x['state'] in ('Draft'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete loan(s) which are already Opened or Done state !'))
#		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
#		return True
		return super(ijarah_hr_emp_loan, self).unlink(cr, uid, ids, context=context)        
    		
	def validate_state(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'Open','apprv_by':uid}, context=context)
		return True
	
	def onchange_date(self, cr, uid,ids,from_date,to_date,context=None):
		today_date = str(datetime.datetime.now())
		result = {'value': {}}
		if not from_date:
			return { 'warning':{'title':'warning','message':'Please Enter From Date'},'value' :{'to_date':False,'nom':0}}	
		if to_date < from_date:
			return { 'warning':{'title':'warning','message':'Please Enter Valid Date'},'value' :{'to_date':False,'nom':0}}	
		if (from_date and to_date) and (from_date <= to_date):
			diff_day = self._get_number_of_days(from_date, to_date)
			result['value']['nom'] = round(math.floor(diff_day))
		else:
			result['value']['nom'] = 1
		return result

	def onchange_from_date(self, cr, uid,ids,from_date,context=None):
#		today_date = str(datetime.datetime.now())
		today_date= time.strftime('%Y-%m-%d')
		result = {'value': {}}
		if from_date < today_date:
			return { 'warning':{'title':'warning','message':'Please Enter Valid Date'},'value' :{'from_date':False,'to_date':False}}	
		return result
	
	def onchange_nom(self, cr, uid,ids,req_amount,nom,context=None):
		default = {
		'value':{'per_month':'',}
		}       	        		  
		a = float(req_amount)
		b = float(nom)
		c = b/a
		if c < 1:
			return { 'warning':{'title':'warning','message':'Installment Amount should be greater than or equal to 1. Received 0 Amount.'},'value' :{'per_month':0.00,'nom':0.00,'to_date':False}}	 
		if c >=1:
			default['value']['per_month'] = float(c)
			return default 
         	return True

	def fetch_data(self, cr, uid, ids, context=None):
	 	
	 	for gp in self.browse(cr, uid, ids, context=context):
			DATETIME_FORMAT = "%Y-%m-%d"
			a = int(gp.nom)
			if not gp.lines:
				for x in range(a):        
					ds = datetime.datetime.strptime(gp.from_date,DATETIME_FORMAT)
					cr.execute("""INSERT INTO ijarah_hr_emp_loan_child(loan_ids,name,month,status,paid)
					  	 	SELECT ijarah_hr_emp_loan.id,ijarah_hr_emp_loan.per_month, %s ,%s , %s
							From ijarah_hr_emp_loan
							WHERE ijarah_hr_emp_loan.id = %s """,(ds+relativedelta.relativedelta(months=x),True,False,ids[0],))
					cr.execute("""Update ijarah_hr_emp_loan SET net_amount = req_amount WHERE id = %s """,ids)		
		    	
	def onchange_empno(self, cr, uid,ids,name,context=None):
			
		if name:		 
			this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
			contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
			value = {'salary':this.contract_id.basic_salary,'emp_name': this.name_related,'job_id':this.job_id.id}
			return {'value': value}
		
ijarah_hr_emp_loan()                     

class ijarah_hr_emp_loan_child(osv.osv):
        
		_name = "ijarah.hr.emp.loan.child"
		_columns = {
			'loan_ids' : fields.many2one("ijarah.hr.emp.loan","LOAN ID",hidden=True,ondelete='cascade'),
			'name':fields.float("Amount",readonly=True),
			'paid' :fields.boolean("Paid",readonly=True),
			'month' : fields.date("Month",readonly=True),
			'status':fields.boolean('Active'),
			'deduct':fields.float("Total Installmment",readonly=True),
			'total_amount':fields.float("Total Amount",readonly=True),
				             
		}                
		_order = "month"                    
		_defaults = {
			'status' : True,
			'paid':False,	
		}

ijarah_hr_emp_loan_child()        

