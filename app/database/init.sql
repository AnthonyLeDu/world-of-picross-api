BEGIN;

DROP TABLE IF EXISTS "game", "user", "trial";

CREATE TABLE "user" (
  "id" SERIAL PRIMARY KEY NOT NULL UNIQUE,
  "pseudo" VARCHAR(32) NOT NULL UNIQUE,
  "email" VARCHAR(254) NOT NULL UNIQUE CHECK (
    email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
  ),
  "password" VARCHAR(256) NOT NULL,
  "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "updated_at" TIMESTAMPTZ
);

CREATE TABLE "game" (
  "id" SERIAL PRIMARY KEY NOT NULL UNIQUE,
  "name" VARCHAR(64) NOT NULL,
  "difficulty" INT NOT NULL,
  "content" BOOLEAN[][],
	"created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  "updated_at" TIMESTAMPTZ,
  "creator_id" INT REFERENCES "user"("id")
);


CREATE TABLE "trial" (
  "id" SERIAL PRIMARY KEY NOT NULL UNIQUE,
  "user_id" INT REFERENCES "user"("id"),
  "game_id" INT REFERENCES "game"("id"),
  "completed" BOOLEAN,
  "current_content" BOOLEAN[][] NOT NULL
);

COMMIT;