import os

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import dotenv
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from marshmallow import Schema, fields

dotenv.load_dotenv()

db_user = os.environ.get('DB_USERNAME')
db_pass = os.environ.get('DB_PASSWORD')
db_hostname = os.environ.get('DB_HOSTNAME')
db_name = os.environ.get('DB_NAME')

DB_URI = f'mysql+pymysql://{db_user}:{db_pass}@{db_hostname}/{db_name}'

engine = create_engine(DB_URI, echo=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Student(db.Model):
    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    cellphone = db.Column(db.String(13), unique=True, nullable=False)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id: int):
        return cls.query.get_or_404(id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class StudentSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    email = fields.Str()
    age = fields.Integer()
    cellphone = fields.Str()


@app.route('/', methods=['GET'])
def home():
    return '<p>Hello from students API!</p>', 200


@app.route('/api', methods=['GET'])
def api_main():
    # Sorry, I am lazy to connect swagger by flask-apispec
    data = {
        '/api/students/modify/<id> (PATCH)': {
            200: 'Student Object'
        },
        '/api/students/change/<id> (PUT),': {
            200: 'Student Object'
        },
        '/api/deleteStudent/<id> (DELETE)': {
            204: 'resource deleted successfully'
        }
    }
    return jsonify(data), 200


@app.route('/api/students', methods=['GET'])
def get_all_students():
    students = Student.get_all()
    student_list = StudentSchema(many=True)
    response = student_list.dump(students)
    return jsonify(response), 200


@app.route('/api/students/get/<int:id>', methods=['GET'])
def get_student(id):
    student_info = Student.get_by_id(id)
    serializer = StudentSchema()
    response = serializer.dump(student_info)
    return jsonify(response), 200


@app.route('/api/students/add', methods=['POST'])
def add_student():
    json_data = request.get_json()
    new_student = Student(
        name=json_data.get('name'),
        email=json_data.get('email'),
        age=json_data.get('age'),
        cellphone=json_data.get('cellphone')
    )
    new_student.save()
    serializer = StudentSchema()
    data = serializer.dump(new_student)
    return jsonify(data), 201


@app.route('/api/health-check/ok', methods=['GET'])
def health_ok():
    return 'Ok', 200


@app.route('/api/health-check/bad', methods=['GET'])
def health_bad():
    return 'Bad', 500


@app.route('/api/students/modify/<int:id>', methods=['PATCH'])
def patch_student(id: int):
    student = Student.get_by_id(id)

    json_data = request.get_json()

    if name := json_data.get('name') is not None:
        student.name = name
    if email := json_data.get('email') is not None:
        student.email = email
    if age := json_data.get('age') is not None:
        student.age = age
    if cellphone := json_data.get('cellphone') is not None:
        student.cellphone = cellphone

    student.save()
    serializer = StudentSchema()
    data = serializer.dump(student)
    return jsonify(data), 200


@app.route('/api/students/change/<int:id>', methods=['PUT'])
def put_student(id: int):
    student = Student.get_by_id(id)

    json_data = request.get_json()

    student.name = json_data.get('name', '')
    student.email = json_data.get('email', '')
    student.age = json_data.get('age', 0)
    student.cellphone = json_data.get('cellphone', '')

    student.save()

    serializer = StudentSchema()
    data = serializer.dump(student)
    return jsonify(data), 200


@app.route('/api/students/delete/<int:id>', methods=['DELETE'])
def delete_student(id: int):
    student = Student.get_by_id(id)

    student.delete()
    return 'resource deleted successfully', 204


if __name__ == '__main__':
    if not database_exists(engine.url):
        create_database(engine.url)
    db.create_all()
    app.run(port=8090, debug=True)
