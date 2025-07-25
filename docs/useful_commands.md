# Useful Postgres Commands for Grateful

## Grant All Privileges to a User on the public Schema

If you encounter `permission denied for schema public` errors, you may need to grant all privileges to your database user (e.g., `grateful`).

**Command:**

```
PGPASSWORD=iamgreatful psql -U postgres -h localhost -d grateful -c "GRANT ALL ON SCHEMA public TO grateful; GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO grateful; GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO grateful; GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO grateful;"
```

- Replace `grateful` with your actual database user if different.
- This command must be run as a superuser (e.g., `postgres`).
- It is safe to re-run if you change privileges or add new tables. 