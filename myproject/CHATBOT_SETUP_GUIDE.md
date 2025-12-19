# 🤖 AI Chatbot Setup Guide - Google Gemini Integration

## ✅ What's Already Done

1. **Frontend Created** ✓
   - Modern circular chat button at bottom-right corner
   - Beautiful chat interface with animations
   - Typing indicators and message bubbles
   - Quick action buttons for common questions
   - Fully responsive design

2. **Backend API Created** ✓
   - Django view endpoint at `/api/chat/`
   - Google Gemini integration code
   - Animal-focused system prompt
   - Error handling

3. **Files Added** ✓
   - `static/css/ai_chatbot.css` - Modern chatbot styling
   - `static/js/ai_chatbot.js` - Frontend chatbot logic
   - `views.py` - Backend API with Gemini integration
   - `urls.py` - API route configured

---

## 🚀 Setup Steps (What You Need to Do)

### Step 1: Install Google Gemini Package

Open your terminal in the project directory and run:

```bash
pip install google-generativeai
```

Or install from the requirements file:

```bash
pip install -r chatbot_requirements.txt
```

---

### Step 2: Get Your Google Gemini API Key

1. **Go to Google AI Studio:**
   - Visit: https://makersuite.google.com/app/apikey
   - Or: https://aistudio.google.com/app/apikey

2. **Sign in with your Google account**

3. **Click "Create API Key"**
   - Choose "Create API key in new project" or select existing project
   - Copy the API key (it looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)

4. **Important:** Keep this key secure and don't share it publicly!

---

### Step 3: Add API Key to Django

Open `myproject/myproject/views.py` and find this line (around line 650):

```python
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
```

Replace it with your actual API key:

```python
GEMINI_API_KEY = "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # Your actual key
```

**Better Option (More Secure):**

Add to your environment variables or Django settings:

1. Create a `.env` file in your project root:
```
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

2. Install python-dotenv:
```bash
pip install python-dotenv
```

3. In `views.py`, change to:
```python
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

---

### Step 4: Test the Chatbot

1. **Start your Django server:**
```bash
python manage.py runserver
```

2. **Open your browser:**
   - Go to: http://localhost:8000/dashboard/

3. **Look for the chatbot:**
   - You'll see a purple circular button with 🐾 at the bottom-right corner
   - Click it to open the chat window

4. **Test with questions:**
   - "How do I care for a new puppy?"
   - "What should I feed my cat?"
   - "Signs of pet illness?"
   - "How to train my dog?"

---

## 🎨 Chatbot Features

### Visual Design
- ✨ Modern gradient purple theme
- 🔵 Circular floating button with pulse animation
- 💬 Smooth slide-up chat window
- 🎭 Beautiful message bubbles (user & bot)
- ⌨️ Typing indicator with animated dots
- 📱 Fully responsive (mobile, tablet, desktop)

### Functionality
- 🤖 Real AI responses using Google Gemini
- 🐾 Specialized in animal/pet topics
- 💡 Quick action buttons for common questions
- 📝 Message history tracking
- ⏰ Timestamps on messages
- 🔄 Auto-resizing input field
- ✅ CSRF protection

### Smart Features
- Only answers animal-related questions
- Provides practical pet care advice
- Recommends vet visits for emergencies
- Friendly and compassionate tone
- Uses emojis for better engagement

---

## 🔧 Troubleshooting

### Problem: "API key not configured" error
**Solution:** Make sure you replaced `YOUR_GEMINI_API_KEY_HERE` with your actual API key

### Problem: "Module not found: google.generativeai"
**Solution:** Install the package: `pip install google-generativeai`

### Problem: Chatbot button not showing
**Solution:** 
- Clear browser cache (Ctrl+Shift+R)
- Check if CSS and JS files are loaded in browser console
- Make sure you're on the dashboard page

### Problem: "Invalid API key" error
**Solution:** 
- Verify your API key is correct
- Check if API key has proper permissions
- Make sure you're using Gemini API (not other Google APIs)

### Problem: Slow responses
**Solution:** 
- This is normal for AI APIs (1-3 seconds)
- Check your internet connection
- Gemini free tier has rate limits

---

## 📊 API Usage & Limits

**Google Gemini Free Tier:**
- ✅ 60 requests per minute
- ✅ 1,500 requests per day
- ✅ Free forever for moderate use

**If you need more:**
- Upgrade to paid tier for higher limits
- Or implement rate limiting in your app

---

## 🎯 Customization Options

### Change Chatbot Name
In `ai_chatbot.js`, find:
```javascript
<h3>PetCare AI</h3>
```

### Change Colors
In `ai_chatbot.css`, modify:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Change System Prompt
In `views.py`, modify the `system_prompt` variable to change chatbot behavior

### Add More Quick Actions
In `ai_chatbot.js`, add more buttons in the `quick-actions` section

---

## 📞 Support

If you encounter issues:
1. Check browser console for errors (F12)
2. Check Django server logs
3. Verify API key is correct
4. Test API key at: https://aistudio.google.com/

---

## 🎉 You're All Set!

Once you add your API key, the chatbot will be fully functional and ready to help users with animal-related questions!

**Test it now:**
1. Add your API key to `views.py`
2. Run: `python manage.py runserver`
3. Visit: http://localhost:8000/dashboard/
4. Click the 🐾 button and start chatting!

Enjoy your AI-powered pet care assistant! 🐾🤖
