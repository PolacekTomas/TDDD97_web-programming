create TABLE users (
  email TEXT PRIMARY KEY,
  password TEXT,
  firstname TEXT,
  familyname TEXT,
  gender TEXT,
  city TEXT,
  country TEXT,
  picture TEXT DEFAULT NULL,
  profile_views INTEGER DEFAULT 0
);

create TABLE tokens (
  token TEXT PRIMARY KEY,
  email TEXT
);

create TABLE messages (
  id INTEGER PRIMARY KEY,
  email_from TEXT,
  email_to TEXT,
  msg_type TEXT,
  message TEXT
);
