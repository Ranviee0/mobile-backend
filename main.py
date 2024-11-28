from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Restaurant, Food
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to a specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request validation
class RestaurantCreate(BaseModel):
    RestaurantName: str
    RestaurantLatitude: float
    RestaurantLongitude: float
    RestaurantImage: str

class FoodCreate(BaseModel):
    FoodName: str
    FoodPrice: int
    RestaurantID: int
    FoodImage: str

@app.get("/restaurant/all")
def read_restaurants(db: Session = Depends(get_db)):
    return db.query(Restaurant).all()

@app.get("/food/")
def read_food(db: Session = Depends(get_db)):
    return db.query(Food).all()

@app.get("/restaurant/search")
def search_restaurants(query: str, db: Session = Depends(get_db)):
    """
    Search for restaurants by name starting with the query string.
    """
    results = db.query(Restaurant).filter(Restaurant.RestaurantName.like(f"{query}%")).all()
    if not results:
        raise HTTPException(status_code=404, detail="No restaurants found matching the query.")
    return results

@app.get("/food/search/")
def search_food(query: str = "", RestaurantName: str = Query(...), db: Session = Depends(get_db)):
    """
    Search for food by name and restaurant.
    - `query`: Optional, searches food names starting with the string.
    - `RestaurantName`: Required, filters food by the given restaurant.
    """
    # Find the restaurant by name
    restaurant = db.query(Restaurant).filter(Restaurant.RestaurantName == RestaurantName).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found.")

    # Search for food items in the found restaurant
    if query:
        food_items = db.query(Food).filter(
            and_(
                Food.RestaurantID == restaurant.RestaurantID,
                Food.FoodName.like(f"{query}%")
            )
        ).all()
    else:
        # Return all food items if no query is provided
        food_items = db.query(Food).filter(Food.RestaurantID == restaurant.RestaurantID).all()

    if not food_items:
        raise HTTPException(status_code=404, detail="No food items found matching the criteria.")

    return food_items

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/restaurant/location/")
def get_restaurant_location(
    name: str = Query(None),
    restaurant_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get the latitude and longitude of a restaurant.
    - `name`: (Optional) The name of the restaurant.
    - `restaurant_id`: (Optional) The ID of the restaurant.
    At least one of `name` or `restaurant_id` must be provided.
    """
    if not name and not restaurant_id:
        raise HTTPException(status_code=400, detail="Either 'name' or 'restaurant_id' must be provided.")

    # Query by name or ID
    restaurant = None
    if name:
        restaurant = db.query(Restaurant).filter(Restaurant.RestaurantName == name).first()
    elif restaurant_id:
        restaurant = db.query(Restaurant).filter(Restaurant.RestaurantID == restaurant_id).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found.")

    return {
        "RestaurantName": restaurant.RestaurantName,
        "Latitude": restaurant.RestaurantLatitude,
        "Longitude": restaurant.RestaurantLongitude,
    }