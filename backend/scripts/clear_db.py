from app.db.session import engine
from app.db import models


def run():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    print("Database cleared and re-created.")


if __name__ == "__main__":
    run()
