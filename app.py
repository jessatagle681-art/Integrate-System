from sqlalchemy import text

with app.app_context():
    db.create_all()

    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(events)"))
            cols = [row[1] for row in result]

            if 'image_url' not in cols:
                conn.execute(text("ALTER TABLE events ADD COLUMN image_url VARCHAR(255)"))

            if 'event_time' not in cols:
                conn.execute(text("ALTER TABLE events ADD COLUMN event_time TIME"))

    except Exception as e:
        print("DB migration skipped:", e)
