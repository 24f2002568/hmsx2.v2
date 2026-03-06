from backend import create_app, db
from backend.models import User, Department, Doctor

app = create_app()

def seed_database():
    """Seed initial data: admin user + departments."""
    with app.app_context():
        db.create_all()

        # Create admin if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@hospital.com', role='admin')
            admin.set_password('admin@123')
            db.session.add(admin)
            print("✅ Admin user created: username=admin, password=admin@123")

        # Seed departments
        departments = [
            ('Cardiology', 'Heart and cardiovascular system specialists'),
            ('Neurology', 'Brain and nervous system specialists'),
            ('Orthopedics', 'Bone, joint, and muscle specialists'),
            ('Pediatrics', 'Child healthcare specialists'),
            ('Dermatology', 'Skin, hair, and nail specialists'),
            ('Oncology', 'Cancer diagnosis and treatment'),
            ('Gynecology', 'Women\'s reproductive health'),
            ('Ophthalmology', 'Eye care and vision specialists'),
            ('ENT', 'Ear, Nose, and Throat specialists'),
            ('General Medicine', 'General health and primary care'),
        ]
        for name, desc in departments:
            if not Department.query.filter_by(name=name).first():
                dept = Department(name=name, description=desc)
                db.session.add(dept)
                print(f"✅ Department created: {name}")

        db.session.commit()
        print("\n🏥 HMS Database initialized successfully!")
        print("   Admin login: username=admin | password=admin@123")

if __name__ == '__main__':
    seed_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
