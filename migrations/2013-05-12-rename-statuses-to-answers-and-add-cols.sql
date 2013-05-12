ALTER TABLE statuses
      RENAME TO answers;

ALTER TABLE answers     
      ALTER COLUMN value SET DATA TYPE text,
      ADD COLUMN question_id integer REFERENCES questions,
      DROP CONSTRAINT statuses_user_id_fkey,
      ADD FOREIGN KEY (user_id) REFERENCES users,
      ADD FOREIGN KEY (question_id) REFERENCES questions;

ALTER INDEX statuses_pkey RENAME TO answers_pkey;
ALTER SEQUENCE statuses_id_seq RENAME TO answers_id_seq;
