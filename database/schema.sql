-- Student Mistakes Management System Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Mistakes table
CREATE TABLE mistakes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    image_path VARCHAR(500) NOT NULL,
    ocr_text TEXT NOT NULL,
    subject VARCHAR(100),
    error_type VARCHAR(50), -- 'conceptual', 'calculation', 'misreading'
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    ai_insights JSONB, -- Store AI analysis results
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Review History table
CREATE TABLE review_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mistake_id UUID NOT NULL REFERENCES mistakes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    review_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    performance_rating INTEGER CHECK (performance_rating >= 0 AND performance_rating <= 5),
    time_spent_seconds INTEGER,
    notes TEXT
);

-- Achievements table
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_type VARCHAR(50) NOT NULL, -- 'streak', 'total_reviews', 'accuracy'
    achievement_name VARCHAR(100) NOT NULL,
    description TEXT,
    points_awarded INTEGER DEFAULT 0,
    unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Progress table
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    total_reviews INTEGER DEFAULT 0,
    total_points INTEGER DEFAULT 0,
    last_review_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scheduled Reviews table
CREATE TABLE scheduled_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mistake_id UUID NOT NULL REFERENCES mistakes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scheduled_date TIMESTAMP WITH TIME ZONE NOT NULL,
    interval_days INTEGER NOT NULL DEFAULT 1,
    ease_factor DECIMAL(3,2) DEFAULT 2.5,
    repetitions INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_mistakes_user_id ON mistakes(user_id);
CREATE INDEX idx_mistakes_created_at ON mistakes(created_at);
CREATE INDEX idx_review_history_mistake_id ON review_history(mistake_id);
CREATE INDEX idx_review_history_user_id ON review_history(user_id);
CREATE INDEX idx_achievements_user_id ON achievements(user_id);
CREATE INDEX idx_scheduled_reviews_user_id ON scheduled_reviews(user_id);
CREATE INDEX idx_scheduled_reviews_scheduled_date ON scheduled_reviews(scheduled_date);
CREATE INDEX idx_scheduled_reviews_completed ON scheduled_reviews(is_completed);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mistakes_updated_at BEFORE UPDATE ON mistakes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_progress_updated_at BEFORE UPDATE ON user_progress FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_scheduled_reviews_updated_at BEFORE UPDATE ON scheduled_reviews FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();