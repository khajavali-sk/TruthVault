# **TruthVault** – Anonymous Complaint Management System  

TruthVault is a secure and anonymous complaint management system designed specifically for educational institutions. It enables students to raise concerns without revealing their identity while ensuring fairness through a class-based voting system that determines which complaints gain wider visibility.  

---

## **🌟 Features**  

### 🔹 For Students  
- **Completely Anonymous:** Submit complaints without disclosing your identity.  
- **Class-Based Visibility:** Complaints are initially visible only to students of the same class.  
- **Tracking System:** Each complaint receives a unique tracking ID for status monitoring.  
- **Voting Mechanism:** Students can upvote or downvote complaints in their class.  
- **Public Complaints:** Complaints that meet voting thresholds become visible across the institution.  

### 🔹 For Administrators  
- **Complaint Management:** Review, respond to, and resolve complaints efficiently.  
- **Class-Based Access:** Manage students, classes, and sections dynamically.  
- **Voting Insights:** Monitor voting patterns to ensure fair representation.  
- **Secure Interactions:** Protect student anonymity while addressing concerns transparently.  

---

## **🔐 Security & Privacy**  
- **Anonymous ID System:** Student identities are hashed to maintain confidentiality.  
- **Anti-Duplicate Voting:** Prevents students from voting multiple times on the same complaint.  
- **CSRF Protection:** Ensures security against cross-site request forgery attacks.  
- **Secure Authentication:** Provides a safe login and complaint submission process.  

---

## **🛠️ Tech Stack**  
- **Backend:** Django 5.1 (Python 3.x)  
- **Frontend:** Bootstrap 5 + Font Awesome 6.4.0  
- **Database:** PostgreSQL / SQLite  
- **Security:** Hashing for anonymity, CSRF protection  

---

## **🚀 Installation Guide**  

1️⃣ **Clone the Repository:**  
```bash
git clone [https://github.com/yourusername/truthvault.git](https://github.com/khajavali-sk/TruthVault.git)
cd truthvault
```

2️⃣ **Set Up a Virtual Environment:**  
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3️⃣ **Install Dependencies:**  
```bash
pip install -r requirements.txt
```

4️⃣ **Run Database Migrations:**  
```bash
python manage.py migrate
```

5️⃣ **Create a Superuser (Admin Panel Access):**  
```bash
python manage.py createsuperuser
```

6️⃣ **Start the Development Server:**  
```bash
python manage.py runserver
```

---

## **📌 How It Works**  

### **🔍 Complaint Submission Process**  
1. **Student Logs In** and submits a complaint anonymously.  
2. **Complaint Visibility**: Initially restricted to the student’s class.  
3. **Class-Based Voting**:  
   - Only classmates can upvote or downvote.  
   - If **60% of students vote positively**, the complaint becomes public.  
4. **Admin Review & Response**:  
   - Admins can address complaints while preserving anonymity.  
   - Students receive updates via their **tracking ID**.  

---

## **📊 Rate Limits & Fair Usage**  
- **Max Complaints:** 2 per month, 8 per year per student.  
- **Voting Eligibility:** Only classmates can vote on a complaint.  
- **Visibility Threshold:** Requires 60% class participation for public listing.  

---

## **🤝 Contributing**  

Want to contribute? Follow these steps:  
1. **Fork the repository**  
2. **Create a new branch** (`git checkout -b feature/new-feature`)  
3. **Commit your changes** (`git commit -m "Added a new feature"`)  
4. **Push the branch** (`git push origin feature/new-feature`)  
5. **Open a Pull Request**  

---

## **🙌 Acknowledgments**  
- **Django Framework** – Powering the backend  
- **Bootstrap & Font Awesome** – Providing a sleek UI  
- **All Contributors** – Helping improve TruthVault  
