# FastAPI-Cloud-Service-Management
This FastAPI Cloud Subscription Service is a robust backend system designed to manage cloud-based subscription plans, user subscriptions, permissions, and API access control. It utilizes FastAPI for efficient API development and SQLAlchemy for seamless database interactions, catering to high-performance cloud services environments.
---------------------
   Link to the Demonstration of the Project
------------------------------------------------
https://drive.google.com/drive/folders/1glbYEe3w4sCLLGcXtVHQt_KbYG5L9AXw?usp=sharing
---------------------
   Prerequisites
-------------------------------
- Python 3.6 or higher
- MySQL Server
---------------------
   Installation
-------------------------------
1. Clone the repository:
   git clone [https://github.com/abhinavkarthik2023/FastAPI-Cloud-Service-Management/tree/main]

2. Navigate to the project directory:
   cd [project-directory]

3. Install required Python packages:
   pip install -r requirements.txt

4. Ensure MySQL Server is installed and running.
---------------------
   Configuration
-------------------------------
1. Update the `DATABASE_URL` in the source code to reflect your MySQL database credentials and server details.
2. Initialize the database by running the provided initialization scripts, if any.
---------------------
   Usage
-------------------------------
1. Start the FastAPI server:
   uvicorn main:app --reload
2. Access the API endpoints through the provided URL (typically `http://127.0.0.1:8000`).
---------------------
   Features
-------------------------------
-  Subscription Plan Management**: Create, read, update, and delete subscription plans.
-  Permission Management**: Modify and delete permissions.
-  User Subscription Handling**: Manage user subscriptions to different plans.
-  Access Control**: Control user access to various API endpoints based on subscription.
-  API Usage Tracking**: Monitor and limit user API usage.


   Database Schema
-------------------------------
The database for the # FastAPI Cloud Subscription Service consists of several tables designed to manage subscription plans, user subscriptions, permissions, and API usage. Below are the details of each table along with their structures and relationships.
---------------------
1. Plan Table
---------------------
- Table Name: plans
- Columns:
  - id: Integer, Primary Key
  - name: String(255), Indexed
  - description: String(20)
  - permissions: String(20) (Comma-separated list of permissions)
  - usage_limit: Integer
---------------------
2. Permission Table
-------------------
- Table Name: permissions
- Columns:
  - id: Integer, Primary Key
  - name: String(1), Indexed
  - description: String(20)
---------------------
3. Subscription Table
---------------------
- Table Name: subscriptions
- Columns:
  - id: Integer, Primary Key
  - user_id: Integer, ForeignKey to 'users.id'
  - plan_id: Integer, ForeignKey to 'plans.id'
---------------------
4. User Table
---------------------
- Table Name: users
- Columns:
  - id: Integer, Primary Key
  - username: String(20), Indexed
  - status: String(20)
  - (Other user attributes can be added here)
---------------------
5. Usage Table
---------------------
- Table Name: usage
- Columns:
  - id: Integer, Primary Key
  - user_id: Integer, ForeignKey to 'users.id'
  - api_endpoint: Integer
  - timestamp: Integer
---------------------
   Relationships
--------------------
- The 'subscriptions' table links users to their subscription plans with foreign keys to the 'users' and 'plans' tables.
- The 'usage' table tracks API usage per user, linked to the 'users' table.

---------------------
   Acknowledgements
---------------------
This project was developed as part of the California State University Fullerton's [CPSC 449/Web-Backend Engineering]. 
Special thanks to Professor Harsh Bodgal and the contributors.

---
End of README.txt
