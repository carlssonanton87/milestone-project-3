# TradeTracker 📈

**TradeTracker** is a full-stack Django web application that helps users track their trades and view key statistics. Users can log in to add, update, and delete trades, and view a personalized dashboard with insights such as win rate, average return, and holding time — all with custom date filtering.

## Features

- User authentication (registration, login, logout)
- Landing page with app description
- Add/Edit/Delete trades with form validation
- Dashboard with:
  - Total trades
  - Win rate %
  - Average return %
  - Average holding time (days)
  - Open vs closed trade count
- Date-based filtering:
  - Preset buttons (Today, Last Week, etc.)
  - Interactive date slider (instant filtering)
- Responsive Bootstrap layout
- Custom 404 and 500 error pages for user-friendly error handling


## UX

### Flash Messages
TradeTracker uses Django’s messages framework, rendered as non-blocking **Bootstrap toasts** with the following characteristics:

- **Location:** Toasts appear stacked at the top-right corner of every page (`.toast-container` in `base.html`).
- **ARIA live region:** Wrapped with `role="status"`, `aria-live="polite"` and `aria-atomic="true"` so screen-readers announce them immediately.
- **Auto-dismiss:** Success toasts auto-close after 4 seconds via a small initialization script.
- **Undo support:** Delete actions include an **Undo** link in the toast, which restores the most recently deleted trade.
- **Customization:** All styling and behavior is defined in `templates/trades/base.html` and can be adjusted there.


### User Stories

- As a trader, I want to log each trade with key details (entry/exit date, return %, etc.)
- As a user, I want to filter trades by time period
- As a user, I want to see a dashboard with visual statistics
- As a user, I want a simple and intuitive UI on both desktop and mobile

## Data Model

**Trade**
- user (FK to User)
- ticker (CharField)
- entry_date (DateField)
- exit_date (DateField)
- entry_price (Decimal)
- exit_price (Decimal)
- outcome (Choice: win/loss/open)

Methods:
- `return_percent()`
- `holding_days()`

## Technologies Used

- Python 3
- Django 4
- SQLite3 (development), Postgres (production)
- Bootstrap 5
- noUiSlider (JS date range slider)
- Moment.js
- GitHub Codespaces

## Testing

We have included all the testing details in a separate document → [TESTING.md](TESTING.md).

## Bugs & Fixes

| Bug                                                                                     | Fix                                                                                     |
|-----------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| **Missing `crispy_forms`** – startup error: “No module named ‘crispy_forms’”            | Removed `crispy_forms` from `INSTALLED_APPS` (or install `django-crispy-forms` package) |
| **URL reverse lookup failures** – templates error “Reverse for ‘trade_list’ not found” | Harmonized view names and URL patterns (`trade_list`, etc.) and updated all template links |
| **Indentation error** – “SyntaxError: ‘return’ outside function”                        | Fixed indentation so each `return` resides inside its corresponding view function       |
| **Missing form template** – “TemplateDoesNotExist: bootstrap5/uni_form.html”            | Installed/configured `django-bootstrap5` or reverted to default Django form templates   |
| **Decimal serialization** – “TypeError: Decimal is not JSON serializable”               | Cast `Decimal` values to `float` (or `str`) before passing into JSON/script tags        |
| **Unbound `context` variable** – “UnboundLocalError: cannot access local variable ‘context’” | Defined the `context = {...}` dictionary before any `context.update()` or `return` calls  |
|


## Error Handling

TradeTracker includes custom error pages for a polished user experience:

- **404 – Page Not Found**: Displayed when a user visits an invalid URL.
- **500 – Server Error**: Displayed when something goes wrong on the server side.

To view these, set `DEBUG = False` in `settings.py` and visit a broken link or trigger an exception.



## Deployment

The app was deployed to [Heroku / Render / Railway] using:

- `gunicorn` for WSGI server
- `whitenoise` for static file handling
- `dj_database_url` for database switching
- Environment variables for secret keys

## Credits

- Bootstrap 5 components
- noUiSlider: https://refreshless.com/nouislider/
- Django documentation


## Agile Development

### Epics, User Stories & Tasks

| Epic | User Story | Task(s) |
|------|------------|---------|
| **User Management** | As a user, I want to register and log in securely, so I can access and manage my trades. | - Set up Django authentication<br>- Configure login/logout views<br>- Style login/register templates |
| **Trade Logging** | As a user, I want to add a new trade with key details, so I can keep track of my trading activity. | - Create `Trade` model<br>- Build add trade form<br>- Set up create view & template |
| | As a user, I want to edit or delete trades, so I can correct mistakes or remove irrelevant ones. | - Add edit view + form<br>- Add delete view with confirmation<br>- Protect views with user check |
| **Dashboard & Insights** | As a user, I want to see my total trades and win rate. | - Write logic for win rate and total count<br>- Display stats in dashboard template |
| | As a user, I want to see average return %, holding time, and open/closed trades. | - Add calculations in views<br>- Format numbers and show in template |
| **UX & Filtering** | As a user, I want to filter trades by outcome or instrument. | - Add filter form (optional)<br>- Build filtering logic into list view |
| **Feedback & Confirmation** | As a user, I want confirmation when I add, edit, or delete a trade. | - Add Django messages to views<br>- Display flash messages in base template |
| **Security** | As a user, I want to be sure only I can see/edit my trades. | - Add login-required decorators<br>- Filter queryset by logged-in user |

