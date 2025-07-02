# TradeTracker 📈

**TradeTracker** is a full-stack Django web application that helps users track their trades and view key statistics. Users can log in to add, update, and delete trades, and view a personalized dashboard with insights such as win rate, average return, and holding time — all with custom date filtering.

## Features

- User authentication (registration, login, logout)
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

## User Stories

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

