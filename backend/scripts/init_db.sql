-- ════════════════════════════════════════════════════════════
--  Nasoma — Initialisation Postgres (Docker entrypoint)
--  Exécuté UNE SEULE FOIS au premier démarrage du container.
--  Les migrations Alembic prennent ensuite le relais.
-- ════════════════════════════════════════════════════════════

-- Extension pour les UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extension pour les recherches trigram (fuzzy match concepts)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Extension pour le chiffrement (PII)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
