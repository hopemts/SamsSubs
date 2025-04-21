# 🥪 Sam's Subs Data Warehouse Project

Welcome to the GitHub repository for our **Sam's Subs** Data Warehouse Project. This project reflects our end-to-end journey as data consultants — from cleaning and normalizing raw sandwich consumption data, to designing a scalable data warehouse, automating ELT pipelines, and producing actionable customer-facing visualizations.

This repository consolidates all **four deliverables** into a comprehensive project document that outlines our process, screenshots, and final results.

---

## 📘 Project Overview

This project was developed as part of a semester-long assignment for a data warehousing course. Acting as consultants for Sam’s Subs, our goal was to help the company improve its data infrastructure and leverage insights to enhance customer engagement and decision-making.

Throughout the project, we:

- Normalized a messy dataset and built a transactional database in SQL Server
- Designed and implemented a dimensional model using the Kimball methodology
- Loaded data into Snowflake using Fivetran and transformed it using dbt
- Built Tableau dashboards with customer-specific visualizations and strategic recommendations

---

## 🧩 Deliverable 1: Data Normalization and SQL Server Database Creation

📌 **Goal**: Transform a denormalized Excel dataset into a normalized relational schema in 3NF and import it into SQL Server.

### Key Tasks:
- Created an ERD using LucidChart, normalized to 3NF
- Imported data into SQL Server using SSMS Import Wizard
- Designed and populated OLTP tables

![51C9F459-7E54-4342-8D5A-9CD81EBEB045](https://github.com/user-attachments/assets/703cb808-fd03-41ef-a6f3-c8288cfdfcd8)

---

## 🧱 Deliverable 2: Enterprise Data Warehouse Design - Dimensional Modeling

📌 **Goal**: Transition the normalized data into a dimensional model optimized for analytics.

### Key Tasks:
- Defined business processes: Order Processing and Web Traffic Analytics
- Created two star schemas, then integrated them into one enterprise model
- Identified conformed dimensions and missing data elements

  
![4029F53C-B972-46E4-960B-3CAB8C93462C](https://github.com/user-attachments/assets/b754dfb3-b104-4ac3-98b2-4b6cb1944e93)

---

## 🔄 Deliverable 3: ELT with Fivetran, Snowflake, and dbt

📌 **Goal**: Populate the dimensional model using modern ELT techniques and cloud infrastructure.

🔗 **Repo Link**: [View Deliverable 3 Code and dbt Project](https://github.com/hopemts/dw_dbt.git)

### Key Tasks:
- Extracted data from:
  - AWS S3 (Web Traffic Events)
  - PostgreSQL (Transactional Database)
- Loaded data into Snowflake staging tables via Fivetran
- Transformed and populated fact/dimension tables in Snowflake using dbt
- Created surrogate keys using `dbt_utils.generate_surrogate_key`
- Wrote 3 business questions and queries based on the dimensional model


- Snowflake schema view
![72EA0F05-2FFE-4E83-B89A-8A272BA19943_1_201_a](https://github.com/user-attachments/assets/03b86882-9247-4641-9678-8608bd4a26b3)


---

# 📊 Deliverable 4: Visualization & Strategic Recommendations

## 📌 Goal
Deliver customer-facing insights and recommend improvements to Sam’s Subs data ecosystem.

## 🧠 Key Features

### 🔧 Full-Stack Web Application: "Sandwich Unwrapped"
We built a full-stack web application using:
- **Django** for the backend
- **React** for the frontend
- **Snowflake** as the data warehouse

This application pulls personalized data for each customer from Snowflake and visualizes:
- Your sandwich journey
- Your favorite sandwich
- Your favorite side
- Your favorite order method
- Your favorite location

### 💡 Strategic Recommendations
We provided a data strategy improvement plan to:
- Enhance the granularity and quality of data collected
- Enable deeper, more actionable customer insights
- Support scalable visualization and reporting

### 📊 Dashboard Mock-Up
Our dashboard prototype demonstrates how improved data quality and structure can power a more insightful and engaging customer experience.

## 📁 Where to Find the Code
All code for this deliverable is located in the **Final Deliverable** folder of this repository.

## 📸 Screenshots Included
- Customer-facing dashboard
![FF205561-A6A6-40F3-B5CC-D0342D7242A1_1_201_a](https://github.com/user-attachments/assets/71c42cc9-3781-41f1-9d36-ce33ed86616a)


---
