from openerp.osv import osv
from openerp.osv import fields
import StringIO
import base64
import xlrd
from openerp.tools.translate import _
from datetime import timedelta
import datetime
from dateutil.relativedelta import relativedelta

class import_ijarah_contract(osv.osv_memory):
	_name = 'import.ijarah.contract'
	_columns = {
		'file':fields.binary("File Path:"),
		'file_name':fields.char('File Name:'),
	}
              
	def import_contract_file(self, cr, uid, ids, context=None):
		#raise osv.except_osv(_('Error!'),_('Testingss!'))
		lst = []
		cur_obj = self.browse(cr, uid, ids)[0]       
		file_data = cur_obj.file
		val = base64.decodestring(file_data)
		fp = StringIO.StringIO()
		fp.write(val)
		wb = xlrd.open_workbook(file_contents=fp.getvalue())
		for sh in range(0, 1):
			sheet = wb.sheet_by_index(sh)
			for i in range(1, sheet.nrows):
				name = str(sheet.row_values(i, 0, sheet.ncols)[0])     # Employee No
				emp_name = sheet.row_values(i, 0, sheet.ncols)[1]  # Employee Name in Eng
				emp_name_ar = sheet.row_values(i, 0, sheet.ncols)[2]  # Employee Name in Arabic
				type_id = sheet.row_values(i, 0, sheet.ncols)[3]  # Contract Type Parent
				cont_type = sheet.row_values(i, 0, sheet.ncols)[4]  # Contract Type Child 1
				cont_detail = sheet.row_values(i, 0, sheet.ncols)[5]  # Contrct Type Child 2
				emp_cont_type = sheet.row_values(i, 0, sheet.ncols)[6]  # Employee Contract type
				contract_dur= sheet.row_values(i, 0, sheet.ncols)[7]  #  Contract Duration
#				date_start= sheet.row_values(i, 0, sheet.ncols)[8]  #  Contract Start Date
#				date_end= sheet.row_values(i, 0, sheet.ncols)[9]  #  Contract End Date		
				date_start=	datetime.datetime.strptime(sheet.row_values(i, 0, sheet.ncols)[8], "%Y/%m/%d")
						
				gender= sheet.row_values(i, 0, sheet.ncols)[9]  #  Gender
				nationality= sheet.row_values(i, 0, sheet.ncols)[10]  #  Nationality
				id_no= int(sheet.row_values(i, 0, sheet.ncols)[11])  #  ID No
				dept_id= sheet.row_values(i, 0, sheet.ncols)[12]  #  Department ID
				job_id= sheet.row_values(i, 0, sheet.ncols)[13]  #  JOB ID 
				dob= sheet.row_values(i, 0, sheet.ncols)[14]  #  Date of Birth
				ticket= sheet.row_values(i, 0, sheet.ncols)[15]  #  Air Ticket
				title= sheet.row_values(i, 0, sheet.ncols)[16]  #  Air Ticket
#				title= ""  #  Air Ticket
				year_diff= sheet.row_values(i, 0, sheet.ncols)[17]  #  Air Ticket
				type_id_char= sheet.row_values(i, 0, sheet.ncols)[18]  #  Air Ticket
				
																					
				print name,emp_name,emp_name_ar
				
				if name:                                        
					name_id = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					
						})
				elif emp_name:
						emp_id = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					


						})

				elif emp_name_ar:
						emp_name_ar = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					



						})
				elif type_id:
						type_id = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					




						})
					
				elif cont_type:
						cont_type = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					




						})
				elif cont_detail:
						cont_detail = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					




						})
				elif emp_cont_type:
						emp_cont_type = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					




						})
				elif contract_dur:
						contract_dur = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					



						})									
					
				elif date_start:
						date_start = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					




						})
				elif date_end:
						date_end = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					




						})

				elif gender:
						gender = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					




						})

				elif nationality:
						nationality = self.pool.get('hr.contract').create(cr, uid,				
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					




						})
				elif id_no:
						id_no = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					




						})
				elif dept_id:
						dept_id = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					



						})

				elif job_id:
						job_id = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					




						})
				elif dob:
						dob = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					



						})

				elif ticket:
						ticket = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'employee_arabic_name':emp_name_ar,'ticket_qty':ticket,'title':title,'year_diff':year_diff,'type_id_char':type_id_char					




						})					
				'''
				elif title:
						title = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,'date_end':date_end,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'ticket_qty':ticket,'title':title,'employee_arabic_name':emp_name_ar,				

						})					
				elif salary:
						salary = self.pool.get('hr.contract').create(cr, uid,
						{'name' : name,'employee_name':emp_name ,'type_id':type_id,'contract_type':cont_type,'contract_detail':cont_detail,
						'employee_contract_type':emp_cont_type,'contract_dur': contract_dur , 'date_start':date_start,'date_end':date_end,
						'gender':gender,'nationality':nationality,'identification_no':id_no,'dept_id':dept_id,'job_id':job_id,
						'birthday':dob,'ticket_qty':ticket,'title':title,'employee_arabic_name':emp_name_ar,					

						})
				'''		
		return True

