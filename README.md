# milestone-project-3

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

