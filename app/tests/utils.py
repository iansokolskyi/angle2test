import json
import os
import re
from datetime import datetime, date

from sqlalchemy import MetaData, Table
from sqlalchemy.orm import Session

from app.core.db import engine


def get_table_by_name(table_name: str) -> Table:
    """
    It returns a SQLAlchemy Table object for the table with the given name

    :param table_name: The name of the table you want to get the model for
    :return: The table object
    """
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return metadata.tables[table_name]


def handle_datetime_fields(obj) -> dict:
    """
    It takes a dictionary, and if any of the values are strings that match the datetime or date
    patterns, it converts them to the appropriate datetime or date object.

    :param obj: The object to be converted
    :return: The converted object
    """
    for key, value in obj.items():
        datetime_pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}$")
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if isinstance(value, str):
            if re.match(datetime_pattern, value):
                obj[key] = datetime.fromisoformat(value)
            elif re.match(date_pattern, value):
                obj[key] = date.fromisoformat(value)

    return obj


def load_fixture_from_file(tablename: str, path, db_session: Session):
    """
    Loads fixture from a given file path

    :param tablename: The name of the table you want to load the fixture into
    :param path: The path to the JSON file containing the fixture data
    :param db_session: The database session to use for the insert
    """
    with open(path, "r") as f:
        fixtures = json.load(f)
        for obj in fixtures:
            obj = handle_datetime_fields(obj)
            model = get_table_by_name(tablename)
            db_session.execute(model.insert().values(**obj))
        db_session.commit()


def load_fixtures(fixtures_dir, db_session: Session, fixture_files=None):
    """
    It loads fixtures from a directory. Only loads fixtures that are in the `fixture_files` list,
    if provided.

    :param fixtures_dir: The directory where the fixtures are stored
    :param db_session: The database session to use for loading the fixtures
    :param fixture_files: a list of fixture names to load. If None, all fixtures are loaded
    """
    if os.path.exists(fixtures_dir):
        for file_name in os.listdir(fixtures_dir):
            fixture_name, ext = os.path.splitext(os.path.basename(file_name))
            file_format = ext.strip(".")
            supported = file_format in ("json",)
            selected = fixture_name in fixture_files if fixture_files else True
            if selected and supported:
                path = os.path.join(fixtures_dir, file_name)
                load_fixture_from_file(fixture_name, path, db_session)
