
-- Indices para melhorar performance de queries

-- AdminLog
CREATE INDEX IF NOT EXISTS idx_admin_log_admin_id ON admin_log(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_log_created_at ON admin_log(created_at);
CREATE INDEX IF NOT EXISTS idx_admin_log_action ON admin_log(action);

-- Notification
CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notification(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_read ON notification(is_read);
CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notification(created_at);

-- DatabaseBackup
CREATE INDEX IF NOT EXISTS idx_backup_created_at ON database_backup(created_at);
CREATE INDEX IF NOT EXISTS idx_backup_type ON database_backup(backup_type);

-- User
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
CREATE INDEX IF NOT EXISTS idx_user_is_admin ON user(is_admin);

-- Challenge
CREATE INDEX IF NOT EXISTS idx_challenge_level ON challenge(level_required);

-- UserChallenge
CREATE INDEX IF NOT EXISTS idx_user_challenge_user ON user_challenge(user_id);
CREATE INDEX IF NOT EXISTS idx_user_challenge_completed ON user_challenge(completed_at);
