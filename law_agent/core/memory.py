"""Agent memory management for persistent learning and user interactions."""

import json
import pickle
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import redis
try:
    import fakeredis
    FAKEREDIS_AVAILABLE = True
except ImportError:
    FAKEREDIS_AVAILABLE = False

from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from .config import settings
from .state import AgentState, UserProfile, UserInteraction, LegalDomain


Base = declarative_base()


class UserProfileDB(Base):
    """Database model for user profiles."""
    __tablename__ = "user_profiles"
    
    user_id = Column(String, primary_key=True)
    user_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    interaction_count = Column(Integer, default=0)
    total_time_spent = Column(Float, default=0.0)
    satisfaction_score = Column(Float, default=0.0)
    preferences = Column(Text)  # JSON string
    preferred_domains = Column(Text)  # JSON string


class InteractionDB(Base):
    """Database model for user interactions."""
    __tablename__ = "interactions"
    
    interaction_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    interaction_type = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    predicted_domain = Column(String)
    confidence_score = Column(Float)
    response = Column(Text)
    feedback = Column(String)
    time_spent = Column(Float)
    interaction_metadata = Column(Text)  # JSON string


class MemoryStore(ABC):
    """Abstract base class for memory storage."""
    
    @abstractmethod
    async def store_state(self, state: AgentState) -> None:
        """Store agent state."""
        pass
    
    @abstractmethod
    async def retrieve_state(self, session_id: str) -> Optional[AgentState]:
        """Retrieve agent state by session ID."""
        pass
    
    @abstractmethod
    async def store_user_profile(self, profile: UserProfile) -> None:
        """Store user profile."""
        pass
    
    @abstractmethod
    async def retrieve_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile by user ID."""
        pass
    
    @abstractmethod
    async def store_interaction(self, interaction: UserInteraction) -> None:
        """Store user interaction."""
        pass
    
    @abstractmethod
    async def get_user_interactions(self, user_id: str, limit: int = 100) -> List[UserInteraction]:
        """Get user interactions history."""
        pass


class RedisMemoryStore(MemoryStore):
    """Redis-based memory store for fast access."""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or settings.redis_url
        self.memory_store = {}

        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis not available, trying FakeRedis: {e}")
            try:
                if FAKEREDIS_AVAILABLE:
                    self.redis_client = fakeredis.FakeRedis(decode_responses=True)
                    logger.info("✅ FakeRedis initialized successfully")
                else:
                    raise ImportError("FakeRedis not available")
            except Exception as fake_e:
                logger.warning(f"FakeRedis also failed, using in-memory storage: {fake_e}")
                self.redis_client = None
        
    async def store_state(self, state: AgentState) -> None:
        """Store agent state in Redis or memory."""
        try:
            key = f"agent_state:{state.session_id}"
            data = state.json()

            if self.redis_client:
                # Store with 24 hour expiration
                self.redis_client.setex(key, 86400, data)
            else:
                # Store in memory
                self.memory_store[key] = data

            logger.debug(f"Stored agent state for session {state.session_id}")
        except Exception as e:
            logger.error(f"Failed to store agent state: {e}")
    
    async def retrieve_state(self, session_id: str) -> Optional[AgentState]:
        """Retrieve agent state from Redis or memory."""
        try:
            key = f"agent_state:{session_id}"

            if self.redis_client:
                data = self.redis_client.get(key)
            else:
                data = self.memory_store.get(key)

            if data:
                return AgentState.parse_raw(data)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve agent state: {e}")
            return None
    
    async def store_user_profile(self, profile: UserProfile) -> None:
        """Store user profile in Redis."""
        try:
            key = f"user_profile:{profile.user_id}"
            data = profile.json()

            if self.redis_client:
                self.redis_client.set(key, data)
            else:
                self.memory_store[key] = data

            logger.debug(f"Stored user profile for {profile.user_id}")
        except Exception as e:
            logger.error(f"Failed to store user profile: {e}")
    
    async def retrieve_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile from Redis."""
        try:
            key = f"user_profile:{user_id}"

            if self.redis_client:
                data = self.redis_client.get(key)
            else:
                data = self.memory_store.get(key)

            if data:
                return UserProfile.parse_raw(data)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve user profile: {e}")
            return None
    
    async def store_interaction(self, interaction: UserInteraction) -> None:
        """Store interaction in Redis list or memory."""
        try:
            key = f"interactions:{interaction.user_id}"
            data = interaction.json()

            if self.redis_client:
                self.redis_client.lpush(key, data)
                # Keep only last 1000 interactions per user
                self.redis_client.ltrim(key, 0, 999)
            else:
                # Store in memory
                if key not in self.memory_store:
                    self.memory_store[key] = []
                self.memory_store[key].insert(0, data)
                # Keep only last 1000 interactions
                if len(self.memory_store[key]) > 1000:
                    self.memory_store[key] = self.memory_store[key][:1000]

            logger.debug(f"Stored interaction for user {interaction.user_id}")
        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
    
    async def get_user_interactions(self, user_id: str, limit: int = 100) -> List[UserInteraction]:
        """Get user interactions from Redis or memory."""
        try:
            key = f"interactions:{user_id}"

            if self.redis_client:
                data_list = self.redis_client.lrange(key, 0, limit - 1)
            else:
                data_list = self.memory_store.get(key, [])[:limit]

            interactions = []
            for data in data_list:
                try:
                    interaction = UserInteraction.parse_raw(data)
                    interactions.append(interaction)
                except Exception as e:
                    logger.warning(f"Failed to parse interaction data: {e}")
            return interactions
        except Exception as e:
            logger.error(f"Failed to get user interactions: {e}")
            return []


class SQLMemoryStore(MemoryStore):
    """SQL database memory store for persistent storage."""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.database_url
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_db(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    async def store_state(self, state: AgentState) -> None:
        """Store agent state (not implemented for SQL - use Redis for sessions)."""
        pass
    
    async def retrieve_state(self, session_id: str) -> Optional[AgentState]:
        """Retrieve agent state (not implemented for SQL - use Redis for sessions)."""
        return None
    
    async def store_user_profile(self, profile: UserProfile) -> None:
        """Store user profile in SQL database."""
        try:
            db = self.get_db()
            try:
                # Check if profile exists
                existing = db.query(UserProfileDB).filter(
                    UserProfileDB.user_id == profile.user_id
                ).first()
                
                if existing:
                    # Update existing profile
                    existing.user_type = profile.user_type.value
                    existing.last_active = profile.last_active
                    existing.interaction_count = profile.interaction_count
                    existing.total_time_spent = profile.total_time_spent
                    existing.satisfaction_score = profile.satisfaction_score
                    existing.preferences = json.dumps(profile.preferences)
                    existing.preferred_domains = json.dumps([d.value for d in profile.preferred_domains])
                else:
                    # Create new profile
                    db_profile = UserProfileDB(
                        user_id=profile.user_id,
                        user_type=profile.user_type.value,
                        created_at=profile.created_at,
                        last_active=profile.last_active,
                        interaction_count=profile.interaction_count,
                        total_time_spent=profile.total_time_spent,
                        satisfaction_score=profile.satisfaction_score,
                        preferences=json.dumps(profile.preferences),
                        preferred_domains=json.dumps([d.value for d in profile.preferred_domains])
                    )
                    db.add(db_profile)
                
                db.commit()
                logger.debug(f"Stored user profile for {profile.user_id}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to store user profile: {e}")
    
    async def retrieve_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile from SQL database."""
        try:
            db = self.get_db()
            try:
                db_profile = db.query(UserProfileDB).filter(
                    UserProfileDB.user_id == user_id
                ).first()
                
                if db_profile:
                    preferred_domains = []
                    if db_profile.preferred_domains:
                        domain_values = json.loads(db_profile.preferred_domains)
                        preferred_domains = [LegalDomain(d) for d in domain_values]
                    
                    preferences = {}
                    if db_profile.preferences:
                        preferences = json.loads(db_profile.preferences)
                    
                    return UserProfile(
                        user_id=db_profile.user_id,
                        user_type=db_profile.user_type,
                        created_at=db_profile.created_at,
                        last_active=db_profile.last_active,
                        preferred_domains=preferred_domains,
                        interaction_count=db_profile.interaction_count,
                        total_time_spent=db_profile.total_time_spent,
                        satisfaction_score=db_profile.satisfaction_score,
                        preferences=preferences
                    )
                return None
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to retrieve user profile: {e}")
            return None
    
    async def store_interaction(self, interaction: UserInteraction) -> None:
        """Store interaction in SQL database."""
        try:
            db = self.get_db()
            try:
                db_interaction = InteractionDB(
                    interaction_id=interaction.interaction_id,
                    user_id=interaction.user_id,
                    session_id=getattr(interaction, 'session_id', ''),
                    timestamp=interaction.timestamp,
                    interaction_type=interaction.interaction_type.value,
                    query=interaction.query,
                    predicted_domain=interaction.predicted_domain.value if interaction.predicted_domain else None,
                    confidence_score=interaction.confidence_score,
                    response=interaction.response,
                    feedback=interaction.feedback.value if interaction.feedback else None,
                    time_spent=interaction.time_spent,
                    interaction_metadata=json.dumps(interaction.metadata)
                )
                db.add(db_interaction)
                db.commit()
                logger.debug(f"Stored interaction for user {interaction.user_id}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
    
    async def get_user_interactions(self, user_id: str, limit: int = 100) -> List[UserInteraction]:
        """Get user interactions from SQL database."""
        try:
            db = self.get_db()
            try:
                db_interactions = db.query(InteractionDB).filter(
                    InteractionDB.user_id == user_id
                ).order_by(InteractionDB.timestamp.desc()).limit(limit).all()
                
                interactions = []
                for db_int in db_interactions:
                    metadata = {}
                    if db_int.interaction_metadata:
                        metadata = json.loads(db_int.interaction_metadata)
                    
                    interaction = UserInteraction(
                        interaction_id=db_int.interaction_id,
                        user_id=db_int.user_id,
                        timestamp=db_int.timestamp,
                        interaction_type=db_int.interaction_type,
                        query=db_int.query,
                        predicted_domain=LegalDomain(db_int.predicted_domain) if db_int.predicted_domain else None,
                        confidence_score=db_int.confidence_score,
                        response=db_int.response,
                        feedback=db_int.feedback if db_int.feedback else None,
                        time_spent=db_int.time_spent,
                        metadata=metadata
                    )
                    interactions.append(interaction)
                
                return interactions
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to get user interactions: {e}")
            return []


class AgentMemory:
    """Unified memory management for the agent."""
    
    def __init__(self):
        self.redis_store = RedisMemoryStore()
        self.sql_store = SQLMemoryStore()
    
    async def store_state(self, state: AgentState) -> None:
        """Store agent state in Redis for fast access."""
        await self.redis_store.store_state(state)
    
    async def retrieve_state(self, session_id: str) -> Optional[AgentState]:
        """Retrieve agent state from Redis."""
        return await self.redis_store.retrieve_state(session_id)
    
    async def store_user_profile(self, profile: UserProfile) -> None:
        """Store user profile in both Redis and SQL."""
        await self.redis_store.store_user_profile(profile)
        await self.sql_store.store_user_profile(profile)
    
    async def retrieve_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile from Redis first, then SQL."""
        profile = await self.redis_store.retrieve_user_profile(user_id)
        if not profile:
            profile = await self.sql_store.retrieve_user_profile(user_id)
            if profile:
                # Cache in Redis for future access
                await self.redis_store.store_user_profile(profile)
        return profile
    
    async def store_interaction(self, interaction: UserInteraction) -> None:
        """Store interaction in both Redis and SQL."""
        await self.redis_store.store_interaction(interaction)
        await self.sql_store.store_interaction(interaction)
    
    async def get_user_interactions(self, user_id: str, limit: int = 100) -> List[UserInteraction]:
        """Get user interactions from Redis first, then SQL."""
        interactions = await self.redis_store.get_user_interactions(user_id, limit)
        if not interactions:
            interactions = await self.sql_store.get_user_interactions(user_id, limit)
        return interactions
