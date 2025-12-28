# LO-Assessment-Grade Mapping Feature

## What Was Added

### 1. Data Model Extension
- **New Model**: `AssessmentLOContribution` (intermediate model)
  - Links Assessment to LearningOutcome with contribution percentage
  - Fields: `assessment`, `learning_outcome`, `contribution_percentage` (0-100%)
  - Unique constraint on (assessment, learning_outcome)
  
- **Updated Model**: `Assessment`
  - Changed `covered_LOs` ManyToManyField to use `through='AssessmentLOContribution'`
  - Now supports contribution percentages per LO

### 2. Calculation Logic Update
- **Updated Function**: `calculate_lo_score()` in `assessments/utils.py`
  - New formula: `LO_score = SUM( score_assessment * (w_assessment / 100) * (c_lo / 100) )`
  - Where:
    - `score_assessment` = student score (0-100)
    - `w_assessment` = assessment weight in course (0-100%)
    - `c_lo` = contribution percentage to this LO (0-100%)
  - Normalized to ensure result is between 0 and 100%
  - Handles cases where assessments measure multiple LOs with different contributions

### 3. Teacher Interface - LO Contribution Management
- **New View**: `manage_lo_contributions()` in `assessments/views.py`
  - URL: `/teacher/courses/<course_id>/assessments/<assessment_id>/lo-contributions/`
  - Allows teachers to:
    - Select which LOs an assessment measures
    - Assign contribution percentage to each LO (0-100%)
    - Validates that sum equals exactly 100%
  - Protected by `@teacher_required` decorator
  - Only accessible for courses taught by the teacher

- **New Template**: `templates/teacher/manage_lo_contributions.html`
  - Form with input fields for each LO
  - Real-time total percentage calculation (JavaScript)
  - Visual feedback when total ≠ 100%
  - Shows current contribution percentages

### 4. Updated Assessment Management
- **Updated View**: `manage_assessments()` in `assessments/views.py`
  - Now shows LO contributions for each assessment
  - Displays: "LO1 (30%), LO2 (70%)" format
  - Added "Manage LO Contributions" button for each assessment

- **Updated Template**: `templates/teacher/manage_assessments.html`
  - Shows LO contributions with percentages
  - Link to manage contributions for each assessment

## Files Modified

1. **assessments/models.py**
   - Added `AssessmentLOContribution` model
   - Updated `Assessment.covered_LOs` to use through model

2. **assessments/migrations/0002_assessmentlocontribution_and_more.py** (NEW)
   - Creates `AssessmentLOContribution` model
   - Removes old ManyToManyField
   - Adds new ManyToManyField with through model

3. **assessments/utils.py**
   - Updated `calculate_lo_score()` to use contribution percentages
   - New normalized calculation formula

4. **assessments/views.py**
   - Added `manage_lo_contributions()` view
   - Updated `manage_assessments()` to show contributions
   - Added validation for 100% sum requirement

5. **assessments/urls.py**
   - Added URL pattern for LO contributions management

6. **templates/teacher/manage_lo_contributions.html** (NEW)
   - Form interface for setting contribution percentages
   - JavaScript for real-time validation

7. **templates/teacher/manage_assessments.html**
   - Updated to show LO contributions
   - Added "Manage LO Contributions" button

## Rules & Validation

### Contribution Percentage Rules
1. **Sum Must Equal 100%**: For each assessment, sum of contribution percentages across all LOs must equal exactly 100%
2. **Range**: Each contribution percentage must be between 0 and 100%
3. **Validation**: 
   - Frontend: JavaScript real-time calculation
   - Backend: Server-side validation before saving
   - Error message if sum ≠ 100%

### Calculation Rules
1. **Normalization**: LO scores are normalized to ensure they never exceed 100%
2. **Multiple Assessments**: A single LO can be measured by multiple assessments
3. **Multiple LOs**: A single assessment can measure multiple LOs with different contributions
4. **No Negative Values**: All calculations ensure non-negative results

## Workflow

### Teacher Workflow
1. **Create Assessment**: Teacher creates assessment with weight percentage
2. **Set LO Contributions**: 
   - Click "Manage LO Contributions" for the assessment
   - Select which LOs the assessment measures
   - Assign contribution percentage to each LO
   - Ensure total equals 100%
   - Save
3. **Enter Scores**: Teacher enters student scores (existing functionality)
4. **View Results**: LO-based achievements are automatically calculated

### Student View
- Students see LO achievement percentages (calculated using new formula)
- No changes to student interface
- Calculations are transparent and automatic

## Backward Compatibility

- ✅ Existing assessment score entry continues to work
- ✅ Existing weighted course grade calculation unchanged
- ✅ Existing letter grade logic unchanged
- ✅ Migration is safe (removes old M2M, adds new with through)
- ⚠️ **Note**: Existing LO-assignment relationships (if any) will need to be recreated with contribution percentages

## API/Backend

- LO-based results are available via `get_student_course_data()` function
- Returns `lo_achievements` dictionary with LO codes and percentages
- Ready for frontend visualization (charts, graphs, etc.)

## Testing Checklist

- [ ] Create assessment
- [ ] Set LO contributions (sum = 100%)
- [ ] Verify validation prevents sum ≠ 100%
- [ ] Enter student scores
- [ ] Verify LO scores calculated correctly
- [ ] Verify LO scores never exceed 100%
- [ ] Verify student view shows correct LO achievements
- [ ] Test with multiple assessments measuring same LO
- [ ] Test with assessment measuring multiple LOs

