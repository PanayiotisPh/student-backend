import bottle
from bottle import Bottle, run, response
from bottle_mysql import Plugin
import bottle_pymysql
import json
from datetime import date

app = bottle.Bottle()

plugin = bottle_pymysql.Plugin(dbuser='root', dbpass='root', dbname='students')
app.install(plugin)

# Serialize date objects to string
def serialize_dates(data):
    if isinstance(data, date):
        return data.isoformat()
    raise TypeError ("Type %s not serializable" % type(data))

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
    
@app.route('/statistics/studentperquarter/<year:int>')
def get_student_per_quarter(pymydb, year):
    try:
        # Get the total number of students per quarter
        pymydb.execute('SELECT QUARTER(`Date Of Birth`) AS Quarter, COUNT(*) AS Students FROM Students WHERE YEAR(`Date Of Birth`)= %s GROUP BY Quarter', (year,))
        result = pymydb.fetchall()
        if result:
            return json.dumps({'students_per_quarter': result})
        else:
            response.status = 404
            return {'error': 'No students found for the year'}
        
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}
    
@app.route('/quarter')
def get_quarters(pymydb):
    try:
        # Get the list of quarters
        pymydb.execute('SELECT DISTINCT QUARTER(`Date Of Birth`) AS Quarter FROM Students')
        result = pymydb.fetchall()
        if result:
            return json.dumps({'quarters': result})
        else:
            response.status = 404
            return {'error': 'No quarters found'}
        
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}
    
# Run the application
if __name__ == '__main__':
    app.run(host='localhost', port=8090, debug=True)
