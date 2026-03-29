from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message as MailMessage
from database import db, User, SkillCategory, Skill, Project, Experience, Education, ContactMessage
import os
import json
import threading
import webbrowser
import requests as http_requests

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload

# ---- Email (Flask-Mail) Configuration ----
# Uses Gmail SMTP. Set MAIL_PASSWORD to your Gmail App Password
# (enable 2FA on Gmail, then create an App Password at myaccount.google.com/apppasswords)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'rehman56012@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')  # Set via env var MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = ('Portfolio Contact Form', os.environ.get('MAIL_USERNAME', 'rehman56012@gmail.com'))

# ---- Your contact details ----
OWNER_EMAIL = 'rehman56012@gmail.com'
OWNER_WHATSAPP = '+923187004439'

mail = Mail(app)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

def send_contact_email(name, email, subject, message_body):
    """Send notification email to owner when a contact form is submitted."""
    try:
        msg = MailMessage(
            subject=f'[Portfolio Contact] {subject}',
            recipients=[OWNER_EMAIL],
            reply_to=email
        )
        msg.body = f"""New message from your portfolio contact form!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
From   : {name}
Email  : {email}
Subject: {subject}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{message_body}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reply directly to this email to respond to {name}.
"""
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error(f'Email send failed: {e}')
        return False

def send_whatsapp_notification(name, email, subject):
    """Send WhatsApp notification via CallMeBot API (free).
    
    Setup: Send "I allow callmebot to send me messages" to +34 644 60 21 27 on WhatsApp
    then set the CALLMEBOT_API_KEY environment variable with the key they send back.
    Without the API key, this will just log the message.
    """
    api_key = os.environ.get('CALLMEBOT_API_KEY', '')
    if not api_key:
        app.logger.info(f'[WhatsApp] New message from {name} ({email}) — Subject: {subject}')
        return False
    try:
        wa_message = f'📩 New Portfolio Message!\nFrom: {name}\nEmail: {email}\nSubject: {subject}\n\nCheck your admin panel: http://127.0.0.1:5000/admin/messages'
        url = f'https://api.callmebot.com/whatsapp.php?phone={OWNER_WHATSAPP}&text={http_requests.utils.quote(wa_message)}&apikey={api_key}'
        r = http_requests.get(url, timeout=10)
        return r.status_code == 200
    except Exception as e:
        app.logger.error(f'WhatsApp send failed: {e}')
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_unread_messages():
    """Inject unread message count into all templates for the sidebar badge."""
    try:
        count = ContactMessage.query.filter_by(is_read=False).count()
    except Exception:
        count = 0
    return {'g_unread_messages': count}

# Fallback hardcoded data (in case database is empty)
fallback_portfolio_data = {
    'personal': {
        'name': 'Abdul Rehman',
        'title': 'Electrical Engineering Student | Computer Engineering Specialist',
        'bio': 'I am an Electrical Engineering student with expertise in circuit design, embedded systems, and IoT development.',
        'email': 'rehman.designworks@gmail.com',
        'phone': '0318 7004439',
        'address': 'Chenab Nagar, Pakistan'
    }
}

# Helper functions to fetch data from database or fallback
def get_projects():
    """Get projects from database or return empty list"""
    try:
        projects = Project.query.order_by(Project.order).all()
        return [{'id': p.id, 'title': p.title, 'description': p.description, 
                'category': p.category, 'details': p.details, 'image_filename': p.image_filename,
                'skills': [s.name for s in p.skills]} for p in projects]
    except:
        return []

def get_experiences():
    """Get experiences from database or return empty list"""
    try:
        experiences = Experience.query.order_by(Experience.order).all()
        return [{'id': e.id, 'title': e.title, 'company': e.company, 'period': e.period,
                'description': e.description, 'responsibilities': e.get_responsibilities(),
                'skills': [s.name for s in e.skills]} for e in experiences]
    except:
        return []

def get_education():
    """Get education from database or return empty list"""
    try:
        education = Education.query.order_by(Education.order).all()
        return [{'id': e.id, 'level': e.level, 'field': e.field, 'school': e.school,
                'location': e.location, 'period': e.period, 'grade': e.grade,
                'details': e.get_details()} for e in education]
    except:
        return []

def get_skills_by_category():
    """Get skills organized by category"""
    try:
        categories = SkillCategory.query.order_by(SkillCategory.order).all()
        result = []
        for cat in categories:
            skills = Skill.query.filter_by(category_id=cat.id).order_by(Skill.order).all()
            result.append({
                'category': cat.name,
                'icon': cat.icon,
                'items': [s.name for s in skills]
            })
        return result
    except:
        return []

# ======================== PUBLIC ROUTES ========================

@app.route('/')
def home():
    projects = get_projects()
    skills = get_skills_by_category()
    return render_template('index.html', projects=projects, skills=skills)

@app.route('/projects')
def projects():
    projects_list = get_projects()
    return render_template('projects.html', projects=projects_list)

@app.route('/experience')
def experience():
    experiences = get_experiences()
    education = get_education()
    return render_template('experience.html', experiences=experiences, education=education)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received.'}), 400

        name    = (data.get('name', '') or '').strip()
        email   = (data.get('email', '') or '').strip()
        subject = (data.get('subject', '') or '').strip()
        body    = (data.get('message', '') or '').strip()

        if not all([name, email, subject, body]):
            return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400

        # 1. Save to database
        contact_msg = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=body,
            ip_address=request.remote_addr
        )
        db.session.add(contact_msg)
        db.session.commit()

        # 2. Send email notification (runs in background so form responds instantly)
        threading.Thread(target=send_contact_email, args=(name, email, subject, body), daemon=True).start()

        # 3. WhatsApp notification
        threading.Thread(target=send_whatsapp_notification, args=(name, email, subject), daemon=True).start()

        return jsonify({'status': 'success', 'message': 'Message received! I\'ll get back to you soon.'})

    return render_template('contact.html')

@app.route('/images/<path:filename>')
def serve_image(filename):
    images_dir = os.path.join(os.path.dirname(__file__), 'images')
    return send_from_directory(images_dir, filename)

# ======================== ADMIN ROUTES ========================

@app.route('/admin')
def admin_home():
    if not current_user.is_authenticated:
        return redirect(url_for('admin_login'))
    
    # Dashboard statistics
    stats = {
        'total_projects': Project.query.count(),
        'total_experiences': Experience.query.count(),
        'total_education': Education.query.count(),
        'total_skills': Skill.query.count(),
        'total_messages': ContactMessage.query.count(),
        'unread_messages': ContactMessage.query.filter_by(is_read=False).count()
    }
    
    projects_list = Project.query.order_by(Project.order).all()
    experiences_list = Experience.query.order_by(Experience.order).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', stats=stats, 
                         projects=projects_list, experiences=experiences_list,
                         recent_messages=recent_messages)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('admin_home'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# ======================== PROJECT MANAGEMENT ========================

@app.route('/admin/projects')
@login_required
def admin_projects():
    projects_list = Project.query.order_by(Project.order).all()
    categories = set(p.category for p in projects_list)
    return render_template('admin/projects/list.html', projects=projects_list, categories=categories)

@app.route('/admin/projects/add', methods=['GET', 'POST'])
@login_required
def admin_add_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        details = request.form.get('details')
        skill_ids = request.form.getlist('skills')
        
        project = Project(
            title=title,
            description=description,
            category=category,
            details=details,
            order=Project.query.count() + 1
        )
        
        project.skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = f"project_{project.id}_{file.filename}"
                os.makedirs(os.path.join(os.path.dirname(__file__), 'images/projects'), exist_ok=True)
                file.save(os.path.join(os.path.dirname(__file__), 'images/projects', filename))
                project.image_filename = filename
        
        db.session.add(project)
        db.session.commit()
        
        flash(f'Project "{title}" created successfully!', 'success')
        return redirect(url_for('admin_projects'))
    
    categories = ['Hardware', 'Web', '3D Model', 'Other']
    skills = SkillCategory.query.order_by(SkillCategory.order).all()
    return render_template('admin/projects/form.html', project=None, categories=categories, skills=skills)

@app.route('/admin/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.category = request.form.get('category')
        project.details = request.form.get('details')
        
        skill_ids = request.form.getlist('skills')
        project.skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = f"project_{project.id}_{file.filename}"
                os.makedirs(os.path.join(os.path.dirname(__file__), 'images/projects'), exist_ok=True)
                file.save(os.path.join(os.path.dirname(__file__), 'images/projects', filename))
                project.image_filename = filename
        
        db.session.commit()
        flash(f'Project "{project.title}" updated successfully!', 'success')
        return redirect(url_for('admin_projects'))
    
    categories = ['Hardware', 'Web', '3D Model', 'Other']
    skills = SkillCategory.query.order_by(SkillCategory.order).all()
    return render_template('admin/projects/form.html', project=project, categories=categories, skills=skills)

@app.route('/admin/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def admin_delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    title = project.title
    
    # Delete image if exists
    if project.image_filename:
        try:
            os.remove(os.path.join(os.path.dirname(__file__), 'images/projects', project.image_filename))
        except:
            pass
    
    db.session.delete(project)
    db.session.commit()
    flash(f'Project "{title}" deleted successfully!', 'success')
    return redirect(url_for('admin_projects'))

# ======================== EXPERIENCE MANAGEMENT ========================

@app.route('/admin/experiences')
@login_required
def admin_experiences():
    experiences_list = Experience.query.order_by(Experience.order).all()
    return render_template('admin/experiences/list.html', experiences=experiences_list)

@app.route('/admin/experiences/add', methods=['GET', 'POST'])
@login_required
def admin_add_experience():
    if request.method == 'POST':
        title = request.form.get('title')
        company = request.form.get('company')
        period = request.form.get('period')
        description = request.form.get('description')
        
        # Get responsibilities from textarea and split by newline
        responsibilities_text = request.form.get('responsibilities')
        responsibilities = [r.strip() for r in responsibilities_text.split('\n') if r.strip()]
        
        skill_ids = request.form.getlist('skills')
        
        experience = Experience(
            title=title,
            company=company,
            period=period,
            description=description,
            order=Experience.query.count() + 1
        )
        experience.set_responsibilities(responsibilities)
        experience.skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
        
        db.session.add(experience)
        db.session.commit()
        
        flash(f'Experience "{title}" created successfully!', 'success')
        return redirect(url_for('admin_experiences'))
    
    skills = SkillCategory.query.order_by(SkillCategory.order).all()
    return render_template('admin/experiences/form.html', experience=None, skills=skills)

@app.route('/admin/experiences/<int:experience_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_experience(experience_id):
    experience = Experience.query.get_or_404(experience_id)
    
    if request.method == 'POST':
        experience.title = request.form.get('title')
        experience.company = request.form.get('company')
        experience.period = request.form.get('period')
        experience.description = request.form.get('description')
        
        responsibilities_text = request.form.get('responsibilities')
        responsibilities = [r.strip() for r in responsibilities_text.split('\n') if r.strip()]
        experience.set_responsibilities(responsibilities)
        
        skill_ids = request.form.getlist('skills')
        experience.skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
        
        db.session.commit()
        flash(f'Experience "{experience.title}" updated successfully!', 'success')
        return redirect(url_for('admin_experiences'))
    
    skills = SkillCategory.query.order_by(SkillCategory.order).all()
    return render_template('admin/experiences/form.html', experience=experience, skills=skills)

@app.route('/admin/experiences/<int:experience_id>/delete', methods=['POST'])
@login_required
def admin_delete_experience(experience_id):
    experience = Experience.query.get_or_404(experience_id)
    title = experience.title
    
    db.session.delete(experience)
    db.session.commit()
    flash(f'Experience "{title}" deleted successfully!', 'success')
    return redirect(url_for('admin_experiences'))

# ======================== EDUCATION MANAGEMENT ========================

@app.route('/admin/education')
@login_required
def admin_education():
    education_list = Education.query.order_by(Education.order).all()
    return render_template('admin/education/list.html', education=education_list)

@app.route('/admin/education/add', methods=['GET', 'POST'])
@login_required
def admin_add_education():
    if request.method == 'POST':
        level = request.form.get('level')
        field = request.form.get('field')
        school = request.form.get('school')
        location = request.form.get('location')
        period = request.form.get('period')
        grade = request.form.get('grade')
        
        # Get subjects from textarea
        subjects_text = request.form.get('subjects')
        subjects = [s.strip() for s in subjects_text.split('\n') if s.strip()]
        
        details = {
            'subjects': subjects,
            'eqf_level': request.form.get('eqf_level', ''),
            'credits': request.form.get('credits', '')
        }
        
        education = Education(
            level=level,
            field=field,
            school=school,
            location=location,
            period=period,
            grade=grade,
            order=Education.query.count() + 1
        )
        education.set_details(details)
        
        db.session.add(education)
        db.session.commit()
        
        flash(f'Education entry "{level}" created successfully!', 'success')
        return redirect(url_for('admin_education'))
    
    return render_template('admin/education/form.html', education=None)

@app.route('/admin/education/<int:education_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_education(education_id):
    education = Education.query.get_or_404(education_id)
    
    if request.method == 'POST':
        education.level = request.form.get('level')
        education.field = request.form.get('field')
        education.school = request.form.get('school')
        education.location = request.form.get('location')
        education.period = request.form.get('period')
        education.grade = request.form.get('grade')
        
        subjects_text = request.form.get('subjects')
        subjects = [s.strip() for s in subjects_text.split('\n') if s.strip()]
        
        details = {
            'subjects': subjects,
            'eqf_level': request.form.get('eqf_level', ''),
            'credits': request.form.get('credits', '')
        }
        education.set_details(details)
        
        db.session.commit()
        flash(f'Education entry "{education.level}" updated successfully!', 'success')
        return redirect(url_for('admin_education'))
    
    return render_template('admin/education/form.html', education=education)

@app.route('/admin/education/<int:education_id>/delete', methods=['POST'])
@login_required
def admin_delete_education(education_id):
    education = Education.query.get_or_404(education_id)
    level = education.level
    
    db.session.delete(education)
    db.session.commit()
    flash(f'Education entry "{level}" deleted successfully!', 'success')
    return redirect(url_for('admin_education'))

# ======================== SKILLS MANAGEMENT ========================

@app.route('/admin/skills')
@login_required
def admin_skills():
    categories = SkillCategory.query.order_by(SkillCategory.order).all()
    return render_template('admin/skills/list.html', categories=categories)

@app.route('/admin/skills/category/add', methods=['GET', 'POST'])
@login_required
def admin_add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        icon = request.form.get('icon', 'fa-star')
        
        category = SkillCategory(
            name=name,
            icon=icon,
            order=SkillCategory.query.count() + 1
        )
        db.session.add(category)
        db.session.commit()
        
        flash(f'Category "{name}" created successfully!', 'success')
        return redirect(url_for('admin_skills'))
    
    return render_template('admin/skills/category_form.html', category=None)

@app.route('/admin/skills/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_category(category_id):
    category = SkillCategory.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.icon = request.form.get('icon', 'fa-star')
        db.session.commit()
        
        flash(f'Category "{category.name}" updated successfully!', 'success')
        return redirect(url_for('admin_skills'))
    
    return render_template('admin/skills/category_form.html', category=category)

@app.route('/admin/skills/category/<int:category_id>/delete', methods=['POST'])
@login_required
def admin_delete_category(category_id):
    category = SkillCategory.query.get_or_404(category_id)
    name = category.name
    
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{name}" deleted successfully!', 'success')
    return redirect(url_for('admin_skills'))

@app.route('/admin/skills/add', methods=['GET', 'POST'])
@login_required
def admin_add_skill():
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        
        skill = Skill(
            name=name,
            category_id=category_id,
            order=Skill.query.count() + 1
        )
        db.session.add(skill)
        db.session.commit()
        
        flash(f'Skill "{name}" created successfully!', 'success')
        return redirect(url_for('admin_skills'))
    
    categories = SkillCategory.query.order_by(SkillCategory.order).all()
    return render_template('admin/skills/skill_form.html', skill=None, categories=categories)

@app.route('/admin/skills/<int:skill_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    if request.method == 'POST':
        skill.name = request.form.get('name')
        skill.category_id = request.form.get('category_id')
        db.session.commit()
        
        flash(f'Skill "{skill.name}" updated successfully!', 'success')
        return redirect(url_for('admin_skills'))
    
    categories = SkillCategory.query.order_by(SkillCategory.order).all()
    return render_template('admin/skills/skill_form.html', skill=skill, categories=categories)

@app.route('/admin/skills/<int:skill_id>/delete', methods=['POST'])
@login_required
def admin_delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    name = skill.name
    
    db.session.delete(skill)
    db.session.commit()
    flash(f'Skill "{name}" deleted successfully!', 'success')
    return redirect(url_for('admin_skills'))

# ======================== MESSAGES MANAGEMENT ========================

@app.route('/admin/messages')
@login_required
def admin_messages():
    page = request.args.get('page', 1, type=int)
    filter_read = request.args.get('filter', 'all')  # all | unread | read
    
    query = ContactMessage.query.order_by(ContactMessage.created_at.desc())
    if filter_read == 'unread':
        query = query.filter_by(is_read=False)
    elif filter_read == 'read':
        query = query.filter_by(is_read=True)
    
    messages = query.paginate(page=page, per_page=20, error_out=False)
    unread_count = ContactMessage.query.filter_by(is_read=False).count()
    return render_template('admin/messages/list.html', messages=messages,
                           unread_count=unread_count, filter_read=filter_read)

@app.route('/admin/messages/<int:message_id>/read', methods=['POST'])
@login_required
def admin_mark_message_read(message_id):
    msg = ContactMessage.query.get_or_404(message_id)
    msg.is_read = True
    db.session.commit()
    flash('Message marked as read.', 'success')
    return redirect(url_for('admin_messages'))

@app.route('/admin/messages/<int:message_id>/unread', methods=['POST'])
@login_required
def admin_mark_message_unread(message_id):
    msg = ContactMessage.query.get_or_404(message_id)
    msg.is_read = False
    db.session.commit()
    flash('Message marked as unread.', 'success')
    return redirect(url_for('admin_messages'))

@app.route('/admin/messages/<int:message_id>/delete', methods=['POST'])
@login_required
def admin_delete_message(message_id):
    msg = ContactMessage.query.get_or_404(message_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.', 'success')
    return redirect(url_for('admin_messages'))

@app.route('/admin/messages/<int:message_id>')
@login_required
def admin_view_message(message_id):
    msg = ContactMessage.query.get_or_404(message_id)
    if not msg.is_read:
        msg.is_read = True
        db.session.commit()
    return render_template('admin/messages/view.html', msg=msg)

# ======================== SETTINGS & BACKUP ========================

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_password':
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            
            if current_user.check_password(old_password):
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password changed successfully!', 'success')
            else:
                flash('Old password is incorrect!', 'danger')
    
    return render_template('admin/settings.html')

@app.route('/admin/backup')
@login_required
def admin_backup():
    """Export database to JSON"""
    backup_data = {
        'projects': [],
        'experiences': [],
        'education': [],
        'skills': [],
        'skill_categories': []
    }
    
    # Export projects
    for p in Project.query.all():
        backup_data['projects'].append({
            'title': p.title,
            'description': p.description,
            'category': p.category,
            'details': p.details,
            'skills': [s.name for s in p.skills],
            'order': p.order
        })
    
    # Export experiences
    for e in Experience.query.all():
        backup_data['experiences'].append({
            'title': e.title,
            'company': e.company,
            'period': e.period,
            'description': e.description,
            'responsibilities': e.get_responsibilities(),
            'skills': [s.name for s in e.skills],
            'order': e.order
        })
    
    # Export education
    for edu in Education.query.all():
        backup_data['education'].append({
            'level': edu.level,
            'field': edu.field,
            'school': edu.school,
            'location': edu.location,
            'period': edu.period,
            'grade': edu.grade,
            'details': edu.get_details(),
            'order': edu.order
        })
    
    # Export skill categories
    for cat in SkillCategory.query.all():
        backup_data['skill_categories'].append({
            'name': cat.name,
            'icon': cat.icon,
            'order': cat.order
        })
    
    # Export skills
    for s in Skill.query.all():
        backup_data['skills'].append({
            'name': s.name,
            'category': s.category.name if s.category else None,
            'order': s.order
        })
    
    response = jsonify(backup_data)
    response.headers['Content-Disposition'] = 'attachment; filename=portfolio_backup.json'
    return response

# ======================== ERROR HANDLERS ========================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# ======================== APP CONTEXT ========================

if __name__ == '__main__':
    debug_mode = True
    host = '127.0.0.1'
    port = 5000

    def open_browser():
        webbrowser.open_new(f'http://{host}:{port}')

    with app.app_context():
        db.create_all()

    # With Flask reloader enabled, only open browser in the reloader child process.
    if not debug_mode or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Timer(1, open_browser).start()

    app.run(host=host, port=port, debug=debug_mode)