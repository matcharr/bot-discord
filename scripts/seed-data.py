#!/usr/bin/env python3
"""
Seed script to populate the database with test data.
Useful for development and testing with realistic data.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.development')

# Add project to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'project'))

from database.services import WarningService
from database.connection import init_database

# Test data configuration
TEST_GUILDS = [
    "123456789012345678",  # Test Server 1
    "987654321098765432",  # Test Server 2
]

TEST_USERS = [
    "111111111111111111",  # Alice
    "222222222222222222",  # Bob
    "333333333333333333",  # Charlie
    "444444444444444444",  # Diana
    "555555555555555555",  # Eve
]

TEST_MODERATORS = [
    "777777777777777777",  # Mod1
    "888888888888888888",  # Mod2
    "999999999999999999",  # Admin
]

SAMPLE_REASONS = [
    "Spam in general chat",
    "Inappropriate language",
    "Off-topic discussion in help channel",
    "Harassment of other members",
    "Posting NSFW content",
    "Advertising without permission",
    "Trolling behavior",
    "Violation of server rules",
    "Excessive caps lock usage",
    "Disrespectful behavior towards staff"
]


def create_sample_warnings():
    """Create sample warnings for testing."""
    print("🌱 Creating sample warnings...")
    
    service = WarningService()
    warnings_created = 0
    
    try:
        # Create warnings for different scenarios
        for guild_id in TEST_GUILDS:
            for i, user_id in enumerate(TEST_USERS):
                # Some users have more warnings than others
                warning_count = (i % 3) + 1  # 1-3 warnings per user
                
                for j in range(warning_count):
                    moderator_id = TEST_MODERATORS[j % len(TEST_MODERATORS)]
                    reason = SAMPLE_REASONS[j % len(SAMPLE_REASONS)]
                    
                    warning = service.add_warning(
                        guild_id=guild_id,
                        user_id=user_id,
                        moderator_id=moderator_id,
                        reason=reason
                    )
                    warnings_created += 1
                    
                    if warnings_created % 5 == 0:
                        print(f"  Created {warnings_created} warnings...")
        
        # Create some deleted warnings for testing soft delete
        print("🗑️  Creating some deleted warnings...")
        deleted_count = 0
        
        # Get some warnings to delete
        for guild_id in TEST_GUILDS[:1]:  # Only first guild
            for user_id in TEST_USERS[:2]:  # Only first 2 users
                warnings = service.get_user_warnings(guild_id, user_id)
                if warnings:
                    # Delete the first warning
                    service.delete_warning(warnings[0].id)
                    deleted_count += 1
        
        print(f"✅ Created {warnings_created} warnings ({deleted_count} deleted)")
        
    except Exception as e:
        print(f"❌ Error creating warnings: {e}")
        return False
    finally:
        service.close()
    
    return True


def create_sample_gdpr_requests():
    """Create sample GDPR requests for testing."""
    print("📋 Creating sample GDPR requests...")
    
    service = WarningService()
    requests_created = 0
    
    try:
        # Create some export requests
        for user_id in TEST_USERS[:2]:
            service.export_user_data(user_id)
            requests_created += 1
        
        print(f"✅ Created {requests_created} GDPR requests")
        
    except Exception as e:
        print(f"❌ Error creating GDPR requests: {e}")
        return False
    finally:
        service.close()
    
    return True


def show_statistics():
    """Show database statistics after seeding."""
    print("\n📊 Database Statistics:")
    print("=" * 50)
    
    service = WarningService()
    
    try:
        for guild_id in TEST_GUILDS:
            print(f"\n🏰 Guild {guild_id[-6:]}...")  # Show last 6 digits
            
            total_warnings = 0
            active_warnings = 0
            
            for user_id in TEST_USERS:
                user_warnings = service.get_user_warnings(guild_id, user_id, include_deleted=True)
                active_user_warnings = service.get_user_warnings(guild_id, user_id, include_deleted=False)
                
                if user_warnings:
                    total_warnings += len(user_warnings)
                    active_warnings += len(active_user_warnings)
                    deleted_count = len(user_warnings) - len(active_user_warnings)
                    
                    print(f"  👤 User {user_id[-6:]}: {len(active_user_warnings)} active, {deleted_count} deleted")
            
            print(f"  📈 Total: {active_warnings} active, {total_warnings - active_warnings} deleted")
        
    except Exception as e:
        print(f"❌ Error showing statistics: {e}")
    finally:
        service.close()


def main():
    """Main seeding function."""
    print("🌱 Database Seeding Script")
    print("=" * 50)
    
    # Ensure database is initialized
    print("🔧 Initializing database...")
    init_database()
    
    # Create sample data
    success = True
    success &= create_sample_warnings()
    success &= create_sample_gdpr_requests()
    
    if success:
        show_statistics()
        print("\n🎉 Database seeding completed successfully!")
        print("\nYou can now:")
        print("  - Run tests: python -m pytest tests/database/ -v")
        print("  - Connect to DB: ./scripts/db-manage.sh psql")
        print("  - View data: SELECT * FROM warnings LIMIT 5;")
    else:
        print("\n❌ Database seeding failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()