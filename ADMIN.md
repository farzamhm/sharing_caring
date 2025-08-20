# Admin Dashboard & Tools

This document describes the administrative tools for monitoring and managing the Neighborhood Food Sharing Platform.

## Web Dashboard

Access the web-based admin dashboard at: `http://localhost:8000/admin/`

### Features:
- **Platform Overview**: Active users, food posts, exchange success rates
- **System Health**: Real-time health monitoring and alerts
- **Active Alerts**: Problematic exchanges requiring attention
- **Quick Actions**: Direct access to common admin tasks

### API Endpoints:
- `GET /admin/dashboard` - Summary data for dashboard
- `GET /admin/stats/platform?days=30` - Platform-wide statistics
- `GET /admin/stats/building/{building_id}?days=30` - Building-specific stats
- `GET /admin/users/{user_id}/activity` - Detailed user activity
- `GET /admin/exchanges/problematic?days=7` - Exchanges needing attention
- `GET /admin/health` - System health check
- `POST /admin/exchanges/{exchange_id}/intervene` - Admin intervention

## CLI Tools

Run admin commands using the CLI tool:

```bash
python -m src.admin_cli --help
```

### Available Commands:

#### Platform Statistics
```bash
# Show 7-day platform stats
python -m src.admin_cli stats

# Show 30-day stats
python -m src.admin_cli stats --days 30
```

#### System Health Check
```bash
python -m src.admin_cli health
```

#### View Alerts
```bash
# Show problematic exchanges from last 3 days
python -m src.admin_cli alerts

# Look back 7 days
python -m src.admin_cli alerts --days 7
```

#### User Management
```bash
# View detailed user activity
python -m src.admin_cli user <user_id>
```

#### Exchange Management
```bash
# Cancel problematic exchange
python -m src.admin_cli exchange <exchange_id> cancel "Reported issue by user"

# Complete stuck exchange
python -m src.admin_cli exchange <exchange_id> complete "Manual completion"

# Reset exchange to pending
python -m src.admin_cli exchange <exchange_id> reset "System error - resetting"
```

#### Building Statistics
```bash
# Show building stats for 30 days
python -m src.admin_cli building <building_id>

# Custom time period
python -m src.admin_cli building <building_id> --days 14
```

#### System Cleanup
```bash
# Clean up expired posts and stale data
python -m src.admin_cli cleanup

# Look back 48 hours
python -m src.admin_cli cleanup --hours 48
```

## Monitoring

### Key Metrics to Watch:
- **Active User Rate**: Should be >20% for healthy engagement
- **Exchange Success Rate**: Should be >80% for good user experience
- **System Health Score**: Should be >80 for stable operation
- **Problematic Exchanges**: Should have <5 outstanding issues

### Alert Types:
- **Overdue Exchanges**: Confirmed but past pickup time
- **Long Pending**: Exchanges pending >24 hours
- **System Health**: Database/service issues

### Common Admin Tasks:

1. **Daily Monitoring**:
   - Check dashboard for alerts
   - Review success rates and engagement
   - Handle any problematic exchanges

2. **Weekly Review**:
   - Review platform statistics
   - Check building-level engagement
   - Identify top contributors

3. **Issue Resolution**:
   - Use CLI tools for quick interventions
   - Contact users for complex issues
   - Document recurring problems

### Database Access

For direct database queries, use your preferred PostgreSQL client with the connection details from your environment configuration.

### Logs

Application logs are structured using `structlog` and include:
- API request/response logging
- Service-level operation logs
- Error tracking with correlation IDs
- Performance metrics

Check your configured log destination (stdout in development, files in production).

## Security Notes

- Admin endpoints should be protected with authentication in production
- CLI tools require direct database access
- Monitor admin actions for security compliance
- Regularly review user permissions and access patterns