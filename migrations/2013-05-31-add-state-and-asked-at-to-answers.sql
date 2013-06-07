ALTER TABLE answers
      ADD COLUMN state VARCHAR(255) DEFAULT 'pending'
          CHECK (state = 'pending'    ::VARCHAR 
              OR state = 'answered'   ::VARCHAR
              OR state = 'unanswered' ::VARCHAR),
      ADD COLUMN answered_at TIMESTAMP;

ALTER TABLE answers
      RENAME COLUMN created_at TO asked_at;

UPDATE answers SET state = 'answered';
UPDATE answers SET answered_at = asked_at; -- for old qs
