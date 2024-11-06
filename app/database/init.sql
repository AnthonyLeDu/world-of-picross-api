BEGIN;

DROP TABLE IF EXISTS "game", "user", "gamestate";

CREATE TABLE "user" (
  "id" SERIAL PRIMARY KEY NOT NULL UNIQUE,
  "pseudo" VARCHAR(32) NOT NULL UNIQUE,
  "username" VARCHAR(254) NOT NULL UNIQUE CHECK (
    username ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
  ),
  "password" VARCHAR(256) NOT NULL,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "updated_at" TIMESTAMPTZ
);

CREATE TABLE "game" (
  "id" SERIAL PRIMARY KEY NOT NULL UNIQUE,
  "name" VARCHAR(64) NOT NULL,
  "difficulty" INT NOT NULL,
  "content" JSONB,
  "clues" JSONB,
	"created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "updated_at" TIMESTAMPTZ,
  "creator_id" INT REFERENCES "user"("id")
);


CREATE TABLE "gamestate" (
  "id" SERIAL PRIMARY KEY NOT NULL UNIQUE,
  "user_id" INT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
  "game_id" INT NOT NULL REFERENCES "game"("id") ON DELETE CASCADE,
  "is_completed" BOOLEAN NOT NULL DEFAULT FALSE,
  "current_content" JSONB
);

COMMIT;