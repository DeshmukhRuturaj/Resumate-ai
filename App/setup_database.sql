-- Resume Analyzer Database Setup Script
-- Run this script in MySQL Workbench to create the database and tables

-- Create database
CREATE DATABASE IF NOT EXISTS cv;
USE cv;

-- Create user_data table for storing resume analysis results
CREATE TABLE IF NOT EXISTS user_data (
    ID int NOT NULL AUTO_INCREMENT,
    sec_token varchar(20) NOT NULL,
    ip_add varchar(50) NOT NULL,
    host_name varchar(50) NOT NULL,
    dev_user varchar(50) NOT NULL,
    os_name_ver varchar(50) NOT NULL,
    latlong varchar(50) NOT NULL,
    city varchar(50) NOT NULL,
    state varchar(50) NOT NULL,
    country varchar(50) NOT NULL,
    act_name varchar(50) NOT NULL,
    act_mail varchar(50) NOT NULL,
    act_mob varchar(20) NOT NULL,
    name varchar(500) NOT NULL,
    email varchar(500) NOT NULL,
    res_score varchar(10) NOT NULL,
    timestamp varchar(50) NOT NULL,
    no_of_pages varchar(5) NOT NULL,
    reco_field varchar(500) NOT NULL,
    cand_level varchar(500) NOT NULL,
    skills varchar(2000) NOT NULL,
    recommended_skills varchar(2000) NOT NULL,
    courses varchar(2000) NOT NULL,
    pdf_name varchar(500) NOT NULL,
    PRIMARY KEY (ID)
);

-- Create user_feedback table for storing user feedback
CREATE TABLE IF NOT EXISTS user_feedback (
    ID int NOT NULL AUTO_INCREMENT,
    feed_name varchar(500) NOT NULL,
    feed_email varchar(500) NOT NULL,
    feed_score varchar(5) NOT NULL,
    comments varchar(2000) NOT NULL,
    Timestamp varchar(50) NOT NULL,
    PRIMARY KEY (ID)
);

-- Create company_profiles table for company job matching
CREATE TABLE IF NOT EXISTS company_profiles (
    ID int NOT NULL AUTO_INCREMENT,
    company_name varchar(500) NOT NULL,
    job_description text NOT NULL,
    culture_requirements text NOT NULL,
    required_skills text NOT NULL,
    job_role varchar(500) NOT NULL,
    PRIMARY KEY (ID)
);

-- Insert sample data into company_profiles
INSERT INTO company_profiles (company_name, job_description, culture_requirements, required_skills, job_role) VALUES
('TechCorp', 'We are looking for a skilled Software Developer with experience in Python, JavaScript, and database management.', 'We value innovation, teamwork, and continuous learning.', 'Python, JavaScript, SQL, Git, Agile', 'Software Developer'),
('DataSoft', 'Seeking a Data Scientist with expertise in machine learning, statistical analysis, and data visualization.', 'We foster a data-driven culture with emphasis on analytical thinking and collaboration.', 'Python, Machine Learning, Statistics, Pandas, Scikit-learn', 'Data Scientist'),
('WebDesigns Inc', 'Looking for a Frontend Developer with strong skills in HTML, CSS, JavaScript, and modern frameworks.', 'We prioritize creativity, user experience, and clean code practices.', 'HTML, CSS, JavaScript, React, Vue.js, UI/UX', 'Frontend Developer');

-- Insert sample user data (optional - for testing)
INSERT INTO user_data (sec_token, ip_add, host_name, dev_user, os_name_ver, latlong, city, state, country, act_name, act_mail, act_mob, name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses, pdf_name) VALUES
('sample123', '127.0.0.1', 'localhost', 'testuser', 'Windows 10', '0.0,0.0', 'Sample City', 'Sample State', 'Sample Country', 'Test User', 'test@example.com', '1234567890', 'John Doe', 'john.doe@email.com', '75', '2024-01-01 12:00:00', '2', 'Data Science', 'Intermediate', 'Python, SQL, Excel', 'Machine Learning, Statistics', 'Python for Data Science, SQL Basics', 'sample_resume.pdf');

-- Insert sample feedback data (optional - for testing)
INSERT INTO user_feedback (feed_name, feed_email, feed_score, comments, Timestamp) VALUES
('Jane Smith', 'jane@example.com', '5', 'Great tool! Very helpful for improving my resume.', '2024-01-01 14:00:00'),
('Bob Johnson', 'bob@example.com', '4', 'Good analysis, would like more detailed suggestions.', '2024-01-01 15:30:00');

-- Display success message
SELECT 'Database setup completed successfully!' as Status;