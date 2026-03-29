"""
Database initialization script - Populate initial data from existing portfolio
Run this once to migrate from hardcoded data to database
"""
from app import app, db
from database import User, SkillCategory, Skill, Project, Experience, Education
import json

def init_db():
    """Initialize database with existing portfolio data"""
    with app.app_context():
        # Drop all tables and recreate
        print("Creating database tables...")
        db.create_all()

        # Create admin user
        print("Creating admin user...")
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='rehman.designworks@gmail.com'
            )
            admin.set_password('admin123')  # Change this!
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created (username: admin, password: admin123 - PLEASE CHANGE!)")

        # Create skill categories
        print("Creating skill categories...")
        categories_data = [
            {"name": "Software & Programming", "icon": "fa-code", "order": 1},
            {"name": "Technical & Engineering", "icon": "fa-microchip", "order": 2},
            {"name": "Hardware & Practical", "icon": "fa-tools", "order": 3},
            {"name": "Soft Skills", "icon": "fa-users", "order": 4}
        ]

        categories = {}
        for cat_data in categories_data:
            cat = SkillCategory.query.filter_by(name=cat_data['name']).first()
            if not cat:
                cat = SkillCategory(
                    name=cat_data['name'],
                    icon=cat_data['icon'],
                    order=cat_data['order']
                )
                db.session.add(cat)
            categories[cat_data['name']] = cat

        db.session.commit()
        print("✓ Skill categories created")

        # Create skills
        print("Creating skills...")
        skills_data = {
            "Software & Programming": [
                "Python", "JavaScript", "HTML/CSS", "Flask", "Arduino", "Embedded C",
                "IoT Development", "Database Design"
            ],
            "Technical & Engineering": [
                "Circuit Analysis", "PCB Design", "Electrical Wiring", "Motor Control",
                "Power Systems", "Signal Processing"
            ],
            "Hardware & Practical": [
                "Soldering", "Component Testing", "Equipment Operation", "Assembly",
                "Troubleshooting", "Installation"
            ],
            "Soft Skills": [
                "Project Management", "Team Collaboration", "Problem Solving",
                "Customer Service", "Communication", "Time Management"
            ]
        }

        all_skills = {}
        skill_counter = 1
        for category_name, skill_names in skills_data.items():
            for skill_name in skill_names:
                if not Skill.query.filter_by(name=skill_name).first():
                    skill = Skill(
                        name=skill_name,
                        category_id=categories[category_name].id,
                        order=skill_counter
                    )
                    db.session.add(skill)
                    skill_counter += 1
                all_skills[skill_name] = skill

        db.session.commit()
        print(f"✓ Created {len(all_skills)} skills")

        # Create projects
        print("Creating projects...")
        projects_data = [
            {
                "title": "IR-Based Remote Control",
                "category": "Hardware",
                "description": "Wireless control system using infrared technology for smart home applications",
                "details": "Designed and implemented a complete IR remote control system with receiver circuits and microcontroller interface",
                "skills": ["Arduino", "Embedded C", "Circuit Analysis", "Soldering"]
            },
            {
                "title": "Solar Panel System",
                "category": "Hardware",
                "description": "Renewable energy system with voltage regulation and load management",
                "details": "Created a complete solar power system including panel mounting, charge controller, and battery management",
                "skills": ["Power Systems", "PCB Design", "Electrical Wiring", "Circuit Analysis"]
            },
            {
                "title": "Street Light System",
                "category": "Hardware",
                "description": "IoT-enabled street lighting with motion detection and automatic scheduling",
                "details": "Developed smart street light controller with motion sensors, IoT connectivity, and energy monitoring",
                "skills": ["IoT Development", "Arduino", "Python", "Signal Processing"]
            },
            {
                "title": "Audio Amplification System",
                "category": "Hardware",
                "description": "Multi-channel audio amplifier with frequency response tuning",
                "details": "Designed amplifier circuits with component selection, PCB layout, and testing procedures",
                "skills": ["Circuit Analysis", "PCB Design", "Signal Processing", "Component Testing"]
            }
        ]

        for idx, proj_data in enumerate(projects_data, 1):
            if not Project.query.filter_by(title=proj_data['title']).first():
                skills = [all_skills[skill_name] for skill_name in proj_data['skills'] if skill_name in all_skills]
                project = Project(
                    title=proj_data['title'],
                    category=proj_data['category'],
                    description=proj_data['description'],
                    details=proj_data['details'],
                    skills=skills,
                    order=idx
                )
                db.session.add(project)

        db.session.commit()
        print("✓ Created 4 projects")

        # Create experiences
        print("Creating experiences...")
        experiences_data = [
            {
                "title": "Open Contract Electrician",
                "company": "Self-Employed",
                "period": "Jan 2024 - Present",
                "description": "Providing professional electrical services including wiring, repairs, and installations for residential and commercial clients",
                "responsibilities": [
                    "Execute residential and commercial electrical wiring projects",
                    "Test and troubleshoot circuit breakers and protection systems",
                    "Install and configure lighting fixtures and systems",
                    "Connect and test three-phase motors and equipment",
                    "Maintain electrical control panel boards",
                    "Repair and maintain household electrical appliances"
                ],
                "skills": ["Electrical Wiring", "Circuit Analysis", "Motor Control", "Equipment Operation", "Problem Solving"]
            },
            {
                "title": "Biryani Cook",
                "company": "Khan Biryani House",
                "period": "Jun 2023 - Dec 2023",
                "description": "Prepared authentic biryani and related Pakistani cuisine for restaurant operations",
                "responsibilities": [
                    "Marinate meat using traditional spice blends",
                    "Prepare and measure spice mixtures for consistent quality",
                    "Layer rice and meat using proper cooking techniques",
                    "Maintain strict food hygiene standards",
                    "Ensure consistent quality across all servings"
                ],
                "skills": ["Time Management", "Customer Service", "Quality Control", "Team Collaboration"]
            },
            {
                "title": "Delivery Executive",
                "company": "Tariq Gas Centre",
                "period": "Mar 2023 - May 2023",
                "description": "Managed gas cylinder delivery operations and customer interactions",
                "responsibilities": [
                    "Deliver gas cylinders to residential and commercial locations",
                    "Verify cylinder safety and quality before delivery",
                    "Provide customer service and handle inquiries",
                    "Optimize delivery routes for efficiency"
                ],
                "skills": ["Customer Service", "Route Optimization", "Safety Procedures", "Communication"]
            },
            {
                "title": "Shop Assistant",
                "company": "A1 Sports",
                "period": "Dec 2022 - Feb 2023",
                "description": "Supported retail operations and customer service for sports equipment store",
                "responsibilities": [
                    "Provide expert product recommendations to customers",
                    "Maintain organized stock and inventory systems",
                    "Process sales transactions and handle payments",
                    "Keep store clean and well-organized",
                    "Repair minor equipment issues"
                ],
                "skills": ["Customer Service", "Sales Management", "Communication", "Problem Solving"]
            }
        ]

        for idx, exp_data in enumerate(experiences_data, 1):
            if not Experience.query.filter_by(title=exp_data['title'], company=exp_data['company']).first():
                skills = [all_skills[skill_name] for skill_name in exp_data['skills'] if skill_name in all_skills]
                experience = Experience(
                    title=exp_data['title'],
                    company=exp_data['company'],
                    period=exp_data['period'],
                    description=exp_data['description'],
                    skills=skills,
                    order=idx
                )
                experience.set_responsibilities(exp_data['responsibilities'])
                db.session.add(experience)

        db.session.commit()
        print("✓ Created 4 experiences")

        # Create education
        print("Creating education...")
        education_data = [
            {
                "level": "BS (Electrical Engineering)",
                "field": "Electrical Engineering",
                "school": "COMSATS University",
                "location": "Pakistan",
                "period": "2021 - Present",
                "grade": "3.5 GPA",
                "details": {
                    "credits": "60 / 120 completed",
                    "eqf_level": "EQF Level 6",
                    "subjects": [
                        "Circuit Analysis & Design",
                        "Electromagnetic Theory",
                        "Power Systems",
                        "Digital Electronics",
                        "Microcontroller Programming",
                        "IoT & Embedded Systems"
                    ]
                }
            },
            {
                "level": "Intermediate",
                "field": "Pre-Engineering",
                "school": "Government College",
                "location": "Pakistan",
                "period": "2019 - 2021",
                "grade": "85%",
                "details": {
                    "subjects": [
                        "Physics",
                        "Chemistry",
                        "Mathematics",
                        "English"
                    ]
                }
            },
            {
                "level": "Matriculation",
                "field": "Science",
                "school": "Government School",
                "location": "Pakistan",
                "period": "2017 - 2019",
                "grade": "82%",
                "details": {
                    "subjects": [
                        "Physics",
                        "Chemistry",
                        "Biology",
                        "Mathematics",
                        "English",
                        "Urdu"
                    ]
                }
            }
        ]

        for idx, edu_data in enumerate(education_data, 1):
            if not Education.query.filter_by(level=edu_data['level']).first():
                education = Education(
                    level=edu_data['level'],
                    field=edu_data['field'],
                    school=edu_data['school'],
                    location=edu_data['location'],
                    period=edu_data['period'],
                    grade=edu_data['grade'],
                    order=idx
                )
                education.set_details(edu_data['details'])
                db.session.add(education)

        db.session.commit()
        print("✓ Created 3 education entries")

        print("\n✅ Database initialized successfully!")
        print("\n⚠️  IMPORTANT: Change the admin password immediately!")
        print("   Go to http://localhost:5000/admin/settings to update password.")

if __name__ == '__main__':
    init_db()
