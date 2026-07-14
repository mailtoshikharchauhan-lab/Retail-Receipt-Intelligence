# Quick Start Guide - Streamlit Dashboard

## ✓ Current Status

Both services are **RUNNING**:
- ✓ FastAPI Backend: http://localhost:8000
- ✓ Streamlit Dashboard: http://localhost:8501

## Access the Dashboard

Open your browser and navigate to:
```
http://localhost:8501
```

## Test the Dashboard

### Option 1: Use the UI

1. Open http://localhost:8501
2. Click "Choose Image"
3. Select: `D:\ComputerVision-Projects\Retail-Receipt-Intelligence\dataset\originals\44.jpg`
4. Click "Upload Button"
5. View the results

### Option 2: Run Automated Tests

```powershell
.\venv\Scripts\Activate.ps1
python test_dashboard.py
```

## Stop Services

Close the PowerShell windows running the services, or press `Ctrl+C` in each terminal.

## Restart Services

### Manual Method:

**Terminal 1 - Backend:**
```powershell
.\venv\Scripts\Activate.ps1
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Dashboard:**
```powershell
.\venv\Scripts\Activate.ps1
streamlit run streamlit_dashboard.py --server.port 8501
```

### Automated Method:

```powershell
.\run_dashboard.ps1
```

## What the Dashboard Does

1. **Upload Section**: Select and upload receipt images
2. **Image Display**: Shows original and cropped receipt side-by-side
3. **Receipt Info**: Displays extracted data (store, date, totals, etc.)
4. **Items Table**: Lists all purchased items
5. **Status**: Shows if receipt needs review
6. **Recent Receipts**: Table of all processed receipts
7. **Analytics**: Summary statistics (total receipts, confidence, reviews needed)

## Backend APIs Used

- `POST /receipts/upload` - Process new receipt
- `GET /receipts` - List all receipts
- `GET /receipts/{id}` - Get specific receipt
- `GET /analytics` - Get statistics

## Test Results

All tests passed ✓:
- ✓ Upload succeeds
- ✓ API returns HTTP 201
- ✓ Original image displays
- ✓ Cropped receipt displays
- ✓ Receipt details display correctly
- ✓ Items table is populated
- ✓ Confidence score is displayed
- ✓ Recent receipts table updates
- ✓ Analytics update correctly

## Architecture

The dashboard is a **simple frontend** that:
- **Does NOT** modify any backend code
- **Does NOT** call OCR directly
- **Does NOT** access the database directly
- **Only** consumes existing FastAPI endpoints

Complete pipeline:
```
Image Upload → YOLO → Crop → EasyOCR → Parser → Confidence → SQLite → FastAPI → Streamlit
```

## Support

For more details, see `DASHBOARD_README.md`
