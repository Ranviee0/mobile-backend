from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Restaurant(Base):
    __tablename__ = 'Restaurants'
    RestaurantID = Column(Integer, primary_key=True, index=True)
    RestaurantName = Column(String, nullable=False)
    RestaurantLatitude = Column(Float, nullable=False)
    RestaurantLongitude = Column(Float, nullable=False)
    RestaurantImage = Column(String, nullable=False)

    foods = relationship("Food", back_populates="restaurant")

class Food(Base):
    __tablename__ = 'Food'
    FoodID = Column(Integer, primary_key=True, index=True)
    FoodName = Column(String, nullable=False)
    FoodPrice = Column(Integer, nullable=False)
    RestaurantID = Column(Integer, ForeignKey('Restaurants.RestaurantID'), nullable=False)
    FoodImage = Column(String, nullable=False)

    restaurant = relationship("Restaurant", back_populates="foods")
