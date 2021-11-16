import os
import secrets
from urllib.request import Request,urlopen
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Classes,EnrolledClasses
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime



def ran(x):
    return range(x)


app.jinja_env.filters["ran"] = ran


@app.route("/")
def home():
    if current_user.is_authenticated:
        get_user = User.query.get_or_404(current_user.id)
        cl = Classes.query.filter_by(author=get_user)
        return render_template("home.html", cl=cl)
    else:
        return redirect(url_for("login"))

@app.route("/home2")
def home2():
    if current_user.is_authenticated:
        get_user = User.query.get_or_404(current_user.id)
        st = EnrolledClasses.query.filter_by(student=get_user)
        for i in st:
            print("rerere", i)
        return render_template("home2.html", st=st)
    else:
        return redirect(url_for("login"))    
    

@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data,  password=hashed_password, 
            user_type=form.user_type.data
        )

        db.session.add(user)
        db.session.commit()
        login_user(user)
        # flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            if current_user.user_type == "teacher":
                return redirect(next_page) if next_page else redirect(url_for("home"))
            else:
                return redirect(next_page) if next_page else redirect(url_for("home2"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    form_1 = RegistrationForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form,form_1=form_1
    )


@app.route("/add-courses", methods=["GET", "POST"])
@login_required
def add_courses():
    form = PostForm()
    if form.validate_on_submit():
        post = Classes(
            class_name=form.class_name.data,
            time=form.time.data,
            limit=form.limit.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash("Your Course has Created!", "success")
        return redirect(url_for("home"))


    return render_template(
        "add_teacher_class.html",
        title="New Review",
        form=form,
    )


# @app.route("/product_detail/<int:product_id>", methods=["GET"])
# def product_detail(product_id):
#     product = Classes.query.get_or_404(product_id)
#     return render_template("product_detail.html", product=product)


@app.route("/course_edit/<int:classes_id>", methods=['GET', 'POST'])
@login_required
def course_edit(classes_id):
    post = Classes.query.get_or_404(classes_id)
    form = PostForm(obj=post)
    if request.method =="POST":
        if form.validate_on_submit():
            post.class_name = form.class_name.data
            post.time = form.time.data
            post.content = form.limit.data
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect('/')
    return render_template('add_teacher_class.html', 
                           form=form )



@app.route("/course_delete/<int:classes_id>", methods=['GET','Post'])
def course_delete(classes_id):
    dlt = Classes.query.get_or_404(classes_id)
    p = EnrolledClasses.query.filter_by(course_enrolled=dlt.class_name).first() 

    if dlt.author != current_user:
        abort(403)
    db.session.delete(dlt)
    db.session.commit()
    db.session.delete(p)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/Show-classes",methods=["GET"])
def show_classes():
    if request.method =="GET":
            get_classes = Classes.query.all()
            return render_template('add_studentclass.html', classes = get_classes)

@app.route("/enroll/<int:classes_id>",methods=["POST"])
def enroll(classes_id):
    post = Classes.query.get_or_404(classes_id)
    if post.class_count < post.limit:
        p = EnrolledClasses.query.filter_by(student_class=post)
        check = 0
        for i in p:
            if i.student.username == current_user.username:
                check = 1
        if request.method =="POST":
            if check == 0:
                enroll = EnrolledClasses(
                    student=current_user,
                    student_class=post,
                )
                post.class_count = post.class_count+1
                db.session.add(enroll, post)
                db.session.commit()
                flash('Course is added', 'success')
                return redirect(url_for("home2"))
            else:
                flash('Course Already added', 'danger') 
                return redirect(url_for("show_classes"))
    else:
        flash('You can not register in this class as strength is already full.', 'danger') 
        return redirect(url_for("show_classes"))
    return redirect(url_for('login'))

@app.route("/enrollement-delete/<int:classes_id>", methods=['GET','Post'])
def enrollement_delete(classes_id):
    get_class = EnrolledClasses.query.get_or_404(classes_id)
    get_class.student_class.class_count = get_class.student_class.class_count - 1
    db.session.add(get_class)
    db.session.delete(get_class)
    db.session.commit()
    flash('Your Class has been deleted!', 'success')
    return redirect(url_for('home2'))

@app.route("/course-detail/<int:class_id>", methods=['GET','Post'])
def course_detail(class_id):
    get_class =Classes.query.get_or_404(class_id)
    get_students = EnrolledClasses.query.filter_by(student_class=get_class)
    return render_template('course_detail.html', students = get_students, class_id = class_id)

@app.route("/edit-grade/<int:class_id>/<int:enrollment_id>", methods=['GET','Post'])
def edit_grade(class_id, enrollment_id):
    if request.method == "POST":
        get_class = EnrolledClasses.query.get(enrollment_id)
        get_class.grade = request.form["grade"]
        db.session.add(get_class)
        db.session.commit()
        return redirect(url_for('course_detail',class_id=class_id))