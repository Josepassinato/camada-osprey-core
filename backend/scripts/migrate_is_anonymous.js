// MongoDB migration script to add is_anonymous field to auto_cases
// Run with: mongosh osprey_db < backend/scripts/migrate_is_anonymous.js

print("Starting migration: Adding is_anonymous field to auto_cases");

// Count total cases
const totalCases = db.auto_cases.countDocuments({});
print(`Found ${totalCases} total cases`);

// Update cases with user_id (authenticated users)
const resultAuthenticated = db.auto_cases.updateMany(
  { user_id: { $ne: null }, is_anonymous: { $exists: false } },
  {
    $set: {
      is_anonymous: false,
      updated_at: new Date()
    }
  }
);
print(`✅ Updated ${resultAuthenticated.modifiedCount} authenticated user cases (is_anonymous=false)`);

// Update cases without user_id (anonymous users)
const resultAnonymous = db.auto_cases.updateMany(
  { user_id: null, is_anonymous: { $exists: false } },
  {
    $set: {
      is_anonymous: true,
      updated_at: new Date()
    }
  }
);
print(`✅ Updated ${resultAnonymous.modifiedCount} anonymous cases (is_anonymous=true)`);

// Verify migration
const authenticatedCount = db.auto_cases.countDocuments({ is_anonymous: false });
const anonymousCount = db.auto_cases.countDocuments({ is_anonymous: true });
const missingFieldCount = db.auto_cases.countDocuments({ is_anonymous: { $exists: false } });

print("\n📊 Migration Summary:");
print(`  - Authenticated cases (is_anonymous=false): ${authenticatedCount}`);
print(`  - Anonymous cases (is_anonymous=true): ${anonymousCount}`);
print(`  - Cases still missing field: ${missingFieldCount}`);

if (missingFieldCount > 0) {
  print(`⚠️  ${missingFieldCount} cases still missing is_anonymous field!`);
} else {
  print("✅ Migration completed successfully! All cases have is_anonymous field.");
}
