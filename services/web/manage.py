from flask.cli import FlaskGroup

from project import app, db
from project.db_handlers import make_db_data, delete_all_files_in_dir

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    # try:
    db.drop_all()
    # except FileNotFoundError:
    #     print('No DB to drop')

    delete_all_files_in_dir('project/static/covers')
    db.create_all()


@cli.command("seed_db")
def seed_db():
    make_db_data(db)


if __name__ == "__main__":
    cli()
