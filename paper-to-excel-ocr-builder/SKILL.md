---
name: paper-to-text-ocr-assistant
description: Design, implement, review, test, and package a local Windows desktop application that receives document photos from a phone over the local network, extracts printed data using PaddleOCR and OpenCV, allows human review, and exports OCR results as TXT, CSV, JSON, or TSV for manual pasting into Excel.
---

# Paper to Text OCR Assistant — Builder Skill

## 1. Purpose

This skill provides a complete, authoritative specification for building **Paper to Excel OCR**, a Windows desktop application that:

1. Accepts scanned or photographed images of fixed-layout printed documents — from a local file system or from a phone over the local network.
2. Extracts structured data from those images using PaddleOCR and OpenCV, entirely offline after initial model download.
3. Matches extracted data against existing records in an Excel workbook using configurable matching keys.
4. Classifies each mapped cell as missing, already complete, conflicting, or not updatable.
5. Presents a change preview showing proposed cell fills alongside confidence scores and validation feedback.
6. Requires human review and approval before any Excel cell is modified.
7. Fills only approved missing cells in the matched existing row — preserving all existing non-empty cells, formula cells, and matching-key cells.
8. Saves changes through a backup-and-atomic-write process using openpyxl, with correct data types.

The application is a **missing-data completion tool**, not a standard row-append tool. Its primary responsibility is to locate an existing Excel record, detect which cells are still empty, and fill only those cells with validated, human-approved OCR values.

The skill is written so that any coding agent can use it — without additional context — to implement, review, debug, test, and extend the application.

---

## 2. Scope

### In Scope

- Windows desktop application using PySide6.
- Local-network mobile upload via a temporary FastAPI server, QR code, and session tokens.
- Image preprocessing with OpenCV.
- Printed-text OCR with PaddleOCR (offline after model installation).
- Fixed-layout document extraction using label-based and region-based strategies.
- Row matching against existing Excel records using configurable single or composite keys.
- Cell-state classification (missing, already complete, conflict, OCR value missing, invalid, not updatable).
- Change preview with proposed actions per field before any Excel modification.
- Editable review form with confidence display, validation, and manual-confirmation gates.
- Missing-cell completion with openpyxl — backup, atomic save, correct data types, leading-zero preservation.
- Conflict display without automatic overwrite.
- Stale-data protection — re-verify workbook state before applying approved changes.
- Merged-cell and formula-cell safety — never overwrite formulas or non-anchor merged cells.
- JSON-driven configuration for document types, field mappings, row matching, update policy, and validation rules.
- Automated tests with pytest.
- Windows packaging with PyInstaller.
- Vietnamese user-facing text; English source code and identifiers.

### Out of Scope

- Handwriting recognition (deferred until representative samples are tested).
- Multi-page document stitching.
- Cloud OCR or cloud storage.
- Database persistence.
- User authentication beyond the local upload session token.
- Automatic public-network exposure.
- Mobile native application.
- Real-time collaborative editing.
- Automatic OCR-to-Excel export without human review.
- Row-append mode (the application fills missing cells in existing rows, not appends new rows).

---

## 3. Trigger Conditions

A coding agent should activate this skill when the user requests any of the following:

- Creating, extending, or modifying the Paper to Excel OCR application.
- Adding a new document type or field mapping.
- Changing OCR, extraction, validation, or export behavior.
- Adding or modifying the mobile upload workflow.
- Writing or updating tests for any application component.
- Packaging the application for Windows.
- Reviewing or auditing the application against this specification.
- Debugging OCR accuracy, extraction logic, validation rules, or Excel export.
- Updating dependencies or resolving compatibility issues.

---

## 4. Supported Tasks

| Task | Description |
|------|-------------|
| **Full Implementation** | Build the complete application from scratch following all phases. |
| **Phase Implementation** | Implement a single phase (models, validation, upload, OCR, Excel, UI, packaging). |
| **Feature Addition** | Add a new document type, field, extraction strategy, or preprocessing profile. |
| **Bug Fix** | Diagnose and fix a defect in any component. |
| **Test Creation** | Write unit or integration tests for a specific component. |
| **Configuration Change** | Add or modify JSON configuration for document types or field mappings. |
| **Dependency Update** | Update a dependency and verify compatibility. |
| **Packaging** | Create or update the PyInstaller spec and build script. |
| **Code Review** | Audit code against this specification's rules and quality requirements. |
| **Documentation** | Create or update README, inline documentation, or configuration guides. |

---

## 5. Required Technology Stack

| Component | Technology | Minimum Version | Notes |
|-----------|-----------|-----------------|-------|
| Language | Python | 3.11 | Use type hints throughout |
| Desktop UI | PySide6 | 6.6+ | Qt for Python |
| OCR Engine | PaddleOCR | 2.7+ | Prefer PP-OCRv6 when stable and compatible; fall back to latest stable model and document reasoning |
| OCR Backend | PaddlePaddle | 2.5+ | CPU version acceptable for MVP |
| Image Processing | OpenCV (opencv-python-headless) | 4.8+ | Headless variant to avoid Qt conflicts with PySide6 |
| Excel | openpyxl | 3.1+ | Support .xlsx and .xlsm |
| Web Server | FastAPI | 0.100+ | Local upload server |
| ASGI Server | Uvicorn | 0.23+ | Run FastAPI |
| Image Library | Pillow | 10.0+ | Validation, format detection |
| QR Code | qrcode | 7.4+ | QR code generation |
| File Watching | watchdog | 3.0+ | Inbox monitoring |
| Multipart | python-multipart | 0.0.6+ | FastAPI file uploads |
| Templates | Jinja2 | 3.1+ | Mobile capture page |
| Testing | pytest | 7.4+ | Automated tests |
| Packaging | PyInstaller | 6.0+ | Windows executable |
| Config Format | JSON | stdlib | Configuration files |
| Logging | logging | stdlib | Python standard logging |
| Paths | pathlib | stdlib | Path handling |
| Models | dataclasses | stdlib | Domain models |
| Secrets | secrets | stdlib | Token generation |
| UUIDs | uuid | stdlib | Safe file naming |
| Hashing | hashlib | stdlib | File deduplication |

### Dependency Compatibility Verification

Before pinning versions in `requirements.txt`:

1. Verify that the selected PaddlePaddle version supports Python 3.11 on Windows.
2. Verify that the selected PaddleOCR version is compatible with the selected PaddlePaddle version.
3. Verify that `opencv-python-headless` is used instead of `opencv-python` to avoid Qt library conflicts with PySide6.
4. Verify that PySide6 and `opencv-python-headless` do not ship conflicting Qt binaries.
5. Document any version pins and the reason for each pin.

### PP-OCRv6 Selection Policy

- If PP-OCRv6 is available, stable, and compatible with the pinned PaddleOCR and PaddlePaddle versions, use it as the default recognition model.
- If PP-OCRv6 is not yet stable or introduces compatibility issues, use the latest stable supported model (e.g., PP-OCRv4) and document the reason in `README.md` and in the OCR engine module docstring.
- The model selection must be configurable so it can be updated without modifying application code.

---

## 6. Disallowed Technologies

The following technologies and services must **never** be used:

| Disallowed | Reason |
|------------|--------|
| OpenAI API | Cloud dependency, data leaves local machine |
| Google Vision API | Cloud dependency |
| Azure Cognitive Services OCR | Cloud dependency |
| AWS Textract | Cloud dependency |
| Any external OCR website or API | Cloud dependency |
| Cloud file-storage services (S3, GCS, Azure Blob) | Data leaves local machine |
| Database servers (PostgreSQL, MySQL, SQLite for primary storage) | Unnecessary complexity for MVP |
| Microsoft Excel COM automation | Requires Excel installed; fragile |
| LibreOffice automation | Requires LibreOffice installed |
| LLM for extracting fixed-layout fields | Unnecessary; deterministic extraction is sufficient |
| Public file-upload services (WeTransfer, etc.) | Data leaves local machine |
| Public tunneling services (ngrok, Cloudflare Tunnel) by default | Exposes local server to the internet |

The application must be fully usable without Microsoft Excel or LibreOffice being installed or running.

---

## 7. Core Design Principles

1. **Local-First Privacy**: All document processing — image storage, OCR, extraction, validation, and export — must remain on the local machine after OCR models are installed. Uploaded files must never be sent to cloud services.

2. **Human-in-the-Loop Review**: OCR results must never be written directly into Excel without human review. Required low-confidence fields must be manually confirmed before export. Missing values must never be guessed or invented.

3. **Existing-Data Preservation**: The application must never overwrite existing non-empty cells by default. Formula cells must never be replaced. Matching-key cells must never be modified. Only explicitly approved missing cells may be filled.

4. **Exact Row Matching**: Before any Excel update, the application must locate exactly one existing row using configurable matching keys. Zero matches or multiple matches must block the update. Fuzzy matching may only suggest candidates for manual selection — never for automatic update.

5. **Change Preview Approval**: Every proposed cell change must be displayed to the user in a change preview before saving. The user must approve the final change set. The default action for conflicts must be "Keep Existing Value."

6. **Stale-Data Protection**: Between preview and save, the workbook may change. The application must re-verify the workbook state (matching keys, cell values) before applying approved changes. If the workbook has changed, the update must be cancelled.

7. **Data Integrity**: The original image and the Excel workbook must remain recoverable at all times. Excel operations must preserve dates, numbers, strings, and leading zeros correctly. Excel backups and atomic saves must be implemented.

8. **Separation of Concerns**: Business logic must not be placed inside UI classes. OCR must not run on the UI thread. Excel operations, validation, and server logic must be independent of the UI framework.

9. **Defensive Input Handling**: Uploaded images must be validated before being saved. Session tokens must be validated on every request. Configuration must be validated at startup.

10. **Security Hygiene**: Sensitive OCR content must not be written to logs. The local upload server must use temporary session tokens. The upload server must only be started when requested by the user. The server must stop when the application exits. The application must not automatically expose itself to public networks.

11. **Graceful Failure**: Errors must not crash the application, delete source images, remove user-edited review data, or damage the original workbook. Every error must be logged safely and reported to the user in a non-technical message.

12. **Testability**: All business services must be testable without PySide6 widgets. PaddleOCR must be mockable in unit tests.

---

## 8. Required User Inputs

The application requires the following inputs from the user at various stages:

| Input | When Required | Default |
|-------|--------------|---------|
| Document image(s) | Before OCR | None — user must select or upload |
| Document type configuration | Before extraction | `document_type_fixed.json` |
| Target Excel workbook | Before export | None — user must select |
| Target worksheet name | Before export | From document type configuration |
| Field corrections | During review | OCR-extracted values |
| Manual confirmation of low-confidence required fields | Before export | Not confirmed — must be explicit |
| Mobile Upload start/stop | Before phone upload | Server is stopped |
| Workspace directory | Optional, at setup | OS-appropriate app-data directory |

---

## 9. Default Assumptions

The following assumptions apply unless the user explicitly overrides them:

1. The target platform is Windows 10 or later (64-bit).
2. Documents are fixed-layout printed forms with Vietnamese labels.
3. Text is printed, not handwritten.
4. One document image produces one data row in Excel.
5. The Excel workbook already exists and contains the target worksheet with headers.
6. The first data row is row 2 (row 1 contains headers).
7. The phone and computer are on the same trusted local Wi-Fi or LAN.
8. The upload server binds to a private local-network interface.
9. The session token expires after 15 minutes by default.
10. The maximum upload size is 15 MB by default.
11. The OCR confidence threshold is 0.85 by default.
12. User-facing text is in Vietnamese.
13. Source code, comments, identifiers, and documentation are in English.
14. The application uses CPU-based PaddlePaddle for the MVP.
15. OCR models are downloaded once during setup and reused offline.

---

## 10. Recommended Project Architecture

`
paper_to_excel/
+-- app.py
+-- requirements.txt
+-- README.md
+-- pytest.ini
+-- build.bat
+-- paper_to_excel.spec
+-- assets/
+-- config/
¦   +-- app_config.json
+-- profiles/
¦   +-- documents/
¦   ¦   +-- fixed_document_v1.json
¦   +-- excel_mappings/
¦       +-- inventory_result_v1.json
+-- src/
¦   +-- __init__.py
¦   +-- models/
¦   ¦   +-- __init__.py
¦   ¦   +-- ocr_result.py
¦   ¦   +-- extracted_field.py
¦   ¦   +-- document_data.py
¦   ¦   +-- validation_result.py
¦   ¦   +-- processing_item.py
¦   ¦   +-- upload_session.py
¦   ¦   +-- cell_update_proposal.py
¦   +-- ui/
¦   ¦   +-- __init__.py
¦   ¦   +-- main_window.py
¦   ¦   +-- image_viewer.py
¦   ¦   +-- review_form.py
¦   ¦   +-- document_queue.py
¦   ¦   +-- mobile_upload_panel.py
¦   ¦   +-- mapping_editor.py
¦   ¦   +-- table_selector.py
¦   ¦   +-- change_preview_dialog.py
¦   +-- transfer/
¦   ¦   +-- __init__.py
¦   ¦   +-- local_upload_server.py
¦   ¦   +-- upload_security.py
¦   ¦   +-- upload_rate_limiter.py
¦   ¦   +-- inbox_watcher.py
¦   +-- web/
¦   ¦   +-- templates/
¦   ¦   ¦   +-- mobile_capture.html
¦   ¦   +-- static/
¦   ¦       +-- mobile_capture.css
¦   ¦       +-- mobile_capture.js
¦   +-- ocr/
¦   ¦   +-- __init__.py
¦   ¦   +-- base_ocr_engine.py
¦   ¦   +-- paddle_ocr_engine.py
¦   ¦   +-- image_preprocessor.py
¦   +-- documents/
¦   ¦   +-- __init__.py
¦   ¦   +-- document_profile.py
¦   ¦   +-- document_profile_repository.py
¦   ¦   +-- document_type_detector.py
¦   ¦   +-- base_document_extractor.py
¦   ¦   +-- fixed_form_extractor.py
¦   +-- mapping/
¦   ¦   +-- __init__.py
¦   ¦   +-- mapping_profile.py
¦   ¦   +-- mapping_profile_repository.py
¦   ¦   +-- mapping_configuration_service.py
¦   ¦   +-- mapping_suggestion_service.py
¦   ¦   +-- mapping_validation_service.py
¦   ¦   +-- mapping_cache.py
¦   ¦   +-- table_detector.py
¦   ¦   +-- table_fingerprint_service.py
¦   +-- excel/
¦   ¦   +-- __init__.py
¦   ¦   +-- workbook_structure_reader.py
¦   ¦   +-- excel_reader.py
¦   ¦   +-- excel_row_matcher.py
¦   ¦   +-- excel_change_planner.py
¦   ¦   +-- excel_completion_service.py
¦   +-- validators/
¦   ¦   +-- __init__.py
¦   ¦   +-- image_validator.py
¦   ¦   +-- field_validator.py
¦   ¦   +-- document_validator.py
¦   ¦   +-- data_normalizer.py
¦   +-- services/
¦   ¦   +-- __init__.py
¦   ¦   +-- config_service.py
¦   ¦   +-- file_service.py
¦   ¦   +-- qr_code_service.py
¦   ¦   +-- upload_session_service.py
¦   ¦   +-- duplicate_service.py
¦   ¦   +-- backup_service.py
¦   +-- workers/
¦       +-- __init__.py
¦       +-- ocr_worker.py
¦       +-- workbook_worker.py
¦       +-- excel_worker.py
¦       +-- processing_queue.py
+-- tests/
    +-- __init__.py
    +-- test_upload_security.py
    +-- test_image_validator.py
    +-- test_upload_server.py
    +-- test_inbox_watcher.py
    +-- test_image_preprocessor.py
    +-- test_document_extractor.py
    +-- test_document_validator.py
    +-- test_table_detector.py
    +-- test_table_fingerprint.py
    +-- test_mapping_profile.py
    +-- test_mapping_validation.py
    +-- test_excel_row_matcher.py
    +-- test_excel_change_planner.py
    +-- test_excel_completion_service.py
    +-- test_processing_queue.py
`

---
## 11. End-to-End Data Flow

The complete data flow from image acquisition to Excel completion:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 1. IMAGE ACQUISITION                                                     │
│    ├── Local Import: User selects file(s) via file dialog                │
│    └── Mobile Upload: Phone → FastAPI → validated → Inbox/               │
├──────────────────────────────────────────────────────────────────────────┤
│ 2. INBOX MONITORING                                                      │
│    ├── InboxWatcher detects finalized file                               │
│    ├── Verify file stability (size + mtime unchanged)                    │
│    ├── Verify image is readable                                          │
│    ├── Calculate file hash for deduplication                             │
│    └── Move accepted file: Inbox/ → Processing/                          │
├──────────────────────────────────────────────────────────────────────────┤
│ 3. IMAGE PREPROCESSING                                                   │
│    ├── Load original image                                               │
│    ├── Apply configured preprocessing profile                            │
│    ├── Produce a working copy (original is preserved)                    │
│    └── Store preprocessed image for viewer comparison                    │
├──────────────────────────────────────────────────────────────────────────┤
│ 4. OCR EXECUTION (background thread)                                     │
│    ├── PaddleOCREngine.recognize(preprocessed_image)                     │
│    ├── Produce list of OCRResult (text, confidence, bbox, order)         │
│    └── Signal completion to UI thread                                    │
├──────────────────────────────────────────────────────────────────────────┤
│ 5. FIELD EXTRACTION                                                      │
│    ├── FixedFormExtractor receives OCR results + document config          │
│    ├── Label-based search: find label → locate adjacent value             │
│    ├── Region-based search: filter OCR results within normalized region   │
│    ├── Candidate ranking: validation → region → distance → confidence     │
│    └── Produce DocumentData with FieldData per configured field           │
├──────────────────────────────────────────────────────────────────────────┤
│ 6. VALIDATION                                                            │
│    ├── DataNormalizer: trim, parse dates, parse numbers                   │
│    ├── FieldValidator: regex, range, required, type checks                │
│    ├── DocumentValidator: cross-field checks                              │
│    └── Each field gets a ValidationResult (valid/invalid/review-needed)   │
├──────────────────────────────────────────────────────────────────────────┤
│ 7. HUMAN REVIEW                                                         │
│    ├── ReviewForm displays fields with confidence + validation status     │
│    ├── Low-confidence required fields are highlighted (yellow)            │
│    ├── Invalid fields are highlighted (red)                              │
│    ├── User edits, corrects, and manually confirms flagged fields         │
│    └── Re-validation runs after each correction                          │
├──────────────────────────────────────────────────────────────────────────┤
│ 8. ROW MATCHING AND CHANGE PLANNING                                      │
│    ├── ExcelReader opens the target workbook and worksheet                │
│    ├── ExcelRowMatcher locates matching row(s) by configured keys         │
│    ├── Exactly one match required — zero or multiple matches block update │
│    ├── ExcelChangePlanner classifies each field:                          │
│    │   ├── MISSING — empty cell, valid OCR value → propose fill           │
│    │   ├── ALREADY_COMPLETE — same value → no change                      │
│    │   ├── CONFLICT — different value → display both, keep existing       │
│    │   ├── OCR_VALUE_MISSING — empty cell, no OCR value → skip            │
│    │   ├── INVALID_OCR_VALUE — OCR value failed validation → skip         │
│    │   └── NOT_UPDATABLE — formula / merged / matching key → preserve     │
│    └── ChangePreviewPanel shows proposed actions for user approval         │
├──────────────────────────────────────────────────────────────────────────┤
│ 9. EXCEL COMPLETION (background thread)                                  │
│    ├── Receive explicitly user-approved change plan                       │
│    ├── Reopen workbook from disk (stale-data protection)                  │
│    ├── Re-verify matching row still exists and keys match                 │
│    ├── Re-verify approved target cells are still empty                    │
│    ├── Cancel if workbook changed since preview                           │
│    ├── Create timestamped backup                                         │
│    ├── Apply only approved cell fills to a temporary workbook copy        │
│    ├── Verify temporary workbook (reopen, check cells)                   │
│    ├── Replace destination with verified temporary file                   │
│    ├── Move source image: Processing/ → Processed/                       │
│    └── Signal completion to UI thread                                    │
├──────────────────────────────────────────────────────────────────────────┤
│ 10. FAILURE HANDLING                                                     │
│    ├── On any processing failure: move image to Failed/                   │
│    ├── Write a safe technical error record (no sensitive content)         │
│    ├── Original image and workbook remain intact                         │
│    └── User is notified with a non-technical error message               │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Mobile-to-PC Upload Workflow

### Sequence

1. The user clicks **Start Mobile Upload** in the desktop application.
2. `LocalUploadServer` starts a FastAPI + Uvicorn instance in a background thread.
3. The server detects a usable private local-network IP address (e.g., `192.168.x.x`, `10.x.x.x`).
4. `UploadSessionService` generates a cryptographically secure random session token (at least 256 bits, using `secrets.token_urlsafe(32)`).
5. The server constructs the upload URL: `http://<local_ip>:<port>/upload/<token>`.
6. `QRCodeService` generates a QR code image encoding the upload URL.
7. The desktop application displays the QR code in the Mobile Upload Panel.
8. The user scans the QR code with their phone (Android or iPhone).
9. The phone opens the mobile-friendly capture page in its default browser.
10. The user captures a document photo using the rear camera or selects an existing image.
11. The user previews the photo on the mobile page.
12. The user taps **Upload**.
13. The mobile page sends the image to the FastAPI upload endpoint via `multipart/form-data`.
14. The server validates the session token.
15. The server validates the uploaded file (size, format, content, dimensions).
16. The server saves the image safely into the Inbox directory with a UUID filename.
17. The server responds with a success or error message.
18. `InboxWatcher` detects the new finalized image and adds it to the processing queue.
19. The user can upload additional images while the session is active.
20. When the session expires or the user clicks **Stop Mobile Upload**, the server stops accepting uploads.

### Prerequisites

- The phone and computer must be connected to the same trusted local Wi-Fi or LAN.
- The computer's firewall must allow inbound connections on the configured port.
- The application does not automatically add Windows Firewall rules.

---

## 13. Local Upload Server Requirements

### Service: `LocalUploadServer`

**Responsibilities:**

- Start FastAPI and Uvicorn in a background thread (never block the PySide6 UI thread).
- Detect an appropriate private local-network IP address using `socket` and `netifaces` or equivalent.
- Use a configurable port (default: `8265`).
- Handle unavailable ports gracefully (try next port or report an error).
- Generate a temporary upload session via `UploadSessionService`.
- Serve the mobile capture page (HTML, CSS, JS) via FastAPI static-file and template routes.
- Receive image uploads at `POST /upload/<token>`.
- Validate sessions and uploaded images on every request.
- Save accepted images safely into the Inbox directory.
- Report new uploads to the desktop application via a Qt signal or thread-safe callback.
- Shut down cleanly when requested by the user.
- Shut down when the desktop application exits (registered via `atexit` or application shutdown hook).

**Constraints:**

- The server must not start automatically when the application launches unless `app_config.json` explicitly sets `"auto_start_server": true`.
- Do not use the FastAPI development auto-reload feature.
- Do not run more than one upload server instance at a time.
- Do not serve on `0.0.0.0` by default. Bind to the detected private interface.
- Warn the user if the selected interface appears to be a public IP address.

### Required UI Controls

| Control | Action |
|---------|--------|
| Start Mobile Upload | Start the local server and display QR code |
| Stop Mobile Upload | Stop the server and invalidate the session |
| Refresh Session | Invalidate current token, generate a new one, update QR code |
| Copy Upload URL | Copy the upload URL to the clipboard |
| Display QR Code | Show the QR code encoding the upload URL |
| Display Server Status | Show running / stopped / error state |
| Display Session Expiration | Show countdown to token expiry |
| Display Received File Count | Show how many images have been uploaded in this session |

---

## 14. QR Code and Session Security

### Token Generation

- Use `secrets.token_urlsafe(32)` to produce a token with at least 256 bits of entropy.
- Store the token, creation time, and expiration time in an `UploadSession` model.
- Default expiration: 15 minutes (configurable in `app_config.json`).
- Issue a new token when the user clicks **Refresh Session**; the old token becomes invalid immediately.

### Token Validation

- Validate the token on every upload request.
- Reject requests with a missing, malformed, expired, or invalid token.
- Use `secrets.compare_digest()` for constant-time token comparison to prevent timing attacks.
- Return a generic `403 Forbidden` error for all token failures — do not distinguish between expired, invalid, or missing.

### Session Lifecycle

1. Session is created when the user starts Mobile Upload.
2. Session expires after the configured duration.
3. Session can be manually invalidated (Refresh Session or Stop Mobile Upload).
4. After expiration, new uploads are rejected.
5. The upload page displays a session-expired message.
6. The server remains running briefly after session expiry to serve the expiration message, then can be stopped by the user.

### Security Notices

- The application must display a notice that the phone and computer must be on the same trusted Wi-Fi or LAN.
- The application must not claim that token-based HTTP upload provides transport encryption.
- If local HTTPS is not implemented, the application must document this limitation in the Mobile Upload Panel and in `README.md`.

---

## 15. Inbox Folder Monitoring

### Service: `InboxWatcher`

**Implementation:** Use the `watchdog` library to monitor the Inbox directory for new files.

**Behavior:**

1. Watch the Inbox directory for `FileCreatedEvent` and `FileModifiedEvent`.
2. When a new file appears, start a stability check:
   - Wait a configurable interval (default: 1 second).
   - Verify that the file size has not changed.
   - Verify that the modification time has not changed.
   - Repeat up to a configurable number of attempts (default: 3).
3. Once the file is stable, verify it is a valid, readable image using Pillow.
4. Calculate a SHA-256 hash of the file content.
5. Check the hash against previously processed files to prevent duplicate processing.
6. If the file passes all checks, move it from `Inbox/` to `Processing/` using `FileService`.
7. Create a `ProcessingItem` and submit it to the `ProcessingQueue`.
8. If the file fails validation, move it to `Failed/` with a safe error record.

**Constraints:**

- Do not run OCR directly inside the filesystem event callback.
- The watcher callback must only submit tasks to a controlled queue.
- Ignore files with temporary extensions (`.tmp`, `.part`, `.partial`).
- Ignore hidden files and system files.
- Avoid infinite reprocessing loops — track which files have been seen.
- The watcher must recover safely after application restart by scanning the Inbox directory for any files that arrived while the application was not running.

---

## 16. Image Preprocessing Requirements

### Service: `ImagePreprocessor`

**Design:** An abstraction that applies a configurable pipeline of OpenCV operations to improve OCR accuracy. The original image is never modified.

### Preprocessing Profiles

| Profile | Description | Typical Operations |
|---------|-------------|-------------------|
| `default` | Balanced settings for clean printed documents | Grayscale, light denoise, CLAHE contrast |
| `low_contrast` | For faded or poorly printed documents | Grayscale, aggressive CLAHE, adaptive threshold |
| `noisy_scan` | For scans with speckle noise | Grayscale, bilateral filter, morphological denoise |
| `camera_photo` | For phone-captured photos with uneven lighting | Grayscale, shadow reduction, deskew, adaptive threshold |

### Available Operations

| Operation | Library | Notes |
|-----------|---------|-------|
| Grayscale conversion | OpenCV | Always applied first |
| Light denoising | OpenCV `fastNlMeansDenoising` | Low strength to avoid blurring text |
| Contrast enhancement (CLAHE) | OpenCV | Clip limit configurable |
| Adaptive thresholding | OpenCV `adaptiveThreshold` | Gaussian or mean, block size configurable |
| Deskewing | OpenCV + Hough or `minAreaRect` | Only when skew angle is small (< 15°) |
| Perspective correction | OpenCV `getPerspectiveTransform` | Only when a reliable document boundary is detected; do not apply blindly |
| Orientation correction | OpenCV or PaddleOCR built-in | Only when detection is reliable; incorrect rotation is worse than no correction |
| Scaling | OpenCV `resize` | Only for images below a minimum DPI threshold |
| Shadow reduction | OpenCV morphological operations | For phone photos with uneven lighting |

**Constraints:**

- Do not apply every operation blindly. Each profile defines which operations are active and their parameters.
- Always keep the original image intact.
- Store the preprocessed working copy separately.
- Allow the user to compare original and processed versions in the image viewer.
- Perspective correction must only be applied when a reliable document boundary (four-corner contour) is detected with high confidence.

---

## 17. OCR Architecture

### Abstract Base Class: `BaseOCREngine`

```
class BaseOCREngine(ABC):
    @abstractmethod
    def initialize(self) -> None: ...

    @abstractmethod
    def recognize(self, image: numpy.ndarray) -> list[OCRResult]: ...

    @abstractmethod
    def is_initialized(self) -> bool: ...

    @abstractmethod
    def shutdown(self) -> None: ...
```

### Concrete Implementation: `PaddleOCREngine`

**Behavior:**

- Initialize the PaddleOCR model once on first use (lazy initialization) or during application startup in a background thread.
- Reuse the initialized model for all subsequent OCR calls.
- Return a list of `OCRResult` objects containing text, confidence, bounding box, and reading-order sequence number.
- Handle model initialization errors (missing model files, incompatible versions, out of memory).
- Log initialization time and per-image OCR duration (without logging OCR content).

**OCR Model Configuration:**

```json
{
  "ocr_engine": "paddleocr",
  "paddleocr": {
    "lang": "vi",
    "use_angle_cls": true,
    "use_gpu": false,
    "det_model_dir": null,
    "rec_model_dir": null,
    "cls_model_dir": null,
    "show_log": false
  }
}
```

- When `det_model_dir`, `rec_model_dir`, or `cls_model_dir` are `null`, PaddleOCR downloads models automatically on first run.
- For offline deployment, set these to paths within the application's `Models/` directory.
- Document the offline model preparation process in `README.md`.

### OCR Result Model

```
@dataclass
class BoundingBox:
    points: list[tuple[float, float]]  # Four corner points

    @property
    def x_min(self) -> float: ...
    @property
    def y_min(self) -> float: ...
    @property
    def x_max(self) -> float: ...
    @property
    def y_max(self) -> float: ...
    @property
    def center(self) -> tuple[float, float]: ...
    @property
    def width(self) -> float: ...
    @property
    def height(self) -> float: ...

@dataclass
class OCRResult:
    text: str
    confidence: float
    bounding_box: BoundingBox
    sequence_number: int
    source_image: str
    page_number: int = 1
```

---

## 18. Document Extraction Requirements

### Abstract Base Class: `BaseDocumentExtractor`

```
class BaseDocumentExtractor(ABC):
    @abstractmethod
    def extract(
        self,
        ocr_results: list[OCRResult],
        config: DocumentTypeConfig,
        image_width: int,
        image_height: int,
    ) -> DocumentData: ...
```

### Concrete Implementation: `FixedFormExtractor`

The MVP supports fixed-layout printed documents. The extractor uses two complementary strategies:

1. **Label-based extraction**: Locate a known label in the OCR results and find the associated value nearby.
2. **Region-based extraction**: Filter OCR results that fall within a configured normalized region.

Both strategies produce candidate values. The extractor ranks candidates and selects the best match for each field.

---

## 19. Label-Based Extraction

### Supported Labels (Vietnamese)

| Field | Primary Label | Alternate Labels |
|-------|--------------|-----------------|
| Document Number | Mã phiếu | Số phiếu |
| Document Date | Ngày chứng từ | Ngày |
| Product Code | Mã sản phẩm | Mã hàng |
| Product Name | Tên sản phẩm | Tên hàng |
| Quantity | Số lượng | SL |
| Unit | Đơn vị | ĐVT |
| Note | Ghi chú | — |

### Value Location Strategies

After detecting a label in the OCR results, search for the associated value in three spatial directions:

1. **Same line**: OCR results on the same horizontal line as the label, to the right of the label's bounding box. Determined by vertical overlap of bounding boxes.

2. **To the right**: OCR results whose left edge is to the right of the label's right edge, within a configurable vertical tolerance (default: 50% of label height).

3. **Directly below**: OCR results whose top edge is below the label's bottom edge, within a configurable horizontal tolerance (default: 100% of label width), and within a configurable maximum vertical distance.

### Spatial Matching Rules

- Use bounding-box coordinates for spatial reasoning, not string splitting or line-based assumptions.
- A "same line" match requires that the vertical center of the candidate is within the vertical bounds of the label, with configurable tolerance.
- Prefer same-line matches over below-label matches for most field types.
- For multi-word labels (e.g., "Mã sản phẩm"), match the full label text using fuzzy or normalized comparison (lowercase, stripped diacritics for matching only — preserve original text in results).

---

## 20. Region-Based Extraction

### Normalized Coordinate System

Document regions are defined as normalized coordinates where both axes range from `0.0` to `1.0`:

- `(0.0, 0.0)` = top-left corner of the image
- `(1.0, 1.0)` = bottom-right corner of the image

### Region Definition

```json
{
  "x1": 0.10,
  "y1": 0.05,
  "x2": 0.50,
  "y2": 0.15
}
```

### Validation Rules

- `0.0 <= x1 < x2 <= 1.0`
- `0.0 <= y1 < y2 <= 1.0`
- Reject configurations that violate these constraints at startup with a clear, actionable error message.

### Extraction Logic

1. Convert the normalized region to pixel coordinates using the image dimensions: `pixel_x = normalized_x * image_width`.
2. Filter OCR results whose bounding-box center falls within the pixel region.
3. If multiple OCR results fall within the region, concatenate them in reading order (top-to-bottom, left-to-right) or select the best candidate based on the ranking algorithm.

---

## 21. Candidate Ranking

When multiple candidate values exist for a field, rank them using the following criteria in priority order:

| Priority | Criterion | Preference |
|----------|----------|------------|
| 1 | Field validation result | Valid candidates ranked higher than invalid |
| 2 | Configured region match | Candidates within the configured region ranked higher |
| 3 | Distance from the label | Closer candidates ranked higher (Euclidean distance from label bbox center to candidate bbox center) |
| 4 | OCR confidence | Higher confidence ranked higher |
| 5 | Regex validity | Candidates matching the field regex ranked higher |
| 6 | Reading order | Earlier in reading order ranked higher (tiebreaker) |

### Fallback Behavior

- If no reliable value is found after ranking, return an empty `FieldData` with `requires_review = True`.
- Never invent, guess, or fabricate a value.
- Never silently substitute a default value for a missing field.

---

## 22. Configuration Requirements

### File: `config/app_config.json`

```json
{
  "app_name": "Paper to Excel OCR",
  "version": "1.0.0",
  "language": "vi",
  "workspace_dir": null,
  "ocr_engine": "paddleocr",
  "paddleocr": {
    "lang": "vi",
    "use_angle_cls": true,
    "use_gpu": false,
    "det_model_dir": null,
    "rec_model_dir": null,
    "cls_model_dir": null,
    "show_log": false
  },
  "preprocessing_profile": "default",
  "confidence_threshold": 0.85,
  "server": {
    "port": 8265,
    "auto_start": false,
    "bind_address": null,
    "session_expiration_minutes": 15,
    "max_upload_size_mb": 15,
    "max_image_width": 8000,
    "max_image_height": 8000,
    "max_pixel_count": 40000000,
    "max_uploads_per_minute": 10,
    "max_concurrent_uploads": 3,
    "allowed_extensions": [".jpg", ".jpeg", ".png", ".webp"],
    "allowed_mime_types": ["image/jpeg", "image/png", "image/webp"]
  },
  "inbox_watcher": {
    "stability_check_interval_seconds": 1.0,
    "stability_check_max_attempts": 3,
    "ignored_extensions": [".tmp", ".part", ".partial"]
  },
  "excel": {
    "backup_enabled": true,
    "backup_dir": null,
    "verify_after_save": true
  },
  "logging": {
    "level": "INFO",
    "max_file_size_mb": 10,
    "max_backup_count": 5
  }
}
```

### File: `config/document_type_fixed.json`

```json
{
  "document_type": "fixed_form_v1",
  "display_name": "Phiếu nhập/xuất kho",
  "sheet_name": "Data",
  "header_row": 1,
  "start_row": 2,
  "confidence_threshold": 0.85,
  "row_matching": {
    "strategy": "composite_key",
    "keys": [
      "document_number",
      "product_code"
    ],
    "required_unique_match": true,
    "case_sensitive": false,
    "trim_whitespace": true
  },
  "update_policy": {
    "fill_empty_cells_only": true,
    "allow_overwrite_existing_values": false,
    "allow_formula_overwrite": false,
    "allow_matching_key_updates": false,
    "require_manual_confirmation": true
  },
  "empty_cell_definition": {
    "treat_as_empty": [null, ""],
    "whitespace_only_is_empty": true,
    "zero_is_empty": false,
    "false_is_empty": false,
    "dash_is_empty": false,
    "na_is_empty": false
  },
  "fields": {
    "document_number": {
      "display_name": "Mã phiếu",
      "excel_column": "A",
      "required": true,
      "matching_key": true,
      "updatable": false,
      "labels": ["Mã phiếu", "Số phiếu"],
      "regex": "^[A-Za-z0-9_\\-/]+$",
      "date_format": null,
      "numeric": false,
      "preserve_leading_zeros": false,
      "region": {
        "x1": 0.10,
        "y1": 0.05,
        "x2": 0.50,
        "y2": 0.15
      }
    },
    "product_code": {
      "display_name": "Mã sản phẩm",
      "excel_column": "B",
      "required": true,
      "matching_key": true,
      "updatable": false,
      "labels": ["Mã sản phẩm", "Mã hàng"],
      "regex": null,
      "date_format": null,
      "numeric": false,
      "preserve_leading_zeros": true,
      "region": null
    },
    "document_date": {
      "display_name": "Ngày chứng từ",
      "excel_column": "C",
      "required": false,
      "matching_key": false,
      "updatable": true,
      "labels": ["Ngày", "Ngày chứng từ"],
      "regex": null,
      "date_format": "dd/MM/yyyy",
      "numeric": false,
      "preserve_leading_zeros": false,
      "region": null
    },
    "quantity": {
      "display_name": "Số lượng",
      "excel_column": "D",
      "required": false,
      "matching_key": false,
      "updatable": true,
      "labels": ["Số lượng", "SL"],
      "regex": "^\\d+([.,]\\d+)?$",
      "date_format": null,
      "numeric": true,
      "preserve_leading_zeros": false,
      "region": null
    },
    "unit": {
      "display_name": "Đơn vị",
      "excel_column": "E",
      "required": false,
      "matching_key": false,
      "updatable": true,
      "labels": ["Đơn vị", "ĐVT"],
      "regex": null,
      "date_format": null,
      "numeric": false,
      "preserve_leading_zeros": false,
      "region": null
    },
    "note": {
      "display_name": "Ghi chú",
      "excel_column": "F",
      "required": false,
      "matching_key": false,
      "updatable": true,
      "labels": ["Ghi chú"],
      "regex": null,
      "date_format": null,
      "numeric": false,
      "preserve_leading_zeros": false,
      "region": null
    }
  }
}
```

### Configuration Validation

At application startup, `ConfigService` must:

1. Load `app_config.json` and `document_type_fixed.json`.
2. Validate all required keys exist.
3. Validate all value types (string, number, boolean, object, array).
4. Validate all normalized regions satisfy `0 <= x1 < x2 <= 1` and `0 <= y1 < y2 <= 1`.
5. Validate that each field has at least one label.
6. Validate that each field's Excel column is a valid column letter or letter pair.
7. Validate that no two fields map to the same Excel column.
8. Validate that `row_matching.keys` reference field names that exist in the `fields` map.
9. Validate that every field listed in `row_matching.keys` has `matching_key: true`.
10. Validate that fields with `matching_key: true` have `updatable: false`.
11. Validate that `update_policy` does not allow matching-key updates when `allow_matching_key_updates` is `false`.
12. Validate that at least one field has `updatable: true`.
13. Validate `empty_cell_definition` values are of expected types.
14. Display exact, actionable error messages for any configuration error, including the file path, key path, expected type, and actual value.

---

## 23. Data Validation Requirements

### Components

| Component | Responsibility |
|-----------|---------------|
| `DataNormalizer` | Trim whitespace, remove accidental line breaks, parse dates, parse numbers, normalize text encoding |
| `FieldValidator` | Validate a single field against its configured rules (required, regex, type, range) |
| `DocumentValidator` | Validate all fields of a document, run cross-field checks, check for duplicate document numbers |
| `ValidationResult` | Hold validation outcome for a single field |

### `ValidationResult` Model

```
@dataclass
class ValidationResult:
    is_valid: bool
    normalized_value: Any
    error_message: str | None = None
    warning_message: str | None = None
    requires_manual_review: bool = False
```

### Field-Specific Validation Rules

#### Document Number

- Required.
- Trim leading and trailing whitespace.
- Remove accidental line breaks and carriage returns.
- Support a configurable regex pattern (default: `^[A-Za-z0-9_\-/]+$`).
- Check for duplicates against existing document numbers in the target Excel workbook.
- Preserve case unless the configuration explicitly specifies case normalization.

#### Document Date

- Required.
- Support input formats: `dd/MM/yyyy`, `dd-MM-yyyy`, `yyyy-MM-dd`.
- Reject invalid calendar dates (e.g., 30/02/2024, 32/01/2024).
- Normalize to a Python `datetime.date` or `datetime.datetime` object.
- Write as a real Excel date value (not a string).
- Apply Excel number format `dd/MM/yyyy` to the cell.

#### Product Code

- Required.
- Trim whitespace.
- Preserve leading zeros (write to Excel as a text value prefixed with `'` or use `openpyxl` number format `@`).
- Do not automatically replace `O` with `0`.
- Do not automatically replace `I` or `l` with `1`.
- Warn the user about potentially ambiguous OCR characters (e.g., `O`/`0`, `I`/`l`/`1`) without auto-correcting.
- Optionally validate against a configured product master list (if provided).

#### Quantity

- Required.
- Must be numeric after normalization.
- Must not be negative.
- Support both integer and decimal values.
- Accept comma as decimal separator (common in Vietnamese formatting) and normalize to a period.
- Write as an Excel number value, not a text string.

#### OCR Confidence Threshold

- Use the configurable threshold from the document type configuration (default: `0.85`).
- Low confidence does not automatically mean the field is invalid.
- Required fields with confidence below the threshold set `requires_manual_review = True`.
- Export must remain disabled until all `requires_manual_review` fields have been manually confirmed by the user.

---

## 24. Confidence and Manual Review

### Confidence Display

- Each field in the review form displays its OCR confidence score as a percentage (e.g., "92%").
- Fields with confidence below the threshold are highlighted with a yellow background.
- Fields that are invalid according to validation rules are highlighted with a red background.
- Fields that are both low-confidence and invalid show the red highlight (invalid takes precedence).

### Manual Review Workflow

1. After OCR and extraction, the review form populates with extracted values.
2. Each field displays its confidence score and validation status.
3. Required fields with confidence below the threshold are marked as "Cần xác nhận" ("Needs confirmation").
4. The user can edit any field value.
5. After editing, the field is re-validated immediately.
6. For low-confidence required fields, the user must explicitly click a "Xác nhận" ("Confirm") button or checkbox next to the field.
7. The "Write to Excel" button is disabled until:
   - All required fields have valid values.
   - All required low-confidence fields have been manually confirmed.
8. Optional fields with low confidence generate a warning but do not block export.

### Tracking Review State

Each `FieldData` must track:

- `raw_value: str` — the original OCR-extracted text.
- `edited_value: str | None` — the user's corrected value, if edited.
- `confidence: float` — the OCR confidence score.
- `validation_result: ValidationResult` — current validation state.
- `manually_reviewed: bool` — whether the user has explicitly confirmed this field.
- `source: str` — "ocr", "manual", or "default".

---

## 22. Workbook Structure Analysis

Create WorkbookStructureReader.

It must inspect without modifying the workbook:
- Worksheet names
- Used ranges
- Existing Excel named tables
- Candidate header rows
- Merged cells
- Formula cells
- Hidden rows and columns
- Duplicate headers
- Potential table regions
- Anchor text
- Data types in sample rows

Do not send complete workbook data to an AI model by default. Use only structural metadata required for mapping.

---

## 23. Table Detection and Fingerprints

Create TableDetector and TableFingerprintService.

A table must be identified through a combination of:
- Worksheet name
- Named Excel table identifier when available
- Table range
- Header row
- Required header fingerprint
- Optional headers
- Optional anchor-cell text

Do not assume one worksheet contains only one table. If multiple tables match, require the user to select the target table. Do not automatically choose the first candidate.

Normalize headers carefully:
- Trim outer whitespace
- Normalize repeated whitespace
- Replace line breaks with spaces
- Optionally compare case-insensitively
- Do not merge distinct business concepts (e.g., Planned vs Actual Quantity).

---

## 24. Reusable Excel Mapping Profiles

The application must use approved mapping profiles so that AI does not repeatedly analyze the workbook and decide which columns to use.

Required workflow:
1. Analyze a new Excel table once.
2. Detect its worksheet, table region, header row, and headers.
3. Display available OCR fields.
4. Optionally generate mapping suggestions.
5. Let the user inspect and correct the suggestions.
6. Configure matching keys and updatable fields.
7. Validate the profile.
8. Require explicit user approval.
9. Save the approved profile locally.
10. Use deterministic code for normal processing.
11. Revalidate the profile when workbook structure changes.

### Mapping Profile Model

A MappingProfile must support:
- Profile ID, version, display name, enabled status
- Workbook identification rules
- Worksheet identification
- Named table identifier or table region
- Header row, data start row, data end strategy
- Required and optional header fingerprints
- Anchor-cell text when needed
- Matching-key fields and updatable fields
- OCR-field-to-Excel-header mappings and last known column positions
- Data types, validation rules
- Empty-cell policy, conflict policy, formula-cell policy, update policy

**Document Profile Separation:** Ensure the application distinguishes between DocumentProfile (how to extract from paper) and ExcelMappingProfile (where fields map in Excel). Do not combine them into one hard-coded configuration.

### Mapping Profile Validation

Before using a saved profile:
1. Open the selected workbook.
2. Confirm the workbook identification rules, worksheet, and table region exist.
3. Compare current structure with the saved fingerprint.
4. Confirm every required header exists exactly once.
5. Resolve current column positions by header name (saved columns are hints).
6. Confirm matching-key and updatable columns exist.
7. Detect duplicate headers, merged headers, and incompatible changes.
8. Build a validated RuntimeMapping.

If a required header is missing or ambiguous, block processing and display: "The Excel table structure has changed. Please review the mapping profile."

### Optional AI Mapping Assistance

AI may be used only while creating, editing, or repairing a mapping profile. AI must not be required during routine document processing.
AI receives only structural metadata (OCR field names, header names, data types), never the complete workbook or confidential values.
AI suggestions must never activate a mapping automatically; the user must explicitly approve.

### Mapping Configuration Mode

The user must be able to:
1. Select a workbook and view/select worksheets and tables.
2. Select a header row and view detected headers.
3. View OCR fields and map them to Excel headers.
4. Mark matching-key and updatable fields.
5. Configure rules (data types, empty-cell, conflict).
6. Test mapping and preview change plan.
7. Save, edit, clone, version, enable/disable profiles.

### Mapping Cache and Performance

Cache validated runtime mappings.
A cache entry should contain: Profile ID, version, workbook identity, modification time, worksheet identity, table fingerprint, resolved runtime columns, and validation timestamp.
Invalidate when: workbook path/time changes, worksheet/table/header changes, profile version changes.
During normal processing: load approved mapping, validate fingerprint, resolve columns, match row, create plan, require review, apply approved changes.

---

## 25. Excel Completion Service Architecture

The application is a **missing-data completion tool**. Its primary Excel responsibility is to locate an existing record, detect which cells are still missing, and fill only the approved empty cells. It does not normally append new rows.

All Excel services must be independent of the UI framework. They must not import PySide6.

### 25.1 Service Components

| Component | Responsibility |
|-----------|---------------|
| `ExcelReader` | Open `.xlsx` and `.xlsm` workbooks. Preserve VBA where required (`keep_vba=True`). Read configured worksheet values. Identify formulas, merged cells, and cell data types. Return typed cell values. |
| `ExcelRowMatcher` | Locate existing rows using configured matching keys. Return zero, one, or multiple matches. Never silently choose between multiple matches. Preserve key values such as leading-zero codes. |
| `ExcelChangePlanner` | Compare OCR values against the matched Excel row. Classify every mapped field into a cell state. Produce a list of `CellUpdateProposal` objects. Reject unsafe update plans. Never modify the workbook. |
| `ExcelCompletionService` | Receive an explicitly user-approved change plan. Revalidate the target workbook before saving. Confirm the matching row still contains the expected key values. Confirm approved target cells are still empty. Detect changes made after the preview was generated. Back up the workbook. Apply only approved changes. Save through a verified temporary file. Replace the destination atomically. |

### 25.2 Supported Formats

- `.xlsx` — standard Excel workbook.
- `.xlsm` — macro-enabled Excel workbook (load with `keep_vba=True` to preserve macros).

### 25.3 Row Matching

Before updating Excel, the application must locate the correct existing row.

The row-matching strategy must be configurable. Support:

- A single matching key (e.g., `document_number`).
- Multiple matching keys — composite key (e.g., `document_number` + `product_code`).
- Exact matching.
- Normalized exact matching (trimmed whitespace, configurable case sensitivity).

**Matching Process:**

1. Extract the configured key fields from OCR.
2. Validate the key fields (required, format, confidence).
3. Read the target worksheet starting from `start_row`.
4. Normalize values only according to the configured rules (`trim_whitespace`, `case_sensitive`).
5. Compare each row's key columns against the OCR key values.
6. Return all matching rows.
7. Continue only when exactly one valid row is found.

**Blocking Conditions — do not update Excel if:**

- A required matching key is missing from OCR.
- A matching key has not been manually reviewed when its OCR confidence is below the threshold.
- No matching row is found.
- More than one row matches.
- The match is based only on an unreliable fuzzy comparison.

**User Messages:**

- No match: "Không tìm thấy dòng phù hợp trong Excel." (No matching Excel record was found.)
- Multiple matches: "Tìm thấy nhiều dòng phù hợp. Cần chọn thủ công." (Multiple matching Excel records were found. Manual selection is required.)

Do not automatically select the first matching row when multiple rows match.

### 25.4 Optional Fuzzy Matching

Fuzzy matching must **not** be used for automatic updates.

If implemented, fuzzy matching may only be used to **suggest candidate rows for manual selection**. For example:

- OCR value: `PN00I`
- Excel value: `PN001`

The application may display `PN001` as a possible candidate, but it must not assume that `I` and `1` are equivalent. The user must explicitly select and confirm a suggested row.

### 25.5 Cell State Classification

After locating exactly one existing row, classify each mapped field into one of these states:

| State | Condition | Default Action |
|-------|-----------|---------------|
| `MISSING` | Excel cell is empty and OCR provides a valid value | Propose filling the cell |
| `ALREADY_COMPLETE` | Excel cell already contains the same normalized value as OCR | No change |
| `CONFLICT` | Excel cell contains a value that differs from the OCR value | Do not overwrite; display both values; require explicit user action if overwriting is permitted |
| `OCR_VALUE_MISSING` | Excel cell is empty but OCR did not extract a usable value | Keep empty; mark for manual input |
| `INVALID_OCR_VALUE` | OCR produced a value but it failed validation | Do not update; display validation error |
| `NOT_UPDATABLE` | Field is not permitted to be updated (formula cell, merged non-anchor cell, matching-key field, or not in `updatable` list) | Keep Excel value unchanged |
| `FORMULA_CELL` | Cell contains a formula | Preserve formula; never overwrite |

### 25.6 CellUpdateProposal Model

```
@dataclass
class CellUpdateProposal:
    field_name: str
    excel_row: int
    excel_column: str
    current_excel_value: Any
    extracted_ocr_value: str | None
    normalized_ocr_value: Any
    state: CellState
    confidence: float
    validation_result: ValidationResult
    is_formula: bool
    is_merged_non_anchor: bool
    update_allowed: bool
    user_approved: bool = False
    user_selected_action: str = ""
```

`CellState` is an enum: `MISSING`, `ALREADY_COMPLETE`, `CONFLICT`, `OCR_VALUE_MISSING`, `INVALID_OCR_VALUE`, `NOT_UPDATABLE`, `FORMULA_CELL`.

### 25.7 Empty Cell Definition

The definition of an empty cell must be configurable. By default:

**Treat as empty:**

- `None`
- An empty string `""`
- A string containing only whitespace

**Do NOT automatically treat as empty:**

- `0` or `0.0`
- `False`
- A valid formula (even if its cached result appears empty)
- A formula returning an empty string
- `"-"` (unless explicitly configured via `dash_is_empty: true`)
- `"N/A"` (unless explicitly configured via `na_is_empty: true`)

A formula cell must not be overwritten merely because its currently displayed result appears empty. If openpyxl cannot reliably determine the calculated result, preserve the formula and classify the cell as `FORMULA_CELL`.

### 25.8 Update Policy

The default update policy enforces safe behavior:

- Fill only empty cells.
- Never overwrite non-empty cells automatically.
- Never overwrite formula cells.
- Never change matching-key cells.
- Never update fields that are not listed as `updatable: true`.
- Require validation before every update.
- Require manual review for low-confidence required fields.
- Require an exact and unique row match.
- Create a workbook backup before saving.

Even if overwrite functionality is added later, it must be **disabled by default** via `allow_overwrite_existing_values: false`.

### 25.9 Change Preview

Before saving, the application must display a change preview. The preview must show:

| Column | Description |
|--------|-------------|
| Target Worksheet | Name of the worksheet |
| Target Row | Row number in the worksheet |
| Matching Keys | Values used to locate the row |
| Field Name | Vietnamese display name |
| Excel Column | Column letter |
| Current Excel Value | The value currently in the cell |
| OCR Value | The OCR-extracted value |
| Confidence | OCR confidence percentage |
| Validation Status | Valid / Invalid / Warning |
| Cell State | MISSING / ALREADY_COMPLETE / CONFLICT / etc. |
| Proposed Action | The action to take |

**Supported Actions:**

- Điền ô trống (Fill Missing Cell)
- Giữ giá trị hiện tại (Keep Existing Value)
- Nhập giá trị thủ công (Enter Value Manually)
- Bỏ qua trường (Skip Field)
- Xử lý xung đột (Resolve Conflict)

**Default Selected Actions:**

| Cell State | Default Action |
|------------|---------------|
| `MISSING` (valid OCR value) | Fill Missing Cell |
| `ALREADY_COMPLETE` | Keep Existing Value |
| `CONFLICT` | Keep Existing Value |
| `OCR_VALUE_MISSING` | Enter Value Manually |
| `INVALID_OCR_VALUE` | Skip Field |
| `NOT_UPDATABLE` | Keep Existing Value |
| `FORMULA_CELL` | Keep Existing Value |

The user must approve the final change set before the workbook is modified. The "Xác nhận thay đổi" (Confirm Changes) button must be explicitly clicked.

### 25.10 Conflict Handling

When an OCR value differs from an existing non-empty Excel value:

- Do not overwrite automatically.
- Highlight the field as a conflict.
- Display both values side by side (Excel value and OCR value).
- Preserve the current Excel value by default.
- Record no sensitive values in the application log.

If business rules later allow overwriting existing values, require all of the following:

1. An explicit configuration enabling overwrite (`allow_overwrite_existing_values: true`).
2. Explicit user selection of "Thay thế giá trị hiện tại" (Replace Existing Value) for that specific field.
3. A second confirmation dialog before saving.
4. An audit record containing only safe metadata (file UUID, field name, action taken — not the actual values).

The default implementation must not allow overwriting existing values.

### 25.11 Merged Cells and Formulas

**Merged Cells:**

- Identify whether a target cell belongs to a merged range using openpyxl's `merged_cells` property.
- Only the top-left cell (anchor) of a merged range may contain a value.
- Do not update a non-anchor merged cell.
- Treat unexpected merged-cell mappings as configuration errors.

**Formula Cells:**

- Preserve formulas by default.
- Do not replace formulas with values.
- Do not rely on cached formula results for deciding whether a cell is empty.
- Classify formula targets as `FORMULA_CELL`.
- If a field maps to a formula cell, classify it as `NOT_UPDATABLE` and report a warning.

### 25.12 Excel Reader Capabilities

| Capability | Description |
|------------|-------------|
| Worksheet validation | Verify the target worksheet exists in the workbook |
| Cell value reading | Read typed values (string, number, date, boolean, None) |
| Formula detection | Detect cells containing formulas (value starts with `=` or `data_type == 'f'`) |
| Merged cell detection | Identify merged cell ranges and anchor cells |
| Leading-zero preservation | Read product codes preserving leading zeros |
| Locked-file detection | Detect when the workbook is locked by another process |
| Permission handling | Detect and report permission errors (read-only, access denied) |
| Workbook preservation | Preserve unrelated worksheets, named ranges, and workbook properties |

**Constraints:**

- Do not hard-code Excel column letters inside any service — use the document type configuration.
- Do not convert every value into a string when reading.

---

## 26. Workbook Backup and Atomic Save

### Backup Process

Before modifying an existing workbook, the following steps must be performed in order:

1. Validate all approved changes (all fill values pass validation).
2. Confirm all required manual reviews are complete.
3. Confirm the user has explicitly approved the change preview.
4. Confirm the destination workbook file exists and is accessible.
5. Confirm the target worksheet exists in the workbook.
6. Create a timestamped backup of the destination workbook.

**Backup Naming Convention:**

```
<original_name>_backup_yyyyMMdd_HHmmss.xlsx
```

Example: `inventory_data_backup_20260902_194500.xlsx`

**Backup Location:** The configured backup directory (default: `Backup/` within the workspace).

### Stale-Data Protection (Concurrency Safety)

The workbook may change between preview and save. Before applying updates:

1. Reopen the workbook from disk.
2. Find the target row again using the matching keys.
3. Confirm the matching keys still identify exactly one row.
4. Confirm each target cell still has its expected previous value (the value shown in the preview).
5. Confirm every approved missing cell is still empty.
6. Cancel the update if the workbook has changed unexpectedly.

If stale data is detected, display:

"File Excel đã thay đổi sau khi xem trước. Vui lòng tải lại và kiểm tra lại." (The Excel workbook changed after the preview was created. Please reload and review the changes again.)

Do not overwrite a cell that another user or process has filled after the preview.

### Atomic Save Process

After creating the backup and verifying stale-data safety:

7. Load the workbook into memory using openpyxl.
8. Apply only the user-approved cell fills (no unapproved changes).
9. Write dates as real Excel date values with correct number format.
10. Write quantities as Excel numbers, not text strings.
11. Write product codes with leading zeros as text using `@` number format.
12. Save the modified workbook to a temporary file in the same directory as the destination (to ensure same-filesystem atomic rename).
13. Verify the temporary file exists and has a non-zero size.
14. Reopen the temporary file using openpyxl.
15. Verify that the expected cells contain the expected values.
16. Close all file handles.
17. Replace the destination file with the verified temporary file using `os.replace()` (atomic on the same filesystem).
18. Remove the temporary file only if it is no longer needed (i.e., the rename succeeded).

### Failure Behavior

- If any step from 7 to 17 fails, the original workbook remains unchanged (the backup is the safety net).
- The temporary file is cleaned up on failure.
- The error is logged with a safe technical description.
- The user is shown a non-technical error message.
- The user's review data and change preview are preserved (not discarded).
- The source image is not moved to `Processed/` on failure — it remains in `Processing/` or is moved to `Failed/`.

### Limitations

- Do not claim transaction-level rollback beyond backup and atomic replacement.
- If the destination file is on a network share, `os.replace()` may not be atomic. Document this limitation.

---

## 27. User Interface Requirements

### General UI Rules

- User-facing text: Vietnamese.
- Source code identifiers: English.
- Framework: PySide6 (Qt for Python).
- UI classes must focus on presentation logic only.
- Business logic, OCR, validation, Excel operations, and server logic must reside in service classes.
- Background operations must use Qt signals and slots to communicate with the UI.
- Background threads must never update PySide6 widgets directly.

### 27.1 Toolbar

| Button | Vietnamese Label | Action |
|--------|-----------------|--------|
| Select Image | Chọn ảnh | Open a file dialog for single image selection |
| Select Multiple Images | Chọn nhiều ảnh | Open a file dialog for multiple image selection |
| Select Excel Workbook | Chọn file Excel | Open a file dialog to select the target workbook |
| Run OCR | Nhận dạng | Start OCR on the currently selected image |
| Validate Data | Kiểm tra dữ liệu | Run validation on the current review form |
| Rotate Left | Xoay trái | Rotate the displayed image 90° counter-clockwise |
| Rotate Right | Xoay phải | Rotate the displayed image 90° clockwise |
| Reset Image | Đặt lại ảnh | Reset rotation and zoom to original state |
| Match & Preview | Tìm dòng và xem trước | Match OCR data to an existing Excel row and show change preview |
| Confirm Changes | Xác nhận thay đổi | Apply approved changes to the matched Excel row |
| Open Output Folder | Mở thư mục kết quả | Open the Output directory in Windows Explorer |
| Start Mobile Upload | Bắt đầu nhận ảnh | Start the local upload server |
| Stop Mobile Upload | Dừng nhận ảnh | Stop the local upload server |

### 27.2 Document Viewer (`ImageViewer`)

**Features:**

- Display the original image at load time.
- Display the preprocessed image when available.
- Toggle between original and processed views.
- Zoom in and zoom out (mouse wheel, buttons, or keyboard shortcuts).
- Fit image to the viewer window.
- Pan the image (click and drag).
- Horizontal and vertical scrollbars.
- Rotation preview (does not modify the source file).
- Overlay OCR bounding boxes on the image.
- Highlight the bounding box of the currently selected field in the review form.
- Visual distinction between high-confidence and low-confidence bounding boxes.

**Constraints:**

- Never modify the source image file directly.
- All visual transformations (rotation, zoom, pan) are view-level only.

### 27.3 Review Form (`ReviewForm`)

**Initial Fields:**

| Field Key | Vietnamese Display Name |
|-----------|----------------------|
| `document_number` | Mã phiếu |
| `document_date` | Ngày chứng từ |
| `product_code` | Mã sản phẩm |
| `product_name` | Tên sản phẩm |
| `quantity` | Số lượng |
| `unit` | Đơn vị |
| `note` | Ghi chú |

**Per-Field UI Elements:**

- Editable text input (pre-filled with OCR-extracted or user-edited value).
- Confidence score label (e.g., "92%").
- Validation status icon and message.
- Warning message label (for non-blocking warnings like ambiguous characters).
- Error message label (for blocking validation errors).
- Yellow background when confidence is below the threshold.
- Red background when the field is invalid.
- "Xác nhận" (Confirm) checkbox or button for low-confidence required fields.
- Indicator showing whether the field has been manually reviewed.

**Behavior:**

- When the user edits a field, re-validate immediately.
- When the user selects a field, highlight the corresponding bounding box in the image viewer.
- The "Tìm dòng và xem trước" (Match & Preview) action is disabled until all matching-key fields are valid and all low-confidence matching-key fields are manually confirmed.

### 27.4 Change Preview Panel (`ChangePreviewPanel`)

The Change Preview Panel displays the cell-by-cell comparison between OCR values and the matched Excel row.

**Display Elements:**

| Element | Description |
|---------|-------------|
| Matched Row Info | Worksheet name, row number, and matching key values |
| Match Status | "Tìm thấy 1 dòng phù hợp" / "Không tìm thấy" / "Nhiều dòng phù hợp" |
| Field Table | One row per mapped field showing current value, OCR value, state, and action |
| Summary | Count of fields to fill, fields already complete, conflicts, and skipped fields |
| Confirm Button | "Xác nhận thay đổi" — enabled only when at least one approved fill exists and all confirmations are complete |

**Per-Field Row in the Table:**

| Column | Description |
|--------|-------------|
| Field Name | Vietnamese display name |
| Excel Column | Column letter |
| Current Value | Value currently in the Excel cell (or "Trống" for empty) |
| OCR Value | Extracted value from OCR |
| Confidence | Percentage |
| State | Cell state badge (color-coded) |
| Action Dropdown | User-selectable action (Fill / Keep / Manual / Skip / Resolve) |

**State Color Coding:**

- `MISSING` — green badge (fillable)
- `ALREADY_COMPLETE` — gray badge (no action needed)
- `CONFLICT` — orange badge (attention required)
- `OCR_VALUE_MISSING` — yellow badge (manual input possible)
- `INVALID_OCR_VALUE` — red badge (cannot fill)
- `NOT_UPDATABLE` — gray badge (locked)
- `FORMULA_CELL` — gray badge with formula icon (preserved)

### 27.5 Document Queue (`DocumentListWidget`)

**Columns:**

| Column | Description |
|--------|-------------|
| Thumbnail | Small preview of the document image |
| File ID | Safe internal identifier (not the original filename) |
| Source | "Local" or "Mobile Upload" |
| Import Time | Timestamp of when the file was added |
| Processing Status | Current processing stage |
| OCR Status | OCR result status |
| Review Status | Whether review is complete |
| Completion Status | Whether data has been written to Excel |
| Error Summary | Brief error description if failed |

**Supported Statuses:**

- `Đã nhận` (Received)
- `Chưa xử lý` (Not Processed)
- `Đang xử lý` (Processing)
- `Cần kiểm tra` (Review Required)
- `Hợp lệ` (Valid)
- `Đã tìm dòng` (Row Matched)
- `Đã hoàn thành` (Completed)
- `Lỗi` (Failed)
- `Trùng lặp` (Duplicate)
- `Không tìm thấy` (No Match Found)

### 27.6 Mobile Upload Panel (`MobileUploadPanel`)

**Elements:**

| Element | Description |
|---------|-------------|
| Server Status | "Đang chạy" (Running) / "Đã dừng" (Stopped) / "Lỗi" (Error) |
| Upload URL | The local upload URL (displayed as text) |
| QR Code | QR code image encoding the upload URL |
| Session Expiration | Countdown timer showing remaining session time |
| Refresh Session | Button to generate a new session token |
| Copy URL | Button to copy the upload URL to the clipboard |
| Received Count | Number of images received in the current session |
| Security Notice | Short text: "Máy tính và điện thoại phải cùng mạng Wi-Fi. Ảnh được gửi trực tiếp, không qua máy chủ bên ngoài." |

---

## 28. Background Processing Requirements

### Operations That Must Not Block the UI Thread

- PaddleOCR model initialization.
- OCR execution on any image.
- Batch image preprocessing.
- File hashing (SHA-256).
- Local upload server execution.
- Large file validation (opening and verifying large images).
- Excel save operations (backup, write, verify, replace).
- Workbook verification (reopening and checking cells).

### Implementation Mechanisms

| Mechanism | Use Case |
|-----------|---------|
| `QThread` with signals/slots | Long-running, stateful operations (OCR worker, Excel worker) |
| `QRunnable` with `QThreadPool` | Short, parallelizable tasks (file hashing, image validation) |
| Background thread (Python `threading.Thread`) | Local upload server (FastAPI + Uvicorn) |
| Thread-safe queue (`queue.Queue`) | Processing queue for coordinating watcher → OCR → review |

### Signal Protocol

Background workers must communicate with the UI exclusively through Qt signals:

| Signal | Payload | Purpose |
|--------|---------|---------|
| `progress_updated` | `(item_id: str, percent: int, message: str)` | Report progress |
| `processing_completed` | `(item_id: str, document_data: DocumentData)` | OCR + extraction done |
| `processing_failed` | `(item_id: str, error_category: str, error_message: str)` | Processing error |
| `upload_received` | `(file_id: str, file_path: Path)` | New upload available |
| `validation_completed` | `(item_id: str, results: dict[str, ValidationResult])` | Validation done |
| `row_match_completed` | `(item_id: str, match_count: int, matched_row: int or None)` | Row matching result |
| `change_plan_ready` | `(item_id: str, proposals: list[CellUpdateProposal])` | Change preview ready |
| `completion_completed` | `(item_id: str, excel_path: Path, filled_count: int)` | Completion successful |
| `completion_failed` | `(item_id: str, error_message: str)` | Completion error |
| `stale_data_detected` | `(item_id: str, changed_fields: list[str])` | Workbook changed since preview |
| `server_status_changed` | `(status: str, message: str)` | Server state change |
| `session_expiring` | `(remaining_seconds: int,)` | Session countdown |

### Cancellation

- OCR workers should support cancellation via a `threading.Event` or equivalent flag.
- Cancelled operations must clean up resources (close files, release memory).
- Cancellation should be best-effort; it is acceptable if a nearly-complete operation finishes before the cancellation flag is checked.

---

## 29. Security and Privacy Requirements

### Data Locality

- All document images and OCR output must remain on the local machine.
- No file must be uploaded to any cloud service.
- No external OCR API must be called.
- OCR models are downloaded once during setup and used offline thereafter.

### Logging Restrictions

Logs **may** contain:

- Timestamps.
- Internal file UUIDs.
- Safe processing status values.
- Processing duration measurements.
- Technical error categories (e.g., "image_validation_error", "ocr_initialization_error").
- Technical exception types and safe messages.
- Non-sensitive recovery information.

Logs **must not** contain:

- Full OCR-extracted text content.
- Extracted business values (document numbers, product codes, quantities).
- Session tokens (current or expired).
- Absolute local paths to user documents or workbooks.
- Upload file original names.

### Server Security

- The local upload server must use a temporary session token generated with `secrets.token_urlsafe(32)`.
- Tokens must be compared using `secrets.compare_digest()`.
- The server must bind only to the configured local interface (not `0.0.0.0` by default).
- The server must warn the user if the detected IP address appears to be public.
- The server must not automatically add Windows Firewall exceptions.
- The server must stop accepting uploads after the session expires.
- The server must stop when the desktop application exits.
- Error responses to the phone must not include stack traces or absolute local paths.

### Upload Validation

- Validate request body size before reading the full body.
- Validate file extension against the allowed list.
- Validate MIME type against the allowed list.
- Verify actual image format using Pillow (`Image.open()` + `verify()`), not just the extension or MIME type.
- Check image dimensions against the configured maximum width and height.
- Check total pixel count against the configured maximum.
- Detect and reject animated images (animated GIF, animated WebP) unless explicitly supported.
- Detect and reject decompression-bomb images (`PIL.Image.MAX_IMAGE_PIXELS` guard).
- Generate a UUID for the saved filename — never use the original filename.
- Store the sanitized original filename only as optional metadata (not as the saved filename).
- Prevent path traversal by constructing the save path from the UUID and the Inbox directory, never from user-supplied input.

### Network Notices

- The application must clearly tell the user that the phone and computer must be on the same trusted Wi-Fi or LAN.
- The application must not claim that HTTP token-based upload provides transport encryption.
- If HTTPS is not implemented, the limitation must be documented in the Mobile Upload Panel, `README.md`, and this skill.

---

## 30. Error Handling

### Error Categories and Required Handling

| Category | Error | Required Action |
|----------|-------|----------------|
| Configuration | Missing `app_config.json` | Show exact file path expected; do not start |
| Configuration | Invalid JSON syntax | Show file path, line number if possible; do not start |
| Configuration | Invalid normalized region | Show field name, invalid values, valid range; do not start |
| Image | Unsupported image format | Reject; move to Failed/; notify user |
| Image | Corrupted or unreadable image | Reject; move to Failed/; notify user |
| Image | Oversized upload (bytes) | Reject upload request; return error to phone |
| Image | Excessive pixel count | Reject upload request; return error to phone |
| Upload | Expired session token | Return generic 403; show expiration message on phone |
| Upload | Invalid or missing token | Return generic 403 |
| Upload | Too many uploads (rate limit) | Return 429 Too Many Requests |
| Server | Port unavailable | Try next port or show error; do not crash |
| Server | No private local IP found | Show error explaining network requirements |
| Server | Startup failure | Show error; allow retry |
| Server | Shutdown failure | Log error; force cleanup on app exit |
| Watcher | Inbox watcher failure | Log error; attempt restart; notify user |
| Watcher | Duplicate uploaded image | Skip; log; notify user |
| OCR | PaddleOCR initialization failure | Show error with model path; suggest re-download |
| OCR | Model files unavailable offline | Show error; suggest running online once to download |
| OCR | Empty OCR result | Notify user; all fields require manual entry |
| Validation | Missing required field | Highlight field; block completion |
| Validation | Low-confidence required field | Highlight field; require manual confirmation |
| Row Match | No matching row found | Display message; block completion |
| Row Match | Multiple rows match | Display message; require manual selection or block |
| Row Match | Matching key missing from OCR | Highlight key field; block match |
| Row Match | Matching key not manually confirmed | Require confirmation before matching |
| Cell State | Formula cell mapped to updatable field | Classify as NOT_UPDATABLE; warn user |
| Cell State | Merged non-anchor cell mapped | Classify as NOT_UPDATABLE; report config issue |
| Excel | Workbook file missing | Show error; ask user to select a valid file |
| Excel | Worksheet missing | Show error listing available worksheets |
| Excel | Workbook locked by another process | Show error; ask user to close the file |
| Excel | Permission denied | Show error; ask user to check file permissions |
| Excel | Workbook corrupted | Show error; do not attempt to modify |
| Excel | Stale workbook data | Cancel save; show message to reload and re-preview |
| Excel | Backup creation failure | Abort completion; notify user |
| Excel | Temporary save failure | Abort completion; original workbook unchanged |
| Excel | Verification failure | Abort completion; remove temp file; original unchanged |
| Excel | Destination replacement failure | Log error; backup is available; notify user |

### Error Handling Rules

1. Do not silently ignore errors.
2. Broad exception handling (`except Exception`) is only acceptable at application boundaries (top-level event handlers, worker thread entry points) where the original error is logged and converted into a safe, user-facing result.
3. An error must not crash the application unnecessarily.
4. An error must not delete the source image.
5. An error must not remove user-edited review data from the review form.
6. An error must not remove the change preview data.
7. An error must not damage the original workbook.
8. An error must not expose sensitive content (OCR text, file paths) in user-facing messages.
9. Custom exception types must be defined for major technical domains: `ConfigurationError`, `ImageValidationError`, `OCRError`, `ExtractionError`, `ValidationError`, `RowMatchError`, `CompletionError`, `ExcelServiceError`, `UploadServerError`, `SessionError`.

---

## 31. Logging Requirements

### Configuration

- Use the Python `logging` standard library.
- Configure via `app_config.json` logging section.
- Default level: `INFO`.
- Log to rotating files in the `Logs/` directory.
- Maximum file size: 10 MB (configurable).
- Maximum backup count: 5 (configurable).
- Log format: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`.
- Use logger names matching module paths (e.g., `paper_to_excel.ocr.paddle_ocr_engine`).

### Content Rules

**Safe to Log:**

- Application startup and shutdown.
- Configuration loaded successfully (without values).
- Server started on `<ip>:<port>` (the IP and port are operational, not sensitive).
- Session created (without the token value).
- Upload received: file UUID, size, format, validation result.
- Processing started/completed: file UUID, duration.
- OCR completed: file UUID, number of results, average confidence.
- Validation result: file UUID, pass/fail counts (without field values).
- Export completed: file UUID, target workbook name (basename only).
- Error details: exception type, safe message, file UUID.

**Forbidden to Log:**

- Full OCR text content.
- Extracted field values (document numbers, product codes, dates, quantities).
- Session tokens.
- Absolute paths to user documents or workbooks (use basenames or UUIDs).
- Original filenames from uploads.
- Stack traces in production logs (log them only at `DEBUG` level).

---

## 32. Testing Requirements

### Framework and Conventions

- Use `pytest` as the test framework.
- Use `pytest.ini` for configuration.
- Mock PaddleOCR so unit tests do not download or initialize the real OCR model.
- Use temporary directories (`tmp_path` fixture) for all file operations.
- Use temporary Excel workbooks created with openpyxl for Excel tests.
- All business services must be testable without importing PySide6.

### Required Unit Tests

| # | Test Case | Module |
|---|-----------|--------|
| 1 | Valid session token accepted | `test_upload_security.py` |
| 2 | Missing session token rejected | `test_upload_security.py` |
| 3 | Expired session token rejected | `test_upload_security.py` |
| 4 | Session invalidation works | `test_upload_security.py` |
| 5 | Unsupported file extension rejected | `test_image_validator.py` |
| 6 | Incorrect MIME type rejected | `test_image_validator.py` |
| 7 | Invalid actual image content rejected | `test_image_validator.py` |
| 8 | Oversized image rejected | `test_image_validator.py` |
| 9 | Excessive pixel count rejected | `test_image_validator.py` |
| 10 | UUID filename generated (no original name used) | `test_upload_security.py` |
| 11 | Path traversal prevented | `test_upload_security.py` |
| 12 | Partial file ignored by InboxWatcher | `test_inbox_watcher.py` |
| 13 | Stable finalized file accepted by InboxWatcher | `test_inbox_watcher.py` |
| 14 | Duplicate file hash rejected | `test_inbox_watcher.py` |
| 15 | File moved safely between managed directories | `test_inbox_watcher.py` |
| 16 | Valid date formats parsed correctly | `test_validator.py` |
| 17 | Impossible date rejected (e.g., 30/02/2024) | `test_validator.py` |
| 18 | Integer quantity accepted | `test_validator.py` |
| 19 | Decimal quantity accepted | `test_validator.py` |
| 20 | Negative quantity rejected | `test_validator.py` |
| 21 | Empty required document number rejected | `test_validator.py` |
| 22 | Product code leading zeros preserved | `test_validator.py` |
| 23 | Same-line label extraction | `test_extractor.py` |
| 24 | Right-side label extraction | `test_extractor.py` |
| 25 | Below-label extraction | `test_extractor.py` |
| 26 | Invalid normalized region rejected | `test_extractor.py` |
| 27 | Empty OCR result produces review-required fields | `test_extractor.py` |
| 28 | Low-confidence field requires manual review | `test_validator.py` |
| 29 | Excel export blocked before manual review complete | `test_excel_service.py` |
| 30 | Duplicate document number detected | `test_excel_service.py` |
| 31 | existing row detected correctly | `test_excel_service.py` |
| 32 | Date written as Excel date type | `test_excel_service.py` |
| 33 | Quantity written as Excel number type | `test_excel_service.py` |
| 34 | Missing worksheet handled gracefully | `test_excel_service.py` |
| 35 | Original workbook preserved when save fails | `test_excel_service.py` |
| 36 | Upload rate limit enforced | `test_upload_security.py` |
| 37 | Expired server session rejects new uploads | `test_upload_server.py` |
| 38 | Server stops cleanly | `test_upload_server.py` |
| 39 | Business services testable without PySide6 | `test_processing_queue.py` |

### Required Integration Tests

| # | Test Case | Description |
|---|-----------|-------------|
| 1 | Upload to Inbox | Simulate a multipart upload to the FastAPI endpoint, verify file lands in Inbox/ |
| 2 | Inbox to Processing Queue | Place a file in Inbox/, verify InboxWatcher moves it to Processing/ and adds it to the queue |
| 3 | Mocked OCR to Review Model | Feed mocked OCR results through the extractor and validator, verify DocumentData is populated correctly |
| 4 | Review Model to Excel | Feed a validated DocumentData through ExcelService, verify the temporary workbook contains correct values |

---

### Mapping Profiles
1. A valid profile resolves one worksheet and table.
2. Missing worksheet invalidates the profile.
3. Multiple matching tables block automatic selection.
4. Required headers are detected.
5. Duplicate headers invalidate the profile.
6. A moved column is resolved by header.
7. A missing header invalidates the profile.
8. A stale mapping cache is invalidated.
9. An AI suggestion cannot activate a profile.
10. A disabled profile cannot be selected automatically.

### Row Matching
11. One row matches a single key.
12. One row matches composite keys.
13. No matching row blocks updates.
14. Multiple rows block updates.
15. Leading-zero identifiers are preserved.
16. Low-confidence keys require review.
17. Fuzzy matching only suggests candidates.

### Cell States
18. None is considered empty.
19. An empty string is considered empty.
20. A whitespace-only string is considered empty.
21. Zero is not considered empty.
22. False is not considered empty.
23. A formula is not considered empty.
24. A valid OCR value creates a MISSING proposal.
25. An equivalent existing value creates ALREADY_COMPLETE.
26. A different existing value creates CONFLICT.
27. A missing OCR value does not clear a cell.
28. An invalid OCR value is not proposed.
29. A non-updatable field is preserved.
30. A matching key is preserved.
31. A formula is preserved.
32. An invalid merged target blocks the plan.

### Excel Completion
33. Only approved changes are applied.
34. Existing non-empty values remain unchanged.
35. Dates remain real Excel dates.
36. Quantities remain numeric.
37. Leading-zero codes remain strings.
38. A backup is created.
39. The original workbook remains unchanged after save failure.
40. A workbook change after preview cancels saving.
41. A matching-key change cancels saving.
42. A cell filled after preview is not overwritten.
43. The temporary workbook is reopened and verified.

## 33. Windows Packaging Requirements

### Tools

- **PyInstaller** version 6.0 or later.
- **Spec file**: `paper_to_excel.spec`.
- **Build script**: `build.bat`.

### `build.bat` Workflow

```
1. Check if the virtual environment exists; create it if not.
2. Activate the virtual environment.
3. Install dependencies from requirements.txt.
4. Run all tests with pytest.
5. If any test fails, stop the build and display an error.
6. Run PyInstaller with the spec file.
7. Display the output directory and executable path.
```

### PyInstaller Spec Requirements

The spec file must:

- Include `src/web/templates/` and `src/web/static/` as data files.
- Include `config/app_config.json` and `config/document_type_fixed.json` as data files.
- Include `assets/` as data files.
- Include required PySide6 resources and plugins.
- Include required PaddleOCR hidden imports (`paddle`, `paddleocr`, `shapely`, `pyclipper`, `imgaug`, etc. as needed).
- Include required OpenCV hidden imports.
- Include required openpyxl hidden imports.
- Set the application icon from `assets/icon.ico`.
- Use `--onedir` mode (not `--onefile`) for better startup time and easier debugging.
- Do not hard-code machine-specific paths.

### Offline OCR Models

- If the packaging strategy requires bundling OCR model files, copy them into the distribution directory as a post-build step.
- Document the expected model directory structure.
- Document the total distribution size.

### Known Limitations

- PaddlePaddle and PaddleOCR have complex native dependencies that may require specific `hiddenimports` and `binaries` entries in the spec file.
- A successful PyInstaller build on one machine does not guarantee compatibility on every Windows machine.
- The application may need the Visual C++ Redistributable installed on target machines.
- Document all known packaging issues and workarounds in `README.md`.

---

## 34. Implementation Phases

Phase 1: Requirements and Architecture
Phase 2: Models and Configuration
Phase 3: Mobile Upload and Security
Phase 4: Inbox and Processing Queue
Phase 5: OCR and Document Extraction
Phase 6: Workbook Structure Analysis and Mapping-Profile Management
Phase 7: Existing-Row Matching and Missing-Cell Change Planning
Phase 8: Excel Completion and Stale-Data Protection
Phase 9: Desktop UI and Mapping Editor
Phase 10: Testing, Packaging, and Documentation
## 35. Code Quality Checklist

Before submitting code for any phase, verify:

- [ ] All functions and methods have type hints.
- [ ] All public classes and methods have docstrings.
- [ ] Domain models use `dataclasses`.
- [ ] All path operations use `pathlib.Path`.
- [ ] Dependency injection is used where it improves testability.
- [ ] `logging` is used instead of `print`.
- [ ] UI classes contain only presentation logic.
- [ ] Business logic is not inside event handlers.
- [ ] OCR code is not inside UI classes.
- [ ] Excel operations are not inside UI classes.
- [ ] Upload-server logic is not inside UI classes.
- [ ] No global mutable state.
- [ ] No circular imports.
- [ ] No classes exceeding approximately 400 lines (split if larger).
- [ ] No duplicated logic across modules.
- [ ] All identifiers (classes, methods, variables, functions) use clear English names.
- [ ] All user-facing text uses Vietnamese.
- [ ] Custom exception types are defined for major domains.
- [ ] Background workers and server threads are cleaned up during shutdown.
- [ ] No `TODO` placeholders in submitted code.
- [ ] No `pass` for methods that must have an implementation.
- [ ] No `...` (ellipsis) to omit code.
- [ ] No single-file monolithic scripts.
- [ ] Excel column letters are not hard-coded inside `ExcelService`.
- [ ] No hard-coded local paths.
- [ ] No invented business requirements.
- [ ] No automatic correction of ambiguous OCR characters.
- [ ] No automatic export of unreviewed OCR results.

---

## 36. Response Rules for Coding Agents

When implementing any part of this application, coding agents must follow these rules:

### General Rules

1. Read and follow this SKILL.md before generating any code.
2. Implement one phase at a time unless instructed otherwise.
3. Do not skip phases or combine phases without explicit approval.
4. Provide complete file contents — never use placeholders, `TODO`, `pass` for required methods, or `...` to omit code.
5. Use the project structure defined in Section 10 unless the user has approved a different structure.
6. Use the technology stack defined in Section 5 — do not substitute disallowed technologies.
7. Verify dependency compatibility before pinning versions.

### Code Rules

8. All source code identifiers must be in English.
9. All user-facing text must be in Vietnamese.
10. All domain models must use `dataclasses` with type hints.
11. All path operations must use `pathlib.Path`.
12. All logging must use the `logging` standard library.
13. Business logic must not be placed inside UI classes or event handlers.
14. OCR must not run on the UI thread.
15. Excel operations must not run on the UI thread.
16. Background threads must not update PySide6 widgets directly — use signals.
17. The original image must never be modified.
18. The original workbook must be recoverable via backup.

### Security Rules

19. OCR results must never be written to Excel without human review.
20. Required low-confidence fields must be manually confirmed before export.
21. Missing values must never be guessed or invented.
22. Uploaded images must be validated using Pillow before being saved.
23. Session tokens must be generated with `secrets.token_urlsafe(32)` and compared with `secrets.compare_digest()`.
24. The upload server must not start automatically unless explicitly configured.
25. The server must stop when the application exits.
26. Sensitive OCR content must not appear in logs.
27. Error responses to the phone must not include stack traces or local paths.

### Testing Rules

28. All business services must be testable without PySide6.
29. PaddleOCR must be mocked in unit tests.
30. Use temporary directories and temporary workbooks in tests.
31. Test both success and failure paths.

### Documentation Rules

32. After each phase, list all files created or modified.
33. After each phase, explain how to run the relevant tests.
34. After each phase, state assumptions and remaining risks.
35. After each phase, stop and wait for user approval.

---

## 37. Definition of Done

The application is considered complete when all of the following conditions are met:
- DocumentProfile and ExcelMappingProfile are separate.
- Mapping profiles are reusable.
- AI is not required during normal processing.
- Mapping profiles require user approval.
- Current workbook structure is validated.
- Multiple worksheets and tables are handled safely.
- Moved columns are resolved by header.
- Exactly one existing row must match.
- Only approved missing cells are filled.
- Existing non-empty values remain unchanged.
- Matching keys remain unchanged.
- Formulas remain unchanged.
- Merged cells are handled safely.
- Conflicts are displayed instead of overwritten.
- Low-confidence values require review.
- Stale workbook changes are detected.
- A backup is created.
- A temporary workbook is verified.
- Excel data types are preserved.
- Sensitive values are not logged.
- Existing relevant tests remain required.
- New mapping and completion tests are included.


### Skill

- [ ] The `SKILL.md` file exists and accurately describes the complete workflow, architecture, and rules.

### Mobile Upload

- [ ] A phone can upload a valid document photo over a trusted local network.
- [ ] The upload requires a valid, non-expired temporary session token.
- [ ] Invalid file content (wrong format, too large, corrupted) is rejected.
- [ ] Partial or in-progress files are not processed by InboxWatcher.
- [ ] The upload server stops when the application exits.

### Image Processing and OCR

- [ ] New finalized files are safely added to the processing queue.
- [ ] OCR runs outside the UI thread (in a background worker).
- [ ] The OCR model is initialized once and reused for subsequent calls.
- [ ] Image preprocessing profiles are configurable and applied correctly.
- [ ] The original image is never modified.

### Extraction and Review

- [ ] Extracted data appears in an editable review form with confidence scores.
- [ ] Low-confidence required fields are highlighted and require manual confirmation.
- [ ] Invalid fields are highlighted and block export.
- [ ] Missing values are not invented — empty fields require review.
- [ ] The user can edit, correct, and re-validate any field.

### Excel Export

- [ ] The target Excel workbook is backed up before modification.
- [ ] Data is saved through a temporary file that is verified before replacing the destination.
- [ ] Dates are written as real Excel date values with correct number format.
- [ ] Quantities are written as Excel numbers, not text.
- [ ] Product-code leading zeros are preserved.
- [ ] Duplicate document numbers are detected and reported.
- [ ] The original workbook is preserved unchanged if any export step fails.

### Security and Privacy

- [ ] Sensitive OCR content is not exposed in log files.
- [ ] Session tokens are not logged.
- [ ] The upload server binds to a local interface, not `0.0.0.0` by default.
- [ ] Error responses to the phone do not include stack traces or local paths.
- [ ] No data is sent to cloud services.

### Testing

- [ ] Automated tests cover all 39 required unit test cases.
- [ ] Automated tests cover all 4 required integration test cases.
- [ ] All tests pass.
- [ ] Business services are tested without importing PySide6.

### Packaging and Documentation

- [ ] The application can be packaged as a Windows executable using PyInstaller.
- [ ] `README.md` documentation matches the actual implementation.
- [ ] `README.md` includes all required sections (security model, setup, troubleshooting, limitations).
- [ ] Configuration files are validated at startup with actionable error messages.

---

## Future Phase: Excel Automation (Not in MVP)

In a future phase, the application will add automated Excel integration:
- Row matching against existing Excel records using configurable matching keys.
- Cell-state classification (missing, already complete, conflict).
- Change preview with proposed actions per field before any Excel modification.
- Missing-cell completion with openpyxl — backup, atomic save, correct data types, leading-zero preservation.
- Conflict display without automatic overwrite.
- Stale-data protection.
- Merged-cell and formula-cell safety.
