import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.session import Base, get_session as _get_session
from data_ingestion.models import WingoRound
import os
from dotenv import load_dotenv

load_dotenv()

# Test database setup
TEST_DB_URL = "postgresql://test:test@localhost:5433/test_db"

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()

@pytest.fixture
def test_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_data(test_session):
    # Create sample game data
    rounds = []
    for i in range(1, 501):
        rounds.append(WingoRound(
            issue_number=str(1000 + i),
            winning_number=i % 10,
            draw_time=f"2023-01-01 {i//60:02d}:{i%60:02d}:00"
        ))
    
    test_session.add_all(rounds)
    test_session.commit()
    
    return test_session