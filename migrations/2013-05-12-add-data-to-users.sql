ALTER TABLE users
      ADD COLUMN timezone varchar (255) DEFAULT 'Z',  -- how to do this right?
      ADD COLUMN name text,
      ADD COLUMN notes text;
