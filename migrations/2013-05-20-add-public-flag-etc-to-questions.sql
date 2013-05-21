ALTER TABLE questions
     ADD COLUMN is_public boolean DEFAULT false, 
     ADD COLUMN created_by integer REFERENCES users(id); -- the user who creates this question

ALTER TABLE scheduled_questions
      ALTER COLUMN scheduled_for SET DATA TYPE time,
      ALTER COLUMN scheduled_for SET DEFAULT '20:00'; -- schedule notifications for 8 PM, default

UPDATE scheduled_questions
      SET scheduled_for = '20:00';
      
      
