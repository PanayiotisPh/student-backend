import bottle
from bottle import response
import bottle_pymysql
import json
from datetime import date
from decimal import Decimal

app = bottle.Bottle()

plugin = bottle_pymysql.Plugin(dbuser='root', dbpass='root', dbname='students')
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
    

@app.route('/<path:path>', method=['OPTIONS'])
def handle_options(path):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    return {}

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

# get student average grades
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

# get subject average grades
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

# get average grades for all subjects
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

# get student grades
@app.route('/student/grades/<id:int>')
def get_student_grades(pymydb, id):
    try:
        query = 'SELECT * FROM Grades WHERE `Student ID` = %s'
        pymydb.execute(query, (id,))
        result = pymydb.fetchall()
        if result:
            json_result = json.dumps({'grades': result}, cls=DecimalEncoder)
            return (json_result)
        else:
            response.status = 404
            return {'error': 'No grades found for the student'}
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}

# Add student grades
@app.route('/student/grades', method='POST')
def post_student_grades(pymydb):
    try:
        data = bottle.request.json
        for item in data:
            if item['Student ID'] is None or item['Mathematics'] is None or item['Computer Science'] is None or item['Literature'] is None or item['Quarter'] is None or item['Year'] is None:
                response.status = 400
                return {'error': 'Student ID, Mathematics, Computer Science, Literature, Quarter and Year are required'}
            
            pymydb.execute('INSERT INTO Grades (`Student ID`, Mathematics, `Computer Science`, Literature, Quarter, Year) VALUES (%s, %s, %s, %s, %s, %s)'
                        , (item['Student ID'], item['Mathematics'], item['Computer Science'], item['Literature'], item['Quarter'], item['Year']))
            
        response.status = 201
        return {'status': 'Grades added successfully'}
    
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}

# Update student data   
@app.route('/student/<id:int>', method='PUT')
def update_student(pymydb, id):
    try:
        data = bottle.request.json
        if data['Student Name'] is None or data['Date Of Birth'] is None or data['Student Class'] is None:
            response.status = 400
            return {'error': 'Name ,DOB and Class are required'}
        
        pymydb.execute('UPDATE Students SET `Student Name`=%s, `Date Of Birth`=%s, `Student Class`=%s WHERE `Student ID`=%s'
                    , (data['Student Name'], data['Date Of Birth'], data['Student Class'], id))
        
        response.status = 200
        return {'status': 'Student updated successfully'}
    
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}

# get student grades at a certain quarter and year
@app.route('/student/grade/<id:int>/<year:int>/<quarter>')
def getStudentsQuarter(pymydb, id, year, quarter):
    try:
        query = 'SELECT * FROM Grades WHERE `Student ID` = %s AND Year = %s AND Quarter = %s'
        pymydb.execute(query, (id, year, quarter))
        result = pymydb.fetchall()
        if result:
            json_result = json.dumps({'grades': result}, cls=DecimalEncoder)
            return (json_result)
        else:
            response.status = 404
            return {'error': 'No grades found for the student'}
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}

# Update student grades at a certain quarter and year
@app.route('/student/grade/<id:int>/<year:int>/<quarter>', method='PUT')
def editGrade(pymydb, id, year, quarter):
    try:
        data = bottle.request.json
        if data['Mathematics'] is None or data['Computer Science'] is None or data['Literature'] is None:
            response.status = 400
            return {'error': 'Mathematics, Computer Science and Literature are required'}
        
        pymydb.execute('UPDATE Grades SET Mathematics=%s, `Computer Science`=%s, Literature=%s WHERE `Student ID`=%s AND Year=%s AND Quarter=%s'
                    , (data['Mathematics'], data['Computer Science'], data['Literature'], id, year, quarter))
        
        response.status = 200
        return {'status': 'Grades updated successfully'}
    
    except Exception as e:
        # Log error and return error message
        print(f"Database error: {e}")
        response.status = 500
        return {'error': 'Database operation failed'}


# Run the application
if __name__ == '__main__':
    app.run(host='localhost', port=8090, debug=True)
