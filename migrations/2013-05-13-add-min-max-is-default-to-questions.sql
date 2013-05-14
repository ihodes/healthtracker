ALTER TABLE questions
      ADD COLUMN min_value integer DEFAULT 0,
      ADD COLUMN max_value integer DEFAULT 5,
      ADD COLUMN is_default boolean DEFAULT false;
