# System Architecture - Dashboard Integration

## Complete System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                              │
│                    http://localhost:8501                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Requests
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                   STREAMLIT DASHBOARD                            │
│                  (streamlit_dashboard.py)                        │
│                                                                   │
│  Features:                                                        │
│  • Upload Receipt Image                                          │
│  • Display Original & Cropped Images                             │
│  • Show Extracted Receipt Info                                   │
│  • Display Items Table                                           │
│  • Show Recent Receipts                                          │
│  • Display Analytics                                             │
│                                                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ REST API Calls
                             │ POST /receipts/upload
                             │ GET /receipts
                             │ GET /analytics
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      FASTAPI BACKEND                             │
│                      (api/main.py)                               │
│                   http://localhost:8000                          │
│                                                                   │
│  Routes:                                                          │
│  • POST /receipts/upload    → Receipt Upload                    │
│  • GET /receipts           → List All Receipts                  │
│  • GET /receipts/{id}      → Get Single Receipt                 │
│  • GET /analytics          → Get Statistics                     │
│                                                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Service Orchestration
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    RECEIPT SERVICE                               │
│                (api/services/receipt_service.py)                 │
│                                                                   │
│  Coordinates:                                                     │
│  1. Detection Service   → YOLO Object Detection                 │
│  2. OCR Service        → EasyOCR Text Extraction                │
│  3. Parser Service     → Data Structuring                       │
│  4. Confidence Service → Quality Scoring                        │
│  5. Database Service   → Data Persistence                       │
│                                                                   │
└─────────┬──────────────────┬──────────────────┬─────────────────┘
          │                  │                  │
          │                  │                  │
   ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
   │   YOLO      │   │  EasyOCR    │   │  SQLite     │
   │  Detection  │   │   Engine    │   │  Database   │
   │             │   │             │   │             │
   │ models/     │   │ ocr/        │   │ database/   │
   │ best.pt     │   │ ocr_engine  │   │ receipts.db │
   │             │   │             │   │             │
   └─────────────┘   └─────────────┘   └─────────────┘
```

## Data Flow

### Upload Flow

```
1. User Action (Browser)
   └─→ Select image file
   └─→ Click "Upload Button"

2. Streamlit Frontend
   └─→ Read file as bytes
   └─→ POST to /receipts/upload

3. FastAPI Backend
   └─→ Receive multipart file
   └─→ Save to uploads/

4. Receipt Service
   └─→ Initialize all sub-services

5. Detection Service
   └─→ Load YOLO model
   └─→ Run inference
   └─→ Detect receipt region
   └─→ Return bounding box

6. Cropping
   └─→ Crop using bbox
   └─→ Save to outputs/crops/

7. OCR Service
   └─→ Load EasyOCR
   └─→ Process cropped image
   └─→ Extract text with coordinates
   └─→ Return OCR results

8. Parser Service
   └─→ Parse store name
   └─→ Parse date/time
   └─→ Parse totals
   └─→ Parse items
   └─→ Parse payment method
   └─→ Return structured data

9. Confidence Service
   └─→ Check data completeness
   └─→ Calculate confidence score
   └─→ Assign confidence level
   └─→ Determine processing status

10. Database Service
    └─→ Create receipt record
    └─→ Create item records
    └─→ Save to SQLite
    └─→ Return receipt ID

11. FastAPI Response
    └─→ Build ReceiptUploadResponse
    └─→ Return JSON (HTTP 201)

12. Streamlit Display
    └─→ Parse JSON response
    └─→ Display images
    └─→ Display receipt info
    └─→ Display items table
    └─→ Display status
    └─→ Refresh recent receipts
    └─→ Refresh analytics
```

## Component Details

### Streamlit Dashboard (NEW)
- **File**: `streamlit_dashboard.py`
- **Port**: 8501
- **Purpose**: User interface
- **Dependencies**: requests, PIL, streamlit
- **Backend**: FastAPI only (no direct DB/OCR access)

### FastAPI Backend (EXISTING - UNCHANGED)
- **File**: `api/main.py`
- **Port**: 8000
- **Purpose**: Business logic orchestration
- **Features**: CORS, validation, error handling

### YOLO Detection (EXISTING - UNCHANGED)
- **Model**: YOLOv11s
- **File**: `models/best.pt`
- **Purpose**: Receipt region detection
- **Output**: Bounding box coordinates

### EasyOCR Engine (EXISTING - UNCHANGED)
- **Engine**: EasyOCR
- **Languages**: English
- **File**: `ocr/ocr_engine.py`
- **Output**: Text with coordinates

### Parser Service (EXISTING - UNCHANGED)
- **File**: `api/services/parser_service.py`
- **Purpose**: Extract structured data from OCR
- **Patterns**: Regex-based field extraction

### Confidence Service (EXISTING - UNCHANGED)
- **File**: `api/services/confidence_service.py`
- **Purpose**: Calculate quality metrics
- **Output**: Score, level, status

### SQLite Database (EXISTING - UNCHANGED)
- **File**: `database/receipts.db`
- **Tables**: receipts, receipt_items
- **Purpose**: Data persistence

## Key Design Decisions

### 1. No Backend Modification ✓
- Dashboard is a pure consumer
- All logic remains in existing services
- No new business logic in frontend

### 2. API-First Integration ✓
- Uses only documented endpoints
- No direct database access
- No direct OCR calls
- Clean separation of concerns

### 3. Minimal UI ✓
- Single page application
- Standard Streamlit components
- No custom styling
- Focus on functionality

### 4. Real-Time Updates ✓
- Analytics refresh after upload
- Recent receipts update automatically
- No caching issues

## Technology Stack

### Frontend
- **Framework**: Streamlit 1.59.2
- **HTTP Client**: requests
- **Image Processing**: PIL
- **Port**: 8501

### Backend (Existing)
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Port**: 8000

### ML/AI (Existing)
- **Object Detection**: YOLO11s
- **OCR**: EasyOCR
- **Deep Learning**: PyTorch

### Database (Existing)
- **Type**: SQLite
- **ORM**: SQLAlchemy
- **File**: receipts.db

## Deployment Notes

### Development
- Both services run locally
- Separate terminal windows
- Virtual environment required

### Production Considerations
- Can deploy Streamlit separately
- FastAPI can scale independently
- Consider containerization (Docker)
- Add authentication if needed
- Add HTTPS for production

## Security

### Current Implementation
- No authentication (dev only)
- CORS enabled (all origins)
- File uploads validated by FastAPI
- SQL injection protected by ORM

### Production Requirements
- Add user authentication
- Restrict CORS origins
- Add rate limiting
- Implement file size limits
- Add HTTPS/SSL
- Secure secret management

## Maintenance

### Dashboard Updates
- Modify `streamlit_dashboard.py` only
- No backend changes needed
- Test with `test_dashboard.py`

### Backend Updates
- Dashboard will automatically use new API features
- API contract must remain compatible
- Version endpoints for breaking changes

## Testing

### Automated Tests
- **File**: `test_dashboard.py`
- **Coverage**: Upload, List, Analytics
- **Test Image**: dataset/originals/44.jpg

### Manual Tests
- Upload various receipt types
- Verify image display
- Check data accuracy
- Validate analytics

## Monitoring

### Health Checks
- FastAPI: http://localhost:8000/health
- Streamlit: http://localhost:8501

### Logs
- Backend: Console output
- Dashboard: Console output
- Database: N/A (SQLite)

## Future Enhancements (Optional)

- Add user authentication
- Add receipt editing
- Add bulk upload
- Add export to CSV/Excel
- Add charts and visualizations
- Add advanced filtering
- Add search functionality
- Add receipt deletion
- Add confidence threshold settings
- Add multi-language support
