from datetime import datetime

from sqlalchemy.sql.schema import ForeignKey
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)

    posts = db.relationship("Classes", backref="author", lazy=True)
    stu = db.relationship("EnrolledClasses", backref="student", lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.id}', '{self.image_file}')"


class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100),unique=True, nullable=False)
    time = db.Column(db.String(30), nullable=False)
    limit = db.Column(db.Integer, nullable=True)
    class_count = db.Column(db.Integer, nullable=True, default = 0)

    stu_class = db.relationship("EnrolledClasses", backref="student_class", lazy=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id",ondelete="CASCADE"), nullable=True)

    def __repr__(self):
        return f"Classes('{self.name}', '{self.date_posted}')"

class EnrolledClasses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id",ondelete="CASCADE"), nullable=True)
    classes_id = db.Column(db.Integer, db.ForeignKey("classes.id",ondelete="CASCADE"), nullable=True)

   
    def __repr__(self):
        return f"EnrolledClasses('{self.student_class.class_name}', '{self.id}')"