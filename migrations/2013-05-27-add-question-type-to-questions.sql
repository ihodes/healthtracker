ALTER TABLE questions
      ADD COLUMN qtype VARCHAR(255),
      DROP CONSTRAINT questions_name_key;

UPDATE questions SET qtype = 'multi_numeric';
