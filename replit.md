# Voter Inquiry Bot - Documentation

## Overview
This is an automated tool that extracts voter information from the Egyptian Higher Elections Commission website using national IDs stored in Google Sheets. The bot reads national IDs from a Google Sheet, queries the elections website for each ID, and writes the results to a new sheet.

## Project Structure
```
├── main.py                 # Main application file
├── credentials.json        # Google Service Account credentials (required)
├── progress.json          # Progress tracking file (auto-generated)
├── README.md              # User documentation (Arabic)
└── replit.md              # Project documentation
```

## Recent Changes
- 2025-10-28: تحسينات كبيرة في استخراج البيانات
  - تحسين استخراج المركز الانتخابي باستخدام طريقتين:
    * الطريقة 1: استخدام Selenium XPath للبحث عن العناصر مباشرة واستخراج القيم من العناصر المجاورة
    * الطريقة 2: BeautifulSoup كنسخة احتياطية للبحث في جميع العناصر
  - إضافة رسائل تأكيد عند استخراج البيانات بنجاح
  - زيادة وقت الانتظار إلى 5 ثوان لضمان تحميل البيانات بالكامل
  - تحسين منطق البحث عن المركز الانتخابي والعنوان ورقم اللجنة والرقم في الكشوف
  - إعداد deployment configuration للنشر على Replit
- 2025-10-28: Replit environment setup completed
  - Installed Chromium 138.0.7204.100 and ChromeDriver 138.0.7204.100 via Nix
  - Configured workflow for Flask dashboard (webview on port 5000)
  - All Python dependencies installed and verified via uv
  - Environment ready for use - only needs credentials.json upload
- Initial project setup with Google Sheets integration
- Implemented Selenium automation for elections website with iframe handling
- Fixed critical zip() bug that was dropping rows when column C shorter than B
- Added robust error handling (captcha detection, invalid IDs, rate limiting)
- Implemented progress tracking with progress.json for resume capability
- Created comprehensive documentation (README.md, SETUP_INSTRUCTIONS.md)
- Support for up to 80,000 rows with proper data ingestion

## User Preferences
- Language: Arabic (العربية)
- Framework: Python 3.11 with Selenium
- Data Source: Google Sheets API
- Target Website: https://www.elections.eg/inquiry

## Architecture

### Key Components

1. **VoterInquiryBot Class**
   - Main bot class that coordinates all operations
   - Manages Google Sheets connection
   - Controls Selenium WebDriver
   - Handles progress tracking

2. **Google Sheets Integration**
   - Uses `gspread` library with OAuth2 authentication
   - Reads from "Voters" worksheet (Column B: National IDs, Column C: Names)
   - Writes results to "نتائج_الاستعلام" worksheet
   - Supports up to 80,000 rows

3. **Web Automation**
   - Uses Selenium WebDriver with Chrome (headless mode)
   - **iframe handling**: Switches to gadget.elections.eg iframe to access inquiry form
   - Automatically queries elections website for each national ID
   - Extracts voter data using BeautifulSoup4
   - Robust error handling: detects captcha, invalid IDs, rate limiting, and network errors
   - Multiple fallback strategies for locating page elements

4. **Progress Tracking**
   - Saves progress to `progress.json` after each row
   - Enables resume functionality if process is interrupted
   - Tracks last processed row and total count

### Data Flow
1. Load progress from `progress.json` (if exists)
2. Connect to Google Sheets using credentials
3. Read national IDs and names from "Voters" worksheet
4. Filter out already processed rows
5. For each unprocessed row:
   - Query elections website using Selenium
   - Extract voter information
   - Write results to new sheet
   - Update progress file
6. Display completion summary

## Dependencies
- Python 3.11
- gspread: Google Sheets API client
- google-auth: Modern authentication library
- selenium: Web browser automation
- beautifulsoup4: HTML parsing
- pandas: Data manipulation
- webdriver-manager: Automatic ChromeDriver management

## Configuration

### Required Setup
1. **Google Service Account**
   - Create project in Google Cloud Console
   - Enable Google Sheets API and Google Drive API
   - Create Service Account and download JSON key
   - Save as `credentials.json` in project root
   - Share target Google Sheet with service account email

2. **Google Sheet Format**
   - Sheet ID: 1-rCGPx6vyEMm3zmR7ks3xZh63XcJk4ks78e5e9jfuyo
   - Source worksheet: "Voters"
   - Column B: National IDs (14 digits)
   - Column C: Names
   - Results worksheet: "نتائج_الاستعلام" (auto-created)

### Environment Variables
- None required (uses credentials.json file)

## Features

### Implemented
✅ Google Sheets API integration with OAuth2  
✅ Selenium-based web automation with iframe handling  
✅ Automatic ChromeDriver management (Replit-compatible)  
✅ Progress tracking and resume capability (progress.json)  
✅ Comprehensive error handling:
  - Captcha detection
  - Invalid national ID detection
  - Rate limiting handling
  - Network error recovery
✅ Support for 80,000+ rows with proper data ingestion  
✅ Real-time progress display  
✅ Automatic retry on interruption  
✅ Complete documentation and setup instructions  
✅ Fixed critical bugs (zip truncation, iframe access)

### Pending Implementation
⚠️ **Important**: The BeautifulSoup selectors for extracting data may need updates based on actual website structure. Test with real credentials first.
- Email notifications on completion
- Web UI for monitoring
- Export to multiple formats (CSV, Excel)
- Concurrent processing with rate limiting

## Usage

### First Run
```bash
python main.py
```

### Resume After Interruption
```bash
python main.py  # Automatically resumes from last position
```

### Reset Progress
```bash
rm progress.json
python main.py
```

## Important Notes

### Security
- `credentials.json` contains sensitive data - never commit to git
- Already added to `.gitignore`
- Service account has editor access to shared sheets only

### Performance
- Processes approximately 1-2 rows per second
- 2-second delay between queries to avoid IP blocking
- Can process 80,000 rows in ~44-88 hours

### Error Handling
- Progress saved after each successful query
- Safe to interrupt with Ctrl+C
- Automatic resume from last successful row
- Failed queries marked in results with error message

## Technical Details

### Google Sheets API
- Uses Service Account authentication
- Scopes: `spreadsheets` and `drive`
- Batch updates for efficiency
- Handles API rate limits automatically

### Selenium Configuration
- Headless Chrome mode
- Arabic language support
- Disabled GPU and dev-shm-usage for cloud compatibility
- Auto-managed ChromeDriver via webdriver-manager

### Data Extraction
- BeautifulSoup4 for HTML parsing
- Custom text matching for Arabic content
- Extracts: voting center, address, committee number, list number
- Status tracking (success/error)

## Future Enhancements
1. Add web UI for real-time monitoring
2. Implement batch processing optimization
3. Add email/SMS notifications
4. Support multiple election databases
5. Add data validation and cleansing
6. Implement concurrent processing (with rate limiting)
7. Add export to Excel with formatting
8. Create dashboard with statistics
