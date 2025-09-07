-- Initial database schema for medical referral system

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100),
    age INTEGER,
    sex VARCHAR(10),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Referral requests table
CREATE TABLE IF NOT EXISTS referral_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id VARCHAR(50),
    referring_location VARCHAR(100),
    staff_name VARCHAR(100),
    cases_data TEXT,
    prioritization_result TEXT,
    context_data TEXT,
    referral_date DATE DEFAULT CURRENT_DATE,
    referral_time TIME DEFAULT CURRENT_TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    urgency_level VARCHAR(20),
    specialty VARCHAR(50),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- Query logs table
CREATE TABLE IF NOT EXISTS query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referral_request_id INTEGER,
    query_text TEXT,
    query_type VARCHAR(20),
    response_llama TEXT,
    response_llava TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (referral_request_id) REFERENCES referral_requests(id)
);