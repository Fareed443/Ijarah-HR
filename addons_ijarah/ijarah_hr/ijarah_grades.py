from openerp.osv import osv, fields

class ijarah_hr_grade(osv.osv):
	
	_name = "ijarah.hr.grade"
	_columns = {
		'name'	: fields.char("Title",required=True),
		#'band':fields.selection([
		#	('30', 'Band 30'),('20', 'Band 20'),('15', 'Band 15'),
		#	('10', 'Band 10'),('4', 'Band 4')],'Band',required=True),
		'band':fields.char("Band",required=True),		
		'grade': fields.char("Grades",required=True),
		'roles'	: fields.char("Roles",required=True),
		#'sal_ranges':fields.selection([
		#	('Between SAR 1000 to 2500', 'Between SAR 1000 to 2500'),('Between SAR 2500 to 5000', 'Between SAR 2500 to 5000'),
		#	('Between SAR 5000 to 10000', 'Between SAR 5000 to 10000'),('Between SAR 10000 to 20000', 'Between SAR 10000 to 20000'),
		#	('Between SAR 20000 to 50000', 'Between SAR 20000 to 50000')],'Salary Range',required=True),
		'amount1':fields.float("Salary Range"),
		'amount2':fields.float("Amount2:"),
	}	        	
ijarah_hr_grade()
