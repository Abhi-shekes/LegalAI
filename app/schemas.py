from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Table, Column, Integer, String, MetaData, Text

metadata = MetaData()



users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, index=True),
    Column("hashed_password", String),
    Column("name", String),  
)

generated_arguments = Table(
    "generated_arguments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("case_id", String),
    Column("generated_arguments", Text),
    Column("created_at", DateTime, default=datetime.utcnow),
        Column("is_solved", Boolean, default=False),  

)

blacklisted_tokens = Table(
    "blacklisted_tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("token", String, unique=True, index=True),
    Column("expires_at", DateTime)
)