# 🧭 Career Compass

*A personalized career guidance web application built for SIH (Smart India Hackathon).*
Career Compass helps students explore careers, discover suitable colleges, prepare with MOOCs, and stay updated with career news — all in one place.

---

## 🚀 Features

* 🔐 *Login/Signup system* with user profile management
* 📝 *Career Quiz* → Maps user interests & strengths to career paths
* 📈 *Career Roadmaps* → Degrees, entrance exams, MOOCs, colleges, and step-by-step guidance
* 🏫 *College Recommendations* → Region-specific and course-specific colleges from curated datasets
* 🔔 *Notifications & News Feed* → Real-time updates using *NewsAPI* (career-relevant, stream-based)
* 🌟 *Success Stories & Fun Facts* → To motivate students
* 👤 *Personalized Dashboard* → Tracks user’s paths, specializations, and preferences
* 📂 *Lightweight Storage* → CSV-based datasets for prototype (easily expandable to DB)

---

## 🏗️ Tech Stack

* *Frontend/UI* → [Streamlit](https://streamlit.io/) (Python-based interactive UI)
* *Backend/Logic* → Python (rule-based keyword matching, quiz scoring, roadmap generation)
* *Database* → CSV-based storage (users, colleges, quiz data)
* *External APIs* → [NewsAPI](https://newsapi.org/) for fetching career-related updates

---

## ⚙️ Workflow

mermaid
flowchart TD
    A[User Input: Interests + Quiz] --> B[Keyword Matching & Scoring]
    B --> C[Career & Roadmap Generation]
    C --> D[Degree + Entrance Exams + MOOCs]
    C --> E[Localized College Recommendations]
    C --> F[News Feed & Notifications]
    D --> G[Personalized Dashboard]
    E --> G
    F --> G


---


## 🎯 Problem Solved

* ❌ Students feel lost while choosing careers
* ❌ Lack of localized college/career data
* ❌ Over-reliance on costly psychometric/AI-driven tools
* ❌ No step-by-step roadmap for skill-building

✅ Career Compass *solves this* by offering a *free, transparent, and region-specific solution*.

---

## 📊 Market Differentiation

| Feature        | Career Compass                                 | Other Career Apps          |
| -------------- | ---------------------------------------------- | -------------------------- |
| Starting Point | Interests & strengths (student-first)          | Generic courses/tests      |
| Guidance       | Rule-based, transparent                        | AI/psychometric, black-box |
| Roadmaps       | Detailed step-by-step (exams → MOOCs → skills) | Only career names          |
| Colleges       | Localized dataset                              | Only top-tier colleges     |
| Accessibility  | Free, lightweight                              | Paid/subscription          |
| Updates        | Live career news & notifications               | Static content             |

---

## 📈 Impact

* 🎓 *Students* → Clearer career direction, affordable guidance
* 🏫 *Colleges* → Better visibility in local regions
* 🌍 *Society* → Democratized access to career guidance in Tier-2/3 & rural areas

---

## 🔮 Future Scope

* Expand to *national-level datasets* of colleges & careers
* Integration with *Govt. education portals* (e.g., NEP 2020, Skill India)
* AI-powered personalization (phase-2, optional)
* Mobile-first responsive version

---

## 👥 Team Pathfinders

* Problem Statement: *SIH25094*
* Theme: *Smart Solutions for Career & Education*
* Category: *Software*
