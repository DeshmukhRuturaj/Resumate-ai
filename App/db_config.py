# Database Configuration for Resume Analyzer
# Update with your MySQL credentials

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # Updated with your MySQL password
    'db': 'cv',
    'charset': 'utf8mb4'
}

# If you're using a different MySQL setup, you can modify these values:
# For example, if you have a password set:
# DB_CONFIG['password'] = 'your_mysql_password'

# For custom port (default is 3306):
# DB_CONFIG['port'] = 3306