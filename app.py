import streamlit as st
import pandas as pd
import json
import os
import requests
import random
from typing import List, Dict


# ----------------------------- CONFIG -----------------------------
st.set_page_config(page_title="Career Compass", page_icon="🧭", layout="wide")

USERS_CSV = "users.csv"
COLLEGES_CSV = "jk_colleges.csv"
AVATAR_FOLDER = "images"
QUIZ_FILE = "career_questions.json"
API_KEY = '1544f28739f54713873b32e7687dac2d'
BASE_URL = 'https://newsapi.org/v2/everything'
# ----------------------------- CAREER ROADMAP DATA -----------------------------
CAREER_TO_DEGREES = {
    # tech/data
    "Data Analyst": ["B.Sc", "BCA", "B.Com"],
    "Software Developer": ["BCA", "B.Sc", "B.Tech", "BE"],
    "AI/ML Engineer": ["B.Tech", "BE", "B.Sc"],
    # business/arts
    "Business Analyst": ["B.Com", "BBA", "B.Sc"],
    "Graphic Designer": ["BA", "Arts"],
    # medical/health
    "Doctor (MBBS)": ["MBBS"],
    "Dentist (BDS)": ["BDS"],
    "Nurse": ["B.Sc. Nursing"],
    # architecture
    "Architect": ["B.Arch"],
}

CAREER_KEYWORDS = {
    "Data Analyst": ["data", "statistics", "analytics", "python"],
    "Software Developer": ["programming", "software", "computer"],
    "AI/ML Engineer": ["ai", "ml", "machine", "data"],
    "Business Analyst": ["finance", "business", "analytics"],
    "Graphic Designer": ["design", "art", "media"],
    "Doctor (MBBS)": ["medicine", "clinical", "biology"],
    "Dentist (BDS)": ["dental", "oral"],
    "Nurse": ["nursing", "health"],
    "Architect": ["architecture", "design"],
}

ENTRANCE_BY_DEGREE = {
    "BA": {"exam": "CUET-UG (where applicable)", "ref": "https://cuet.nta.nic.in/"},
    "B.Sc": {"exam": "CUET-UG (where applicable)", "ref": "https://cuet.nta.nic.in/"},
    "B.Com": {"exam": "CUET-UG (where applicable)", "ref": "https://cuet.nta.nic.in/"},
    "BBA": {"exam": "CUET-UG / Univ process", "ref": "https://cuet.nta.nic.in/"},
    "BCA": {"exam": "CUET-UG / Univ process", "ref": "https://cuet.nta.nic.in/"},
    "B.Tech": {"exam": "JEE Main", "ref": "https://jeemain.nta.nic.in/"},
    "BE": {"exam": "JEE Main", "ref": "https://jeemain.nta.nic.in/"},
    "MBBS": {"exam": "NEET-UG", "ref": "https://neet.nta.nic.in/"},
    "BDS": {"exam": "NEET-UG", "ref": "https://neet.nta.nic.in/"},
    "B.Arch": {"exam": "JEE Main (Paper 2) / NATA (varies)", "ref": "https://jeemain.nta.nic.in/"},
    "B.Sc. Nursing": {"exam": "University/State process", "ref": ""},
}

MOOC_BY_CAREER = {
    "Data Analyst": [
        {"title": "Python for Data Science", "platform": "NPTEL/SWAYAM", "ref": "https://onlinecourses.nptel.ac.in/"},
        {"title": "Statistics for Data Analysis", "platform": "SWAYAM", "ref": "https://swayam.gov.in/"},
    ],
    "Software Developer": [
        {"title": "Data Structures & Algorithms", "platform": "NPTEL", "ref": "https://onlinecourses.nptel.ac.in/"},
        {"title": "Databases / SQL", "platform": "SWAYAM", "ref": "https://swayam.gov.in/"},
    ],
    "AI/ML Engineer": [
        {"title": "Intro to Machine Learning", "platform": "NPTEL", "ref": "https://onlinecourses.nptel.ac.in/"},
    ],
    "Business Analyst": [
        {"title": "Financial Accounting", "platform": "SWAYAM", "ref": "https://swayam.gov.in/"},
        {"title": "Business Analytics", "platform": "SWAYAM", "ref": "https://swayam.gov.in/"},
    ],
    "Graphic Designer": [
        {"title": "Design Basics / Visual Communication", "platform": "SWAYAM", "ref": "https://swayam.gov.in/"},
    ],
    "Doctor (MBBS)": [
        {"title": "Human Physiology Basics", "platform": "SWAYAM", "ref": "https://swayam.gov.in/"},
    ],
    "Dentist (BDS)": [
        {"title": "Oral Biology Foundations", "platform": "SWAYAM", "ref": "https://swayam.gov.in/"},
    ],
    "Nurse": [
        {"title": "Foundations of Nursing", "platform": "SWAYAM", "ref": "https://swayam.gov.in/"},
    ],
    "Architect": [
        {"title": "Architectural Graphics", "platform": "SWAYAM", "ref": "https://swayam.gov.in/"},
    ],
}

def _split_list(cell: str):
    if not isinstance(cell, str):
        return []
    return [c.strip() for c in cell.split(",") if c.strip()]

def career_roadmap(career: str, location_pref: str = None, limit: int = 20) -> Dict:
    degrees = CAREER_TO_DEGREES.get(career, [])
    if not degrees:
        return {"career": career, "message": "No mapping found", "colleges": [], "steps": []}

    if os.path.exists(COLLEGES_CSV):
        df = pd.read_csv(COLLEGES_CSV)
    else:
        df = pd.DataFrame(columns=["College","Location","Website","Courses","Skills"])
    for c in ["College", "Location", "Website", "Courses", "Skills"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    df["CourseTokens"] = df["Courses"].apply(_split_list)
    df["SkillTokens"] = df.get("Skills", pd.Series([""]*len(df))).apply(_split_list)

    mask = df["CourseTokens"].apply(
        lambda toks: any(any(d.lower() in t.lower() for d in degrees) for t in toks)
    )
    filtered = df[mask].copy()

    if location_pref:
        filtered["loc_boost"] = filtered["Location"].str.contains(location_pref, case=False, na=False).astype(int)
    else:
        filtered["loc_boost"] = 0

    kw = [k.lower() for k in CAREER_KEYWORDS.get(career, [])]
    def score_row(r):
        toks = [t.lower() for t in r["CourseTokens"]]
        base = sum(any(d.lower() in t for d in degrees) for t in toks)
        skills = [s.lower() for s in r["SkillTokens"]]
        hits = sum(any(k in s for s in skills) for k in kw)
        return base + 0.5 * hits

    filtered["score"] = filtered.apply(score_row, axis=1)
    filtered = filtered.sort_values(["loc_boost", "score", "College"], ascending=[False, False, True])

    show = [c for c in ["College", "Location", "Website", "Courses", "Skills"] if c in filtered.columns]
    colleges = filtered[show].drop_duplicates().head(limit).to_dict(orient="records")

    entrances = []
    seen = set()
    for d in degrees:
        info = ENTRANCE_BY_DEGREE.get(d)
        if info:
            key = (info["exam"], info["ref"])
            if key not in seen:
                entrances.append(info)
                seen.add(key)

    steps = [
        f"Match your 10+2 subjects to degree options for {career} and shortlist colleges offering {', '.join(degrees)}",
        "Pick the admission route that applies to your shortlist (CUET‑UG/JEE Main/NEET‑UG or university process) and calendar deadlines",
        "Apply to 5–8 colleges across difficulty tiers; prepare required documents and subject prerequisites",
        "Enroll in 1 public MOOC per term aligned to core skills; build a small project or portfolio artifact each semester",
        "Do a short internship or supervised project each summer; expand your portfolio or clinical/community experience",
        "In final year, add a capstone aligned to the target role and prepare for placements or PG entrance"
    ]

    return {
        "career": career,
        "degrees": degrees,
        "entrance": entrances,
        "colleges": colleges,
        "moocs": MOOC_BY_CAREER.get(career, []),
        "steps": steps
    }

# ----------------------------- SESSION STATE -----------------------------
if "login" not in st.session_state:
    st.session_state.login = False
if "user" not in st.session_state:
    st.session_state.user = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []
if "temp_signup" not in st.session_state:
    st.session_state.temp_signup = {}
if "page" not in st.session_state:
    st.session_state.page = "login"
if "quiz_done" not in st.session_state:
    st.session_state.quiz_done = False
if "main_result" not in st.session_state:
    st.session_state.main_result = {}
if "sub_done" not in st.session_state:
    st.session_state.sub_done = False

# ----------------------------- LOAD DATA -----------------------------
def load_users():
    if os.path.exists(USERS_CSV):
        df = pd.read_csv(USERS_CSV)
        required_cols = ["email","password","name","age","gender","city","state","education","avatar","your_paths"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    else:
        df = pd.DataFrame(columns=required_cols)
        df.to_csv(USERS_CSV,index=False)
        return df

def save_users(df):
    df.to_csv(USERS_CSV,index=False)

def load_colleges():
    if os.path.exists(COLLEGES_CSV):
        return pd.read_csv(COLLEGES_CSV)
    else:
        df = pd.DataFrame({
            "College":["SKUAST-Kashmir","GCET Jammu"],
            "Location":["Srinagar","Jammu"],
            "Website":["https://www.skuastkashmir.ac.in","https://gcetjammu.ac.in"],
            "Courses":["Engineering,Science","Commerce,Arts,Engineering"]
        })
        df.to_csv(COLLEGES_CSV,index=False)
        return df

def load_quiz():
    if os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE,"r") as f:
            return json.load(f)
    else:
        return {"main": [], "sub": {}}

users_df = load_users()
colleges_df = load_colleges()
quiz_data = load_quiz()

# ----------------------------- AUTH FUNCTIONS -----------------------------
def login(email,password):
    df = load_users()
    if email in df["email"].values:
        row = df[df["email"]==email].iloc[0]
        if row["password"]==password:
            return row.to_dict()
    return None

def signup(email, password, name, age, gender, city, state, education):
    df = load_users()
    if email in df["email"].values:
        return False
    # Default avatar based on gender
    if gender=="Male":
        avatar_file = os.path.join(AVATAR_FOLDER,"avatar2.png")
    elif gender=="Female":
        avatar_file = os.path.join(AVATAR_FOLDER,"avatar1.png")
    else:
        avatar_file = os.path.join(AVATAR_FOLDER,"avatar3.png")

    new_row = {
        "email": email,
        "password": password,
        "name": name,
        "age": age,
        "gender": gender,
        "city": city,
        "state": state,
        "education": education,
        "avatar": avatar_file,
        "your_paths": ""
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_users(df)
    return True

def save_user_data(email, user_dict):
    df = load_users()
    idx = df.index[df["email"]==email][0]
    for key, val in user_dict.items():
        df.at[idx, key] = val
    save_users(df)

# ----------------------------- QUIZ FUNCTIONS -----------------------------
def calculate_scores(questions, answers):
    scores = {}
    for q_key, ans in zip(sorted(questions.keys()), answers):
        question = questions[q_key]
        if ans in question["options"]:
            for stream, weight in question["options"][ans]["weights"].items():
                scores[stream] = scores.get(stream, 0) + weight
    return scores

def recommend(scores):
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    major = ranked[0][0] if ranked else None
    minor = ranked[1][0] if len(ranked) > 1 else None
    backup = ranked[2][0] if len(ranked) > 2 else None
    return major, minor, backup

# ----------------------------- NEWS FUNCTION -----------------------------
# Replace your old function with this
# --- Stream-specific whitelisted domains ---
STREAM_DOMAINS = {
    "Engineering": ["ieee.org", "techcrunch.com", "arstechnica.com", "theverge.com"],
    "Science": ["nature.com", "sciencedaily.com", "scientificamerican.com", "arxiv.org"],
    "Medical": ["nejm.org", "thelancet.com", "who.int", "nih.gov"],
    "Arts": ["theguardian.com", "nytimes.com", "smithsonianmag.com"],
    "Commerce": ["ft.com", "economist.com", "wsj.com", "business-standard.com"]
}

# --- Low-quality / irrelevant domains to exclude ---
EXCLUDE = ["rumble.com", "brighteon.com", "apple.com", "facebook.com"]

def build_query_terms(stream_keywords, extra_keywords=None):
    phrases = [f"\"{k}\"" for k in stream_keywords]
    extras = extra_keywords or []
    return " OR ".join(phrases + extras)
def fetch_relevant_news(stream, interests, days=21, page_size=50, max_items=30):
    from datetime import datetime, timedelta
    from_date = (datetime.utcnow() - timedelta(days=days)).date().isoformat()

    # Keywords and domains
    query = build_query_terms(interests)
    whitelist = ",".join(STREAM_DOMAINS.get(stream, [])) or None
    exclude = ",".join(EXCLUDE)

    params = {
        "q": query,
        "searchIn": "title,description",
        "sortBy": "relevancy",
        "language": "en",
        "from": from_date,
        "pageSize": page_size,
        "apiKey": API_KEY
    }

    if whitelist:
        params["domains"] = whitelist
    if exclude:
        params["excludeDomains"] = exclude

    r = requests.get(BASE_URL, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    articles = data.get("articles", [])

    # Post-filter and score
    keywords = [k.lower() for k in interests]
    scored = []
    for a in articles:
        title = (a.get("title") or "").lower()
        desc = (a.get("description") or "").lower()
        text = title + " " + desc
        hits = sum(1 for k in keywords if k in text)
        if hits == 0:
            continue
        title_hits = sum(1 for k in keywords if k in title)
        score = hits + 0.5 * title_hits
        scored.append((score, {
            "title": a.get("title"),
            "description": a.get("description"),
            "url": a.get("url"),
            "source": (a.get("source") or {}).get("name"),
            "publishedAt": a.get("publishedAt").split("T")[0] if a.get("publishedAt") else None
        }))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:max_items]]


# ----------------------------- LOGIN / SIGNUP PAGE -----------------------------
def login_page():
    st.title("🔐 Login to Career Compass")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            user = login(email,password)
            if user:
                st.session_state.login=True
                st.session_state.user=user
                st.session_state.page="home"
                st.success(f"Welcome {user['name']}!")
            else:
                st.error("Invalid credentials")

    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pwd")
        name = st.text_input("Full Name", key="signup_name")
        age = st.number_input("Age", min_value=10, max_value=100, step=1, key="signup_age")
        gender = st.selectbox("Gender", ["Select","Male","Female","Other"], key="signup_gender")
        city = st.text_input("City", key="signup_city")
        state = st.text_input("State", key="signup_state")
        education = st.text_input("Education Qualification", key="signup_edu")

        if st.button("Sign Up"):
            if gender=="Select":
                st.error("Please select a gender first!")
            else:
                success = signup(email,password,name,age,gender,city,state,education)
                if success:
                    st.success("Signup successful! Please login.")
                else:
                    st.error("Email already exists.")

# ----------------------------- HOME PAGE -----------------------------
def home_page():
    # Sidebar avatar & title
    if st.session_state.user:
        avatar_path = st.session_state.user.get("avatar") or os.path.join(AVATAR_FOLDER, "avatar3.png")
        st.sidebar.image(avatar_path, width=80)
        st.sidebar.title(f"Welcome, {st.session_state.user['name']}")
    else:
        st.sidebar.image(os.path.join(AVATAR_FOLDER, "avatar3.png"), width=80)
        st.sidebar.title("Welcome, Guest")

    # Sidebar menu
    menu = st.sidebar.radio(
        "📍 Menu", ["Home","Quiz","Your Paths","Explore","Notifications","Profile","About Us","Logout"]
    )

    # --- Home Page ---
    if menu=="Home":
        st.title("🧭 Career Compass")
        st.subheader("Your personalized guide to career paths, colleges, and opportunities.")

        # --- Quick Actions ---
       # st.markdown("### 🚀 Quick Actions")
        
        st.markdown("---")

        # --- Did You Know? Fun Career Facts ---
        st.markdown("### 💡 Did You Know?")
        facts = [
            "The fastest-growing career in India is **Data Science**, expected to create 11M+ jobs by 2030.",
            "The average salary of an **AI Engineer** in India is ₹8–12 LPA for freshers.",
            "**Graphic Designers** are now in demand in media, healthcare & finance sectors.",
            "By 2030, **50% of jobs will require new skills** due to automation and AI.",
            "India produces **1.5 million engineers** every year, but only ~20% work in core fields."
        ]
        st.info(random.choice(facts))

        st.markdown("---")

        # --- Success Stories ---
        st.markdown("### 🌟 Success Stories")
        stories = [
            {"name":"Aditi Sharma","story":"From a small town in J&K, Aditi cracked **IIT-JEE** and is now a researcher in AI at Google.","quote":"Never doubt your potential, guidance + hard work = success!"},
            {"name":"Ravi Kumar","story":"Started as a diploma student in civil engineering, Ravi built a startup in **Sustainable Housing**.","quote":"Your background doesn’t define you, your choices do."},
            {"name":"Mehak Ali","story":"A passionate artist who turned her hobby into a career in **Graphic Design** freelancing worldwide.","quote":"Follow your passion, and success will follow you."}
        ]
        for s in stories:
            with st.expander(f"🌟 {s['name']}"):
                st.write(s["story"])
                st.success(f"“{s['quote']}”")

    # --- Notifications Page ---
        # --- Notifications Page ---
    elif menu=="Notifications":
        st.title("🔔 Notifications")
        st.markdown("Here you will find career news, tips, and updates tailored for you!")

        if st.session_state.user and st.session_state.user.get("your_paths"):
            # Extract stream (major) from quiz results
            paths = st.session_state.user["your_paths"]
            major = None
            try:
                major = paths.split("Major:")[1].split(",")[0].strip()
            except:
                major = None

            if major:
                st.info(f"Fetching latest news for your major: **{major}**...")

                # Map majors to keywords
                STREAM_KEYWORDS = {
                    "Engineering": ["robotics", "AI", "automation", "IoT"],
                    "Science": ["space", "physics", "biology", "chemistry"],
                    "Medical": ["healthcare", "medicine", "clinical trials", "pharma"],
                    "Arts": ["design", "media", "painting", "music"],
                    "Commerce": ["finance", "stock market", "economics", "entrepreneurship"]
                }

                keywords = STREAM_KEYWORDS.get(major, [major])

                try:
                    news_items = fetch_relevant_news(major, keywords, days=14, page_size=30, max_items=10)
                    if news_items:
                        for n in news_items:
                            st.markdown(f"**[{n['title']}]({n['url']})**")
                            if n['description']:
                                st.write(n['description'])
                            st.caption(f"{n['source']} | {n['publishedAt']}")
                            st.markdown("---")
                    else:
                        st.info("No recent news found for your major. Check back later!")
                except Exception as e:
                    st.error(f"Error fetching news: {e}")

            else:
                st.info("Your quiz results are incomplete. Take the quiz to get personalized news!")
        else:
            st.info("Take the quiz to get news tailored to your career interests!")


    # --- Other pages ---
    elif menu=="Quiz":
       
        quiz_page()
  
    elif menu=="Your Paths":
        st.title("📈 Your Career Paths")
        user_paths = st.session_state.user.get("your_paths", "")
        if user_paths:
            st.write(user_paths)
        else: 
            st.info("Take the quiz to generate your career paths!")

        # ---------------- Career Roadmap UI ----------------
        st.subheader("Career Roadmap")
        selected_career = st.selectbox("Select a Career", options=list(CAREER_TO_DEGREES.keys()))
        location_pref = st.text_input("Preferred Location (optional)")
        if st.button("Show Roadmap"):
            roadmap = career_roadmap(selected_career, location_pref)
            st.markdown("**Relevant Degrees:**")
            st.write(", ".join(roadmap["degrees"]))
            st.markdown("**Entrance Exams:**")
            for e in roadmap["entrance"]: st.write(f"- {e['exam']} ([Link]({e['ref']}))")
            st.markdown("**Top Colleges:**")
            for c in roadmap["colleges"]:
                st.write(f"- [{c['College']}]({c['Website']}) | Location: {c['Location']} | Courses: {c.get('Courses','')} | Skills: {c.get('Skills','')}")
            st.markdown("**Recommended MOOCs:**")
            for m in roadmap["moocs"]: st.write(f"- [{m['title']}]({m['ref']}) on {m['platform']}")
            st.markdown("**Suggested Steps:**")
            for step in roadmap["steps"]: st.write(f"- {step}")
    elif menu=="Explore":
        st.title("🏫 College Recommendations")
        search = st.text_input("Search by Course or College")
        df = colleges_df
        if search:
            df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().to_string(), axis=1)]
        st.dataframe(df)
    elif menu=="Profile":
        st.subheader("👤 Edit Profile")
        if st.session_state.user:
            user = st.session_state.user
            name = st.text_input("Full Name", user.get("name", ""))
            age = st.number_input("Age", min_value=10, max_value=100, value=int(user.get("age", 18)))
            gender = st.selectbox("Gender", ["Male","Female","Other"], index=["Male","Female","Other"].index(user.get("gender","Other")))
            city = st.text_input("City", user.get("city", ""))
            state = st.text_input("State", user.get("state", ""))
            education = st.text_input("Education Qualification", user.get("education", ""))

            avatar = st.file_uploader("Upload Avatar", type=["png","jpg","jpeg"])
            if avatar:
                avatar_path = os.path.join(AVATAR_FOLDER, avatar.name)
                with open(avatar_path, "wb") as f:
                    f.write(avatar.getbuffer())
                user["avatar"] = avatar_path

            if st.button("💾 Save Profile"):
                user.update({
                    "name": name, "age": age, "gender": gender,
                    "city": city, "state": state, "education": education
                })
                save_user_data(user["email"], user)
                st.success("Profile updated successfully!")
    elif menu=="About Us":
        st.title("ℹ️ About Us")
        st.write("Career Compass is your personal career guidance tool built for SIH.")
        st.write("It helps students in J&K explore careers, colleges, and roadmaps.")
    elif menu=="Logout":
        st.session_state.login = False
        st.session_state.user = None
        st.session_state.quiz_answers = []
        st.session_state.page = "login"
        st.success("Logged out successfully.")

# ----------------------------- QUIZ PAGE -----------------------------
def quiz_page():
    st.header("📝 Career Quiz")

    # Ensure session flags exist
    if "quiz_done" not in st.session_state:
        st.session_state.quiz_done = False
    if "main_result" not in st.session_state:
        st.session_state.main_result = {}
    if "sub_done" not in st.session_state:
        st.session_state.sub_done = False

    # ---- MAIN QUIZ ----
    if not st.session_state.quiz_done:
        answers = []
        with st.form("quiz_form"):
            st.info("Answer the following questions to identify your **Major**.")
            for i, q_key in enumerate(sorted(quiz_data.get("main", {}).keys())):
                q = quiz_data["main"][q_key]
                st.write(f"**Q{i+1}: {q['question']}**")
                option_texts = [opt["text"] for opt in q["options"].values()]
                ans_idx = st.radio("", option_texts, key=f"main_{i}")
                ans_key = [k for k, v in q["options"].items() if v["text"] == ans_idx][0]
                answers.append(ans_key)

            submitted = st.form_submit_button("🚀 Submit ")
            if submitted:
                main_scores = calculate_scores(quiz_data["main"], answers)
                major, minor, backup = recommend(main_scores)
                st.session_state.main_result = {"major": major, "minor": minor, "backup": backup}
                st.session_state.quiz_done = True

    # ---- SUB QUIZ ----
    elif st.session_state.quiz_done and not st.session_state.sub_done:
        major = st.session_state.main_result.get("major")
        if not major:
            st.error("No major stream identified. Please retake the quiz.")
            if st.button("🔄 Retake Quiz"):
                st.session_state.quiz_done = False
                st.session_state.sub_done = False
                st.session_state.main_result = {}
                st.rerun()
            return

        st.subheader(f"🧩 Specialization Quiz: {major}")

        if major in quiz_data.get("sub", {}):
            sub_answers = []
            with st.form("sub_quiz_form"):
                st.info("Now let’s narrow down to your **specialization**.")
                for j, q_key in enumerate(sorted(quiz_data["sub"][major].keys())):
                    q = quiz_data["sub"][major][q_key]
                    st.write(f"**Q{j+1}: {q['question']}**")
                    option_texts = [opt["text"] for opt in q["options"].values()]
                    ans_idx = st.radio("", option_texts, key=f"sub_{j}")
                    ans_key = [k for k, v in q["options"].items() if v["text"] == ans_idx][0]
                    sub_answers.append(ans_key)

                sub_submitted = st.form_submit_button("✨ Submit Specialization Quiz")
                if sub_submitted:
                    sub_scores = calculate_scores(quiz_data["sub"][major], sub_answers)
                    sub_major, sub_minor, sub_backup = recommend(sub_scores)
                    st.session_state.sub_done = True

                    # Save results
                    df = load_users()
                    idx = df.index[df["email"] == st.session_state.user["email"]][0]
                    df.at[idx, "your_paths"] = (
                        f"Major: {major}, Minor: {st.session_state.main_result['minor']}, Backup: {st.session_state.main_result['backup']} | "
                        f"Specializations Major: {sub_major}, Minor: {sub_minor}, Backup: {sub_backup}"
                    )
                    save_users(df)
                    st.session_state.user = df.iloc[idx].to_dict()

                    # Fancy UI results
                    st.success("🎉 Your career recommendations are ready!")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("🌟 Major 1", major)
                    with cols[1]:
                        st.metric("📌 Major 2", st.session_state.main_result['minor'])
                    with cols[2]:
                        st.metric("🛡 Major 3", st.session_state.main_result['backup'])

                    st.markdown("---")
                    st.subheader("🔬 Specialization Results")
                    cols2 = st.columns(3)
                    with cols2[0]:
                        st.metric("⭐ Specilization 1", sub_major)
                    with cols2[1]:
                        st.metric("📌 specilization 2", sub_minor)
                    with cols2[2]:
                        st.metric("🛡 specilization 3", sub_backup)

        else:
            st.info("No specialization quiz available for this stream.")
            st.session_state.sub_done = True
        if st.button("🔄 Retake Quiz"):
            st.session_state.quiz_done = False
            st.session_state.sub_done = False
            st.session_state.main_result = {}
            st.rerun()
        
    # ---- RESULTS ----
  
        

# ----------------------------- ROUTER -----------------------------
if st.session_state.page=="login":
    login_page()
else:
    home_page()
