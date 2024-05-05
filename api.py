import bottle
from bottle import Bottle, run, response
from bottle_mysql import Plugin
import bottle_pymysql
import json
from datetime import date
from decimal import Decimal

app = bottle.Bottle()

plugin = bottle_pymysql.Plugin(dbuser='root', dbpass='root', dbname='Students')
app.install(plugin)

# Serialize date objects to string
def serialize_dates(data):
    if isinstance(data, date):
        return data.isoformat()
    raise TypeError ("Type %s not serializable" % type(data))

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

# return all students
@app.route('/student')
def get_students(pymydb):
    try:
        pymydb.execute('SELECT * FROM Students')
        result = pymydb.fetchall()
        if result:
            return json.dumps({'students': result}, default=serialize_dates)
        
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}
    
# return student by id
@app.route('/student/<id:int>')
def get_student(pymydb, id):
    try:
        pymydb.execute('SELECT * FROM Students WHERE `Student ID`=%s', (id,))
        result = pymydb.fetchone()
        if result:
            return json.dumps({'student': result}, default=serialize_dates)
        else:
            response.status = 404
            return {'error': 'Student not found'}
        
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}

# Add new students
@app.route('/student', method='POST')
def add_student(pymydb):
    try:
        data = bottle.request.json
        for item in data:
            if item['Student Name'] is None or item['Date Of Birth'] is None or item['Student Class'] is None:
                response.status = 400
                return {'error': 'Name ,DOB and Class are required'}
            
            pymydb.execute('INSERT INTO Students (`Student Name`, `Date Of Birth`, `Student Class`) VALUES (%s, %s, %s)'
                        , (item['Student Name'], item['Date Of Birth'], item['Student Class']))
            
        # pymydb.commit()
        response.status = 201
        return {'status': 'Student added successfully'}
    
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}
    
@app.route('/student/averageperquarter/<id:int>')
def get_student_per_quarter(pymydb, id):
    try:
        pymydb.execute('SELECT (Mathematics + `Computer Science` + Literature)/3.0 AS Average_Grade, Quarter, Year FROM Grades WHERE `Student ID` = %s GROUP BY Year, Quarter ORDER BY Year, Quarter;'
                        , (id, ))
        result = pymydb.fetchall()
        if result:
            json_result = json.dumps({'student_per_quarter': result}, cls=DecimalEncoder)
            return (json_result)
        else:
            response.status = 404
            return {'error': 'No students found for the year'}
        
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}
    
@app.route('/subject/averageperquarter/<subject>')
def get_quarters(pymydb, subject):
    try:
        query = f'SELECT AVG(`{subject}`) AS Average_Grade, Quarter, Year FROM Grades GROUP BY Year, Quarter'
        pymydb.execute(query)
        result = pymydb.fetchall()
        if result:
            json_result = json.dumps({'subject_per_quarter': result}, cls=DecimalEncoder)
            return (json_result)
        else:
            response.status = 404
            return {'error': 'No subject found for the year'}
        
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}

@app.route('/subject/averageperyearall/<year:int>/<quarter>')
def get_averageperyearall(pymydb, year, quarter):
    try:
        query = 'SELECT AVG(Mathematics) AS Mathematics, AVG(`Computer Science`) AS `Computer Science`, AVG(Literature) AS Literature FROM Grades WHERE Year = %s AND Quarter = %s'
        pymydb.execute(query, (year, quarter))
        result = pymydb.fetchall()
        if result:
            json_result = json.dumps({'average_per_year_all': result}, cls=DecimalEncoder)
            return (json_result)
        else:
            response.status = 404
            return {'error': 'No subject found for the year'}
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}
    
# Run the application
if __name__ == '__main__':
    app.run(host='localhost', port=8090, debug=True)
