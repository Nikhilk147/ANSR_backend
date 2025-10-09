from core.setup import DB

def limit_checker(id):
    db = DB
    alert_msg = ""

    #daily 
    daily_limit = db.get_daily_limit(id)
    daily_sum = db.get_daily_sum(id)
    if daily_sum >= daily_limit: 
        alert_msg += f"Daily limit exceeded\n"
    elif daily_sum >= 0.8 * daily_limit:
        alert_msg += f"80% of daily limit reached\n"
    elif daily_sum >= 0.5 * daily_limit:
        alert_msg += f"50% of daily limit reached\n"
    
    #weekly
    weekly_limit = db.get_weekly_limit(id)
    weekly_sum = db.get_weekly_sum(id)
    if weekly_sum >= weekly_limit: 
        alert_msg += f"Weekly limit exceeded\n"
    elif weekly_sum >= 0.8 * weekly_limit:
        alert_msg += f"80% of weekly limit reached\n"
    elif weekly_sum >= 0.5 * weekly_limit:
        alert_msg += f"50% of weekly limit reached\n"

    #monthly
    monthly_limit = db.get_monthly_limit(id)
    monthly_sum = db.get_monthly_sum(id)
    if monthly_sum >= monthly_limit: 
        alert_msg += f"Monthly limit exceeded\n"
    elif monthly_sum >= 0.8 * monthly_limit:
        alert_msg += f"80% of monthly limit reached\n"
    elif monthly_sum >= 0.5 * monthly_limit:
        alert_msg += f"50% of monthly limit reached\n"

    #yearly
    yearly_limit = db.get_yearly_limit(id)
    yearly_sum = db.get_yearly_sum(id)
    if yearly_sum >= yearly_limit: 
        alert_msg += f"Yearly limit exceeded\n"
    elif yearly_sum >= 0.8 * yearly_limit:
        alert_msg += f"80% of yearly limit reached\n"
    elif yearly_sum >= 0.5 * yearly_limit:
        alert_msg += f"50% of yearly limit reached\n"


    if alert_msg == "":
        return "No alerts"
    return alert_msg