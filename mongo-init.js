// MongoDB initialization script for OSPREY
// This script creates the database and user with proper permissions

// Switch to admin database
db = db.getSiblingDB('admin');

// Create application database
db = db.getSiblingDB('osprey_immigration');

// Create application user with read/write permissions
db.createUser({
    user: 'osprey_user',
    pwd: 'osprey_pass_2024',
    roles: [
        {
            role: 'readWrite',
            db: 'osprey_immigration'
        }
    ]
});

// Create initial collections with indexes for better performance
db.createCollection('users');
db.createCollection('documents');
db.createCollection('auto_cases');
db.createCollection('cases');
db.createCollection('applications');
db.createCollection('disclaimer_acceptances');
db.createCollection('notifications');
db.createCollection('workflow_executions');
db.createCollection('analytics_events');

// Create indexes for performance
// Users collection
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "user_id": 1 }, { unique: true });
db.users.createIndex({ "created_at": 1 });

// Documents collection
db.documents.createIndex({ "document_id": 1 }, { unique: true });
db.documents.createIndex({ "user_id": 1 });
db.documents.createIndex({ "document_type": 1 });
db.documents.createIndex({ "upload_date": 1 });
db.documents.createIndex({ "case_id": 1 });

// Auto cases collection
db.auto_cases.createIndex({ "case_id": 1 }, { unique: true });
db.auto_cases.createIndex({ "user_id": 1 });
db.auto_cases.createIndex({ "visa_type": 1 });
db.auto_cases.createIndex({ "created_at": 1 });
db.auto_cases.createIndex({ "status": 1 });

// Cases collection
db.cases.createIndex({ "case_id": 1 }, { unique: true });
db.cases.createIndex({ "user_id": 1 });
db.cases.createIndex({ "created_at": 1 });

// Applications collection
db.applications.createIndex({ "application_id": 1 }, { unique: true });
db.applications.createIndex({ "user_id": 1 });
db.applications.createIndex({ "case_id": 1 });
db.applications.createIndex({ "created_at": 1 });

// Disclaimer acceptances collection
db.disclaimer_acceptances.createIndex({ "case_id": 1 });
db.disclaimer_acceptances.createIndex({ "user_id": 1 });
db.disclaimer_acceptances.createIndex({ "stage": 1 });
db.disclaimer_acceptances.createIndex({ "timestamp": 1 });

// Notifications collection
db.notifications.createIndex({ "notification_id": 1 }, { unique: true });
db.notifications.createIndex({ "user_id": 1 });
db.notifications.createIndex({ "type": 1 });
db.notifications.createIndex({ "created_at": 1 });

// Workflow executions collection
db.workflow_executions.createIndex({ "execution_id": 1 }, { unique: true });
db.workflow_executions.createIndex({ "workflow_type": 1 });
db.workflow_executions.createIndex({ "status": 1 });
db.workflow_executions.createIndex({ "started_at": 1 });

// Analytics events collection
db.analytics_events.createIndex({ "event_id": 1 }, { unique: true });
db.analytics_events.createIndex({ "event_type": 1 });
db.analytics_events.createIndex({ "user_id": 1 });
db.analytics_events.createIndex({ "timestamp": 1 });

print('OSPREY MongoDB initialization completed successfully');
print('Created database: osprey_immigration');
print('Created user: osprey_user');
print('Created collections with performance indexes');