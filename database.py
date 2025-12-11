import os
import asyncpg
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    join_date = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_banned = Column(Boolean, default=False)
    searches_count = Column(Integer, default=0)

class SearchLog(Base):
    __tablename__ = 'search_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    search_type = Column(String(50))
    query = Column(Text)
    result = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50))

class Database:
    def __init__(self, database_url=None):
        if database_url and database_url.startswith("postgresql://"):
            # Railway PostgreSQL
            self.database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            # SQLite local
            self.database_url = "sqlite+aiosqlite:///./osintbot.db"
        
        self.engine = None
        self.async_session = None
    
    async def init(self):
        """Inicializar base de datos"""
        self.engine = create_async_engine(self.database_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Crear tablas
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def register_user(self, user_id, username, first_name, last_name):
        """Registrar nuevo usuario"""
        async with self.async_session() as session:
            user = await session.get(User, user_id)
            if not user:
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
            else:
                user.last_activity = datetime.utcnow()
            
            await session.commit()
            return user
    
    async def log_search(self, user_id, search_type, query, result):
        """Registrar búsqueda"""
        async with self.async_session() as session:
            log = SearchLog(
                user_id=user_id,
                search_type=search_type,
                query=query,
                result=result
            )
            session.add(log)
            
            # Actualizar contador del usuario
            user = await session.get(User, user_id)
            if user:
                user.searches_count += 1
                user.last_activity = datetime.utcnow()
            
            await session.commit()
    
    async def get_statistics(self):
        """Obtener estadísticas"""
        async with self.async_session() as session:
            from sqlalchemy import func, select
            
            # Total usuarios
            total_users = await session.scalar(select(func.count()).select_from(User))
            
            # Búsquedas hoy
            today = datetime.utcnow().date()
            searches_today = await session.scalar(
                select(func.count()).select_from(SearchLog)
                .where(func.date(SearchLog.timestamp) == today)
            )
            
            # Total búsquedas
            total_searches = await session.scalar(
                select(func.count()).select_from(SearchLog)
            )
            
            return {
                "total_users": total_users or 0,
                "searches_today": searches_today or 0,
                "total_searches": total_searches or 0,
                "bot_uptime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
