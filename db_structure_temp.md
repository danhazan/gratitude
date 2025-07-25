# Temporary Database Structure Mapping

## Tables and Fields

### users
- id (String, PK, UUID)
- email (String, unique, indexed, not null)
- username (String, unique, indexed, not null)
- full_name (String, nullable)
- bio (Text, nullable)
- avatar_url (String, nullable)
- is_verified (Boolean, default False)
- is_active (Boolean, default True)
- created_at (DateTime, default now)
- updated_at (DateTime, on update)
- hashed_password (String, not null)
- location (String, nullable)
- birthday (String, nullable)
- gender (String, nullable)
- website (String, nullable)
- interests (String, nullable)
- occupation (String, nullable)

### posts
- id (String, PK, UUID)
- author_id (String, FK to users.id, not null)
- title (String, nullable)
- content (Text, not null)
- post_type (Enum, default daily, not null)
- image_url (String, nullable)
- location (String, nullable)
- is_public (Boolean, default True)
- created_at (DateTime, default now)
- updated_at (DateTime, on update)

### likes
- id (String, PK, UUID)
- user_id (String, FK to users.id, not null)
- post_id (String, FK to posts.id, not null)
- created_at (DateTime, default now)
- UniqueConstraint(user_id, post_id)

### comments
- id (String, PK, UUID)
- author_id (String, FK to users.id, not null)
- post_id (String, FK to posts.id, not null)
- parent_id (String, FK to comments.id, nullable)
- content (Text, not null)
- created_at (DateTime, default now)
- updated_at (DateTime, on update)

### follows
- id (String, PK, UUID)
- follower_id (String, FK to users.id, not null)
- followed_id (String, FK to users.id, not null)
- created_at (DateTime, default now)
- UniqueConstraint(follower_id, followed_id)

### notification
- id (String, PK, UUID)
- user_id (String, FK to users.id, not null, indexed)
- type (String, not null)
- priority (String, not null, default normal)
- title (String, not null)
- message (Text, not null)
- data (JSON, nullable)
- channel (String, not null, default in_app)
- read_at (DateTime, nullable)
- created_at (DateTime, default utcnow)

---

This document is a temporary mapping of the current ORM-based database structure before purging the database and removing migrations. 