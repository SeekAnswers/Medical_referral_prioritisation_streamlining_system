from typing import List, Dict
from datetime import datetime

class MedicalReferralTestDataset:
    """
    Test dataset with ground truth based on NHS Clinical Guidelines and NICE recommendations
    
    Priority Classifications (NHS Standards):
    - EMERGENT: Life-threatening, immediate response required (<15 minutes)
    - URGENT: Serious conditions requiring rapid assessment (<2 hours) 
    - ROUTINE: Scheduled care, non-urgent (<18 weeks standard)
    
    References:
    - NHS Emergency Care Standards
    - NICE Clinical Guidelines  
    - Royal College Emergency Medicine Standards
    - NHS Referral to Treatment Standards
    """
    
    @staticmethod
    def get_priority_classification_dataset() -> List[Dict]:
        """Medical test cases with known correct priorities for your system"""
        return [
            {
                "case_id": "URGENT_001",
                "referral_text": """
                Patient ID: PT001
                Name: John Smith
                Age: 65
                Address: 123 High Street, London
                
                Patient presents with severe crushing chest pain 9/10, radiating to left arm and jaw.
                Started 2 hours ago during rest. Associated shortness of breath, nausea, diaphoresis.
                Known CAD, previous MI 2019. Current medications: Aspirin, Atorvastatin, Metoprolol.
                ECG shows ST elevation V2-V5. Troponin elevated at 450 ng/L.
                Requires immediate cardiology assessment for acute STEMI.
                
                Staff: Dr. Sarah Wilson
                Location: Emergency Department, City Hospital
                """,
                "ground_truth": {
                    "priority": "Emergent",
                    "specialty": "Cardiology", 
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_001", 
                "referral_text": """
                Patient ID: PT002
                Name: Mary Johnson
                Age: 58
                Address: 456 Oak Avenue, Manchester
                
                Annual diabetes review. Patient reports good glucose control with metformin 1g BD.
                Recent HbA1c 6.8% (improved from 7.2% six months ago). BP 128/78 on lisinopril 10mg.
                No symptoms of diabetic complications. Feet examination normal, pulses present.
                Requests dietary advice and annual retinal screening due.
                
                Staff: Practice Nurse Jenkins
                Location: Greenfield Medical Centre
                """,
                "ground_truth": {
                    "priority": "Routine",
                    "specialty": "Endocrinology",
                    "urgency_score": 1,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_002",
                "referral_text": """
                Patient ID: PT003
                Name: Robert Thompson
                Age: 45
                Address: 789 Pine Road, Birmingham
                
                Suspicious pigmented lesion on back, noted during routine skin check.
                Lesion 8mm diameter, asymmetric borders, color variation (black/brown). 
                Patient reports recent increase in size over 3 months.
                Strong family history of melanoma (father diagnosed age 50).
                No other concerning skin lesions noted on examination.
                
                Staff: Dr. Michael Chang
                Location: Dermatology Clinic, Regional Hospital
                """,
                "ground_truth": {
                    "priority": "Urgent",
                    "specialty": "Dermatology",
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "EMERGENT_002",
                "referral_text": """
                Patient ID: PT004
                Name: Emily Wilson
                Age: 28
                Address: 321 Maple Street, Leeds
                
                Sudden onset severe headache 10/10, described as "worst headache of my life".
                Started 1 hour ago during exercise. Associated neck stiffness, photophobia, vomiting.
                No previous history of migraine. Temperature 37.8°C, kernig's sign positive.
                CT head shows possible subarachnoid hemorrhage.
                Requires immediate neurosurgical consultation.
                
                Staff: Dr. James Mitchell
                Location: Emergency Department, Leeds General
                """,
                "ground_truth": {
                    "priority": "Emergent",
                    "specialty": "Neurosurgery",
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_002",
                "referral_text": """
                Patient ID: PT005
                Name: David Brown
                Age: 42
                Address: 654 Cedar Lane, Bristol
                
                Routine annual health check. Patient feels well, no specific concerns.
                Blood pressure 118/76, BMI 24.5. Non-smoker, moderate alcohol intake.
                Family history of hypertension (father). Exercises regularly.
                Cholesterol screening due, last checked 3 years ago normal.
                Requests general health advice.
                
                Staff: Dr. Lisa Parker
                Location: Westfield Health Centre
                """,
                "ground_truth": {
                    "priority": "Routine",
                    "specialty": "General Practice",
                    "urgency_score": 1,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_003",
                "referral_text": """
                Patient ID: PT006
                Name: Susan Taylor
                Age: 72
                Address: 987 Birch Road, Newcastle
                
                Progressive shortness of breath over 2 weeks, worse on exertion.
                Bilateral ankle swelling, orthopnea requiring 3 pillows to sleep.
                Known heart failure, EF 35% on last echo. Weight gain 4kg in 1 week.
                Current medications: Furosemide, ACE inhibitor, beta-blocker.
                Requires urgent cardiology assessment for decompensated heart failure.
                
                Staff: Dr. Mark Roberts
                Location: Community Cardiology Clinic
                """,
                "ground_truth": {
                    "priority": "Urgent",
                    "specialty": "Cardiology",
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_003",
                "referral_text": """
                Patient ID: PT007
                Name: Peter Davis
                Age: 35
                Address: 147 Elm Street, Sheffield
                
                Follow-up for stable asthma management. Well-controlled on salbutamol PRN.
                Peak flow readings stable, no recent exacerbations or steroid courses.
                Exercises regularly without limitation. Non-smoker.
                Requests repeat prescription and inhaler technique review.
                Annual spirometry due next month.
                
                Staff: Practice Nurse Thompson
                Location: Hillside Medical Practice
                """,
                "ground_truth": {
                    "priority": "Routine",
                    "specialty": "Respiratory Medicine",
                    "urgency_score": 2,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_004",
                "referral_text": """
                Patient ID: PT008
                Name: Rachel Green
                Age: 31
                Address: 852 Willow Avenue, Liverpool
                
                38 weeks pregnant, severe headache, visual disturbances, epigastric pain.
                BP 170/110, proteinuria 3+, recent weight gain 2kg in 3 days.
                Hyperreflexia present, ankle clonus positive.
                No previous history of hypertension or pre-eclampsia.
                Requires immediate obstetric assessment for severe pre-eclampsia.
                
                Staff: Midwife Sarah Collins
                Location: Maternity Assessment Unit
                """,
                "ground_truth": {
                    "priority": "Emergent",  
                    "specialty": "Obstetrics",
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_004",
                "referral_text": """
                Patient ID: PT009
                Name: Michael Clark
                Age: 55
                Address: 741 Pine View, Norwich
                
                Routine colonoscopy screening. Family history of colorectal cancer (brother at 60).
                No gastrointestinal symptoms, normal bowel habits.
                Previous FIT test negative. Good general health, no weight loss.
                Patient counseled about procedure and consents to screening.
                
                Staff: Dr. Helen Wright
                Location: Endoscopy Unit, Norfolk Hospital
                """,
                "ground_truth": {
                    "priority": "Routine",
                    "specialty": "Gastroenterology",
                    "urgency_score": 1,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "EMERGENT_003",
                "referral_text": """
                Patient ID: PT010
                Name: Jennifer Adams
                Age: 67
                Address: 963 Oak Hill, Cardiff
                
                Sudden onset right-sided weakness and speech difficulties 45 minutes ago.
                Unable to lift right arm, facial droop, slurred speech.
                FAST test positive, NIHSS score 12. No head trauma.
                Known atrial fibrillation, stopped warfarin 3 days ago for dental procedure.
                Requires immediate stroke team assessment for thrombolysis.
                
                Staff: Paramedic crew 247
                Location: Emergency Department, University Hospital Wales
                """,
                "ground_truth": {
                    "priority": "Emergent",
                    "specialty": "Stroke Medicine",
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_005",
                "referral_text": """
                Patient ID: PT011
                Name: Thomas Harris
                Age: 29
                Address: 258 Valley Road, Glasgow
                
                Recurrent severe abdominal pain, right iliac fossa tenderness.
                Pain 8/10, started 6 hours ago, worsening with movement.
                Low-grade fever 37.5°C, nausea but no vomiting.
                WBC 14.5, CRP elevated. McBurney's point tenderness positive.
                Clinical suspicion of acute appendicitis requiring surgical review.
                
                Staff: Dr. Anna MacDonald
                Location: Emergency Department, Glasgow Royal Infirmary
                """,
                "ground_truth": {
                    "priority": "Urgent",
                    "specialty": "General Surgery",
                    "urgency_score": 7,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_005",
                "referral_text": """
                Patient ID: PT012
                Name: Angela Moore
                Age: 48
                Address: 369 Rose Gardens, Exeter
                
                Routine mammography screening. No breast symptoms or concerns.
                No family history of breast or ovarian cancer.
                Previous mammograms normal, last performed 3 years ago.
                Patient well, no medications, regular menstrual cycle.
                Part of national breast screening programme.
                
                Staff: Radiographer Team
                Location: Breast Screening Unit, Royal Devon Hospital
                """,
                "ground_truth": {
                    "priority": "Routine",
                    "specialty": "Radiology",
                    "urgency_score": 1,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_006",
                "referral_text": """
                Patient ID: PT013
                Name: Christopher Lee
                Age: 54
                Address: 147 Church Street, Bath
                
                Sudden onset severe back pain radiating to groin, unable to find comfortable position.
                Pain started 3 hours ago, 9/10 severity, colicky nature.
                Microscopic hematuria on dipstick, no fever or dysuria.
                Previous history of kidney stones 5 years ago.
                Requires urgent urology assessment for suspected renal colic.
                
                Staff: Dr. Patricia Hughes
                Location: Emergency Department, Royal United Hospital
                """,
                "ground_truth": {
                    "priority": "Urgent",
                    "specialty": "Urology",
                    "urgency_score": 7,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_006",
                "referral_text": """
                Patient ID: PT014
                Name: Margaret White
                Age: 63
                Address: 582 Garden Close, Canterbury
                
                Routine eye examination for diabetic retinopathy screening.
                Type 2 diabetes for 8 years, well controlled with metformin.
                Last eye check 12 months ago showed no retinopathy.
                No visual symptoms, reading glasses only for presbyopia.
                Annual screening as per diabetes care pathway.
                
                Staff: Practice Nurse Kelly
                Location: Cathedral Medical Centre
                """,
                "ground_truth": {
                    "priority": "Routine",
                    "specialty": "Ophthalmology",
                    "urgency_score": 2,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_007",
                "referral_text": """
                Patient ID: PT015
                Name: Kevin Turner
                Age: 71
                Address: 194 High Road, Brighton
                
                Worsening confusion and agitation over 48 hours, not recognizing family.
                Temperature 38.9°C, recent fall with minor head injury 3 days ago.
                Urinalysis shows leucocytes and nitrites, drowsy but rousable.
                Known dementia but significant deterioration from baseline.
                Requires urgent assessment for delirium and possible UTI.
                
                Staff: Dr. Fiona Stewart
                Location: Elderly Care Assessment Unit
                """,
                "ground_truth": {
                    "priority": "Urgent",
                    "specialty": "Geriatric Medicine",
                    "urgency_score": 7,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_007",
                "referral_text": """
                Patient ID: PT016
                Name: Helen Baker
                Age: 39
                Address: 825 Meadow Lane, York
                
                Contraceptive review and cervical screening due.
                Currently on combined oral contraceptive pill, no side effects.
                Regular cycles, no breakthrough bleeding or other concerns.
                Last smear 3 years ago normal, sexually active in stable relationship.
                Requests contraceptive advice and routine screening.
                
                Staff: Practice Nurse Williams
                Location: Minster Health Centre
                """,
                "ground_truth": {
                    "priority": "Routine",
                    "specialty": "Gynecology",
                    "urgency_score": 1,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_008",
                "referral_text": """
                Patient ID: PT017
                Name: Daniel Miller
                Age: 8
                Address: 736 School Lane, Oxford
                
                High fever 39.5°C for 24 hours, refusing to walk, crying when hip moved.
                No obvious injury or trauma, child appears unwell and irritable.
                Parents report child limping yesterday before fever started.
                CRP 85, WBC 16.2. Unable to bear weight on right leg.
                Urgent pediatric orthopedic assessment for possible septic arthritis.
                
                Staff: Dr. Sophie Reynolds
                Location: Children's Emergency Department
                """,
                "ground_truth": {
                    "priority": "Urgent",
                    "specialty": "Pediatric Orthopedics",
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_008",
                "referral_text": """
                Patient ID: PT018
                Name: Sarah Cooper
                Age: 26
                Address: 491 Sunset Drive, Portsmouth
                
                Routine antenatal appointment at 28 weeks gestation.
                Pregnancy progressing normally, all previous scans normal.
                Blood pressure 115/70, urine clear, appropriate weight gain.
                Fetal movements felt regularly, no concerns or symptoms.
                Glucose tolerance test and routine bloods due.
                
                Staff: Midwife Rachel Jones
                Location: Community Midwifery Unit
                """,
                "ground_truth": {
                    "priority": "Routine",
                    "specialty": "Obstetrics",
                    "urgency_score": 2,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_009",
                "referral_text": """
                Patient ID: PT019
                Name: Richard Evans
                Age: 59
                Address: 612 Victoria Street, Nottingham
                
                Worsening shortness of breath and productive cough with blood-stained sputum.
                Symptoms over 3 weeks, weight loss 5kg in 2 months.
                Heavy smoker 40 pack-years, no previous respiratory issues.
                Chest X-ray shows right upper lobe mass with hilar lymphadenopathy.
                Urgent respiratory referral for suspected lung malignancy.
                
                Staff: Dr. Graham Foster
                Location: Respiratory Outpatient Clinic
                """,
                "ground_truth": {
                    "priority": "Urgent",
                    "specialty": "Respiratory Medicine",
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_009",
                "referral_text": """
                Patient ID: PT020
                Name: Caroline Phillips
                Age: 44
                Address: 378 Park View, Cambridge
                
                Routine medication review for well-controlled hypertension.
                Currently on amlodipine 5mg daily, BP consistently 125/78.
                No side effects, good compliance with medication.
                Lifestyle modifications maintained: regular exercise, low salt diet.
                Annual review as per hypertension management protocol.
                
                Staff: Clinical Pharmacist Davies
                Location: University Health Centre
                """,
                "ground_truth": {
                    "priority": "Routine",
                    "specialty": "General Practice",
                    "urgency_score": 1,
                    "expected_response_time_ms": 3000
                }
            },
            
            {
                "case_id": "EMERGENT_004",
                "referral_text": """
                Patient ID: PT021
                Name: James Wilson
                Age: 34
                Address: 145 Market Street, Edinburgh
                
                Anaphylactic reaction to peanuts, severe respiratory distress and hypotension.
                Facial and laryngeal swelling, wheeze, BP 80/40, tachycardia 140bpm.
                Patient received adrenaline auto-injector 5 minutes ago with partial improvement.
                Known severe nut allergy, accidental exposure at restaurant.
                Requires immediate emergency care for ongoing anaphylaxis.
                
                Staff: Paramedic Team Alpha-7
                Location: Emergency Department, Royal Infirmary Edinburgh
                """,
                "ground_truth": {
                    "priority": "Emergent",  
                    "specialty": "Emergency Medicine",
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_010",
                "referral_text": """
                Patient ID: PT022
                Name: Linda Thompson
                Age: 52
                Address: 267 Kings Road, Windsor
                
                Severe epigastric pain radiating to back, 8/10 severity for 4 hours.
                Associated nausea and vomiting, unable to find comfortable position.
                Known gallstones, lipase elevated at 850 U/L (normal <60).
                CT shows pancreatic inflammation consistent with acute pancreatitis.
                Requires urgent gastroenterology assessment.
                
                Staff: Dr. Andrew Mitchell
                Location: Emergency Department, Wexham Park Hospital
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Gastroenterology",
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_010",
                "referral_text": """
                Patient ID: PT023
                Name: Robert Davies
                Age: 67
                Address: 834 Church Lane, Stratford-upon-Avon
                
                Routine follow-up for stable COPD. Well controlled on inhalers.
                Spirometry stable, no recent exacerbations requiring steroids.
                Smoking cessation achieved 2 years ago. Exercise tolerance maintained.
                Annual review as per COPD care pathway, flu vaccination due.
                
                Staff: Respiratory Nurse Specialist
                Location: Warwick Hospital Respiratory Clinic
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Respiratory Medicine",
                    "urgency_score": 2,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "EMERGENT_005",
                "referral_text": """
                Patient ID: PT024
                Name: Sophie Anderson
                Age: 19
                Address: 492 University Road, Durham
                
                Attempted suicide by paracetamol overdose 3 hours ago, 40 tablets taken.
                Patient now expressing regret but psychiatrically unstable.
                Paracetamol level 180mg/L at 4 hours post-ingestion.
                Requires immediate N-acetylcysteine and psychiatric assessment.
                High risk of hepatotoxicity without urgent treatment.
                
                Staff: Dr. Emma Richardson
                Location: Emergency Department, University Hospital Durham
                """,
                "ground_truth": {
                    "priority": "Emergent",  
                    "specialty": "Emergency Medicine",
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_011",
                "referral_text": """
                Patient ID: PT025
                Name: Mark Edwards
                Age: 41
                Address: 716 Riverside Drive, Chester
                
                Sudden onset diplopia and ptosis, difficulty speaking and swallowing.
                Symptoms developed over 6 hours, progressive weakness.
                Recent history of minor wound infection treated with antibiotics.
                Clinical suspicion of botulism or myasthenia gravis crisis.
                Requires urgent neurology assessment.
                
                Staff: Dr. Catherine Bell
                Location: Countess of Chester Hospital
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Neurology",
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_011",
                "referral_text": """
                Patient ID: PT026
                Name: Patricia Morgan
                Age: 73
                Address: 553 Garden Square, Harrogate
                
                Routine cataract assessment. Gradual vision deterioration over 2 years.
                No pain or acute symptoms, can still read with glasses.
                Activities of daily living mildly affected, drives during daylight only.
                Referred for routine cataract surgery consideration.
                
                Staff: Optometrist Johnson
                Location: Harrogate District Hospital Eye Clinic
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Ophthalmology",
                    "urgency_score": 1,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_012",
                "referral_text": """
                Patient ID: PT027
                Name: Graham Foster
                Age: 68
                Address: 329 Hill View, Gloucester
                
                Acute urinary retention, unable to pass urine for 12 hours.
                Severe suprapubic pain, palpable bladder to umbilicus.
                Known BPH, previous episodes but resolved spontaneously.
                Attempted catheterization failed in community, requires urgent urology.
                
                Staff: District Nurse Williams
                Location: Gloucestershire Royal Hospital
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Urology",
                    "urgency_score": 7,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_012",
                "referral_text": """
                Patient ID: PT028
                Name: Jennifer Clark
                Age: 29
                Address: 681 Victoria Avenue, Blackpool
                
                Preconception counseling appointment. Planning pregnancy in 6 months.
                Previous uncomplicated pregnancy 3 years ago. Taking folic acid.
                General health excellent, up-to-date with cervical screening.
                Requests advice on optimization and genetic counseling.
                
                Staff: Dr. Samantha Price
                Location: Blackpool Teaching Hospital Family Planning
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Obstetrics",
                    "urgency_score": 1,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "EMERGENT_006",
                "referral_text": """
                Patient ID: PT029
                Name: William Roberts
                Age: 76
                Address: 147 Oak Street, Swansea
                
                Massive upper GI bleed, coffee ground vomiting and melena.
                Haemoglobin dropped from 14.2 to 8.1 g/dL in 6 hours.
                BP 90/50, pulse 110, cold peripheries, confused.
                Known peptic ulcer disease, taking NSAIDs despite advice.
                Requires immediate endoscopy and blood transfusion.
                
                Staff: Dr. Rhodri Evans
                Location: Morriston Hospital Emergency Department
                """,
                "ground_truth": {
                    "priority": "Emergent",  
                    "specialty": "Gastroenterology",
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_013",
                "referral_text": """
                Patient ID: PT030
                Name: Helen Watson
                Age: 55
                Address: 892 Forest Road, Nottingham
                
                New onset seizures, 3 episodes in past 24 hours.
                No previous history of epilepsy, fully conscious between episodes.
                Recent headaches and personality changes noted by family.
                CT head shows possible space-occupying lesion.
                Requires urgent neurosurgical opinion.
                
                Staff: Dr. Martin Hughes
                Location: Queen's Medical Centre
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Neurosurgery", 
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_013",
                "referral_text": """
                Patient ID: PT031
                Name: Charles Bennett
                Age: 61
                Address: 436 Park Lane, Cheltenham
                
                Routine PSA follow-up. Previous elevated PSA 6.8, biopsy negative.
                Current PSA stable at 6.2, no urinary symptoms.
                Digital rectal examination normal, good general health.
                Annual monitoring as per active surveillance protocol.
                
                Staff: Dr. Julia Armstrong
                Location: Cheltenham General Hospital Urology
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Urology",
                    "urgency_score": 2,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_014",
                "referral_text": """
                Patient ID: PT032
                Name: Sandra Lewis
                Age: 43
                Address: 758 Mill Street, Stoke-on-Trent
                
                Sudden onset severe vertigo with nausea and vomiting.
                Unable to stand or walk, symptoms started 2 hours ago.
                No hearing loss or tinnitus, no focal neurological signs.
                Blood pressure and temperature normal.
                Requires urgent ENT assessment to exclude central cause.
                
                Staff: Dr. Peter Collins
                Location: Royal Stoke University Hospital
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "ENT",
                    "urgency_score": 7,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_014",
                "referral_text": """
                Patient ID: PT033
                Name: Andrew Murphy
                Age: 38
                Address: 621 Station Road, Preston
                
                Routine skin lesion check. Multiple moles, family history of melanoma.
                No concerning changes in existing moles noted.
                Annual screening as recommended by dermatologist.
                Patient performs regular self-examination.
                
                Staff: Dr. Rebecca Turner
                Location: Royal Preston Hospital Dermatology
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Dermatology",
                    "urgency_score": 1,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "EMERGENT_007",
                "referral_text": """
                Patient ID: PT034
                Name: Mary Phillips
                Age: 82
                Address: 394 Church Hill, Bury St Edmunds
                
                Acute confusion and high fever 39.8°C, rigors and hypotension.
                Blood pressure 75/45, tachycardia 130bpm, decreased urine output.
                Clinical signs of sepsis with organ dysfunction.
                Likely source urinary tract, requires immediate IV antibiotics.
                Sepsis Six protocol initiated.
                
                Staff: Dr. Jonathan Clarke
                Location: West Suffolk Hospital Emergency Department
                """,
                "ground_truth": {
                    "priority": "Emergent",  
                    "specialty": "Emergency Medicine",
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_015",
                "referral_text": """
                Patient ID: PT035
                Name: Paul Harrison
                Age: 49
                Address: 517 Valley View, Shrewsbury
                
                Acute severe asthma attack, not responding to nebulizers.
                Peak flow 40% of predicted, using accessory muscles.
                Difficulty completing sentences, saturations 91% on air.
                Previous ICU admission for asthma 2 years ago.
                Requires urgent respiratory assessment and steroids.
                
                Staff: Dr. Amanda Scott
                Location: Royal Shrewsbury Hospital
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Respiratory Medicine",
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_015",
                "referral_text": """
                Patient ID: PT036
                Name: Elizabeth Green
                Age: 54
                Address: 283 Meadowbrook Lane, Truro
                
                Routine mammography recall. Asymmetric density on screening mammogram.
                No palpable lump or family history of breast cancer.
                Previous mammograms normal, requires additional views and ultrasound.
                Triple assessment clinic appointment arranged.
                
                Staff: Breast Screening Coordinator
                Location: Royal Cornwall Hospital Breast Unit
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Radiology",
                    "urgency_score": 3,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_016",
                "referral_text": """
                Patient ID: PT037
                Name: Simon Kelly
                Age: 33
                Address: 659 Riverside Walk, Worcester
                
                Testicular pain and swelling for 4 hours, sudden onset.
                Left testicle enlarged, exquisitely tender, high riding.
                Negative cremasteric reflex, nausea present.
                Clinical suspicion of testicular torsion.
                Requires immediate urological assessment for detorsion.
                
                Staff: Dr. Rachel Thompson
                Location: Worcestershire Royal Hospital
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Urology",
                    "urgency_score": 9,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_016",
                "referral_text": """
                Patient ID: PT038
                Name: Dorothy Wilson
                Age: 69
                Address: 742 Sunset Close, Bournemouth
                
                Routine hearing aid review. Gradual hearing loss over years.
                Current hearing aids functioning well but due for upgrade.
                No ear pain or discharge, tinnitus stable and manageable.
                Annual audiology assessment as per care pathway.
                
                Staff: Audiologist Sarah Davies
                Location: Royal Bournemouth Hospital Audiology
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "ENT",
                    "urgency_score": 1,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "EMERGENT_008",
                "referral_text": """
                Patient ID: PT039
                Name: Jacob Martin
                Age: 15
                Address: 185 School Street, Wolverhampton
                
                Diabetic ketoacidosis, blood glucose 28mmol/L, ketones 6.2mmol/L.
                Vomiting, dehydration, Kussmaul breathing, drowsy but responsive.
                Known Type 1 diabetes, poor compliance with insulin.
                pH 7.1, bicarbonate 8mmol/L. Requires immediate IV insulin and fluids.
                
                Staff: Dr. Priya Patel
                Location: New Cross Hospital Pediatric Emergency
                """,
                "ground_truth": {
                    "priority": "Emergent",  
                    "specialty": "Pediatric Endocrinology",
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_017",
                "referral_text": """
                Patient ID: PT040
                Name: Catherine Wood
                Age: 26
                Address: 428 Garden Road, Ipswich
                
                24 weeks pregnant, reduced fetal movements for 24 hours.
                Previously active baby, now minimal movement felt.
                No bleeding or pain, blood pressure normal.
                Requires urgent obstetric assessment and CTG monitoring.
                First pregnancy, very anxious.
                
                Staff: Midwife Karen Lewis
                Location: Ipswich Hospital Maternity Unit
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Obstetrics",
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_017",
                "referral_text": """
                Patient ID: PT041
                Name: Brian Cooper
                Age: 77
                Address: 856 Hill Top, Grimsby
                
                Routine cardiology follow-up. Stable angina well controlled.
                Atorvastatin and aspirin, exercise tolerance unchanged.
                No recent chest pain or breathlessness at rest.
                Annual echo shows stable mild LV impairment.
                
                Staff: Dr. Neil Richardson
                Location: Diana Princess of Wales Hospital Cardiology
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Cardiology",
                    "urgency_score": 2,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_018",
                "referral_text": """
                Patient ID: PT042
                Name: Louise Taylor
                Age: 37
                Address: 573 Manor Drive, Salisbury
                
                Severe migraine with visual aura, different from usual pattern.
                Sudden onset occipital headache with zigzag visual disturbance.
                Temperature 37.9°C, mild neck stiffness.
                Previous migraines never this severe or with fever.
                Requires urgent assessment to exclude secondary headache.
                
                Staff: Dr. David Brown
                Location: Salisbury District Hospital
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Neurology",
                    "urgency_score": 7,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_018",
                "referral_text": """
                Patient ID: PT043
                Name: Geoffrey Hall
                Age: 51
                Address: 319 Orchard Way, Exeter
                
                Routine dermatology follow-up for stable psoriasis.
                Topical treatments controlling symptoms well.
                Small plaques on elbows and knees, not spreading.
                Annual review as per chronic disease management.
                
                Staff: Dermatology Nurse Specialist
                Location: Royal Devon and Exeter Hospital
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Dermatology",
                    "urgency_score": 2,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "EMERGENT_009",
                "referral_text": """
                Patient ID: PT044
                Name: Oliver Johnson
                Age: 12
                Address: 664 Park Avenue, Hull
                
                Acute epiglottitis, severe difficulty swallowing and drooling.
                High fever 39.5°C, muffled voice, sitting forward position.
                Respiratory distress with stridor, oxygen saturations 89%.
                Requires immediate ENT and anesthetic assessment.
                Risk of complete airway obstruction.
                
                Staff: Dr. Michelle Parker
                Location: Hull Royal Infirmary Children's Emergency
                """,
                "ground_truth": {
                    "priority": "Emergent",  
                    "specialty": "Pediatric ENT",
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_019",
                "referral_text": """
                Patient ID: PT045
                Name: Stephanie Wright
                Age: 44
                Address: 791 Cedar Court, Coventry
                
                New breast lump discovered 1 week ago, firm and irregular.
                No family history but strong personal concern.
                Lump 2cm, fixed to underlying tissue, no skin changes.
                Requires urgent triple assessment within 2-week pathway.
                
                Staff: GP Dr. Simon Evans
                Location: University Hospital Coventry Breast Clinic
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Breast Surgery",
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_019",
                "referral_text": """
                Patient ID: PT046
                Name: Alan Mitchell
                Age: 66
                Address: 428 Woodland Drive, Derby
                
                Routine ophthalmology review for stable glaucoma.
                Intraocular pressure well controlled on drops.
                Visual fields stable, optic discs unchanged.
                No new visual symptoms, good compliance with treatment.
                
                Staff: Optometrist Team
                Location: Royal Derby Hospital Eye Department
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Ophthalmology",
                    "urgency_score": 2,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_020",
                "referral_text": """
                Patient ID: PT047
                Name: Victoria Adams
                Age: 31
                Address: 552 River View, Cambridge
                
                Sudden onset severe abdominal pain, left-sided, with shoulder tip pain.
                Missed period, positive pregnancy test, pain 9/10.
                Hypotensive 95/55, tachycardia 115bpm, pale and sweaty.
                Clinical suspicion of ruptured ectopic pregnancy.
                Requires immediate gynecological assessment and urgent scan.
                
                Staff: Dr. James Wilson
                Location: Addenbrooke's Hospital Emergency Department
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Gynecology",
                    "urgency_score": 9,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_020",
                "referral_text": """
                Patient ID: PT048
                Name: Ronald Green
                Age: 58
                Address: 637 Church View, Peterborough
                
                Routine orthopedic follow-up post knee replacement surgery.
                Operation 6 months ago, good functional recovery.
                Physiotherapy completed, walking normally without aids.
                Annual review to assess implant and function.
                
                Staff: Orthopedic Nurse Practitioner
                Location: Peterborough City Hospital Orthopedics
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Orthopedics",
                    "urgency_score": 1,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "EMERGENT_010",
                "referral_text": """
                Patient ID: PT049
                Name: Hannah Clarke
                Age: 23
                Address: 173 University Close, Bath
                
                Meningococcal septicemia with purpuric rash spreading rapidly.
                High fever 40.1°C, neck stiffness, photophobia, altered consciousness.
                Non-blanching petechial rash on trunk and limbs.
                Blood pressure 85/50, requires immediate IV antibiotics.
                Lumbar puncture contraindicated due to raised ICP signs.
                
                Staff: Dr. Elizabeth Murphy
                Location: Royal United Hospital Bath Emergency
                """,
                "ground_truth": {
                    "priority": "Emergent",  
                    "specialty": "Infectious Diseases",
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_021",
                "referral_text": """
                Patient ID: PT050
                Name: Marcus Roberts
                Age: 47
                Address: 894 High Street, Blackburn
                
                Acute cholangitis with Charcot's triad: fever, jaundice, RUQ pain.
                Temperature 38.7°C, bilirubin 89μmol/L, elevated WBC 18.5.
                MRCP shows bile duct dilatation with stones.
                Requires urgent ERCP and biliary decompression.
                
                Staff: Dr. Alison Ward
                Location: Royal Blackburn Hospital Gastroenterology
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Gastroenterology",
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_021",
                "referral_text": """
                Patient ID: PT051
                Name: Susan Robinson
                Age: 72
                Address: 756 Garden Street, Warrington
                
                Routine memory clinic assessment. Family concerns about forgetfulness.
                MMSE 26/30, activities of daily living preserved.
                Gradual onset over 18 months, no acute confusion.
                Requires cognitive assessment and screening for dementia.
                
                Staff: Memory Clinic Nurse
                Location: Warrington Hospital Memory Services
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Geriatric Medicine",
                    "urgency_score": 2,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_022",
                "referral_text": """
                Patient ID: PT052
                Name: David Thompson
                Age: 52
                Address: 381 Oak Lane, Stockport
                
                Acute kidney injury with oliguria and rising creatinine.
                Creatinine increased from 98 to 387μmol/L in 48 hours.
                Urea 28mmol/L, potassium 5.8mmol/L, minimal urine output.
                Known diabetes, recent contrast CT scan 3 days ago.
                Requires urgent nephrology assessment.
                
                Staff: Dr. Helen Carter
                Location: Stepping Hill Hospital
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Nephrology",
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_022",
                "referral_text": """
                Patient ID: PT053
                Name: Margaret Davis
                Age: 64
                Address: 519 Mill Lane, Burnley
                
                Routine endocrinology follow-up for stable thyroid nodules.
                Ultrasound shows multiple benign-appearing nodules, unchanged.
                Thyroid function normal, no compressive symptoms.
                Annual surveillance as per guidelines.
                
                Staff: Dr. Peter Wilson
                Location: Burnley General Hospital Endocrinology
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Endocrinology",
                    "urgency_score": 2,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "EMERGENT_011",
                "referral_text": """
                Patient ID: PT054
                Name: Christopher Lee
                Age: 68
                Address: 642 Valley Road, Oldham
                
                Acute aortic dissection Type A, tearing chest pain radiating to back.
                Blood pressure differential between arms 40mmHg.
                CT angiogram confirms ascending aortic dissection.
                Requires immediate cardiothoracic surgical intervention.
                High risk of rupture and cardiac tamponade.
                
                Staff: Dr. Sarah Bennett
                Location: Royal Oldham Hospital Emergency
                """,
                "ground_truth": {
                    "priority": "Emergent",  
                    "specialty": "Cardiothoracic Surgery",
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_023",
                "referral_text": """
                Patient ID: PT055
                Name: Rachel Anderson
                Age: 36
                Address: 728 Park Road, Preston
                
                Postpartum hemorrhage 500ml, 6 hours post normal delivery.
                Continuing to bleed despite syntometrine and massage.
                Hemoglobin dropped from 11.8 to 9.2 g/dL.
                Placenta complete, uterus well contracted.
                Requires urgent obstetric assessment for retained products.
                
                Staff: Midwife Carol Hughes
                Location: Royal Preston Hospital Maternity
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Obstetrics",
                    "urgency_score": 7,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_023",
                "referral_text": """
                Patient ID: PT056
                Name: Kenneth White
                Age: 45
                Address: 593 Church Street, Rochdale
                
                Routine vasectomy consultation. Family complete with 3 children.
                No medical contraindications, partner supportive.
                Counseled about permanence and alternative contraception.
                Referred for routine minor surgery.
                
                Staff: Family Planning Nurse
                Location: Rochdale Infirmary Urology
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Urology",
                    "urgency_score": 1,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "URGENT_024",
                "referral_text": """
                Patient ID: PT057
                Name: Emma Johnson
                Age: 28
                Address: 467 Riverside Court, Wakefield
                
                Acute psychotic episode, paranoid delusions and auditory hallucinations.
                Believes neighbors are poisoning her food, not eating for 3 days.
                Previous bipolar disorder, stopped medication 2 months ago.
                Risk to self and others, requires urgent psychiatric assessment.
                
                Staff: Crisis Team Practitioner
                Location: Pinderfields Hospital Mental Health Unit
                """,
                "ground_truth": {
                    "priority": "Urgent",  
                    "specialty": "Psychiatry",
                    "urgency_score": 8,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_024",
                "referral_text": """
                Patient ID: PT058
                Name: Philip Turner
                Age: 59
                Address: 812 Hill View, Huddersfield
                
                Routine rheumatology follow-up for stable rheumatoid arthritis.
                Well controlled on methotrexate and hydroxychloroquine.
                ESR and CRP normal, no active joint inflammation.
                Annual monitoring bloods and disease activity assessment.
                
                Staff: Rheumatology Nurse Specialist
                Location: Huddersfield Royal Infirmary
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Rheumatology",
                    "urgency_score": 2,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "EMERGENT_012",
                "referral_text": """
                Patient ID: PT059
                Name: Isabella Martin
                Age: 7
                Address: 345 School Lane, Barnsley
                
                Status epilepticus, continuous seizure for 25 minutes.
                Rectal diazepam given by parents, minimal response.
                No fever, known epilepsy usually well controlled.
                Requires immediate IV access and further anticonvulsants.
                Risk of permanent neurological damage.
                
                Staff: Paramedic Advanced Team
                Location: Barnsley Hospital Children's Emergency
                """,
                "ground_truth": {
                    "priority": "Emergent",  
                    "specialty": "Pediatric Neurology",
                    "urgency_score": 10,
                    "expected_response_time_ms": 3000
                }
            },
            {
                "case_id": "ROUTINE_025",
                "referral_text": """
                Patient ID: PT060
                Name: Anthony Walker
                Age: 53
                Address: 684 Maple Avenue, Halifax
                
                Routine podiatry assessment for diabetic foot care.
                Type 2 diabetes well controlled, no foot ulcers.
                Peripheral pulses present, sensation intact.
                Annual screening as per diabetic foot pathway.
                
                Staff: Diabetes Specialist Nurse
                Location: Halifax Podiatry Services
                """,
                "ground_truth": {
                    "priority": "Routine",  
                    "specialty": "Podiatry",
                    "urgency_score": 2,
                    "expected_response_time_ms": 3000
                }
            }
        ]

class PerformanceBenchmarks:
    """Healthcare industry performance benchmarks"""
    
    @staticmethod
    def get_response_time_benchmarks() -> Dict:
        """Expected response time benchmarks"""
        return {
            "authentication": {"target_avg_ms": 100, "acceptable_max_ms": 500},
            "dashboard": {"target_avg_ms": 300, "acceptable_max_ms": 1000},
            "ai_analysis": {"target_avg_ms": 3000, "acceptable_max_ms": 10000},
            "referrals_manage": {"target_avg_ms": 500, "acceptable_max_ms": 2000}
        }
    
    @staticmethod 
    def get_accuracy_benchmarks() -> Dict:
        """AI accuracy benchmarks for clinical use"""
        return {
            "priority_classification": {
                "target_accuracy": 85,
                "excellent_accuracy": 90,
                "baseline_accuracy": 70
            },
            "specialty_recommendation": {
                "target_accuracy": 80,
                "excellent_accuracy": 85,
                "baseline_accuracy": 65
            }
        }