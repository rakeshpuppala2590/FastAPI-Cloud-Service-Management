from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse


# Configure your MySQL connection URL
DATABASE_URL = "mysql+mysqlconnector://root:root@localhost/cloud"

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a SQLAlchemy session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for your models
Base = declarative_base()

# Define models for database tables
class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True) 
    description = Column(String(20))
    permissions = Column(String(20))  # Comma-separated list of permissions
    usage_limit = Column(Integer)

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(1), index=True)
    description = Column(String(20))

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), index=True)
    status = Column(String(20))
    # Add other user attributes here

class Usage(Base):
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    api_endpoint = Column(Integer)
    timestamp = Column(Integer)

# Initialize the database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Model for creating a subscription plan
class PlanCreate(BaseModel):
    name: str
    description: str
    permissions: str
    usage_limit: int
    

# Model for creating a permission
class PermissionCreate(BaseModel):
    name: str
    description : str

# Model for creating a subscription
class SubscriptionCreate(BaseModel):
    plan_id: int

class Subscriptionpost(BaseModel):
    user_id: int
    plan_id: int


# Model for tracking API usage
class UsageCreate(BaseModel):
    user_id: int
    

# Model for user
class UserCreate(BaseModel):
    # id: int
    username: str
    status:str




# @app.post("/plans/{token}", response_model=PlanCreate)
# async def create_plan(plan: PlanCreate, token: str, db: Session = Depends(get_db)):

    
#     # Check if the provided permission exists
#     permission_exists = db.query(Permission).filter(Permission.name == plan.permissions).first()
#     if not permission_exists:
#         raise HTTPException(status_code=403, detail="Permission does not exist")

    
#     # Check if the user has admin privileges
#     if token != "1":
#         raise HTTPException(status_code=403, detail="User does not have admin privileges")

#     # Create and commit the new plan
#     db_plan = Plan(**plan.dict())
#     db.add(db_plan)
#     db.commit()
#     db.refresh(db_plan)

    
#     # Convert the Plan object to a dictionary
#     db_plan_dict = jsonable_encoder(db_plan)

#     # Return the response
#     return JSONResponse(content={"message": "Plan created successfully", "plan": db_plan_dict}, status_code=200)

@app.post("/plans/{token}", response_model=PlanCreate)
async def create_plan(token:str, plan: PlanCreate, db: Session = Depends(get_db)):
    print("Token:", token)  # Add this line for debugging
    if token != "admin":
        raise HTTPException(status_code=403, detail="User cannot create plans")

    que = db.query(Permission).filter(Permission.name == plan.permissions).first()
    if not que:
        raise HTTPException(status_code=403, detail="Permission does not exist")

    db_plan = Plan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    db_plan_dict = jsonable_encoder(db_plan)
    
    return JSONResponse(content={"message": "Plan created successfully", "plan": db_plan_dict}, status_code=200)

# Get
@app.get("/plans/{plan_id}", response_model=PlanCreate)
async def get_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if db_plan:
        # Convert the Plan object to a dictionary
        db_plan_dict = jsonable_encoder(db_plan)
        return JSONResponse(content={"message": "Plan retrieved successfully", "plan": db_plan_dict}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Plan not found")

    
from fastapi.encoders import jsonable_encoder

@app.put("/plans/{plan_id}/{token}", response_model=PlanCreate)
async def modify_plan(plan_id: int, token: str, plan: PlanCreate, db: Session = Depends(get_db)):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()

    status_check = db.query(User).filter(token == "admin").first()
    if not status_check:
        raise HTTPException(status_code=404, detail="user cannot modify plans")

    que = db.query(Permission).filter(plan.permissions == Permission.name)
    if not que:
        raise HTTPException(status_code=403, detail="Permission does not exist")

    if db_plan:
        for key, value in plan.dict().items():
            setattr(db_plan, key, value)
        db.commit()
        db.refresh(db_plan)

        # Convert the Plan object to a dictionary
        db_plan_dict = jsonable_encoder(db_plan)
        
        return JSONResponse(content={"message": "Plan modified or Created successful", "plan": db_plan_dict}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Plan not found")

@app.delete("/plans/{plan_id}/{token}", response_model=PlanCreate)
async def delete_plan(plan_id: int,token:str, db: Session = Depends(get_db)):
    status_check = db.query(User).filter(token=="admin").first()
    if not status_check:
        raise HTTPException(status_code=404, detail="User cannot modify subscriptions")
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if db_plan:
        # Convert the Plan object to a dictionary
        db_plan_dict = jsonable_encoder(db_plan)
        db.delete(db_plan)
        db.commit()
        return JSONResponse(content={"message": "Plan deleted successfully", "plan": db_plan_dict}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Plan not found")


#Permission Modify or create
@app.put("/permissions/{user_id}", response_model=PermissionCreate)
async def create_permission(user_id: int, permission: PermissionCreate, db: Session = Depends(get_db)):
    status_check = db.query(User).filter(User.id == user_id, User.status == "user").first()
    if status_check:
        raise HTTPException(status_code=404, detail="Access Denied")

    # Create a new Permission object without specifying user_id
    new_permission = Permission(**permission.dict())
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)

    # Convert the Permission object to a dictionary
    new_permission_dict = jsonable_encoder(new_permission)

    return JSONResponse(content={"message": "Permission created successfully", "permission": new_permission_dict}, status_code=201)

#permission delete
@app.delete("/permissions/{permission_id}/{user_id}", response_model=PermissionCreate)
async def delete_permission(permission_id: int, user_id: int, db: Session = Depends(get_db)):
    status_check = db.query(User).filter(User.id == user_id, User.status == "user").first()
    if status_check:
        raise HTTPException(status_code=404, detail="Access Denied")
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if db_permission:
        db.delete(db_permission)
        db.commit()

        # Convert the Permission object to a dictionary
        db_permission_dict = jsonable_encoder(db_permission)

        return JSONResponse(content={"message": "Allows Deleting data, Deleting now", "permission": db_permission_dict}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Permission not found")



# User Subscription Handling
@app.post("/subscriptions/{user_id}", response_model=Subscriptionpost)
async def subscribe_user(user_id: int, subscription: Subscriptionpost, db: Session = Depends(get_db)):
    # Check if the user exists
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    # Check if the user already has a plan in the Subscription table
    

    # Add the user_id to the subscription
    subscription.user_id = user_id

    # Check if the plan exists
    db_plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail=f"Plan with id {subscription.plan_id} not found")

    existing_subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if existing_subscription:
        raise HTTPException(status_code=400, detail="User already has an existing subscription plan")

    # Add the subscription to the database
    db_subscription = Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)

    # Create a row in the usage table
    usage_limit = db_plan.usage_limit if db_plan.usage_limit is not None else 0
    db_usage = Usage(user_id=user_id, api_endpoint=usage_limit, timestamp=usage_limit)
    db.add(db_usage)
    db.commit()

    # Convert the Subscription object to a dictionary
    db_subscription_dict = jsonable_encoder(db_subscription)

    return JSONResponse(content={"message": "Subscription successful", "Usage table updated": db_subscription_dict}, status_code=200)



#Sub Get
@app.get("/subscriptions/{user_id}", response_model=SubscriptionCreate)
async def view_subscription(user_id: int, db: Session = Depends(get_db)):
    status_check = db.query(User).filter(user_id==1, User.status == "admin").first()
    if status_check:
        raise HTTPException(status_code=404, detail="admin don't have any plans")
    db_subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if db_subscription:
        # Convert the Subscription object to a dictionary
        db_subscription_dict = jsonable_encoder(db_subscription)
        return JSONResponse(content={"subscription": db_subscription_dict}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Subscription not found")


# Access Control
@app.get("/access/{user_id}/{api_request}")
async def check_access_permission(user_id: int, api_request: str, db: Session = Depends(get_db)):
    # Implement access control logic based on user's subscription plan and permissions
    return {"message": "Access granted"}


@app.post("/user", response_model=UserCreate)
async def createuser(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Convert the User object to a dictionary
    db_user_dict = jsonable_encoder(db_user)
    return JSONResponse(content={"user": db_user_dict}, status_code=200)

#user delete
@app.delete("/user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    status_check = db.query(User).filter(user_id==1, User.status == "admin").first()
    if status_check:
        raise HTTPException(status_code=404, detail="You cannot delete admin")
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()

    return JSONResponse(content={"message": "User deleted successfully"}, status_code=200)


@app.put("/subscriptions/{userid}", response_model=Subscriptionpost)
async def assign_user_plan(userid: int, subscription: Subscriptionpost, db: Session = Depends(get_db)):
    # Check if the user exists
    user = db.query(User).filter(User.id == subscription.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    status_check = db.query(User).filter(User.id == userid, User.status == "admin").first()
    if not status_check:
        raise HTTPException(status_code=404, detail="User doesn't have admin status")

    # Check if the plan exists
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Check if the subscription exists for the user
    db_subscription = db.query(Subscription).filter(Subscription.user_id == subscription.user_id).first()

    if db_subscription:
        # Update the existing subscription details
        db_subscription.user_id = subscription.user_id
        db_subscription.plan_id = subscription.plan_id
    else:
        # Create a new subscription
        db_subscription = Subscription(user_id=userid, plan_id=subscription.plan_id)
        db.add(db_subscription)

    # Create a row in the usage table
    usage_limit = plan.usage_limit if plan.usage_limit is not None else 0
    db_usage = Usage(user_id=userid, api_endpoint=usage_limit, timestamp=usage_limit)
    db.add(db_usage)

    db.commit()
    db.refresh(db_subscription)

    # Convert the Subscription object to a dictionary
    db_subscription_dict = jsonable_encoder(db_subscription)

    return JSONResponse(content={"message": "Subscription successful", "subscription": db_subscription_dict}, status_code=200)


@app.delete("/subscriptions/{userid}", response_model=Subscriptionpost)
async def cancel_user_subscription(userid: int, db: Session = Depends(get_db)):
    # Check if the user exists
    user = db.query(User).filter(User.id == userid).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the user has admin status
    status_check = db.query(User).filter(User.id == 1, User.status == "admin").first()
    if not status_check:
        raise HTTPException(status_code=404, detail="Admin cannot cancel subscriptions")

    # Check if the subscription exists for the user
    db_subscription = db.query(Subscription).filter(Subscription.user_id == userid).first()

    if db_subscription:
        # Delete the subscription
        db.delete(db_subscription)
        db.commit()

        # Convert the Subscription object to a dictionary
        db_subscription_dict = jsonable_encoder(db_subscription)

        return JSONResponse(content={"message": "Subscription canceled successfully", "subscription": db_subscription_dict}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Subscription not found")



# API endpoint to view usage statistics
@app.get("/usage/a/{user_id}", response_model=UsageCreate)
async def view_usage_statistics(user_id: int, db: Session = Depends(get_db)):
    # Get the user's usage record
    user_usage = db.query(Usage).filter(Usage.user_id == user_id).first()

    # Check if the user exists
    if user_usage is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the user has a specific plan (e.g., Plan A) with the required permission ('a')
    user_plan = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .first()
    )

    p = (
        db.query(Plan)
        .filter(Plan.id==user_plan.plan_id)
        .first()
    )

    if user_plan and 'a' in p.permissions:
        # Decrease the value of "usage" by 1 (you can modify this based on your requirements)
        if user_usage.api_endpoint > 0:
            user_usage.api_endpoint -= 1
            # Commit the changes to the database
            db.commit()
            # Return the updated usage record
            return JSONResponse(content={"access": "Premium API endpoint Granted"}, status_code=200)
        else:
            return JSONResponse(content={"access": "Blocked - Usage limit reached"}, status_code=200)
    else:
        return JSONResponse(content={"access": "Blocked - User does not have access to premium API"}, status_code=200)


# API endpoint to view usage statistics
@app.get("/usage/b/{user_id}", response_model=UsageCreate)
async def view_usage_statistics(user_id: int, db: Session = Depends(get_db)):
    # Get the user's usage record
    user_usage = db.query(Usage).filter(Usage.user_id == user_id).first()

    # Check if the user exists
    if user_usage is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the user has a specific plan (e.g., Plan A) with the required permission ('a')
    user_plan = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .first()
    )

    p = (
        db.query(Plan)
        .filter(Plan.id==user_plan.plan_id)
        .first()
    )

    if user_plan and 'b' in p.permissions:
        # Decrease the value of "usage" by 1 (you can modify this based on your requirements)
        if user_usage.api_endpoint > 0:
            user_usage.api_endpoint -= 1
            # Commit the changes to the database
            db.commit()
            # Return the updated usage record
            return JSONResponse(content={"access": "Basic API endpoint Granted /n ONLY PERMISSION TO READ"}, status_code=200)
        else:
            return JSONResponse(content={"access": "Blocked - Usage limit reached"}, status_code=200)
    else:
        return JSONResponse(content={"access": "Blocked - User does not have access to Basic API"}, status_code=200)
    
# API endpoint to view usage statistics
@app.get("/usage/c/{user_id}", response_model=UsageCreate)
async def view_usage_statistics(user_id: int, db: Session = Depends(get_db)):
    # Get the user's usage record
    user_usage = db.query(Usage).filter(Usage.user_id == user_id).first()

    # Check if the user exists
    if user_usage is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the user has a specific plan (e.g., Plan A) with the required permission ('a')
    user_plan = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .first()
    )

    p = (
        db.query(Plan)
        .filter(Plan.id==user_plan.plan_id)
        .first()
    )

    if user_plan and 'c' in p.permissions:
        # Decrease the value of "usage" by 1 (you can modify this based on your requirements)
        if user_usage.api_endpoint > 0:
            user_usage.api_endpoint -= 1
            # Commit the changes to the database
            db.commit()
            # Return the updated usage record
            return JSONResponse(content={"access": "Standard API endpoint Granted /n ONLY PERMISSION TO READ"}, status_code=200)
        else:
            return JSONResponse(content={"access": "Blocked - Usage limit reached"}, status_code=200)
    else:
        return JSONResponse(content={"access": "Blocked - User does not have access to Standard API"}, status_code=200)
