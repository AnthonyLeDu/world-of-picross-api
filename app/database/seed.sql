BEGIN;

WITH
inserted_users AS (
  INSERT INTO "user" (
    "pseudo",
    "username",
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
    '[
      [null, null, null, [255,0,0,1.0], null],
      [null, [0,0,0,1.0], [255,0,0,1.0], [0,0,0,1.0], null],
      [null, [0,0,0,1.0], null, [0,0,0,1.0], null],
      [null, [0,0,0,1.0], null, [0,0,0,1.0], null],
      [[0,0,0,1.0], [0,0,0,1.0], [0,0,0,1.0], [0,0,0,1.0], [0,0,0,1.0]],
      [[200,150,200,1.0], [0,0,0,1.0], null, [0,0,0,1.0], [0,0,0,1.0]],
      [[0,0,0,1.0], null, null, null, [0,0,0,1.0]]
    ]',
    (SELECT id FROM inserted_users WHERE pseudo = 'User1')
  ),
  (
    'B',
    1,
    '[
      [[255,0,0,1.0], [255,0,0,1.0], [255,0,0,1.0], [255,0,0,1.0], null],
      [[0,0,0,1.0], null, null, null, [0,0,0,1.0]],
      [[0,0,0,1.0], null, null, null, [0,0,0,1.0]],
      [[0,0,0,1.0], [0,0,0,1.0], [0,0,0,1.0], [0,0,0,1.0], null],
      [[0,0,0,1.0], null, null, null, [0,0,0,1.0]],
      [[0,0,0,1.0], null, null, null, [0,0,0,1.0]],
      [[255,0,0,1.0], [255,0,0,1.0], [255,0,0,1.0], [255,0,0,1.0], null]
    ]',
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
    '[
      [null, null, null, null, null],
      [[0,0,0,1.0], null, null, null, [0,0,0,1.0]],
      [[0,0,0,1.0], null, null, null, [0,0,0,1.0]],
      [[0,0,0,1.0], [0,0,0,1.0], [0,0,0,1.0], [0,0,0,1.0], null],
      [[0,0,0,1.0], null, null, null, [0,0,0,1.0]],
      [[0,0,0,1.0], null, null, null, [0,0,0,1.0]],
      [[255,0,0,1.0], [255,0,0,1.0], [255,0,0,1.0], [255,0,0,1.0], null]
    ]'
);

COMMIT;