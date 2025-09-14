-- Minimal schema; expand as needed.
CREATE TABLE IF NOT EXISTS articles (
  id SERIAL PRIMARY KEY,
  url TEXT UNIQUE,
  title TEXT,
  summary TEXT,
  published_at TIMESTAMPTZ,
  source TEXT,
  metadata JSONB,
  is_clickbait BOOLEAN,
  is_ragebait BOOLEAN,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS claims (
  id SERIAL PRIMARY KEY,
  article_id INT REFERENCES articles(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS claim_reviews (
  id SERIAL PRIMARY KEY,
  claim_id INT REFERENCES claims(id) ON DELETE CASCADE,
  verdict TEXT CHECK (verdict IN ('true','false','unverified')),
  evidence JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);
