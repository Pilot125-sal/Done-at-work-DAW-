import pandas as pd

# def export_monthly(data, month):
#     df = pd.DataFrame(data)
#     filename = f"choir_payments_{month}.xlsx"
#     df.to_excel(filename, index=False)
#     return filename

def export_monthly(data, month):
    """Export all payments for a given month to Excel"""
    df = pd.DataFrame(data, columns=["ID", "Member", "Amount", "Month", "Note"])
    df_month = df[df["Month"] == month]
    filename = f"choir_payments_{month}.xlsx"
    df_month.to_excel(filename, index=False)
    return filename

def export_member(data, member_name):
    """Export all payments for a single member"""
    df = pd.DataFrame(data, columns=["ID", "Member", "Amount", "Month", "Note"])
    df_member = df[df["Member"] == member_name]
    filename = f"{member_name}_payments.xlsx"
    df_member.to_excel(filename, index=False)
    return filename