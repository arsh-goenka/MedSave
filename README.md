## Inspiration
Every year, billions of dollars in unused medications are discarded by:
- Pharmacies
- Hospitals
- Nursing homes

Often, this is simply due to expiration dates.  
One study found that hospitals waste over **$800 million** in usable drugs annually.  
Meanwhile, **1 in 3 Americans** skip medications due to cost.

---

## What it does
**MedSave** bridges the gap between surplus medications and communities in need.

It connects:
- Pharmacies with excess or soon-to-expire inventory that can offer steep discounts 
- Nonprofits and clinics serving underserved populations:
  - Community health centers
  - Shelters
  - Aid organizations

By reducing waste and improving access to essential medicine, MedSave makes a tangible impact — both environmentally and socially.

---

## How we built it
- **Frontend:** React, HTML, CSS, JavaScript, Tailwind CSS  
- **Authentication:** Google OAuth  
- **Address Lookup:** Mapbox API  
- **Backend:** Flask with multiple RESTful endpoints  
- **Database:** SQLite (for user, drug, and pharmacy data)  
- **External API:** NDC Directory API (for drug metadata)

---

## How it works
Upon visiting MedSave:
- Users log in via **Google authentication**
- They select one of two roles:
  - **Pharmacy**
  - **Nonprofit**

**Pharmacy users** can:
- List surplus/soon-to-expire medications by entering:
  - NDC code
  - Pharmacy name
  - Location
  - Price
  - Expiration date
- The backend uses the **NDC Directory API** to autofill:
  - Generic drug name
  - Manufacturer info
- All data is stored in a **SQLite database** and displayed in the marketplace

**Nonprofit users** can:
- Search for medications by entering:
  - Drug name
  - Their address
- The backend returns:
  - Listings from the nearest pharmacies selling the drug
  - Prioritized by proximity

---

## Challenges we ran into
As first-time hackathon participants, we faced challenges such as:
- ⚙️ Git and version control mishaps
- 🎨 Frontend styling and layout tweaks
- 🔐 Troubleshooting authentication flow
- 🔄 Keeping backend and frontend in sync

---

## Accomplishments that we're proud of
- ✅ Completed and deployed a full-stack web application  
- 🔐 Successfully integrated Google OAuth and Mapbox  
- 🤝 Collaborated and adapted quickly under time pressure  
- 🧠 Gained practical experience with APIs, databases, and user roles

---

## What we learned
- 📁 Effective use of Git/GitHub for collaboration  
- 🐞 Debugging full-stack issues  
- 🔒 Best practices for authentication and session management  
- 🔁 Frontend-to-backend integration techniques

---

## What's next for MedSave
We plan to expand MedSave’s functionality with:
- 🔍 More advanced filtering (by radius, drug brand, etc.)  
- 📬 Alerts for nonprofits when needed medications become available  
- 📊 Dashboards with analytics and request tracking  
- 🧱 Upgrade to a scalable backend (e.g., PostgreSQL)  
- ✅ Verification & incentive systems to promote responsible listings
