-- Separate database for the backend test suite (tests/conftest.py).
-- Tests do Base.metadata.create_all/drop_all around every test - pointing
-- them at the same database as local dev/alembic would wipe real dev data
-- every time `pytest` runs.
CREATE DATABASE mesdocuments_test;
