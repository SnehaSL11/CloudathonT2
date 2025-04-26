import boto3
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import json

# AWS Secrets Manager client
client = boto3.client('secretsmanager', region_name="us-east-1")  # Adjust region if necessary

# Fetch the password from AWS Secrets Manager
def get_db_password(secret_name):
    try:
        secret = client.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(secret['SecretString'])
        return secret_dict['password']
    except Exception as e:
        print("Error fetching secret: ", e)
        raise

# Fetch password from Secrets Manager
secret_name = "rds-postgres-credentials"  # Replace with your actual secret name
db_password = get_db_password(secret_name)

# Static database URL components
username = "postgres"  # Your PostgreSQL username
host = "database-1.cluster-ckx6wm6m08z0.us-east-1.rds.amazonaws.com"  # Your RDS PostgreSQL endpoint
port = "5432"  # Default PostgreSQL port
dbname = "mydb"  # Your database name

# Construct the DATABASE_URL with the fetched password
DATABASE_URL = f"postgresql+psycopg2://{username}:{db_password}@{host}:{port}/{dbname}"

# FastAPI instance
app = FastAPI()

# SQLAlchemy setup
Base = declarative_base()

# Define the Users table
class User(Base):
    _tablename_ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)

# Define the Products table
class Product(Base):
    _tablename_ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String)
    price = Column(Float)

# SQLAlchemy session setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydantic models for data validation
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str

class ProductCreate(BaseModel):
    product_name: str
    price: float

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API route to get all users
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# API route to get a specific user by ID
@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()

# API route to add a new user
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(first_name=user.first_name, last_name=user.last_name, phone_number=user.phone_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# API route to get all products
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

# API route to get a specific product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.id == product_id).first()

# API route to add a new product
@app.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(product_name=product.product_name, price=product.price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
