def total_paid(payments):
    return sum(p["amount"] for p in payments)

def outstanding(total_due, paid):
    return total_due - paid

def total_paid_per_member(payments, member_name):
    """payments = list of tuples: (id, name, amount, month, note)"""
    return sum(p[2] for p in payments if p[1] == member_name)

def outstanding_balance(total_due, payments, member_name):
    paid = total_paid_per_member(payments, member_name)
    return total_due - paid