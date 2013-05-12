ALTER TABLE user_question_relation
      ADD COLUMN scheduled_for timestamp with time zone, 
      ADD COLUMN notification_method varchar (255);
