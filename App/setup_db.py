#!/usr/bin/env python3
"""
Database setup script for Resume Analyzer
This script creates the database and tables if they don't exist
"""

import pymysql
from db_config import DB_CONFIG

def setup_database():
    try:
        # Connect to MySQL server (without specifying database)
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )
        cursor = conn.cursor()
        
        print("✅ Connected to MySQL server")
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS cv")
        print("✅ Database 'cv' created or already exists")
        
        # Use the cv database
        cursor.execute("USE cv")
        
        # Create user_data table
        cursor.execute("""
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
            )
        """)
        print("✅ Table 'user_data' created or already exists")
        
        # Create user_feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                ID int NOT NULL AUTO_INCREMENT,
                feed_name varchar(500) NOT NULL,
                feed_email varchar(500) NOT NULL,
                feed_score varchar(5) NOT NULL,
                comments varchar(2000) NOT NULL,
                Timestamp varchar(50) NOT NULL,
                PRIMARY KEY (ID)
            )
        """)
        print("✅ Table 'user_feedback' created or already exists")
        
        # Create company_profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_profiles (
                ID int NOT NULL AUTO_INCREMENT,
                company_name varchar(500) NOT NULL,
                job_description text NOT NULL,
                culture_requirements text NOT NULL,
                required_skills text NOT NULL,
                job_role varchar(500) NOT NULL,
                PRIMARY KEY (ID)
            )
        """)
        print("✅ Table 'company_profiles' created or already exists")
        
        # Check if company_profiles has data, if not, insert sample data
        cursor.execute("SELECT COUNT(*) FROM company_profiles")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_companies = [
                ('TechCorp', 'We are looking for a skilled Software Developer with experience in Python, JavaScript, and database management.', 'We value innovation, teamwork, and continuous learning.', 'Python, JavaScript, SQL, Git, Agile', 'Software Developer'),
                ('DataSoft', 'Seeking a Data Scientist with expertise in machine learning, statistical analysis, and data visualization.', 'We foster a data-driven culture with emphasis on analytical thinking and collaboration.', 'Python, Machine Learning, Statistics, Pandas, Scikit-learn', 'Data Scientist'),
                ('WebDesigns Inc', 'Looking for a Frontend Developer with strong skills in HTML, CSS, JavaScript, and modern frameworks.', 'We prioritize creativity, user experience, and clean code practices.', 'HTML, CSS, JavaScript, React, Vue.js, UI/UX', 'Frontend Developer')
            ]
            
            for company in sample_companies:
                cursor.execute("""
                    INSERT INTO company_profiles (company_name, job_description, culture_requirements, required_skills, job_role) 
                    VALUES (%s, %s, %s, %s, %s)
                """, company)
            
            print("✅ Sample company profiles inserted")
        else:
            print(f"✅ Company profiles table already has {count} records")
        
        # Commit all changes
        conn.commit()
        print("✅ All database changes committed")
        
        # Test the connection with the cv database
        cursor.execute("SELECT 'Database setup completed successfully!' as Status")
        result = cursor.fetchone()
        print(f"✅ {result[0]}")
        
        cursor.close()
        conn.close()
        print("✅ Database connection closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database setup...")
    if setup_database():
        print("🎉 Database setup completed successfully!")
        print("You can now run the Resume Analyzer applications with full database support.")
    else:
        print("💥 Database setup failed. Please check your MySQL configuration.")