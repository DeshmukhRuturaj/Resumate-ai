#Made with Streamlit


###### Packages Used ######
import pandas as pd
import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time,datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
# libraries used to parse the pdf files
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
# pre stored data for prediction purposes
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos,cyber_course,cloud_course,iot_course,ml_course,devops_course,ai_course
import nltk
nltk.download('stopwords')
import requests


###### Preprocessing functions ######


# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# course recommendations which has data already loaded from Courses.py
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
    c = 0
    rec_course = []
    ## slider to choose from range 1-10
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


###### Database Stuffs ######

# Import database configuration
try:
    from db_config import DB_CONFIG
except ImportError:
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root', 
        'password': '',
        'db': 'cv',
        'charset': 'utf8mb4'
    }

# Mock database objects for fallback when MySQL is not available
class MockCursor:
    def execute(self, query, values=None):
        if values:
            print(f"Mock DB: Would execute query with values: {values[:3]}..." if len(values) > 3 else f"Mock DB: Would execute query with values: {values}")
        else:
            print(f"Mock DB: Would execute query: {query[:50]}...")
        pass
    
    def fetchall(self):
        # Return mock data for SELECT queries
        return []  # Return empty results for queries
    
    def commit(self):
        pass
    
class MockConnection:
    def cursor(self):
        return MockCursor()
    
    def commit(self):
        print("Mock DB: Would commit transaction")
        pass

# Try to connect to MySQL, fall back to mock if connection fails
try:
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    print("✅ Connected to MySQL database successfully!")
    using_real_db = True
except Exception as e:
    print(f"⚠️ Could not connect to MySQL database: {e}")
    print("📝 Using mock database for demo purposes")
    connection = MockConnection()
    cursor = connection.cursor()
    using_real_db = False


# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    insertfeed_sql = "insert into " + DBf_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()


###### Company Profile Functions ######

# Function to insert company profile into the database
def insert_company_profile(company_name, job_description, culture_requirements, required_skills, job_role):
    DB_table_name = 'company_profiles'
    insert_sql = "INSERT INTO " + DB_table_name + " (company_name, job_description, culture_requirements, required_skills, job_role) VALUES (%s, %s, %s, %s, %s)"
    rec_values = (company_name, job_description, culture_requirements, required_skills, job_role)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

# Function to match resume with company profiles
def match_resume_with_companies(resume_data):
    query = "SELECT * FROM company_profiles"
    cursor.execute(query)
    company_profiles = cursor.fetchall()
    
    matches = []
    for profile in company_profiles:
        company_name, job_description, culture_requirements, required_skills, job_role = profile[1], profile[2], profile[3], profile[4], profile[5]
        score, alignment = calculate_compatibility_score(resume_data, job_description, culture_requirements, required_skills)
        matches.append((company_name, score, alignment, job_role))
    
    # Sort matches by score and return top 3
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:3]

# Function to calculate compatibility score
def calculate_compatibility_score(resume_data, job_description, culture_requirements, required_skills):
    score = 0
    alignment = []
    
    for skill in resume_data['skills']:
        if skill.lower() in job_description.lower() or skill.lower() in required_skills.lower():
            score += 10
            alignment.append(skill)
    
    # Add culture matching logic here
    # For now, let's assume that the culture requirements are not matched
    culture_score = 0
    culture_alignment = []
    
    score += culture_score
    alignment += culture_alignment

    return score, alignment


###### Job Search API Function ######

def fetch_job_listings(query, limit="5"):
    """Fetch job listings from Glassdoor API"""
    url = "https://glassdoor-real-time.p.rapidapi.com/salaries/search"
    
    querystring = {
        "query": query,
        "limit": limit
    }
    
    headers = {
        "x-rapidapi-key": "f11509220amshacdf4a37eb0525bp13b188jsn95e091e6f6f7",
        "x-rapidapi-host": "glassdoor-real-time.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        print("API Response Status Code:", response.status_code)
        print("API Response JSON:", response.json())
        return response.json()
    except Exception as e:
        print("API Error:", str(e))
        return None


###### Setting Page Configuration (favicon, Logo, Title) ######


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon='./Logo/recommend.png',
    layout="wide",  # Use wide layout for better spacing
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
    <style>
    /* Main Content Area */
    .main {
        padding: 2.5rem;
        background-color: #f0f5ff;  /* Light blue background */
        font-family: 'Open Sans', sans-serif;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;  /* Dark blue-grey */
        font-weight: 600;
        margin-bottom: 1.2rem;
    }

    /* Cards for important sections */
    .stCard {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
        border-left: 4px solid #3498db;  /* Blue accent */
    }

    /* Special cards */
    .personal-details-card {
        background-color: #ebf7ff;  /* Light blue */
        border-left: 4px solid #2980b9;  /* Darker blue */
    }

    .upload-card {
        background-color: #e8f5e9;  /* Light green */
        border-left: 4px solid #27ae60;  /* Green accent */
    }

    .results-card {
        background-color: #fff8e1;  /* Light yellow */
        border-left: 4px solid #f39c12;  /* Orange accent */
    }

    /* Buttons */
    .stButton>button {
        background-color: #3498db;
        color: #fff;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980b9;
        transform: translateY(-1px);
    }

    /* Progress bars */
    .stProgress > div > div > div > div {
        background-color: #3498db;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #2c3e50;
    }
    .css-1d391kg, .sidebar .sidebar-content {
        color: #ecf0f1;
    }

    /* File uploader */
    .uploadedFile {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }

    /* Success and warning messages */
    .success {
        background-color: #27ae60;
        color: #fff;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning {
        background-color: #e67e22;
        color: #fff;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    /* Tags */
    .stTags {
        background-color: #e8f0fe;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        margin: 0.25rem;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)


###### Main function run() ######


def run():
    
    # Get the directory where the script is located for proper file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # (Logo, Heading, Sidebar etc)
    try:
        logo_path = os.path.join(script_dir, 'Logo', 'Resu.png')
        img = Image.open(logo_path)
        st.image(img)
    except FileNotFoundError:
        st.title("📄 Resume Analyzer")
        st.write("Logo not found, but the app is working!")
    
    st.sidebar.markdown("# Choose Something...")
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    link = '<b>Built with 🤍 by <a href="" style="text-decoration: none; color: #021659;">Team Resumate AI</a></b>' 
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.sidebar.markdown('''
        <!-- site visitors -->

        <div id="sfct2xghr8ak6lfqt3kgru233378jya38dy" hidden></div>

        <noscript>
            <a href="https://www.freecounterstat.com" title="hit counter">
                <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" border="0" title="hit counter" alt="hit counter"> -->
            </a>
        </noscript>
    
        <p>Visitors <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" title="Free Counter" Alt="web counter" width="60px"  border="0" /></p>
    
    ''', unsafe_allow_html=True)

    ###### Creating Database and Table ######


    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)


    # Create table user_data and user_feedback
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    sec_token varchar(20) NOT NULL,
                    ip_add varchar(50) NULL,
                    host_name varchar(50) NULL,
                    dev_user varchar(50) NULL,
                    os_name_ver varchar(50) NULL,
                    latlong varchar(50) NULL,
                    city varchar(50) NULL,
                    state varchar(50) NULL,
                    country varchar(50) NULL,
                    act_name varchar(50) NOT NULL,
                    act_mail varchar(50) NOT NULL,
                    act_mob varchar(20) NOT NULL,
                    Name varchar(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    pdf_name varchar(50) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                        feed_name varchar(50) NOT NULL,
                        feed_email VARCHAR(50) NOT NULL,
                        feed_score VARCHAR(5) NOT NULL,
                        comments VARCHAR(100) NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        PRIMARY KEY (ID)
                    );
                """
    cursor.execute(tablef_sql)

    # Create table company_profiles
    DB_table_name = 'company_profiles'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    company_name varchar(100) NOT NULL,
                    job_description TEXT NOT NULL,
                    culture_requirements TEXT NOT NULL,
                    required_skills TEXT NOT NULL,
                    job_role varchar(100) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    ###### CODE FOR CLIENT SIDE (USER) ######

    if choice == 'User':
        
        # Create columns for better layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
                <div class="stCard upload-card">
                    <h2 style='color: #27ae60;'>📄 Upload Your Resume</h2>
                    <p>Get smart recommendations and detailed analysis</p>
                </div>
                
                <div class="stCard personal-details-card">
                    <h2 style='color: #2980b9;'>👤 Personal Details</h2>
                    <p>Please fill in your information</p>
                """, unsafe_allow_html=True)
            
            act_name = st.text_input('Full Name*', placeholder="John Doe")
            act_mail = st.text_input('Email Address*', placeholder="john@example.com")
            act_mob = st.text_input('Mobile Number*', placeholder="+1 234 567 8900")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            # Display user stats or tips
            st.markdown("""
                <div class="stCard">
                    <h3>💡 Quick Tips</h3>
                    <ul>
                        <li>Upload PDF format only</li>
                        <li>Make sure the file is readable</li>
                        <li>Include updated information</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        # Collecting Miscellaneous Information
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_ver = platform.system() + " " + platform.release()
        
        # Try to get location information with proper error handling
        try:
            g = geocoder.ip('me')
            latlong = g.latlng
            geolocator = Nominatim(user_agent="http", timeout=10)
            location = geolocator.reverse(latlong, language='en')
            address = location.raw['address']
            cityy = address.get('city', '')
            statee = address.get('state', '')
            countryy = address.get('country', '')  
            city = cityy
            state = statee
            country = countryy
        except Exception as e:
            print(f"⚠️ Geocoding failed: {e}")
            # Use fallback location data
            latlong = [0.0, 0.0]
            city = "Unknown"
            state = "Unknown"
            country = "Unknown"


        # Upload Resume
        st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload Your Resume, And Get Smart Recommendations</h5>''',unsafe_allow_html=True)
        
        ## file upload in pdf format
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Hang On While We Cook Magic For You...'):
                time.sleep(4)
        
            ### saving the uploaded resume to folder
            save_image_path = os.path.join(script_dir, 'Uploaded_Resumes', pdf_file.name)
            pdf_name = pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            ### parsing and extracting whole resume 
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                
                ## Get the whole resume data into resume_text
                resume_text = pdf_reader(save_image_path)

                ## Showing Analyzed data from (resume_data)
                st.header("**Resume Analysis 🤘**")
                st.success("Hello "+ resume_data['name'])
                st.subheader("**Your Basic info 👀**")
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Degree: '+str(resume_data['degree']))                    
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))

                except:
                    pass
                ## Predicting Candidate Experience Level 

                ### Trying with different possibilities
                cand_level = ''
                if resume_data['no_of_pages'] < 1:                
                    cand_level = "NA"
                    st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                
                #### if internship then intermediate level
                elif 'INTERNSHIP' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIPS' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internship' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internships' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                
                #### if Work Experience/Experience then Experience level
                elif 'EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'WORK EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!</h4>''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!</h4>''',unsafe_allow_html=True)
                elif 'Work Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!</h4>''',unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',unsafe_allow_html=True)


                ## Skills Analyzing and Recommendation
                st.subheader("**Skills Recommendation 💡**")
                
                ### Current Analyzed Skills
                keywords = st_tags(label='### Your Current Skills',
                text='See our skills recommendation below',value=resume_data['skills'],key = '1  ')

                ### Keywords for Recommendations
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']
                cyber_keyword = ['cyber security','ethical hacking','network security','information security','penetration testing','cryptography','security analysis','security auditing','security testing','security monitoring','security compliance','security operations','security incident response','security architecture','security engineering','security consulting','security awareness','security policy','security governance','security risk management','security training','security certification','security standards','security best practices','security tools','security software','security hardware','security protocols','security procedures','security guidelines','security frameworks','security controls','security measures','security strategies','security tactics','security techniques','security technologies','security concepts','security principles','security practices','security operations','security management','security administration','security operations center','security information and event management','security information management','security information systems management','security information systems administration','security information systems operations','security information systems architecture','security information systems design','security information systems development','security information systems implementation','security information systems maintenance','security information systems support','security information systems monitoring','security information systems analysis','security information systems testing','security information systems evaluation','security information systems assessment','security information systems audit','security information systems compliance','security information systems governance','security information systems risk management','security information systems incident response','security information systems architecture','security information systems engineering','security information systems consulting','security information systems awareness','security information systems policy','security information systems standards','security information systems best practices','security information systems tools','security information systems software','security information systems hardware','security information systems protocols','security information systems procedures','security information systems guidelines','security information systems frameworks','security information systems controls','security information systems measures','security information systems strategies','security information systems tactics','security information systems techniques','security information systems technologies','security information systems concepts','security information systems principles','security information systems practices','security information systems operations','security information systems management','security information systems administration','security information systems operations center','security information systems information and event management','security information systems information management','security information systems information systems management','security information systems information systems administration','security information systems information systems operations','security information systems information systems architecture','security information systems information systems design','security information systems information systems development','security information systems information systems implementation','security information systems information systems maintenance','security information systems information systems support','security information systems information systems monitoring','security information systems information systems analysis','security information systems information systems testing','security information systems information systems evaluation','security information systems information systems assessment','security information systems information systems audit','security information systems information systems compliance','security information systems information systems governance','security information systems information systems risk management','security information systems information systems incident response','security information systems information systems architecture','security information systems information systems engineering','security information systems information systems consulting','security information systems information systems awareness','security information systems information systems policy','security information systems information systems standards','security information systems information systems best practices','security information systems information systems tools','security information systems information systems software','security information systems information systems hardware','security information systems information systems protocols','security information systems information systems procedures','security information systems information systems guidelines','security information systems information systems frameworks','security information systems information systems controls','security information systems information systems measures','security information systems information systems strategies','security information systems information systems tactics','security information systems information systems techniques','security information systems information systems technologies','security information systems information systems concepts','security information systems information systems principles','security information systems information systems practices','security information systems information systems operations','security information systems information systems management','security information systems information systems administration','security information systems information systems operations center','security information systems information and event management','security information systems information management','security information systems information systems management','security information systems information systems administration','security information systems information systems operations','security information systems information systems architecture','security information systems information systems design','security information systems information systems development','security information systems information systems implementation','security information systems information systems maintenance    ']
                cloud_keyword = ['cloud computing','aws','amazon web services','microsoft azure','google cloud','google cloud platform','ibm cloud','ibm cloud platform','oracle cloud','oracle cloud platform','alibaba cloud','alibaba cloud platform','tencent cloud','tencent cloud platform','cloud security','cloud architecture','cloud design','cloud development','cloud implementation','cloud migration','cloud monitoring','cloud management','cloud administration','cloud operations','cloud governance','cloud compliance','cloud risk management','cloud incident response','cloud architecture','cloud engineering','cloud consulting','cloud awareness','cloud policy','cloud standards','cloud best practices','cloud tools','cloud software','cloud hardware','cloud protocols','cloud procedures','cloud guidelines','cloud frameworks','cloud controls','cloud measures','cloud strategies','cloud tactics','cloud techniques','cloud technologies','cloud concepts','cloud principles','cloud practices','cloud operations','cloud management','cloud administration','cloud operations center','cloud information and event management','cloud information management','cloud information systems management','cloud information systems administration','cloud information systems operations','cloud information systems architecture','cloud information systems design','cloud information systems development','cloud information systems implementation','cloud information systems maintenance','cloud information systems support','cloud information systems monitoring','cloud information systems analysis','cloud information systems testing','cloud information systems evaluation','cloud information systems assessment','cloud information systems audit','cloud information systems compliance','cloud information systems governance','cloud information systems risk management','cloud information systems incident response','cloud information systems architecture','cloud information systems engineering','cloud information systems consulting','cloud information systems awareness','cloud information systems policy','cloud information systems standards','cloud information systems best practices','cloud information systems tools','cloud information systems software','cloud information systems hardware','cloud information systems protocols','cloud information systems procedures','cloud information systems guidelines','cloud information systems frameworks','cloud information systems controls','cloud information systems measures','cloud information systems strategies','cloud information systems tactics','cloud information systems techniques','cloud information systems technologies','cloud information systems concepts','cloud information systems principles','cloud information systems practices','cloud information systems operations','cloud information systems management','cloud information systems administration','cloud information systems operations center','cloud information systems information and event management','cloud information systems information management','cloud information systems information systems management','cloud information systems information systems administration','cloud information systems information systems operations','cloud information systems information systems architecture','cloud information systems information systems design','cloud information systems information systems development','cloud information systems information systems implementation','cloud information systems information systems maintenance    ']
                iot_keyword = ['iot','internet of things','iot security','iot architecture','iot design','iot development','iot implementation','iot monitoring','iot management','iot administration','iot operations','iot governance','iot compliance','iot risk management','iot incident response','iot architecture','iot engineering','iot consulting','iot awareness','iot policy','iot standards','iot best practices','iot tools','iot software','iot hardware','iot protocols','iot procedures','iot guidelines','iot frameworks','iot controls','iot measures','iot strategies','iot tactics','iot techniques','iot technologies','iot concepts','iot principles','iot practices','iot operations','iot management','iot administration','iot operations center','iot information and event management','iot information management','iot information systems management','iot information systems administration','iot information systems operations','iot information systems architecture','iot information systems design','iot information systems development','iot information systems implementation','iot information systems maintenance','iot information systems support','iot information systems monitoring','iot information systems analysis','iot information systems testing','iot information systems evaluation','iot information systems assessment','iot information systems audit','iot information systems compliance','iot information systems governance','iot information systems risk management','iot information systems incident response','iot information systems architecture','iot information systems engineering','iot information systems consulting','iot information systems awareness','iot information systems policy','iot information systems standards','iot information systems best practices','iot information systems tools','iot information systems software','iot information systems hardware','iot information systems protocols','iot information systems procedures','iot information systems guidelines','iot information systems frameworks','iot information systems controls','iot information systems measures','iot information systems strategies','iot information systems tactics','iot information systems techniques','iot information systems technologies','iot information systems concepts','iot information systems principles','iot information systems practices','iot information systems operations','iot information systems management','iot information systems administration','iot information systems operations center','iot information systems information and event management','iot information systems information management','iot information systems information systems management','iot information systems information systems administration','iot information systems information systems operations','iot information systems information systems architecture','iot information systems information systems design','iot information systems information systems development','iot information systems information systems implementation','iot information systems information systems maintenance','iot information systems information systems support','iot information systems information systems monitoring','iot information systems information systems analysis','iot information systems information systems testing','iot information systems information systems evaluation','iot information systems information systems assessment','iot information systems information systems audit','iot information systems information systems compliance',' ']
                ml_keyword = ['machine learning','deep learning','data science','data analysis','data visualization','predictive analysis','statistical modeling','data mining','clustering & classification','data analytics','quantitative analysis','web scraping','ml algorithms','keras','pytorch','probability','scikit-learn','tensorflow','flask','streamlit']  
                devops_keyword = ['devops','continuous integration','continuous deployment','continuous delivery','continuous monitoring','continuous testing','continuous feedback','continuous improvement','continuous development','continuous operations','continuous security','continuous compliance','continuous risk management','continuous incident response','continuous architecture','continuous engineering','continuous consulting','continuous awareness','continuous policy','continuous standards','continuous best practices','continuous tools','continuous software','continuous hardware','continuous protocols','continuous procedures','continuous guidelines','continuous frameworks','continuous controls','continuous measures','continuous strategies','continuous tactics','continuous techniques','continuous technologies','continuous concepts','continuous principles','continuous practices','continuous operations','continuous management','continuous administration','continuous operations center','continuous information and event management','continuous information management','continuous information systems management','continuous information systems administration','continuous information systems operations','continuous information systems architecture','continuous information systems design','continuous information systems development','continuous information systems implementation','continuous information systems maintenance','continuous information systems support','continuous information systems monitoring','continuous information systems analysis','continuous information systems testing','continuous information systems evaluation','continuous information systems assessment','continuous information systems audit','continuous information systems compliance','continuous information systems governance','continuous information systems risk management','continuous information systems incident response','continuous information systems architecture','continuous information systems engineering','continuous information systems consulting','continuous information systems awareness','continuous information systems policy','continuous information systems standards','continuous information systems best practices','continuous information systems tools','continuous information systems software','continuous information systems hardware','continuous information systems protocols','continuous information systems procedures','continuous information systems guidelines','continuous information systems frameworks','continuous information systems controls','continuous information systems measures','continuous information systems strategies','continuous information systems tactics','continuous information systems techniques','continuous information systems technologies','continuous information systems concepts','continuous information systems principles','continuous information systems practices','continuous information systems operations','continuous information systems management','continuous information systems administration','continuous information systems operations center','continuous information systems information and event management','continuous information systems information management','continuous information systems information systems management','continuous information systems information systems administration','continuous information systems information systems operations','continuous information systems information systems architecture','continuous information systems information systems design','continuous information systems information systems development','continuous information systems information systems implementation','continuous information systems information systems maintenance','continuous information systems information systems support','continuous information systems information systems monitoring','continuous information systems information systems analysis   ']
                ai_keyword = ['artificial intelligence','ai','machine learning','deep learning','data science','data analysis','data visualization','predictive analysis','statistical modeling','data mining','clustering & classification','data analytics','quantitative analysis','web scraping','ml algorithms','keras','pytorch','probability','scikit-learn','tensorflow','flask','streamlit','natural language processing','nlp','speech recognition','image recognition','object detection','object recognition','face recognition','emotion recognition','gesture recognition','handwriting recognition','pattern recognition','voice recognition','speaker recognition','speaker identification','speaker verification','speaker diarization','speaker separation','speaker localization','speaker tracking','speaker counting','speaker clustering','speaker classification','speaker labeling','speaker tagging','speaker annotation','speaker transcription','speaker translation','speaker synthesis','speaker generation','speaker conversion','speaker enhancement','speaker normalization','speaker equalization','speaker adaptation','speaker alignment','speaker registration','speaker calibration','speaker verification','speaker identification','speaker diarization','speaker separation    ']


                ### Skill Recommendations Starts                
                recommended_skills = []
                reco_field = ''
                rec_course = ''

                ### condition starts to check skills from keywords and predict field
                for i in resume_data['skills']:
                
                    #### Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '2')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ds_course)
                        break

                    #### Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '3')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(web_course)
                        break

                    #### Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '4')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(android_course)
                        break

                    #### IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '5')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ios_course)
                        break

                    #### Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(uiux_course)
                        break

                    #### Cyber Security Recommendation
                    elif i.lower() in cyber_keyword:
                        print(i.lower())
                        reco_field = 'Cyber Security'
                        st.success("** Our analysis says you are looking for Cyber Security Jobs **")
                        recommended_skills = ['Cyber Security','Ethical Hacking','Network Security','Information Security','Penetration Testing','Cryptography','Security Analysis','Security Auditing','Security Testing','Security Monitoring','Security Compliance','Security Operations','Security Incident Response','Security Architecture','Security Engineering','Security Consulting','Security Awareness','Security Policy','Security Governance','Security Risk Management','Security Training','Security Certification','Security Standards','Security Best Practices','Security Tools','Security Software','Security Hardware','Security Protocols','Security Procedures','Security Guidelines','Security Frameworks','Security Controls','Security Measures','Security Strategies','Security Tactics','Security Techniques','Security Technologies','Security Concepts','Security Principles','Security Practices','Security Operations','Security Management','Security Administration','Security Operations Center','Security Information and Event Management','Security Information Management','Security Information Systems Management','Security Information Systems Administration','Security Information Systems Operations','Security Information Systems Architecture','Security Information Systems Design','Security Information Systems Development','Security Information Systems Implementation','Security Information Systems Maintenance','Security Information Systems Support','Security Information Systems Monitoring','Security Information Systems Analysis','Security Information Systems Testing','Security Information Systems Evaluation','Security Information Systems Assessment','Security Information Systems Audit','Security Information Systems Compliance','Security Information Systems Governance','Security Information Systems Risk Management','Security Information Systems Incident Response','Security Information Systems Architecture','Security Information Systems Engineering','Security Information Systems Consulting','Security Information Systems Awareness','Security Information Systems Policy','Security Information Systems Standards','Security Information Systems Best Practices','Security Information Systems Tools','Security Information Systems Software','Security Information Systems Hardware','Security Information Systems Protocols','Security Information Systems Procedures','Security Information Systems Guidelines','Security Information Systems Frameworks','Security Information Systems Controls','Security Information Systems Measures','Security Information Systems Strategies','Security Information Systems Tactics','Security Information Systems Techniques','Security Information Systems Technologies','Security Information Systems Concepts','Security Information Systems Principles','Security Information Systems Practices','Security Information Systems Operations','Security Information Systems Management','Security Information Systems Administration','Security Information Systems Operations Center','Security Information Systems Information and Event Management','Security Information Systems Information Management','Security Information Systems Information Systems Management','Security Information Systems Information Systems Administration','Security Information Systems Information Systems Operations','Security Information Systems Information Systems Architecture','Security Information Systems Information Systems Design','Security Information Systems Information Systems Development','Security Information Systems Information Systems Implementation','Security Information Systems Information Systems  ']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System',value=recommended_skills,key = '7')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)   
                        # course recommendation
                        rec_course = course_recommender(cyber_course)
                        break

                    #### Cloud Computing Recommendation
                    elif i.lower() in cloud_keyword:
                        print(i.lower())
                        reco_field = 'Cloud Computing'
                        st.success("** Our analysis says you are looking for Cloud Computing Jobs **")
                        recommended_skills = ['Cloud Computing','AWS','Amazon Web Services','Microsoft Azure','Google Cloud','Google Cloud Platform','IBM Cloud','IBM Cloud Platform','Oracle Cloud','Oracle Cloud Platform','Alibaba Cloud','Alibaba Cloud Platform','Tencent Cloud','Tencent Cloud Platform','Cloud Security','Cloud Architecture','Cloud Design','Cloud Development','Cloud Implementation','Cloud Migration','Cloud Monitoring','Cloud Management','Cloud Administration','Cloud Operations','Cloud Governance','Cloud Compliance','Cloud Risk Management','Cloud Incident Response','Cloud Architecture','Cloud Engineering','Cloud Consulting','Cloud Awareness','Cloud Policy','Cloud Standards','Cloud Best Practices','Cloud Tools','Cloud Software','Cloud Hardware','Cloud Protocols','Cloud Procedures','Cloud Guidelines','Cloud Frameworks','Cloud Controls','Cloud Measures','Cloud Strategies','Cloud Tactics','Cloud Techniques','Cloud Technologies','Cloud Concepts','Cloud Principles','Cloud Practices','Cloud Operations','Cloud Management','Cloud Administration','Cloud Operations Center','Cloud Information and Event Management','Cloud Information Management','Cloud Information Systems Management']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System',value=recommended_skills,key = '8')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)   
                        # course recommendation
                        rec_course = course_recommender(cloud_course)
                        break

                    #### IOT Recommendation
                    elif i.lower() in iot_keyword:
                        print(i.lower())
                        reco_field = 'IOT Development'
                        st.success("** Our analysis says you are looking for IOT Development Jobs **")
                        recommended_skills = ['IOT','Internet of Things','IOT Security','IOT Architecture','IOT Design','IOT Development','IOT Implementation','IOT Monitoring','IOT Management','IOT Administration','IOT Operations','IOT Governance','IOT Compliance','IOT Risk Management','IOT Incident Response','IOT Architecture','IOT Engineering','IOT Consulting','IOT Awareness','IOT Policy','IOT Standards','IOT Best Practices','IOT Tools','IOT Software','IOT Hardware','IOT Protocols','IOT Procedures','IOT Guidelines','IOT Frameworks','IOT Controls','IOT Measures','IOT Strategies','IOT Tactics','IOT Techniques','IOT Technologies','IOT Concepts','IOT Principles','IOT Practices','IOT Operations','IOT Management','IOT Administration','IOT Operations Center','IOT Information and Event Management','IOT Information Management','IOT Information Systems Management','IOT Information Systems Administration','IOT Information Systems Operations','IOT Information Systems Architecture','IOT Information Systems Design','IOT Information Systems Development','IOT Information Systems Implementation','IOT Information Systems Maintenance','IOT Information Systems Support','IOT Information Systems Monitoring','IOT Information Systems Analysis','IOT Information Systems Testing','IOT Information Systems Evaluation','IOT Information Systems Assessment','IOT Information Systems Audit','IOT Information Systems Compliance','IOT Information Systems Governance','IOT Information Systems Risk Management','IOT Information Systems Incident Response','IOT Information Systems Architecture','IOT Information Systems Engineering','IOT Information Systems Consulting','IOT Information Systems Awareness','IOT Information Systems Policy','IOT Information Systems Standards','IOT Information Systems Best Practices','IOT Information Systems Tools','IOT Information Systems Software','IOT Information Systems Hardware','IOT Information Systems Protocols','IOT Information Systems Procedures','IOT Information Systems Guidelines','IOT Information Systems Frameworks','IOT Information Systems Controls','IOT Information Systems Measures','IOT Information Systems Strategies','IOT Information Systems Tactics','IOT Information Systems Techniques','IOT Information Systems Technologies','IOT Information Systems Concepts','IOT Information Systems Principles','IOT Information Systems Practices','IOT Information Systems Operations','IOT Information Systems Management','IOT Information Systems Administration','IOT Information Systems Operations Center','IOT Information Systems Information and Event Management','IOT Information Systems Information Management','IOT Information Systems Information Systems Management','IOT Information Systems Information Systems Administration','IOT Information Systems Information Systems Operations','IOT Information Systems Information Systems Architecture','IOT Information Systems Information Systems Design','IOT Information Systems Information Systems Development','IOT Information Systems Information Systems Implementation','IOT Information Systems Information Systems Maintenance','IOT Information Systems Information Systems Support','IOT Information Systems Information Systems Monitoring','IOT Information Systems Information Systems Analysis','IOT Information Systems Information Systems Testing','IOT Information Systems Information Systems Evaluation','IOT Information Systems Information Systems Assessment','IOT Information Systems Information Systems Audit','IOT Information Systems Information Systems Compliance',' ']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System',value=recommended_skills,key = '9')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)   
                        # course recommendation
                        rec_course = course_recommender(iot_course)
                        break

                    #### Machine Learning Recommendation
                    elif i.lower() in ml_keyword:
                        print(i.lower())
                        reco_field = 'Machine Learning'
                        st.success("** Our analysis says you are looking for Machine Learning Jobs **")
                        recommended_skills = ['Machine Learning','Deep Learning','Data Science','Data Analysis','Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow','Flask','Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System',value=recommended_skills,key = '10')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)   
                        # course recommendation
                        rec_course = course_recommender(ml_course)
                        break

                    #### DevOps Recommendation
                    elif i.lower() in devops_keyword:
                        print(i.lower())
                        reco_field = 'DevOps'
                        st.success("** Our analysis says you are looking for DevOps Jobs **")
                        recommended_skills = ['DevOps','Continuous Integration','Continuous Deployment','Continuous Delivery','Continuous Monitoring','Continuous Testing','Continuous Feedback','Continuous Improvement','Continuous Development','Continuous Operations','Continuous Security','Continuous Compliance','Continuous Risk Management','Continuous Incident Response','Continuous Architecture','Continuous Engineering','Continuous Consulting','Continuous Awareness','Continuous Policy','Continuous Standards','Continuous Best Practices','Continuous Tools','Continuous Software','Continuous Hardware','Continuous Protocols','Continuous Procedures','Continuous Guidelines','Continuous Frameworks','Continuous Controls','Continuous Measures','Continuous Strategies','Continuous Tactics','Continuous Techniques','Continuous Technologies','Continuous Concepts','Continuous Principles','Continuous Practices','Continuous Operations','Continuous Management','Continuous Administration','Continuous Operations Center','Continuous Information and Event Management','Continuous Information Management','Continuous Information Systems Management','Continuous Information Systems Administration','Continuous Information Systems Operations','Continuous Information Systems Architecture','Continuous Information Systems Design','Continuous Information Systems Development','Continuous Information Systems Implementation','Continuous Information Systems Maintenance','Continuous Information Systems Support','Continuous Information Systems Monitoring','Continuous Information Systems Analysis','Continuous Information Systems Testing','Continuous Information Systems Evaluation','Continuous Information Systems Assessment','Continuous Information Systems Audit','Continuous Information Systems Compliance','Continuous Information Systems Governance','Continuous Information Systems Risk Management','Continuous Information Systems Incident Response','Continuous Information Systems Architecture','Continuous Information Systems Engineering','Continuous Information Systems Consulting','Continuous Information Systems Awareness','Continuous Information Systems Policy','Continuous Information Systems Standards','Continuous Information Systems Best Practices','Continuous Information Systems Tools','Continuous Information Systems Software','Continuous Information Systems Hardware','Continuous Information Systems Protocols','Continuous Information Systems Procedures','Continuous Information Systems Guidelines','Continuous Information Systems Frameworks','Continuous Information Systems Controls','Continuous Information Systems Measures','Continuous Information Systems Strategies','Continuous Information Systems Tactics','Continuous Information Systems Techniques','Continuous Information Systems Technologies','Continuous Information Systems Concepts','Continuous Information Systems Principles','Continuous Information Systems Practices','Continuous Information Systems Operations','Continuous Information Systems Management','Continuous Information Systems Administration','Continuous Information Systems Operations Center','Continuous Information Systems Information and Event Management','Continuous Information Systems Information Management','Continuous Information Systems Information Systems Management','Continuous Information Systems Information Systems Administration','Continuous Information Systems Information Systems Operations','Continuous Information Systems Information Systems Architecture','Continuous Information Systems Information Systems Design','Continuous Information Systems Information Systems Development','Continuous Information Systems Information Systems Implementation','Continuous Information Systems Information Systems Maintenance','Continuous Information Systems Information Systems Support','Continuous Information Systems Information Systems Monitoring','Continuous Information Systems Information Systems Analysis   ']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System',value=recommended_skills,key = '11')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)   
                        # course recommendation
                        rec_course = course_recommender(devops_course)
                        break

                    #### AI Recommendation
                    elif i.lower() in ai_keyword:
                        print(i.lower())
                        reco_field = 'AI Development'
                        st.success("** Our analysis says you are looking for AI Development Jobs **")
                        recommended_skills = ['Artificial Intelligence','AI','Machine Learning','Deep Learning','Data Science','Data Analysis','Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow','Flask','Streamlit','Natural Language Processing','NLP','Speech Recognition','Image Recognition','Object Detection','Object Recognition','Face Recognition','Emotion Recognition','Gesture Recognition','Handwriting Recognition','Pattern Recognition','Voice Recognition','Speaker Recognition','Speaker Identification','Speaker Verification','Speaker Diarization','Speaker Separation','Speaker Localization','Speaker Tracking','Speaker Counting','Speaker Clustering','Speaker Classification','Speaker Labeling','Speaker Tagging','Speaker Annotation','Speaker Transcription','Speaker Translation','Speaker Synthesis','Speaker Generation','Speaker Conversion','Speaker Enhancement','Speaker Normalization','Speaker Equalization','Speaker Adaptation','Speaker Alignment','Speaker Registration','Speaker Calibration','Speaker Verification','Speaker Identification','Speaker Diarization','Speaker Separation    ']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System',value=recommended_skills,key = '12')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)   
                        # course recommendation
                        rec_course = course_recommender(ai_course)
                        break

                    #### For Not Any Recommendations
                    elif i.lower() in n_any:
                        print(i.lower())
                        reco_field = 'NA'
                        st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, IOS ,UI/UX Development, Cyber Security, Cloud , IOT , DevOps , Machine Learning**")
                        recommended_skills = ['No Recommendations']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Currently No Recommendations',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = "Sorry! Not Available for this Field"
                        break

                ## Resume Scorer & Resume Writing Tips
                st.subheader("**Resume Tips & Ideas 🥂**")
                resume_score = 0
                
                ### Predicting Whether these key points are added to the resume
                if 'Objective' or 'Summary' in resume_text:
                    resume_score = resume_score+6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective/Summary</h4>''',unsafe_allow_html=True)                
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

                if 'Education' or 'School' or 'College'  in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Education Details</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Education. It will give Your Qualification level to the recruiter</h4>''',unsafe_allow_html=True)

                if 'EXPERIENCE' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Experience. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                if 'INTERNSHIPS'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIP'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'Internships'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'Internship'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Internships. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                if 'SKILLS'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'SKILL'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'Skills'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'Skill'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Skills. It will help you a lot</h4>''',unsafe_allow_html=True)

                if 'HOBBIES' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                elif 'Hobbies' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

                if 'INTERESTS'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                elif 'Interests'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Interest. It will show your interest other that job.</h4>''',unsafe_allow_html=True)

                if 'ACHIEVEMENTS' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                elif 'Achievements' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                if 'CERTIFICATIONS' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                elif 'Certifications' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                elif 'Certification' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Certifications. It will show that you have done some specialization for the required position.</h4>''',unsafe_allow_html=True)

                if 'PROJECTS' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                elif 'PROJECT' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                elif 'Projects' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                elif 'Project' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)

                st.subheader("**Resume Score 📝**")
                
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )

                ### Score Bar
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)

                ### Score
                st.success('** Your Resume Writing Score: ' + str(score)+'**')
                st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")

                # Hide everything after this point for the user
                return

                # print(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)
                # Match resume with company profiles
                st.subheader("**Company-Resume Matcher 🏢**")
                matches = match_resume_with_companies(resume_data)
                for company_name, score, alignment, job_role in matches:
                    st.markdown(f"""
                        <div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                            <h3 style="color: #4CAF50;">{company_name}</h3>
                            <p><strong>Compatibility Score:</strong> {score}</p>
                            <p><strong>Role:</strong> {job_role}</p>
                            <p><strong>Alignment:</strong> {', '.join(alignment)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("---")
                    
                # Manual job search input fields
                st.subheader("**Job Search**")
                job_query = st.text_input("Job Title", value="Software Engineer")
                
                if st.button("Search Jobs"):
                    with st.spinner('🔍 Searching for relevant positions...'):
                        # Fetch and display job listings based on user input
                        job_listings = fetch_job_listings(job_query)
                        
                        if job_listings and job_listings.get('data') and job_listings['data'].get('aggregateSalaryResponse'):
                            results = job_listings['data']['aggregateSalaryResponse']['results']
                            st.success(f"🎯 Found {len(results)} matching positions")
                            
                            for job in results:
                                company = job['employer']
                                total_pay = job['totalPayStatistics']['percentiles']
                                base_pay = job['basePayStatistics']['mean']
                                
                                st.markdown(f"""
                                    <div class="stCard" style="border-left: 5px solid #2196F3;">
                                        <div style="display: flex; justify-content: space-between; align-items: start;">
                                            <div>
                                                <h3 style="color: #2196F3; margin: 0;">{job['jobTitle']['text']}</h3>
                                                <h4 style="color: #666; margin: 5px 0;">{company['name']}</h4>
                                            </div>
                                            <img src="{company.get('squareLogoUrl', '')}" alt="Company Logo" style="width: 60px; height: 60px; object-fit: contain;">
                                        </div>
                                        <div style="display: flex; gap: 20px; margin: 15px 0;">
                                            <div class="metric">
                                                <span style="color: #666;">Company Rating</span>
                                                <h4 style="margin: 5px 0;">{company['ratings']['overallRating']}/5.0 ⭐</h4>
                                            </div>
                                            <div class="metric">
                                                <span style="color: #666;">Open Positions</span>
                                                <h4 style="margin: 5px 0;">{company['counts']['globalJobCount']['jobCount']} 📋</h4>
                                            </div>
                                        </div>
                                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 10px;">
                                            <h4 style="margin: 0 0 10px 0;">💰 Compensation Details</h4>
                                            <p><strong>Base Salary:</strong> ${base_pay:,.2f}/year</p>
                                            <p><strong>Total Compensation Range:</strong></p>
                                            <ul style="margin: 5px 0;">
                                                <li>Median: ${total_pay[2]['value']:,.2f}</li>
                                                <li>Range: ${total_pay[0]['value']:,.2f} - ${total_pay[4]['value']:,.2f}</li>
                                            </ul>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning("No matching positions found. Try adjusting your search criteria.")

                ### Getting Current Date and Time
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)


                ## Calling insert_data to add all the data into user_data                
                insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)

                ## Recommending Resume Writing Video
                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                st.video(resume_vid)

                ## Recommending Interview Preparation Video
                st.header("**Bonus Video for Interview Tips💡**")
                interview_vid = random.choice(interview_videos)
                st.video(interview_vid)

                ## On Successful Result 
                st.balloons()

            else:
                st.error('Something went wrong..')                

    ###### CODE FOR FEEDBACK SIDE ######
    elif choice == 'Feedback':   
    
        # timestamp 
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date+'_'+cur_time)

        # Feedback Form
        with st.form("my_form"):
            st.write("Feedback form")            
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            Timestamp = timestamp        
            submitted = st.form_submit_button("Submit")
            if submitted:
                ## Calling insertf_data to add dat into user feedback
                insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
                ## Success Message 
                st.success("Thanks! Your Feedback was recorded.") 
                ## On Successful Submit
                st.balloons()    


        # query to fetch data from user feedback table
        query = 'select * from user_feedback'        
        plotfeed_data = pd.read_sql(query, connection)                        


        # fetching feed_score from the query and getting the unique values and total value count 
        labels = plotfeed_data.feed_score.unique()
        values = plotfeed_data.feed_score.value_counts()


        # plotting pie chart for user ratings
        st.subheader("**Past User Rating's**")
        fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig)


        #  Fetching Comment History
        cursor.execute('select feed_name, comments from user_feedback')
        plfeed_cmt_data = cursor.fetchall()

        st.subheader("**User Comment's**")
        dff = pd.DataFrame(plfeed_cmt_data, columns=['User', 'Comment'])
        st.dataframe(dff, width=1000)

    
    ###### CODE FOR ABOUT PAGE ######
    elif choice == 'About':   

        st.subheader("**About The Tool - AI RESUME ANALYZER**")

        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>

        <p align="justify">
            <b>How to use it: -</b> <br/><br/>
            <b>User -</b> <br/>
            In the Side Bar choose yourself as user and fill the required fields and upload your resume in pdf format.<br/>
            Just sit back and relax our tool will do the magic on it's own.<br/><br/>
            <b>Feedback -</b> <br/>
            A place where user can suggest some feedback about the tool.<br/><br/>
            <b>Admin -</b> <br/>
            For login use <b>admin</b> as username and <b>admin@resume-analyzer</b> as password.<br/>
            It will load all the required stuffs and perform analysis.
        </p><br/><br/>

        <p align="justify">
            Built with 🤍 by 
            <a href="" style="text-decoration: none; color: grey;">Team Resumate AI</a> through 
            <a href="" style="text-decoration: none; color: grey;">Dr Bright --(Data Scientist)</a>
        </p>

        ''',unsafe_allow_html=True)  


    ###### CODE FOR ADMIN SIDE (ADMIN) ######
    else:
        st.success('Welcome to Admin Side')

        #  Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            
            ## Credentials 
            if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':
                
                ### Fetch miscellaneous data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                datanalys = cursor.fetchall()
                plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                ### Total Users Count with a Welcome Message
                values = plot_data.Idt.count()
                st.success("Welcome Admin ! Total %d " % values + " User's Have Used Our Tool : )")                
                
                ### Fetch user data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                data = cursor.fetchall()                

                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                                                 'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                 'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                
                ### Viewing the dataframe
                st.dataframe(df)
                
                ### Downloading Report of user_data in csv file
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                ### Fetch feedback data from user_feedback(table) and convert it into dataframe
                cursor.execute('''SELECT * from user_feedback''')
                data = cursor.fetchall()

                st.header("**User's Feedback Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                st.dataframe(df)

                ### query to fetch data from user_feedback(table)
                query = 'select * from user_feedback'
                plotfeed_data = pd.read_sql(query, connection)                        

                ### Analyzing All the Data's in pie charts

                # fetching feed_score from the query and getting the unique values and total value count 
                labels = plotfeed_data.feed_score.unique()
                values = plotfeed_data.feed_score.value_counts()
                
                # Pie chart for user ratings
                st.subheader("**User Rating's**")
                fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5 🤗", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                st.plotly_chart(fig)

                # fetching Predicted_Field from the query and getting the unique values and total value count                 
                labels = plot_data.Predicted_Field.unique()
                values = plot_data.Predicted_Field.value_counts()

                # Create a DataFrame from labels and values
                df = pd.DataFrame({'labels': labels, 'values': values})

                # Pie chart for predicted field recommendations
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(df, values='values', names='labels', title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                st.plotly_chart(fig)
                
                # fetching User_Level from the query and getting the unique values and total value count                 
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()
                
                # Create a DataFrame from labels and values
                df = pd.DataFrame({'labels': labels, 'values': values})

                # Pie chart for User's👨‍💻 Experienced Level
                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(df, values='values', names='labels', title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig)
                
                # fetching resume_score from the query and getting the unique values and total value count                 
                labels = plot_data.resume_score.unique()                
                values = plot_data.resume_score.value_counts()
                
                # Create a DataFrame from labels and values
                df = pd.DataFrame({'labels': labels, 'values': values})
                
                # Pie chart for Resume Score
                st.subheader("**Pie-Chart for Resume Score**")
                fig = px.pie(df, values='values', names='labels', title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                st.plotly_chart(fig)
                
                # fetching IP_add from the query and getting the unique values and total value count 
                labels = plot_data.IP_add.unique()
                values = plot_data.IP_add.value_counts()

                # Create a DataFrame from labels and values
                df = pd.DataFrame({'labels': labels, 'values': values})
                
                # Pie chart for Users
                st.subheader("**Pie-Chart for Users App Used Count**")
                fig = px.pie(df, values='values', names='labels', title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                st.plotly_chart(fig)
                
                # fetching City from the query and getting the unique values and total value count 
                labels = plot_data.City.unique()
                values = plot_data.City.value_counts()
                
                # Create a DataFrame from labels and values
                df = pd.DataFrame({'labels': labels, 'values': values})
                
                # Pie chart for City
                st.subheader("**Pie-Chart for City**")
                fig = px.pie(df, values='values', names='labels', title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                st.plotly_chart(fig)
                
                # fetching State from the query and getting the unique values and total value count 
                labels = plot_data.State.unique()
                values = plot_data.State.value_counts()
                
                # Create a DataFrame from labels and values
                df = pd.DataFrame({'labels': labels, 'values': values})
                
                # Pie chart for State
                st.subheader("**Pie-Chart for State**")
                fig = px.pie(df, values='values', names='labels', title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                st.plotly_chart(fig)
                
                # fetching Country from the query and getting the unique values and total value count 
                labels = plot_data.Country.unique()
                values = plot_data.Country.value_counts()
                
                # Create a DataFrame from labels and values
                df = pd.DataFrame({'labels': labels, 'values': values})
                
                # Pie chart for Country
                st.subheader("**Pie-Chart for Country**")
                fig = px.pie(df, values='values', names='labels', title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                st.plotly_chart(fig)

                # Add company profile section
                st.header("**Add Company Profile**")
                with st.form("company_form"):
                    company_name = st.text_input('Company Name')
                    job_description = st.text_area('Job Description')
                    culture_requirements = st.text_area('Culture Requirements')
                    required_skills = st.text_area('Required Skills')
                    job_role = st.text_input('Job Role')
                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        insert_company_profile(company_name, job_description, culture_requirements, required_skills, job_role)
                        st.success("Company profile added successfully.")

            ## For Wrong Credentials
            else:
                st.error("Wrong ID & Password Provided")

# Calling the main (run()) function to make the whole process run
run()
