BEGIN;

WITH
inserted_users AS (
  INSERT INTO "user" (
    "pseudo",
    "email",
    "password"
  )
  VALUES
  (
    'User1',
    'test.user@mail.com',
    'azerty123'
  ),
  (
    'User2',
    'user.test@mail.com',
    'abcd789'
  )
  RETURNING id, pseudo
),

inserted_games AS (
  INSERT INTO "game" (
    "name",
    "difficulty",
    "content",
    "creator_id"
  )
  VALUES
  (
    'A',
    1,
    '{
      {0, 0, 1, 0, 0},
      {0, 1, 1, 1, 0},
      {0, 1, 0, 1, 0},
      {0, 1, 0, 1, 0},
      {1, 1, 1, 1, 1},
      {1, 1, 0, 1, 1},
      {1, 0, 0, 0, 1}
    }',
    (SELECT id FROM inserted_users WHERE pseudo = 'User1')
  ),
  (
    'B',
    1,
    '{
      {1, 1, 1, 1, 0},
      {1, 0, 0, 0, 1},
      {1, 0, 0, 0, 1},
      {1, 1, 1, 1, 0},
      {1, 0, 0, 0, 1},
      {1, 0, 0, 0, 1},
      {1, 1, 1, 1, 0}
    }',
    null
  )
  RETURNING id, "name"
)

INSERT INTO "gamestate" (
  "user_id",
  "game_id",
  "is_completed",
  "current_content"
)
VALUES
(
  (SELECT id FROM inserted_users WHERE pseudo = 'User2'),
  (SELECT id FROM inserted_games WHERE "name" = 'A'),
  TRUE,
  '{
    {0, 0, 1, 0, 0},
    {0, 1, 1, 1, 0},
    {0, 1, 0, 1, 0},
    {0, 1, 0, 1, 0},
    {1, 1, 1, 1, 1},
    {1, 1, 0, 1, 1},
    {1, 0, 0, 0, 1}
  }'
);

COMMIT;