
import os

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "brightloop-development-secret-key"
    )

    DATABASE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "instance",
        "brightloop.db"
    )
