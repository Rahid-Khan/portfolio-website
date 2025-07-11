from flask import Flask, render_template, flash, redirect, url_for, request, make_response, current_app, abort
from flask_login import login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from form import LoginForm, RegistrationForm, ProjectForm,ContactForm,ResetPasswordForm,ResetPasswordRequestForm
from models import User, Project
from extensions import db, bcrypt
from fpdf import FPDF
import io
from app import app
from werkzeug.utils import secure_filename
import os
import secrets
from flask_mail import Mail, Message
from datetime import datetime  # Add this at the top
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from io import BytesIO
import traceback
from flask import make_response, render_template
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config["SECRET_PASSWORD_SALT"] )
def varify_reset_token(token,expiration= 3600):
    serizalizer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serizalizer.loads(
            token,
            salt= app.config["SECRET_PASSWORD_SALT"],
            max_age=expiration
        )
    except:
        return False
    return email
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_reset_token(user.email)
            msg = Message('Password Reset Request',
                          sender='noreply@yourdomain.com',
                          recipients=[user.email])
            reset_url = url_for('reset_password', token=token, _external=True)
            msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email.
'''
            # mail.send(msg)  # Uncomment if you have Flask-Mail configured
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    email = verify_reset_token(token)
    if not email:
        flash('That is an invalid or expired token', 'danger')
        return redirect(url_for('reset_password_request'))
    
    user = User.query.filter_by(email=email).first()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', title='Reset Password', form=form)

@app.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Ensure the current user owns the project
    if project.user_id != current_user.id:
        abort(403)
    
    form = ProjectForm(obj=project)  # Use the same form as create
    
    if form.validate_on_submit():
        form.populate_obj(project)  # Update project with form data
        
        # Handle file upload if a new image was provided
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(app.root_path, 'static/project_images', filename)
            form.image.data.save(filepath)
            project.image_file = filename
        
        db.session.commit()
        flash('Your project has been updated!', 'success')
        return redirect(url_for('projects'))
    
    return render_template('create_project.html', title='Edit Project', form=form, project=project)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'download_cv' in request.form:
        try:
            # Create buffer and PDF document
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, 
                                  pagesize=letter,
                                  rightMargin=40,
                                  leftMargin=40,
                                  topMargin=40,
                                  bottomMargin=40,
                                  title="Rahid Khan - CV")
            
            # Create styles
            styles = getSampleStyleSheet()
            
            # Add custom styles
            styles.add(ParagraphStyle(
                name='Header1',
                fontSize=16,
                leading=18,
                alignment=TA_LEFT,
                spaceAfter=12,
                textColor=colors.HexColor('#3a0ca3'),
                fontName='Helvetica-Bold'
            ))
            
            styles.add(ParagraphStyle(
                name='Header2',
                fontSize=14,
                leading=16,
                alignment=TA_LEFT,
                spaceAfter=6,
                textColor=colors.HexColor('#4361ee'),
                fontName='Helvetica-Bold'
            ))
            
            styles.add(ParagraphStyle(
                name='NormalJustify',
                fontSize=11,
                leading=13,
                alignment=TA_JUSTIFY,
                spaceAfter=12
            ))
            
            styles.add(ParagraphStyle(
                name='CenterTitle',
                fontSize=18,
                leading=22,
                alignment=TA_CENTER,
                spaceAfter=12,
                textColor=colors.HexColor('#2b2d42'),
                fontName='Helvetica-Bold'
            ))
            
            styles.add(ParagraphStyle(
                name='CenterSubtitle',
                fontSize=14,
                leading=16,
                alignment=TA_CENTER,
                spaceAfter=24,
                textColor=colors.HexColor('#4a4e69')
            ))

            # Content elements
            elements = []
            
            # Header Section
            elements.append(Paragraph("RAHID KHAN", styles['CenterTitle']))
            elements.append(Paragraph("Artificial Intelligence Student", styles['CenterSubtitle']))
            
            # Contact Information
            contact_info = """
            <b>Address:</b> Peshawar Saddar Super Market, Peshawar, Pakistan<br/>
            <b>Phone:</b> 0307 042 9192 | <b>Email:</b> rahidka524@gmail.com<br/>
            <b>LinkedIn:</b> linkedin.com/in/rahid-khan | <b>GitHub:</b> github.com/Rahid-Khan
            """
            elements.append(Paragraph(contact_info, styles['NormalJustify']))
            elements.append(Spacer(1, 24))
            
            # Personal Statement
            elements.append(Paragraph("PERSONAL STATEMENT", styles['Header1']))
            statement = """
            Enthusiastic AI student currently pursuing Bachelor's in Artificial Intelligence with 
            foundational knowledge in Python programming, Flask web development, and machine learning concepts. 
            Fluent in Pashto, Urdu, and English with strong communication skills and passion for 
            developing technology solutions to real-world problems.
            """
            elements.append(Paragraph(statement, styles['NormalJustify']))
            elements.append(Spacer(1, 12))
            
            # Education
            elements.append(Paragraph("EDUCATION", styles['Header1']))
            
            edu_content = [
                ListItem(Paragraph("<b>Bachelor of Science in Artificial Intelligence</b>", styles['NormalJustify'])),
                ListItem(Paragraph("City University of Science and Information Technology, Peshawar", styles['NormalJustify'])),
                ListItem(Paragraph("Expected Graduation: May 2027 | Current Semester: 5th | GPA: 3.59/4.0", styles['NormalJustify'])),
                ListItem(Paragraph("<b>Relevant Coursework:</b>", styles['NormalJustify'])),
            ]
            
            coursework = [
                "Python Programming",
                "Data Structures & Algorithms",
                "Introduction to Machine Learning",
                "Generative AI",
                "Database Systems",
                "Web Development"
            ]
            
            for course in coursework:
                edu_content.append(ListItem(Paragraph(f"• {course}", styles['NormalJustify']), 
                                          bulletColor=colors.HexColor('#4361ee')))
            
            elements.append(ListFlowable(
                edu_content,
                bulletType='bullet',
                start='circle',
                bulletFontName='Helvetica',
                bulletFontSize=10,
                leftIndent=20,
                spaceBefore=6,
                spaceAfter=12
            ))
            
            # Technical Skills
            elements.append(Paragraph("TECHNICAL SKILLS", styles['Header1']))
            
            skills_content = [
                ["<b>Programming Languages:</b>", "Python (Intermediate), HTML/CSS (Basic)"],
                ["<b>Frameworks & Tools:</b>", "Flask, NumPy, Pandas, Scikit-learn"],
                ["<b>Machine Learning:</b>", "Supervised/Unsupervised Learning, Regression, Classification"],
                ["<b>Development Tools:</b>", "Git, VS Code, Jupyter Notebook"]
            ]
            
            for skill in skills_content:
                elements.append(Paragraph(f"{skill[0]} {skill[1]}", styles['NormalJustify']))
            
            elements.append(Spacer(1, 12))
            
            # Projects
            elements.append(Paragraph("PROJECTS", styles['Header1']))
            
            projects = [
                {
                    "title": "AI-Based Web Application (Flask)",
                    "description": [
                        "Developed web app with Python/Flask framework",
                        "Integrated machine learning model for predictions",
                        "Implemented user authentication system",
                        "GitHub: github.com/Rahid-Khan/flask-app"
                    ]
                },
                {
                    "title": "Data Analysis Project",
                    "description": [
                        "Cleaned and analyzed dataset using Pandas",
                        "Created visualizations with Matplotlib/Seaborn",
                        "Performed statistical analysis on results"
                    ]
                }
            ]
            
            for project in projects:
                elements.append(Paragraph(f"<b>{project['title']}</b>", styles['Header2']))
                for desc in project['description']:
                    elements.append(Paragraph(f"• {desc}", styles['NormalJustify']))
                elements.append(Spacer(1, 6))
            
            elements.append(Spacer(1, 12))
            
            # Languages
            elements.append(Paragraph("LANGUAGES", styles['Header1']))
            languages = [
                "Pashto (Native)",
                "Urdu (Fluent)",
                "English (Intermediate)"
            ]
            for lang in languages:
                elements.append(Paragraph(f"• {lang}", styles['NormalJustify']))
            
            elements.append(Spacer(1, 12))
            
            # Certifications
            elements.append(Paragraph("CERTIFICATIONS", styles['Header1']))
            certs = [
                "Programming for AI - National Vocational and Technical Training Commission",
                "Machine Learning Fundamentals - Online Course",
                "Web Development with Flask - Self-Taught"
            ]
            for cert in certs:
                elements.append(Paragraph(f"• {cert}", styles['NormalJustify']))
            
            # Build PDF
            doc.build(elements)
            
            # Create response
            pdf_data = buffer.getvalue()
            buffer.close()
            
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            if 'view' in request.form:
                response.headers['Content-Disposition'] = 'inline; filename=Rahid_Khan_CV.pdf'
            else:
                response.headers['Content-Disposition'] = 'attachment; filename=Rahid_Khan_CV.pdf'
                
            return response
            
        except Exception as e:
            buffer.close()
            print(f"Error generating PDF: {str(e)}")
            print(traceback.format_exc())
            flash('Error generating CV. Please try again.', 'error')
            return redirect(url_for('index'))
    
    return render_template('index.html')
@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact', methods = ["GET", "POST"])
def contact():
    form  = ContactForm()
    if form.validate_on_submit():
        try:
            message = Message(
                name = form.name.data,
                email = form.email.data,
                subject=form.subject.data,
                message = form.message.data
                
            )
            db.session.add(message)
            db.session.commit()
            
        #     msg = Message(
        #         subject=f"new contact : {form.subject.data}",
        #         sender=app.config["MAIL_USERNAME"],
        #         recipients=[app.config["MAIL_RECEIVER"]],
        #         body= f"""
        #         from : {form.name.data} < {form.email.data}> 
        #         message : 
        #         {form.message.data}
        #         """
        #     )
        #     mail.send(msg)
            flash('Your message has been sent! We\'ll contact you soon.', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"error saving message: {e}")
            flash("sorry, there was an error sending your message.","danger")
    return render_template("contact.html",form = form)

@app.route("/register", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            if existing_user.username == form.username.data:
                flash('Username already taken', 'danger')
            else:
                flash('Email already registered', 'danger')
            return render_template('register.html', form=form)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Your account has been created. You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/projects") 
def projects():
    projects = Project.query.order_by(Project.date_posted.desc()).all()  
    return render_template('projects.html', projects=projects)  
    
@app.route("/projects/new", methods=['GET', 'POST'])
@login_required
def new_project():
    form = ProjectForm()
    if form.validate_on_submit():
        if form.image.data:
            image_file = save_image(form.image.data)
        else:
            image_file = 'default.jpg'
        
        project = Project(
            title=form.title.data,
            description=form.description.data,
            image_file=image_file,
            project_url=form.project_url.data,
            category=form.category.data,
            user_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        flash('Your project has been added!', 'success')  
        return redirect(url_for('projects'))  
    return render_template("create_project.html", form=form)  

def save_image(image_file):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(image_file.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(app.root_path, 'static/project_images', image_fn)
    image_file.save(image_path)
    return image_fn
            

@app.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)
        
    try:
        # Delete associated image
        if project.image_file and project.image_file != 'default.jpg':
            image_path = os.path.join(
                current_app.root_path,
                'static/project_images',
                project.image_file
            )
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Delete from database
        db.session.delete(project)
        db.session.commit()
        
        flash('Project deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting project: {e}")
        flash('Error deleting project', 'danger')
    
    return redirect(url_for('projects'))






@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))