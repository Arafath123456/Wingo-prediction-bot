from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class WingoRound(Base):
    __tablename__ = 'wingo_rounds'
    
    issue_number = Column(String(20), primary_key=True)
    winning_number = Column(Integer, nullable=False)
    draw_time = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), 
                       default=lambda: datetime.now(timezone.utc))
    
    @property
    def color(self):
        if self.winning_number == 5:
            return "Green"
        elif self.winning_number in [1, 3, 7, 9]:
            return "Red"
        return "Violet"
    
    @property
    def size(self):
        return "Big" if self.winning_number >= 5 else "Small"