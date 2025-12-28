# Quick Start Guide

## ⚠️ IMPORTANT: Always Use Virtual Environment

The error `ModuleNotFoundError: No module named 'rest_framework'` occurs when you run Python without activating the virtual environment.

## Solution

### Option 1: Activate Virtual Environment (Recommended)

```bash
cd /Users/beryakoc/Desktop/muz
source venv/bin/activate  # This activates the virtual environment
python manage.py runserver
```

You should see `(venv)` in your terminal prompt when it's activated.

### Option 2: Use the Helper Script

```bash
cd /Users/beryakoc/Desktop/muz
./run.sh
```

### Option 3: Install Packages Globally (Not Recommended)

If you want to use system Python (not recommended):

```bash
pip3 install -r requirements.txt
python3 manage.py runserver
```

## Verify Virtual Environment is Active

After running `source venv/bin/activate`, you should see:
- `(venv)` prefix in your terminal prompt
- Running `which python` should show: `/Users/beryakoc/Desktop/muz/venv/bin/python`

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'rest_framework'"
**Solution**: You're not using the virtual environment. Run `source venv/bin/activate` first.

### Issue: "venv/bin/activate: No such file or directory"
**Solution**: The virtual environment wasn't created. Run:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Packages not found even with venv activated
**Solution**: Reinstall packages:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Step-by-Step First Time Setup

```bash
# 1. Navigate to project directory
cd /Users/beryakoc/Desktop/muz

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install/verify packages
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Create superuser (optional)
python manage.py createsuperuser

# 6. Start server
python manage.py runserver
```

Then open http://127.0.0.1:8000/ in your browser.


