BEGIN;

INSERT INTO "user" (
  "pseudo",
  "email",
  "password"
)
VALUES
(
  'TestUser',
  'test.user@mail.com',
  'azerty123'
)
;

INSERT INTO "game" (
  "name",
  "difficulty",
  "content"
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
  }'
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
  }'
)
;

COMMIT;