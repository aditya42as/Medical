import os
from datetime import datetime
from fpdf import FPDF
from database_manager import RayaDB

class TokenProcessor:
    def __init__(self):
        try: 
            self.db = RayaDB()
        except: 
            self.db = None
        
        # Files setup
        self.logo_path = "image_1.jpeg" 
        self.patient_img_path = "patient_photo.jpg" 

    def get_triage_info(self, report):
        """Symptom ke hisaab se Dept aur Color decide karna"""
        rep = str(report).lower()
        dept, color, level = "GENERAL MEDICINE", (0, 128, 0), "NORMAL (GREEN)"

        # Logic for Departments & Triage Colors
        if any(x in rep for x in ["heart", "chest pain", "cardiac", "breathing"]):
            dept, color, level = "CARDIOLOGY", (255, 0, 0), "EMERGENCY (RED)"
        elif any(x in rep for x in ["bone", "fracture", "joint", "back pain", "ortho"]):
            dept, color, level = "ORTHOPEDICS", (255, 165, 0), "URGENT (YELLOW)"
        elif any(x in rep for x in ["stomach", "acidity", "digestion", "vomit", "gastric"]):
            dept, color, level = "GASTROENTEROLOGY", (0, 128, 0), "NORMAL (GREEN)"
        elif any(x in rep for x in ["brain", "headache", "seizure", "paralysis", "nerve"]):
            dept, color, level = "NEUROLOGY", (255, 0, 0), "EMERGENCY (RED)"
        elif any(x in rep for x in ["skin", "rash", "itching", "allergy"]):
            dept, color, level = "DERMATOLOGY", (0, 128, 0), "NORMAL (GREEN)"
        elif any(x in rep for x in ["child", "baby", "pediatric", "infant"]):
            dept, color, level = "PEDIATRICS", (0, 128, 0), "NORMAL (GREEN)"
        elif any(x in rep for x in ["ear", "nose", "throat", "hearing", "sinus"]):
            dept, color, level = "ENT SPECIALIST", (0, 128, 0), "NORMAL (GREEN)"
        elif any(x in rep for x in ["eye", "vision", "blind", "glasses"]):
            dept, color, level = "OPHTHALMOLOGY", (0, 128, 0), "NORMAL (GREEN)"

        return dept, color, level

    def generate_pdf(self, data, report, dept_name, triage_color, triage_level):
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # 1. BACKGROUND WATERMARK (Oxway Logo)
            if os.path.exists(self.logo_path):
                with pdf.local_context(fill_opacity=0.08):
                    pdf.image(self.logo_path, x=60, y=95, w=90) 

            # Header
            pdf.set_font("Arial", 'B', 24)
            pdf.set_text_color(0, 51, 102) 
            pdf.cell(0, 12, "OXWAY SMART HEALTHCARE", align='L')
            pdf.ln(15)

            # 2. PATIENT PHOTO (Right Side Frame)
            if os.path.exists(self.patient_img_path):
                pdf.image(self.patient_img_path, x=160, y=35, w=35, h=40)
            else:
                pdf.set_draw_color(200, 200, 200)
                pdf.rect(160, 35, 35, 40)
                pdf.set_font("Arial", '', 7)
                pdf.set_text_color(150, 150, 150)
                pdf.text(163, 55, "NO PHOTO")

            # Token & Major ID
            pdf.set_font("Arial", 'B', 14)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(70, 15, f"MAJOR ID: {data['major_id']}", border=1, align='C')
            pdf.cell(70, 15, f"SUB TOKEN: {data['sub_token']}", border=1, align='C')
            pdf.ln(20)
            
            # 3. TRIAGE COLOR BAR
            pdf.set_fill_color(*triage_color)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(140, 10, f" DEPT: {dept_name} | PRIORITY: {triage_level}", fill=True, align='C')
            pdf.ln(15)

            # Patient Info
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", 'B', 11)
            name_fixed = str(data['name']).encode('ascii', 'ignore').decode('ascii')
            pdf.cell(0, 10, f"PATIENT: {name_fixed.upper()}")
            pdf.ln(7)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 7, f"AGE: {data['age']} | MOBILE: {data['mobile']} | DATE: {data['date']}")
            pdf.ln(15)
            
            # --- PROBLEM & SUMMARY SECTION ---
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 150, pdf.get_y()) 
            pdf.ln(5)

            # 4. MAIN PROBLEM
            pdf.set_font("Arial", 'B', 12)
            prob_text = f"PROBLEM: {data.get('main_problem', 'General Checkup').upper()}"
            pdf.cell(0, 10, prob_text.encode('ascii', 'ignore').decode('ascii'))
            pdf.ln(12)

            # 5. CLINICAL SUMMARY (Bullet Points)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 10, "CLINICAL SUMMARY & HISTORY:")
            pdf.ln(8)
            
            pdf.set_font("Arial", '', 10)
            # Breaking report into sentences for bullet points
            summary_points = str(report).replace('\n', '.').split('.') 
            for point in summary_points:
                clean_point = point.strip().encode('ascii', 'ignore').decode('ascii')
                if len(clean_point) > 5: 
                    pdf.set_x(15) # Indentation
                    pdf.cell(0, 7, f"- {clean_point}")
                    pdf.ln(7)

            # Footer
            pdf.set_y(-25)
            pdf.set_font("Arial", 'I', 8)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 10, "Generated by RAYA AI - Oxway Smart Healthcare Systems", align='C')

            # Save PDF
            os.makedirs("tokens", exist_ok=True)
            path = f"tokens/{data['sub_token']}.pdf"
            pdf.output(path)
            return path
        except Exception as e:
            print(f"PDF Error: {e}")
            return None

    def process_user_dynamic(self, patient_data, report, original_problem="General Checkup"):
        dept, color, level = self.get_triage_info(report)
        today = datetime.now().strftime("%Y-%m-%d")
        
        major_count, dept_count = 0, 0
        if self.db:
            major_count, dept_count = self.db.get_counts(today, dept)

        data = {
            "name": patient_data['name'], "age": patient_data['age'], 
            "mobile": patient_data['mobile'], "date": today,
            "major_id": major_count + 1, 
            "sub_token": f"{dept[:4].upper()}-{(dept_count + 1):03d}",
            "main_problem": original_problem
        }

        if self.db:
            self.db.save_token(today, data['sub_token'], dept, data['name'])
            
        return data, self.generate_pdf(data, report, dept, color, level)