from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    # products = relationship("ProductModel", back_populates="category")