ALTER TABLE user_question_relation RENAME TO scheduled_questions;

ALTER TABLE scheduled_questions
      DROP CONSTRAINT user_question_relation_question_id_fkey,
      DROP CONSTRAINT user_question_relation_user_id_fkey,
      ALTER COLUMN scheduled_for SET DATA TYPE timestamp,
      ADD COLUMN id SERIAL;

UPDATE scheduled_questions
       SET id = nextval(pg_get_serial_sequence('scheduled_questions','id'));

ALTER TABLE scheduled_questions
      ADD PRIMARY KEY (id),
      ADD FOREIGN KEY (user_id) REFERENCES users,
      ADD FOREIGN KEY (question_id) REFERENCES questions;
