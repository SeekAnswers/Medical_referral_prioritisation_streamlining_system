# Import necessary modules from FastAPI for handling requests, file uploads, and errors
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, Request, status
# Import Jinja2Templates for rendering HTML templates
from fastapi.templating import Jinja2Templates
# Import StaticFiles for serving static assets (CSS, JS, images)
from fastapi.staticfiles import StaticFiles
# Import HTMLResponse and JSONResponse for handling responses
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
# Import SessionMiddleware for session management
from starlette.middleware.sessions import SessionMiddleware

# Import required modules for image encoding, API requests, and processing
import base64  # Module for encoding images in base64 format
import requests  # Module for making API requests
import io  # Module for handling byte streams
import time  # Module for adding delays
from PIL import Image  # Library for image processing
from dotenv import load_dotenv  # Module for loading environment variables
import os  # Module for interacting with the operating system
import logging  # Module for logging errors and events
from datetime import datetime, date
from contextlib import asynccontextmanager

# Database and Authentication imports
from sqlalchemy.orm import Session  
from sqlalchemy import case  
from database.database import get_db, create_tables
from database.models import User, ReferralRequest, QueryLog, Patient
from utils.auth import get_current_active_user, auth_service, require_role
from utils.database_helpers import (
    extract_patient_id_from_query,
    extract_referring_location,
    extract_staff_name,
    extract_highest_urgency,
    extract_primary_specialty,
    get_or_create_patient,
    create_default_admin_user
)
from routes.auth import router as auth_router
from routes.referrals import router as referrals_router
from routes.fhir import fhir_router # Import FHIR routes(for FHIR integration)


# Configure logging for debugging and error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

# Modern lifespan pattern instead of deprecated on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and create default admin user"""
    try:
        create_tables()
        
        # Create default admin user for development
        db = next(get_db())
        try:
            create_default_admin_user(db)
            print(" Database initialized with default admin user")
        finally:
            db.close()
    except Exception as e:
        print(f" Database initialization error: {e}")
    
    yield
    # Cleanup code would go here if needed

# Initialize FastAPI application with lifespan
app = FastAPI(
    title="Medical Referral Priority System", 
    version="1.0.0",
    lifespan=lifespan
)

# FOR SESSION MIDDLEWARE (before mounting static files)
app.add_middleware(
    SessionMiddleware,
    secret_key="medical-referral-secret-key-change-in-production",
    max_age=3600,  # 1 hour
    same_site="lax",
    https_only=False  # To be set to True in production with HTTPS
)

# Set up Jinja2Templates for rendering HTML templates
templates = Jinja2Templates(directory="templates")

# Mounting of static files for CSS, JS, favicon, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Authentication and referral route inclusion
app.include_router(auth_router)
app.include_router(referrals_router)

# ==========================================
# AI MODEL CONFIGURATION
# ==========================================

# ORIGINAL GROQ CONFIGURATION (COMMENTED OUT - had 45% accuracy)
# Define API endpoint and retrieve API key from environment variables
# GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Ensure the API key is available; raise an error if it's missing
# if not GROQ_API_KEY:
#     raise ValueError("GROQ_API_KEY is not set in the .env file")

# NEW GITHUB MODELS CONFIGURATION (FREE PHI-4-REASONING - Expected 82%+ accuracy, however, achieved 91.37%)
GITHUB_API_URL = "https://models.inference.ai.azure.com/v1/chat/completions"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # GitHub Personal Access Token
MODEL_NAME = "phi-4"  # Free high-performance reasoning model 

# Ensure the GitHub token is available; raise an error if it's missing
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN is not set in the .env file. Please add your GitHub Personal Access Token.")

def make_api_request(model, messages):
    """Make API request to GitHub Models (Phi-4-Reasoning) - FREE during preview"""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": 750,   # Reduced for faster responses - NHS triage is usually concise
        "temperature": 0.05, # set very low for consistent clinical decisions
        "top_p": 0.8,        # Focused reasoning for medical accuracy
        "frequency_penalty": 0.1,  # Reduce repetition
        "presence_penalty": 0.1    # Encourage focused responses
    }
    
    return requests.post(GITHUB_API_URL, headers=headers, json=data)

# ORIGINAL GROQ FUNCTION (COMMENTED OUT)
# def make_api_request(model, messages):
#     """Make API request to Groq"""
#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }
    
#     data = {
#         "model": model,
#         "messages": messages,
#         "max_tokens": 1000,
#         "temperature": 0.7
#     }
    
#     return requests.post(GROQ_API_URL, headers=headers, json=data)

# Add favicon endpoint to prevent 404
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return RedirectResponse(url='/static/favicon.ico')

# Root route to handle authenticated users
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Root route - redirect to appropriate page based on auth status"""
    # Check if user is already authenticated
    token = request.cookies.get("access_token")
    if token:
        try:
            # Try to get current user to validate token
            from utils.auth import auth_service
            if token.startswith("Bearer "):
                token = token.replace("Bearer ", "")
            payload = auth_service.verify_token(token)
            if payload:
                return RedirectResponse(url="/dashboard", status_code=302)
        except:
            pass  # Token invalid, continue to login
    
    return templates.TemplateResponse("login.html", {"request": request})

# Dashboard endpoint (protected)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    current_user: User = Depends(get_current_active_user)
):
    """Protected dashboard for authenticated users"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user
    })

# Main referral interface (protected)
@app.get("/referral", response_class=HTMLResponse)
async def referral_interface(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Protected referral interface"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": current_user
    })

# Referral management route
@app.get("/referrals/management", response_class=HTMLResponse)
async def referrals_management_page(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Referrals management page"""
    return templates.TemplateResponse("referrals_management.html", {
        "request": request,
        "user": current_user
    })

@app.get("/referrals/manage")
async def get_referrals_data(
    search: Optional[str] = None,
    sort_by: str = "referral_date",
    sort_order: str = "desc",
    urgency_filter: Optional[str] = None,
    specialty_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get referrals data with search and filter options"""
    try:
        # Base query - filter by hospital
        query = db.query(ReferralRequest).filter(
            ReferralRequest.created_by == current_user.id
        )
        
        # Application of search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (ReferralRequest.patient_id.ilike(search_term)) |
                (ReferralRequest.staff_name.ilike(search_term)) |
                (ReferralRequest.referring_location.ilike(search_term)) |
                (ReferralRequest.cases_data.ilike(search_term))
            )
        
        # Application of urgency filter
        if urgency_filter and urgency_filter != "all":
            query = query.filter(ReferralRequest.urgency_level == urgency_filter)
        
        # Application of specialty filter
        if specialty_filter and specialty_filter != "all":
            query = query.filter(ReferralRequest.specialty == specialty_filter)
        
        # Application of date range filter
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
                query = query.filter(ReferralRequest.referral_date >= from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
                query = query.filter(ReferralRequest.referral_date <= to_date)
            except ValueError:
                pass
        
        # Application of sorting with proper case import
        if sort_by == "referral_date":
            if sort_order == "desc":
                query = query.order_by(ReferralRequest.referral_date.desc(), ReferralRequest.referral_time.desc())
            else:
                query = query.order_by(ReferralRequest.referral_date.asc(), ReferralRequest.referral_time.asc())
        elif sort_by == "urgency_level":
            if sort_order == "desc":
                query = query.order_by(
                    case(
                        (ReferralRequest.urgency_level == "Emergent", 1),
                        (ReferralRequest.urgency_level == "Urgent", 2),
                        (ReferralRequest.urgency_level == "Routine", 3),
                        else_=4
                    )
                )
            else:
                query = query.order_by(
                    case(
                        (ReferralRequest.urgency_level == "Routine", 1),
                        (ReferralRequest.urgency_level == "Urgent", 2),
                        (ReferralRequest.urgency_level == "Emergent", 3),
                        else_=4
                    )
                )
        elif sort_by == "patient_id":
            if sort_order == "desc":
                query = query.order_by(ReferralRequest.patient_id.desc())
            else:
                query = query.order_by(ReferralRequest.patient_id.asc())
        elif sort_by == "specialty":
            if sort_order == "desc":
                query = query.order_by(ReferralRequest.specialty.desc())
            else:
                query = query.order_by(ReferralRequest.specialty.asc())
        
        # Execute query
        referrals = query.all()
        
        # Prepare response data
        referrals_data = []
        for referral in referrals:
            referrals_data.append({
                "id": referral.id,
                "patient_id": referral.patient_id or "N/A",
                "referring_location": referral.referring_location or "N/A",
                "staff_name": referral.staff_name or "N/A",
                "urgency_level": referral.urgency_level or "Routine",
                "specialty": referral.specialty or "General",
                "referral_date": referral.referral_date.strftime("%Y-%m-%d") if referral.referral_date else "N/A",
                "referral_time": referral.referral_time.strftime("%H:%M") if referral.referral_time else "N/A",
                "status": referral.status or "pending",
                "cases_data": (referral.cases_data[:100] + "...") if referral.cases_data and len(referral.cases_data) > 100 else referral.cases_data or "No data",
                "created_at": referral.created_at.strftime("%Y-%m-%d %H:%M") if referral.created_at else "N/A"
            })
        
        return {
            "referrals": referrals_data,
            "total": len(referrals_data),
            "filters_applied": {
                "search": search,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "urgency_filter": urgency_filter,
                "specialty_filter": specialty_filter,
                "date_from": date_from,
                "date_to": date_to
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching referrals: {e}")
        raise HTTPException(status_code=500, detail="Error fetching referrals data")

# Admin panel endpoint (protected)
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(
    request: Request,
    current_user: User = Depends(require_role("admin"))
):
    """Protected admin panel"""
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": current_user
    })

# Defining endpoint for handling image uploads and queries
@app.post("/upload_and_query")
async def upload_and_query(
    image: Optional[UploadFile] = File(None), 
    query: str = Form(...), 
    request_type: str = Form("general"), 
    context_data: str = Form(""),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        # Consistent handling of image processing
        encoded_image = None
        if image is not None:
            image_content = await image.read()
            if image_content:
                try:
                    # Validate image
                    img = Image.open(io.BytesIO(image_content))
                    img.verify()
                    # Encoding for API use
                    encoded_image = base64.b64encode(image_content).decode("utf-8")
                except Exception as e:
                    logger.error(f"Invalid image format: {str(e)}")
                    raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

        # Initialize responses
        responses = {}

        # Handling different request types with proper message construction
        if request_type == "referral":
            # Domain knowledge informed advanced NHS-compliant referral prioritization prompt 
            referral_prompt = (
                "You are an NHS clinical triage specialist. Classify this referral according to NHS Emergency Care Standards:\n\n"
                "**NHS PRIORITY CLASSIFICATIONS (BE PRECISE - AVOID OVER-ESCALATION):**\n\n"
                "• **EMERGENT (<15 minutes)**: ONLY life-threatening conditions requiring immediate intervention\n"
                "  - Examples: Active cardiac arrest, acute stroke <4.5hrs, severe trauma with shock\n"
                "  - Anaphylaxis with hypotension, DKA with severe acidosis, sepsis with organ failure\n"
                "  - Type A aortic dissection, status epilepticus >5min, severe pre-eclampsia with seizure risk\n"
                "  - Massive GI bleed with shock, meningococcal sepsis with purpuric rash\n\n"
                "• **URGENT (<2 hours)**: Serious conditions requiring prompt assessment\n"
                "  - Examples: Acute appendicitis, testicular torsion, acute urinary retention\n"
                "  - Suspected ectopic pregnancy with pain, severe asthma not responding to treatment\n"
                "  - New seizures with focal signs, acute cholangitis, new breast lump (2-week rule)\n"
                "  - Reduced fetal movements <28 weeks, acute kidney injury with hyperkalemia\n\n"
                "• **ROUTINE (<18 weeks)**: MOST standard NHS care - DO NOT over-escalate these\n"
                "  - ALL routine follow-ups and monitoring (diabetes, hypertension, COPD, stable heart disease)\n"
                "  - ALL screening appointments (mammography, colonoscopy, cervical, diabetic eye)\n"
                "  - Medication reviews, health checks, contraceptive consultations\n"
                "  - Stable chronic conditions without acute changes (psoriasis, stable angina, controlled asthma)\n"
                "  - Elective procedures (vasectomy, cataract surgery, joint replacement follow-up)\n"
                "  - Annual reviews for stable conditions (well-controlled epilepsy, stable thyroid nodules)\n\n"
                "**CRITICAL RULE: If the case mentions 'routine', 'annual', 'follow-up', 'screening', 'stable', 'well-controlled', or 'monitoring' - it is likely ROUTINE unless there are acute concerning features.**\n\n"
                "**CASE DETAILS:**\n"
                f"{query}\n\n"
                "For each case, provide: the NHS-compliant level of urgency (Emergent, Urgent, Routine), "
                "appropriate timeframe, the correct referral destination (specialist unit following NHS pathways), "
                "and clinical justification based on NHS guidelines. Present cases in descending order of urgency.\n\n"
                "Respond using a Markdown table with columns: 'Patient ID', 'Name', 'Age', 'Sex', 'Address', "
                "'Clinical Presentation', 'NHS Priority', 'Response Time', 'NHS Specialty', 'Clinical Justification', 'Urgency Rank'."
            )

            # Creation of separate message object for referral with NHS clinical context
            referral_messages = [
                {
                    "role": "system",
                    "content": "You are a senior NHS clinical triage specialist with 15+ years emergency medicine experience. Follow NHS Emergency Care Standards and NICE guidelines for accurate medical referral prioritization. CRITICAL: Avoid over-escalation of routine cases - most NHS referrals are routine unless there are acute concerning features. Be concise and decisive."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": referral_prompt}
                    ]
                }
            ]

            # Add image if available
            if encoded_image:
                referral_messages[1]["content"].append({
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
                })

            # Send requests to Phi-4-Reasoning model 
            phi4_response = make_api_request(MODEL_NAME, referral_messages)
            
            # ORIGINAL GROQ MODELS (COMMENTED OUT - 45% accuracy)
            # llama_response = make_api_request("meta-llama/llama-4-scout-17b-16e-instruct", referral_messages)
            # llava_response = make_api_request("meta-llama/llama-4-scout-17b-16e-instruct", referral_messages)

            # Process responses from Phi-4-Reasoning model
            if phi4_response.status_code == 200:
                result = phi4_response.json()
                answer = result["choices"][0]["message"]["content"]
                responses["phi4_reasoning"] = answer
                # Set primary response for compatibility
                responses["llama"] = answer  # Keep existing UI compatibility
                responses["llava"] = "Using Phi-4-Reasoning for enhanced NHS compliance"
            else:
                error_msg = f"Error from Phi-4-Reasoning API: {phi4_response.status_code}"
                logger.error(f"Phi-4 API error: {error_msg}")
                responses["phi4_reasoning"] = error_msg
                responses["llama"] = error_msg
                responses["llava"] = error_msg

            # ORIGINAL GROQ PROCESSING (COMMENTED OUT)
            # Process responses
            # for model, response in [("llama", llama_response), ("llava", llava_response)]:
            #     if response.status_code == 200:
            #         result = response.json()
            #         answer = result["choices"][0]["message"]["content"]
            #         responses[model] = answer
            #     else:
            #         responses[model] = f"Error from {model} API: {response.status_code}"

            # Set referral priority from llama response
            responses["referral_priority"] = responses.get("llama", "Error generating referral prioritization.")

            # Addition of database persistence for referral requests
            try:
                # Extract information for database storage
                patient_id = extract_patient_id_from_query(query)
                referring_location = extract_referring_location(query)
                staff_name = extract_staff_name(query)
                urgency_level = extract_highest_urgency(responses.get("referral_priority", ""))
                specialty = extract_primary_specialty(responses.get("referral_priority", ""))

                # Create patient record if patient_id exists
                if patient_id:
                    patient_data = {
                        "patient_id": patient_id,
                        "name": f"Patient {patient_id}",
                        "hospital_id": current_user.hospital_id
                    }
                    patient = get_or_create_patient(db, patient_data)

                # Create referral record
                referral_record = ReferralRequest(
                    patient_id=patient_id,
                    referring_location=referring_location,
                    staff_name=staff_name,
                    cases_data=query,
                    prioritization_result=responses.get("referral_priority"),
                    context_data=f"Original Cases:\n{query}\n\nReferral Prioritisation Result:\n{responses.get('referral_priority')}",
                    referral_date=date.today(),
                    referral_time=datetime.now().time(),
                    status='processed',
                    urgency_level=urgency_level,
                    specialty=specialty,
                    created_by=current_user.id
                )
                
                db.add(referral_record)
                db.commit()
                db.refresh(referral_record)

                # Log the query
                query_log = QueryLog(
                    referral_request_id=referral_record.id,
                    user_id=current_user.id,
                    query_text=query,
                    query_type=request_type,
                    response_llama=responses.get("llama"),
                    response_llava=responses.get("llava")
                )
                db.add(query_log)
                db.commit()

                responses["referral_id"] = referral_record.id

            except Exception as db_error:
                logger.error(f"Database error: {db_error}")
                # Continue without failing the request

        elif request_type == "context_aware":
            # Refined context-aware handling with error checking
            try:
                # Validate context_data
                if not context_data or context_data.strip() == "":
                    # If no context provided, treat as general query
                    context_aware_prompt = f"Medical Question: {query}\n\nPlease provide a detailed medical explanation."
                else:
                    context_aware_prompt = (
                        f"Based on the following medical referral context:\n\n{context_data}\n\n"
                        f"User question: {query}\n\n"
                        "Please provide a detailed explanation addressing the user's question about the referral prioritization. "
                        "Focus on explaining the medical reasoning, urgency criteria, ranking factors, and clinical decision-making "
                        "that led to the specific prioritization outcomes."
                    )

                # Creation of separate message object for context-aware
                context_messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": context_aware_prompt}
                        ]
                    }
                ]

                # Add image if available
                if encoded_image:
                    context_messages[0]["content"].append({
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
                    })

                # Send requests to AI models
                llama_response = make_api_request("meta-llama/llama-4-scout-17b-16e-instruct", context_messages)
                llava_response = make_api_request("meta-llama/llama-4-scout-17b-16e-instruct", context_messages)

                # Process responses with refined error handling
                for model, response in [("llama", llama_response), ("llava", llava_response)]:
                    try:
                        if response.status_code == 200:
                            result = response.json()
                            if "choices" in result and len(result["choices"]) > 0:
                                answer = result["choices"][0]["message"]["content"]
                                responses[model] = answer
                            else:
                                responses[model] = f"No response from {model} API"
                        else:
                            logger.error(f"{model} API error: {response.status_code}, {response.text}")
                            responses[model] = f"Error from {model} API: {response.status_code}"
                    except Exception as model_error:
                        logger.error(f"Error processing {model} response: {model_error}")
                        responses[model] = f"Error processing {model} response"

                # Preservation of existing referral table
                try:
                    if context_data and "Referral Prioritisation Result:" in context_data:
                        parts = context_data.split("Referral Prioritisation Result:")
                        if len(parts) > 1:
                            existing_table = parts[1].strip()
                            responses["referral_priority"] = existing_table
                        else:
                            responses["referral_priority"] = None
                    else:
                        responses["referral_priority"] = None
                except Exception as table_error:
                    logger.error(f"Error preserving referral table: {table_error}")
                    responses["referral_priority"] = None

                # Log context-aware query with better error handling
                try:
                    query_log = QueryLog(
                        user_id=current_user.id,
                        query_text=query,
                        query_type=request_type,
                        response_llama=responses.get("llama", "No response"),
                        response_llava=responses.get("llava", "No response")
                    )
                    db.add(query_log)
                    db.commit()
                    logger.info(f"Context-aware query logged successfully")
                except Exception as db_error:
                    logger.error(f"Database logging error: {db_error}")
                    # Continue without failing the request

            except Exception as context_error:
                logger.error(f"Context-aware processing error: {context_error}")
                # Fallback to basic response
                responses = {
                    "llama": f"Error processing context-aware query: {str(context_error)}",
                    "llava": "Context processing unavailable",
                    "referral_priority": None
                }

        else:
            # Handling general questions with separate message object
            general_messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query}
                    ]
                }
            ]

            # Add image if available
            if encoded_image:
                general_messages[0]["content"].append({
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
                })

            # Send requests to AI models
            llama_response = make_api_request("meta-llama/llama-4-scout-17b-16e-instruct", general_messages)
            llava_response = make_api_request("meta-llama/llama-4-scout-17b-16e-instruct", general_messages)

            # Process responses
            for model, response in [("llama", llama_response), ("llava", llava_response)]:
                if response.status_code == 200:
                    result = response.json()
                    answer = result["choices"][0]["message"]["content"]
                    responses[model] = answer
                else:
                    responses[model] = f"Error from {model} API: {response.status_code}"

            responses["referral_priority"] = None

            # Log general query
            try:
                query_log = QueryLog(
                    user_id=current_user.id,
                    query_text=query,
                    query_type=request_type,
                    response_llama=responses.get("llama"),
                    response_llava=responses.get("llava")
                )
                db.add(query_log)
                db.commit()
            except Exception as db_error:
                logger.error(f"Database logging error: {db_error}")

        return JSONResponse(status_code=200, content=responses)

    except HTTPException as he:
        raise he
    except Exception as e:
        # Error logging for debugging
        logger.error(f"An unexpected error occurred in upload_and_query: {str(e)}")
        logger.error(f"Request type: {request_type}")
        logger.error(f"Query length: {len(query) if query else 0}")
        logger.error(f"Context data length: {len(context_data) if context_data else 0}")
        logger.error(f"User: {current_user.username if current_user else 'None'}")
        
        # Traceback for detailed error info
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={"error": f"An error occurred: {str(e)}", "type": "context_aware_error"}
        )

def generate_referral_table(llama_response):
    """Generate HTML table from referral prioritization response"""
    if not llama_response:
        return "No referral prioritization available."
    
    lines = llama_response.split('\n')
    table_html = """
    <div class="referral-table-container">
        <table class="referral-priority-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Case Description</th>
                    <th>Urgency Level</th>
                    <th>Refer To</th>
                    <th>Clinical Reasoning</th>
                </tr>
            </thead>
            <tbody>
    """
    
    rank = 1
    for line in lines:
        if line.strip() and any(keyword in line.lower() for keyword in ['case', 'patient', 'emergent', 'urgent', 'routine']):
            urgency = "Routine"
            if "emergent" in line.lower():
                urgency = "Emergent"
            elif "urgent" in line.lower():
                urgency = "Urgent"
            
            specialty = "General"
            if "cardiology" in line.lower():
                specialty = "Cardiology"
            elif "emergency" in line.lower():
                specialty = "Emergency"
            elif "surgery" in line.lower():
                specialty = "Surgery"
            
            table_html += f"""
                <tr>
                    <td>{rank}</td>
                    <td>{line.strip()[:100]}...</td>
                    <td class="urgency-{urgency.lower()}">{urgency}</td>
                    <td>{specialty}</td>
                    <td>Based on clinical assessment</td>
                </tr>
            """
            rank += 1
            if rank > 5:
                break
    
    table_html += """
            </tbody>
        </table>
    </div>
    """
    
    return table_html

# Health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint for Docker"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "timestamp": time.time(),
            "service": "Medical Referral Priority System"
        }
    )

# Admin endpoint to create users (protected)
@app.post("/admin/create-user")
async def create_user_admin(
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    department: str = Form(...),
    role: str = Form(...),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )

        # Hash password
        hashed_password = auth_service.hash_password(password)
        
        # Create new user with same hospital_id as admin
        new_user = User(
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            department=department,
            role=role,
            hospital_id=current_user.hospital_id,  # Inherit admin's hospital
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Admin {current_user.username} created user {username}")
        
        return {
            "username": new_user.username,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "department": new_user.department,
            "hospital_id": new_user.hospital_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error creating user"
        )

# Patient search
@app.get("/patient_search", response_class=HTMLResponse)
async def patient_search_page(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Patient search interface page"""
    return templates.TemplateResponse("patient_search.html", {
        "request": request,
        "user": current_user
    })

@app.post("/search_patient")
async def search_patient(
    query: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search for patient referrals by name or partial information"""
    try:
        if not query.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Search query cannot be empty"}
            )
        
        search_term = f"%{query.strip()}%"
        
        # Search in referrals created by current user's hospital
        referrals_query = db.query(ReferralRequest).filter(
            ReferralRequest.created_by == current_user.id
        ).filter(
            # Search in patient details, staff names, locations, and case data
            (ReferralRequest.patient_id.ilike(search_term)) |
            (ReferralRequest.staff_name.ilike(search_term)) |
            (ReferralRequest.referring_location.ilike(search_term)) |
            (ReferralRequest.cases_data.ilike(search_term)) |
            (ReferralRequest.prioritization_result.ilike(search_term))
        ).order_by(
            ReferralRequest.referral_date.desc(),
            ReferralRequest.referral_time.desc()
        ).limit(20)  # Results were limited for performance
        
        referrals = referrals_query.all()
        
        if not referrals:
            return JSONResponse(
                status_code=200,
                content={
                    "found": False,
                    "message": f"No referrals found matching '{query}'",
                    "suggestions": [
                        "Try searching with partial names (e.g., 'John' instead of 'John Smith')",
                        "Search by patient ID or location",
                        "Check spelling of patient name or details"
                    ]
                }
            )
        
        # Format results for display
        results = []
        for referral in referrals:
            # Extract patient name from cases_data if available
            patient_name = extract_patient_name_from_data(referral.cases_data)
            
            results.append({
                "referral_id": referral.id,
                "patient_id": referral.patient_id or "Not specified",
                "patient_name": patient_name or "Name not found in records",
                "staff_name": referral.staff_name or "Not specified",
                "referring_location": referral.referring_location or "Not specified",
                "urgency_level": referral.urgency_level or "Routine",
                "specialty": referral.specialty or "General",
                "referral_date": referral.referral_date.strftime("%Y-%m-%d") if referral.referral_date else "Not specified",
                "referral_time": referral.referral_time.strftime("%H:%M") if referral.referral_time else "Not specified",
                "status": referral.status or "pending",
                "case_summary": (referral.cases_data[:200] + "...") if referral.cases_data and len(referral.cases_data) > 200 else referral.cases_data or "No case data",
                "created_at": referral.created_at.strftime("%Y-%m-%d %H:%M") if referral.created_at else "Unknown"
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "found": True,
                "total_results": len(results),
                "search_query": query,
                "results": results
            }
        )
        
    except Exception as e:
        logger.error(f"Error in patient search: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Search failed: {str(e)}"}
        )

def extract_patient_name_from_data(cases_data):
    """Extract patient name from case data using simple text parsing"""
    if not cases_data:
        return None
    
    try:
        # Common patterns for patient names in medical records
        import re
        
        # Looking for patterns like "Patient: John Smith" or "Name: Jane Doe"
        name_patterns = [
            r"patient[:\s]+([A-Za-z\s]+)(?:\n|,|\.|$)",
            r"name[:\s]+([A-Za-z\s]+)(?:\n|,|\.|$)",
            r"pt[:\s]+([A-Za-z\s]+)(?:\n|,|\.|$)",
            r"([A-Z][a-z]+\s+[A-Z][a-z]+)",  
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, cases_data, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Filtering out common medical terms that might match
                exclude_terms = ['patient', 'male', 'female', 'year', 'old', 'years', 'history', 'diagnosis']
                if not any(term in name.lower() for term in exclude_terms) and len(name.split()) <= 4:
                    return name
        
        return None
    except Exception:
        return None


# Temporary debug endpoint
@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to see all registered routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    return {"routes": routes}

# Middleware
@app.middleware("http")
async def debug_auth_middleware(request: Request, call_next):
    """Debug authentication middleware"""
    
    # Logging request details for debugging
    logger.info(f"Request: {request.method} {request.url}")
    
    # To check for authentication cookie
    auth_cookie = request.cookies.get("access_token")
    logger.info(f"Auth cookie present: {bool(auth_cookie)}")
    
    if auth_cookie:
        logger.info(f"Auth cookie value: {auth_cookie[:20]}...")
    
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    
    return response

# Evaluation route
@app.get("/health")
async def health_check():
    """Health check endpoint for evaluation"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Debug endpoint 
@app.get("/debug/cookies")
async def debug_cookies(request: Request):
    """Debug endpoint to check cookies"""
    return {
        "cookies": dict(request.cookies),
        "headers": {k: v for k, v in request.headers.items() if k.lower() in ['authorization', 'cookie']},
        "auth_cookie": request.cookies.get("access_token", "Not found"),
        "session_data": dict(request.session) if hasattr(request, 'session') else "No session"
    }

# FHIR integration
app.include_router(fhir_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
