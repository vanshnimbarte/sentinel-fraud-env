# Fraud Risk Level Categorization (3 Levels per Fraud Type)
## Plan Steps

### 1. Update models.py [x]

### 2. Update tasks/*.py [x]
- Standardized ground_truth='FRAUD'
- Added CASE['risk_level'] = 'EASY|MEDIUM|HARD'

### 3. Update environment.py

### 4. Update inference.py [x]
- Prompt updated for risk reasoning

### 5. Test & Deploy [x]

**Progress:**
- [x] 1. models.py
- [x] 2. tasks/*.py
- [x] 3. environment.py (added dynamic/static risk_level on RULE FRAUD, simplified rulings)
