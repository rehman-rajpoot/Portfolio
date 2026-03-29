# Web Through Python - Portfolio Project Structure

## 📁 Project Overview

This is a professional portfolio website built with Flask and modern web technologies.

```
WEB THROUGH PYTHON/
├── app.py                          # Main Flask application
├── static/                         # Static assets
│   ├── css/                       # Stylesheets (organized by page)
│   │   ├── base.css              # Base/global styles
│   │   ├── index.css             # Home page styles
│   │   ├── projects.css          # Projects page styles
│   │   ├── scholarships.css      # Scholarships page styles
│   │   └── contact.css           # Contact page styles
│   └── style.css                  # Legacy stylesheet (can be archived)
├── templates/                      # HTML templates
│   ├── base.html                 # Base template (inherited by all pages)
│   ├── index.html                # Home page
│   ├── projects.html             # Projects portfolio page
│   ├── scholarships.html         # Scholarships & awards page
│   └── contact.html              # Contact page
├── images/                         # Image assets (WebP format)
│   ├── README.md                 # Image guidelines and conversion script
│   ├── profile/                  # Profile pictures
│   ├── projects/                 # Project screenshots
│   ├── portfolio/                # General portfolio images
│   └── icons/                    # Custom icons
└── README.md                       # Project documentation (this file)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. Navigate to the project directory:
```bash
cd "c:\Users\rehma\OneDrive\Desktop\Something new to me\Web through Python"
```

2. Install Flask:
```bash
pip install flask
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and visit:
```
http://localhost:5000
```

## 📄 File Descriptions

### App.py
Main Flask application containing:
- Route definitions (/, /projects, /scholarships, /contact)
- Portfolio data (projects, scholarships, skills)
- Contact form handling

### CSS Files

**base.css**
- Global styles for body, navbar, footer
- Scrollbar customization
- Page transitions and animations
- Responsive design basics

**index.css**
- Hero section styling
- Profile circle animation
- Stats section
- Skills grid
- Call-to-action section

**projects.css**
- Projects grid layout
- Project card hover effects
- Filter button styles
- Tech badge styling

**scholarships.css**
- Timeline layout
- Scholarship cards
- Summary statistics
- Responsive timeline adjustments

**contact.css**
- Contact form styling
- Contact info cards
- Form validation messages
- Social links section

### HTML Templates

**base.html**
- Bootstrap navigation bar
- Footer with social links
- Page content wrapper
- Script includes

**index.html**
- Hero section with profile
- Technical skills showcase
- Statistics display
- Call-to-action buttons

**projects.html**
- Project portfolio grid
- Filter buttons for categories
- Project cards with tech stack
- Links to project details

**scholarships.html**
- Timeline view of awards
- Scholarship statistics
- Honor badges
- Achievement information

**contact.html**
- Contact information display
- Contact form
- Social media links
- Map or location information

## 🎨 Design System

### Color Palette
- **Primary**: #38bdf8 (Cyan)
- **Primary Light**: #0ea5e9
- **Background**: #0f172a (Dark Navy)
- **Surface**: #1e293b
- **Text Primary**: #f1f5f9
- **Text Secondary**: #cbd5e1
- **Text Tertiary**: #94a3b8

### Typography
- Font Family: 'Inter', 'Segoe UI', sans-serif
- Weights: 500, 600, 700, 800
- Base Size: 16px

### Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## 🔧 Customization Guide

### Adding a New Page

1. Create HTML template in `templates/`:
```html
{% extends 'base.html' %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/newpage.css') }}">
{% endblock %}

{% block content %}
<!-- Your content here -->
{% endblock %}
```

2. Create CSS file in `static/css/newpage.css`

3. Add route in `app.py`:
```python
@app.route('/newpage')
def newpage():
    return render_template('newpage.html')
```

### Adding Projects

Edit the `portfolio_data['projects']` list in `app.py`:
```python
{
    'title': 'Project Name',
    'description': 'Brief description',
    'tech': ['Python', 'Flask', 'HTML'],
    'link': '#'
}
```

### Updating Contact Information

Modify the contact route and form handler in `app.py` to match your details.

## 📱 Responsive Design

All pages are optimized for:
- **Mobile**: Full stack layout, touch-friendly buttons
- **Tablet**: 2-column layouts where applicable
- **Desktop**: 3-4 column grids, full width layouts

## 🎯 Performance Optimization

### WebP Images
- All images should be converted to WebP format
- Use the conversion script in `images/README.md`

### CSS Organization
- Separate CSS files reduce per-page load
- Only loaded CSS is transferred to the browser

### Minification (Optional)
Consider using tools for production:
- CSS Minifier: https://minifier.org/
- JavaScript Minifier: https://javascript-minifier.com/

## 🔗 Dependencies

```
Flask==2.3.x
Jinja2==3.1.x
Bootstrap 5.3.0 (CDN)
Font Awesome 6.4.0 (CDN)
```

## 🤝 Contributing

To add new features:
1. Create feature branch
2. Make changes
3. Test locally
4. Commit with clear messages

## 📝 License

This portfolio template is open for personal use.

## 📞 Support

For issues or questions, refer to:
- Flask Documentation: https://flask.palletsprojects.com/
- Bootstrap Documentation: https://getbootstrap.com/docs/5.3/
- Font Awesome: https://fontawesome.com/

---

**Last Updated**: March 15, 2026
