# LO-Centric UI Update

## What Was Changed

### UI/Input Flow Change Only
- **No data model changes**: All models remain unchanged
- **No calculation changes**: All formulas remain unchanged
- **Only presentation layer**: Changed how instructors view and enter data

## New Instructor Workflow

### Previous Flow (Assessment-Centric)
1. Teacher selects an assessment
2. Teacher assigns contribution percentages to multiple LOs
3. View: Assessment → LOs

### New Flow (LO-Centric) - PRIMARY INTERFACE
1. Teacher selects a course
2. Teacher navigates to "Manage Learning Outcomes"
3. Teacher selects a single LO
4. System displays all assessments for that course
5. Teacher assigns contribution percentages from each assessment to that LO
6. View: LO → Assessments

### Example
For **LO1**:
- Midterm 1 → 30%
- Midterm 2 → 40%
- Final → 30%
- **Total: 100%** ✓

## Files Added/Modified

### New Views
1. **`manage_lo_assessments()`** in `assessments/views.py`
   - LO-centric view for managing assessment contributions
   - URL: `/teacher/courses/<course_id>/los/<lo_id>/assessments/`
   - Takes `course_id` and `lo_id` (not `assessment_id`)
   - Shows all assessments, allows setting contributions to the selected LO

2. **`teacher_course_los()`** in `courses/views.py`
   - Lists all Learning Outcomes for a course
   - Shows contribution status for each LO
   - URL: `/teacher/courses/<course_id>/los/`

### New Templates
1. **`templates/teacher/course_los.html`** (NEW)
   - Lists all LOs for a course
   - Shows how many assessments contribute to each LO
   - Shows total contribution percentage (should be 100%)
   - Link to manage assessments for each LO

2. **`templates/teacher/manage_lo_assessments.html`** (NEW)
   - LO-centric interface
   - Shows selected LO at top
   - Lists all assessments for the course
   - Input fields for contribution percentage from each assessment
   - Real-time validation (sum must = 100%)
   - JavaScript for visual feedback

### Updated Templates
1. **`templates/teacher/courses.html`**
   - Added "Manage Learning Outcomes" button
   - Links to the new LO-centric interface

### URL Patterns
1. **`assessments/urls.py`**
   - Added: `manage_lo_assessments` route

2. **`courses/urls.py`**
   - Added: `teacher_course_los` route

## Data Model (Unchanged)

- **AssessmentLOContribution** model remains the same
- Fields: `assessment`, `learning_outcome`, `contribution_percentage`
- Relationship direction: Assessment → Learning Outcome (unchanged)
- Only the UI perspective changed, not the underlying structure

## Validation Rules (Unchanged)

1. **For a given LO**: Sum of contribution percentages from all assessments = 100%
2. **Range**: Each contribution percentage: 0-100%
3. **Multiple LOs**: A single assessment can contribute to multiple LOs
4. **Multiple Assessments**: A single LO can receive contributions from multiple assessments

## Calculation Logic (Unchanged)

- `calculate_lo_score()` function remains exactly the same
- Formula: `LO_score = SUM( score * (weight/100) * (contribution/100) )`
- Normalization logic unchanged
- All existing calculations continue to work

## Backward Compatibility

- ✅ Old assessment-centric view (`manage_lo_contributions`) still exists
- ✅ Both interfaces use the same data model
- ✅ Both interfaces can be used interchangeably
- ✅ No breaking changes
- ✅ Existing data remains valid

## User Experience

### Primary Workflow (New)
1. Teacher → Courses → Select Course
2. Click "Manage Learning Outcomes"
3. See list of LOs with contribution status
4. Click "Manage Assessments" for an LO
5. Set contribution percentages from each assessment
6. Save (validates sum = 100%)

### Alternative Workflow (Still Available)
1. Teacher → Courses → Select Course
2. Click "Manage Assessments"
3. Click "Manage LO Contributions" for an assessment
4. Set contribution percentages to multiple LOs
5. Save

Both workflows work with the same data and produce the same results.

## Key Points

- **No refactoring**: Only UI/input flow changed
- **No model changes**: Same AssessmentLOContribution model
- **No calculation changes**: Same formulas and logic
- **Dual interface**: Both LO-centric and assessment-centric views available
- **Same validation**: Sum must equal 100% (per LO in new view, per assessment in old view)
- **Same data**: Both views read/write to the same database tables

