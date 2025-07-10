-- Create emails table if it doesn't exist
CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    data TIMESTAMP NOT NULL,
    assunto VARCHAR(255) NOT NULL,
    mensagem TEXT NOT NULL,
    email VARCHAR(255) NOT NULL
);

-- Create index on data for better performance
CREATE INDEX IF NOT EXISTS idx_emails_data ON emails(data); 