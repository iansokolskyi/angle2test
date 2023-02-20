import json
import os
import re
from datetime import datetime, date

from sqlalchemy import MetaData
from sqlalchemy.orm import Session

from app.core.db import engine


def get_model_by_table_name(table_name: str):
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return metadata.tables[table_name]


def handle_datetime_fields(obj):
    for key, value in obj.items():
        datetime_pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}$")
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if isinstance(value, str):
            if re.match(datetime_pattern, value):
                obj[key] = datetime.fromisoformat(value)
            elif re.match(date_pattern, value):
                obj[key] = date.fromisoformat(value)

    return obj


def load_fixture_from_file(table: str, path, db_session: Session):
    with open(path, "r") as f:
        fixtures = json.load(f)
        for obj in fixtures:
            obj = handle_datetime_fields(obj)
            model = get_model_by_table_name(table)
            db_session.execute(model.insert().values(**obj))
        db_session.commit()


def load_fixtures(fixtures_dir, db_session: Session, fixture_files=None):
    if os.path.exists(fixtures_dir):
        for file_name in os.listdir(fixtures_dir):
            fixture_name, ext = os.path.splitext(os.path.basename(file_name))
            file_format = ext.strip(".")
            supported = file_format in ("json",)
            selected = fixture_name in fixture_files if fixture_files else True
            if selected and supported:
                path = os.path.join(fixtures_dir, file_name)
                load_fixture_from_file(fixture_name, path, db_session)
