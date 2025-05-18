# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base
from app.models.models import User, Document, DocumentEmbedding, Question, RLModelState 