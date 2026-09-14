from .models import Base
from .connection import engine

Base.metadata.drop_all(engine)