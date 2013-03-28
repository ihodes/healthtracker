# from https://alembic.readthedocs.org/en/latest/tutorial.html#building-an-up-to-date-database-from-scratch

# create all of the tables:
my_metadata.create_all(engine)

# Load the Alembic configuration and generate the
# version table, "stamping" it with the most recent rev:
from alembic.config import Config
from alembic import command
alembic_cfg = Config("../alembic.ini")
command.stamp(alembic_cfg, "head")
