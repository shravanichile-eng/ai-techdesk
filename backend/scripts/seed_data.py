"""Database seeding script"""

import sys
import logging
from datetime import datetime
from sqlalchemy.orm import Session

sys.path.insert(0, '/app')

from app.database.base import SessionLocal, engine, Base
from app.models.user import User, Role, Department, UserStatus
from app.models.ticket import Category, SubCategory
from app.models.team import Team, TeamMember, TeamCategory
from app.models.sla import SLAPolicy
from app.core.security import hash_password

logger = logging.getLogger(__name__)


def seed_database():
    """Seed database with initial data"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if already seeded
        if db.query(Role).first():
            print("Database already seeded. Skipping.")
            return
        
        print("\n=== Seeding Database ===")
        
        # 1. Create Roles
        print("\n1. Creating roles...")
        roles = [
            Role(name="ADMIN", description="Administrator with full access"),
            Role(name="MANAGER", description="Manager can view reports and escalations"),
            Role(name="AGENT", description="Support agent handling tickets"),
            Role(name="USER", description="Regular user creating tickets"),
        ]
        db.add_all(roles)
        db.commit()
        print(f"   Created {len(roles)} roles")
        
        # 2. Create Departments
        print("\n2. Creating departments...")
        departments = [
            Department(name="IT Support", description="Information Technology", code="IT"),
            Department(name="Human Resources", description="Human Resources", code="HR"),
            Department(name="Finance", description="Finance Department", code="FIN"),
            Department(name="Operations", description="Operations", code="OPS"),
        ]
        db.add_all(departments)
        db.commit()
        print(f"   Created {len(departments)} departments")
        
        # 3. Create Categories
        print("\n3. Creating ticket categories...")
        categories = [
            Category(name="Hardware", description="Hardware issues", icon="monitor"),
            Category(name="Software", description="Software issues", icon="code"),
            Category(name="Network", description="Network connectivity issues", icon="wifi"),
            Category(name="Account & Access", description="User account and access issues", icon="lock"),
            Category(name="Security", description="Security concerns", icon="shield"),
            Category(name="Email", description="Email and communication issues", icon="mail"),
            Category(name="HR", description="Human Resources", icon="users"),
            Category(name="Finance", description="Finance and billing", icon="dollar-sign"),
            Category(name="Facilities", description="Facilities and office", icon="building"),
            Category(name="Other", description="Other issues", icon="help-circle"),
        ]
        db.add_all(categories)
        db.commit()
        print(f"   Created {len(categories)} categories")
        
        # 4. Create Subcategories
        print("\n4. Creating subcategories...")
        category_map = {cat.name: cat for cat in db.query(Category).all()}
        
        subcategories = [
            # Hardware
            SubCategory(category_id=category_map["Hardware"].id, name="Laptop", description="Laptop issues"),
            SubCategory(category_id=category_map["Hardware"].id, name="Desktop", description="Desktop computer issues"),
            SubCategory(category_id=category_map["Hardware"].id, name="Printer", description="Printer issues"),
            SubCategory(category_id=category_map["Hardware"].id, name="Monitor", description="Monitor issues"),
            SubCategory(category_id=category_map["Hardware"].id, name="Keyboard/Mouse", description="Keyboard and mouse issues"),
            # Network
            SubCategory(category_id=category_map["Network"].id, name="VPN", description="VPN connectivity"),
            SubCategory(category_id=category_map["Network"].id, name="WiFi", description="WiFi connectivity"),
            SubCategory(category_id=category_map["Network"].id, name="DNS", description="DNS resolution issues"),
            SubCategory(category_id=category_map["Network"].id, name="Internet", description="Internet connectivity"),
            # Account & Access
            SubCategory(category_id=category_map["Account & Access"].id, name="Password Reset", description="Password reset request"),
            SubCategory(category_id=category_map["Account & Access"].id, name="Account Locked", description="Locked account"),
            SubCategory(category_id=category_map["Account & Access"].id, name="Access Request", description="Request access to resource"),
            SubCategory(category_id=category_map["Account & Access"].id, name="MFA Setup", description="Multi-factor authentication setup"),
            # Email
            SubCategory(category_id=category_map["Email"].id, name="Cannot Send", description="Unable to send emails"),
            SubCategory(category_id=category_map["Email"].id, name="Cannot Receive", description="Unable to receive emails"),
            SubCategory(category_id=category_map["Email"].id, name="Signature Issue", description="Email signature problems"),
            # Software
            SubCategory(category_id=category_map["Software"].id, name="Installation", description="Software installation issues"),
            SubCategory(category_id=category_map["Software"].id, name="Licensing", description="License activation issues"),
            SubCategory(category_id=category_map["Software"].id, name="Performance", description="Software performance issues"),
        ]
        db.add_all(subcategories)
        db.commit()
        print(f"   Created {len(subcategories)} subcategories")
        
        # 5. Create SLA Policies
        print("\n5. Creating SLA policies...")
        sla_policies = [
            SLAPolicy(
                name="Critical SLA",
                description="SLA for critical priority tickets",
                response_time_minutes=15,
                resolution_time_minutes=120,
                applicable_priority="CRITICAL",
                warning_threshold_percent=80,
                is_active=True
            ),
            SLAPolicy(
                name="High SLA",
                description="SLA for high priority tickets",
                response_time_minutes=30,
                resolution_time_minutes=240,
                applicable_priority="HIGH",
                warning_threshold_percent=80,
                is_active=True
            ),
            SLAPolicy(
                name="Medium SLA",
                description="SLA for medium priority tickets",
                response_time_minutes=120,
                resolution_time_minutes=480,
                applicable_priority="MEDIUM",
                warning_threshold_percent=80,
                is_active=True
            ),
            SLAPolicy(
                name="Low SLA",
                description="SLA for low priority tickets",
                response_time_minutes=480,
                resolution_time_minutes=1440,
                applicable_priority="LOW",
                warning_threshold_percent=80,
                is_active=True
            ),
        ]
        db.add_all(sla_policies)
        db.commit()
        print(f"   Created {len(sla_policies)} SLA policies")
        
        # 6. Create Teams
        print("\n6. Creating teams...")
        department_map = {dept.name: dept for dept in db.query(Department).all()}
        default_sla = db.query(SLAPolicy).filter(SLAPolicy.name == "High SLA").first()
        
        teams = [
            Team(
                name="IT Support",
                description="General IT support team",
                department_id=department_map["IT Support"].id,
                default_sla_policy_id=default_sla.id if default_sla else None,
                is_active=True
            ),
            Team(
                name="Network Team",
                description="Network and connectivity support",
                department_id=department_map["IT Support"].id,
                default_sla_policy_id=default_sla.id if default_sla else None,
                is_active=True
            ),
            Team(
                name="Hardware Team",
                description="Hardware and device support",
                department_id=department_map["IT Support"].id,
                default_sla_policy_id=default_sla.id if default_sla else None,
                is_active=True
            ),
            Team(
                name="Security Team",
                description="Security and access control",
                department_id=department_map["IT Support"].id,
                default_sla_policy_id=default_sla.id if default_sla else None,
                is_active=True
            ),
            Team(
                name="HR Support",
                description="Human Resources support",
                department_id=department_map["Human Resources"].id,
                is_active=True
            ),
        ]
        db.add_all(teams)
        db.commit()
        print(f"   Created {len(teams)} teams")
        
        # 7. Create Users
        print("\n7. Creating users...")
        role_map = {role.name: role for role in db.query(Role).all()}
        
        users = [
            User(
                email="admin@techdesk.local",
                full_name="Admin User",
                password_hash=hash_password("Admin@12345"),
                role_id=role_map["ADMIN"].id,
                department_id=department_map["IT Support"].id,
                status=UserStatus.ACTIVE.value,
                is_active=True,
                phone="+1-555-0001"
            ),
            User(
                email="manager@techdesk.local",
                full_name="Manager User",
                password_hash=hash_password("Manager@12345"),
                role_id=role_map["MANAGER"].id,
                department_id=department_map["IT Support"].id,
                status=UserStatus.ACTIVE.value,
                is_active=True,
                phone="+1-555-0002"
            ),
            User(
                email="agent@techdesk.local",
                full_name="Agent User",
                password_hash=hash_password("Agent@12345"),
                role_id=role_map["AGENT"].id,
                department_id=department_map["IT Support"].id,
                status=UserStatus.ACTIVE.value,
                is_active=True,
                phone="+1-555-0003"
            ),
            User(
                email="user@techdesk.local",
                full_name="Regular User",
                password_hash=hash_password("User@12345"),
                role_id=role_map["USER"].id,
                department_id=department_map["Operations"].id,
                status=UserStatus.ACTIVE.value,
                is_active=True,
                phone="+1-555-0004"
            ),
        ]
        db.add_all(users)
        db.commit()
        print(f"   Created {len(users)} users")
        
        # 8. Add team members
        print("\n8. Adding team members...")
        user_map = {user.email: user for user in db.query(User).all()}
        team_map = {team.name: team for team in db.query(Team).all()}
        
        team_members = [
            TeamMember(
                team_id=team_map["IT Support"].id,
                user_id=user_map["agent@techdesk.local"].id,
                role="MEMBER",
                is_active=True
            ),
            TeamMember(
                team_id=team_map["Network Team"].id,
                user_id=user_map["agent@techdesk.local"].id,
                role="MEMBER",
                is_active=True
            ),
        ]
        db.add_all(team_members)
        db.commit()
        print(f"   Added {len(team_members)} team members")
        
        print("\n=== Database Seeding Complete ===")
        print("\nDefault Credentials:")
        print("  Admin:    admin@techdesk.local / Admin@12345")
        print("  Manager:  manager@techdesk.local / Manager@12345")
        print("  Agent:    agent@techdesk.local / Agent@12345")
        print("  User:     user@techdesk.local / User@12345")
        print()
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
