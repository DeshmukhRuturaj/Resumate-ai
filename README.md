# 📄 Resume Analyzer & Career Recommendation System

A comprehensive AI-powered Resume Analysis and Career Recommendation System built with Streamlit and Python. This intelligent system analyzes resumes, provides insights, suggests improvements, and recommends relevant courses and career paths.

## 🌟 Features

### 📊 Resume Analysis
- **PDF Resume Parsing**: Upload and analyze PDF resumes with advanced text extraction
- **Skills Extraction**: Automatically identify technical and soft skills from resumes
- **Experience Level Detection**: Determine candidate's experience level (Fresher, Intermediate, Experienced)
- **Resume Score Calculation**: Get a comprehensive score based on various parameters
- **ATS (Applicant Tracking System) Compatibility**: Check how well your resume performs with ATS systems

### 🎯 Career Recommendations
- **Course Suggestions**: Get personalized course recommendations based on your skills and career goals
- **Interview Preparation**: Access curated interview preparation materials and videos
- **Career Path Guidance**: Receive insights on potential career trajectories
- **Skill Gap Analysis**: Identify missing skills for your desired career path

### 📈 Analytics Dashboard
- **Admin Panel**: Comprehensive analytics for administrators
- **User Statistics**: Track user engagement and resume submissions
- **Geographic Analytics**: Visualize user distribution and trends
- **Performance Metrics**: Monitor system usage and effectiveness

### 🔧 Additional Features
- **Multi-format Support**: Support for various resume formats
- **Real-time Processing**: Instant analysis and feedback
- **User-friendly Interface**: Intuitive Streamlit web interface
- **Database Integration**: Secure data storage and retrieval
- **Export Functionality**: Download analysis reports and recommendations

## 🛠️ Tech Stack

### Backend
- **Python 3.13**: Core programming language
- **Streamlit**: Web application framework for ML/AI applications
- **PyMySQL**: MySQL database connector
- **NLTK**: Natural language processing toolkit

### Resume Processing
- **pyresparser**: Resume parsing and information extraction
- **pdfminer3**: PDF text extraction and processing
- **spaCy**: Advanced natural language processing
- **Regular Expressions**: Pattern matching for data extraction

### Data Visualization
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations

### Database
- **MySQL**: Primary database for storing user data and analytics
- **pymysql**: Database connection and operations

### Additional Libraries
- **Pillow (PIL)**: Image processing
- **Geocoder & Geopy**: Geographic data processing
- **Requests**: HTTP requests handling
- **Streamlit-tags**: Enhanced UI components

## 🚀 Installation & Setup

### Prerequisites
- Python 3.13 or higher
- MySQL Server
- Git (for cloning the repository)

### Step 1: Clone the Repository
```bash
git clone https://github.com/DeshmukhRuturaj/Resumate-ai.git
cd Resume-Analyser-Python
```

### Step 2: Install Dependencies
```bash
cd App
pip install -r requirements.txt
```

### Step 3: MySQL Database Setup
1. **Install MySQL Server** on your system
2. **Start MySQL Service**
3. **Configure Database Connection**:
   - Open `db_config.py`
   - Update your MySQL credentials:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'your_mysql_username',
       'password': 'your_mysql_password',
       'db': 'cv',
       'charset': 'utf8mb4'
   }
   ```

### Step 4: Initialize Database
```bash
python setup_db.py
```
This will create the required database and tables automatically.

### Step 5: Download NLTK Data
The application will automatically download required NLTK data on first run, but you can also do it manually:
```python
import nltk
nltk.download('stopwords')
```

## 🏃‍♂️ Running the Application

### Method 1: Basic Run
```bash
cd App
streamlit run App_Updated_Backup.py
```

### Method 2: Custom Port
```bash
cd App
streamlit run App_Updated_Backup.py --server.port 8501
```

### Method 3: Alternative App Version
```bash
cd App
streamlit run App.py
```

The application will open in your web browser at `http://localhost:8501`

## 📁 Project Structure

```
Resume-Analyser-Python/
├── App/
│   ├── App.py                     # Main application file
│   ├── App_Updated_Backup.py      # Updated version of the application
│   ├── Courses.py                 # Course recommendations data
│   ├── db_config.py               # Database configuration
│   ├── setup_db.py                # Database setup script
│   ├── requirements.txt           # Python dependencies
│   ├── Logo/                      # Application logos and images
│   └── Uploaded_Resumes/          # Storage for uploaded resume files
├── pyresparser/
│   └── resume_parser.py           # Custom resume parsing utilities
├── screenshots/                   # Application screenshots
├── LICENSE                        # License information
└── README.md                      # This file
```

## 🎯 Usage Guide

### For Job Seekers
1. **Upload Resume**: Upload your PDF resume through the web interface
2. **Get Analysis**: Receive comprehensive analysis including:
   - Resume score and rating
   - Skills extraction
   - Experience level assessment
   - Improvement suggestions
3. **View Recommendations**: Get personalized course and career recommendations
4. **Download Report**: Export your analysis report

### For Administrators
1. **Access Admin Panel**: Use admin credentials to access analytics
2. **View User Statistics**: Monitor user engagement and submissions
3. **Analyze Trends**: View geographic distribution and usage patterns
4. **Export Data**: Download user data and analytics reports

## 🔒 Database Schema

The application uses the following main tables:
- **user_data**: Stores resume analysis results and user information
- **feedback**: Collects user feedback and ratings
- **admin_data**: Stores administrative information and settings

## 🛡️ Security Features

- **Input Validation**: Comprehensive validation of uploaded files
- **SQL Injection Protection**: Parameterized queries for database operations
- **File Type Validation**: Strict validation of uploaded file formats
- **Error Handling**: Robust error handling and logging

## 🔧 Configuration

### Environment Variables
You can configure the following settings in `db_config.py`:
- Database host, username, and password
- Database name and charset
- Connection parameters

### Application Settings
Streamlit configuration can be customized through `.streamlit/config.toml`:
```toml
[server]
port = 8501
address = "localhost"

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## 📊 Features in Detail

### Resume Scoring Algorithm
The system uses a multi-factor scoring algorithm considering:
- Skills relevance and quantity
- Experience level appropriateness
- Resume structure and formatting
- ATS compatibility factors
- Industry-specific requirements

### Course Recommendation Engine
- **Skill-based Matching**: Recommends courses based on extracted skills
- **Career Path Analysis**: Suggests learning paths for career progression
- **Industry Trends**: Incorporates current industry demands
- **Personalized Learning**: Adapts to user's experience level

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```
   Solution: Check MySQL service status and db_config.py credentials
   ```

2. **Module Import Error**
   ```
   Solution: Ensure all dependencies are installed using pip install -r requirements.txt
   ```

3. **NLTK Data Error**
   ```
   Solution: Run nltk.download('stopwords') in Python console
   ```

4. **File Upload Issues**
   ```
   Solution: Ensure PDF files are not password-protected and are readable
   ```

### Performance Optimization
- Use SSD storage for faster file processing
- Increase MySQL connection pool size for high traffic
- Consider using Redis for session management in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Shripad735** - *Initial work* - [GitHub](https://github.com/Shripad735)
- **RuturajD1517** - *Final work* - [GitHub](https://github.com/DeshmukhRuturaj)


## 🙏 Acknowledgments

- Thanks to the open-source community for the amazing libraries
- Special thanks to Streamlit for the excellent web framework
- NLTK and spaCy teams for natural language processing capabilities
- Contributors and testers who helped improve this project

## 📞 Support

For support, email [your-email] or create an issue in the GitHub repository.

## 🔄 Version History

- **v2.0**: Enhanced UI, improved parsing accuracy, added admin analytics
- **v1.5**: Added course recommendations and career guidance
- **v1.0**: Initial release with basic resume analysis

---

⭐ **Star this repository if you found it helpful!**

## 🚀 Future Enhancements

- [ ] Integration with job portals APIs
- [ ] Machine learning model for better skill extraction
- [ ] Support for multiple file formats (DOC, DOCX)
- [ ] Real-time collaboration features
- [ ] Mobile-responsive design improvements
- [ ] Advanced analytics with predictive modeling
- [ ] Multi-language support
- [ ] API endpoints for third-party integrations
