# from logging import root
from logging import root
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from turtle import clear
from unicodedata import name
from datetime import datetime
from logic.database import create_tables, add_payment, get_all_payments, get_all_payments_with_id, get_all_payments_with_id,edit_payment,allocate_and_save, delete_payment, delete_member
from logic.export_excel import export_monthly, export_member

def start_app():
    create_tables()
    
    # THIS IS THE ROOT WINDOW
    root = tk.Tk()
    root.title("Choir Dues Tracker")
    root.geometry("650x750") #width x height
    global ANNUAL_DUES
    ANNUAL_DUES = 60 # Annual dues per member
    

# --- Entries on the App UI ---
    # Title
    tk.Label(root, text="Choir Dues Management", font=("Arial", 20)).pack(pady=10)

    # --- Main container frame ---
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=5, pady=5)

    # --- Left side: inputs + listbox ---
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0,5))

    # --- Right side: mini-dashboard ---
    dashboard_frame = tk.Frame(main_frame, bd=2, relief="groove", padx=5, pady=5)
    dashboard_frame.pack(side="right", fill="y")

    tk.Label(dashboard_frame, text="Mini Dashboard: Totals & Outstanding", font=("Arial", 10, "bold")).pack(pady=(0,5))
    dashboard_text = tk.Text(dashboard_frame, width=45, height=25, state="disabled", bg="#f9f9f9")
    
    dashboard_text.pack(fill="y")
    dashboard_text.tag_configure("paid", foreground="green") #color coding for dashboard
    dashboard_text.tag_configure("owing", foreground="red")
    dashboard_text.tag_configure("month_paid", foreground="blue")
    dashboard_text.tag_configure("month_unpaid", foreground="gray")
    dashboard_frame.pack_configure(pady=5)
    

    year_var = tk.StringVar(value=str(datetime.now().year)) # Default to current year

    tk.Label(dashboard_frame, text="Year").pack()#label for year dropdown, just more ui friendly
    year_dropdown = ttk.Combobox(
        dashboard_frame,
        textvariable=year_var,
        values=[str(y) for y in range(2024, 2039)],
        width=8,
        state="readonly"
    )
    year_dropdown.pack(pady=2)


    def update_dashboard():
        # Dashboard text
        dashboard_text.config(state="normal")
        dashboard_text.delete("1.0", tk.END)

        payments = get_all_payments_with_id()
        
        # Organize payments per member
        member_totals = {}
        member_months = {} # to track months paid per member
        for _, member, amount, month, note in payments:
            member_totals[member] = member_totals.get(member, 0) + (amount or 0)
            member_months.setdefault(member, set()).add(month)


        # months_of_year = [f"{str(m).zfill(2)}-2026" for m in range(1,13)]  # Example year ---reworked below on 20.01.2026 to make year dynamic based on dropdown selection
        selected_year = year_var.get()
        months_of_year = [f"{str(m).zfill(2)}-{selected_year}" for m in range(1,13)]#dynamic year based on dropdown selection
        year_dropdown.bind("<<ComboboxSelected>>", lambda e: update_dashboard())


        for member, total_paid in member_totals.items():
            outstanding = ANNUAL_DUES - total_paid
            
            tag_name = f"member_{member.replace(' ', '_')}"

            # dashboard_text.insert(tk.END, f"{member}: Paid €{total_paid:.2f} | ",)
            # dashboard_text.tag_bind(member, "<Button-1>", lambda e, m=member: highlight_member(m))

            start_index = dashboard_text.index(tk.END)
            dashboard_text.insert(tk.END, f"{member}: Paid €{total_paid:.2f} | ")
            end_index = dashboard_text.index(tk.END)

            dashboard_text.tag_add(member, start_index, end_index) #tagging member name for binding
            dashboard_text.tag_bind(member, "<Button-1>", lambda e, m=member: highlight_member(m))#highlight member in listbox when clicked on dashboard

            if outstanding <= 0:
                dashboard_text.insert(tk.END, "✅ Paid\n", "paid")#color coding for dashboard used here
            else:
                dashboard_text.insert(tk.END, f"⚠ Owes €{outstanding:.2f}\n", "owing")#color coding for dashboard used here

            
            month_line = ""
            for month in months_of_year:
                if month in member_months.get(member, set()):
                        month_line += f"{month.split('-')[0]} "  # show month number
                        dashboard_text.insert(tk.END, f"{month.split('-')[0]} ", "month_paid")
                else:
                        dashboard_text.insert(tk.END, f"{month.split('-')[0]} ", "month_unpaid")
            dashboard_text.insert(tk.END, "\n\n")

        if not member_totals:
            dashboard_text.insert(tk.END, "No payments recorded yet")
        dashboard_text.config(state="disabled")  
    update_dashboard() # Initial dashboard update, withoutit dashboard is blank

    def highlight_member(member_name):
        # Loop through listbox and select all lines belonging to that member
        listbox.selection_clear(0, tk.END)
        first_idx = None
        for idx, m in listbox_index_to_member.items():
            if m == member_name:
                listbox.selection_set(idx)
                if first_idx is None:
                    first_idx = idx
        if first_idx is not None:
            listbox.see(first_idx)

    button_frame = ttk.Frame(dashboard_frame) #button needs to associated with a value and thats what these lines here are for
    button_frame.pack(fill="y",padx=5, pady=5) #otherwise button will not appear in dashboard frame

    refresh_dashboard= tk.Button(
            button_frame,
            text="Refresh Dashboard",
            width=20,
            command=update_dashboard
        )
    refresh_dashboard.pack(padx=5, pady=5)

    # Member Name
    tk.Label(left_frame, text="Member Name (e.g. Bro XYZ)").pack()
    name_entry = tk.Entry(left_frame, width=30)
    name_entry.pack()

    # Month
    tk.Label(left_frame, text="Month (e.g. 03-2025)").pack()
    month_entry = tk.Entry(left_frame, width=30)
    month_entry.pack()

    # Amount
    tk.Label(left_frame, text="Amount Paid (€)").pack()
    amount_entry = tk.Entry(left_frame, width=30)
    amount_entry.pack()

    # Note
    tk.Label(left_frame, text="Note (optional) (e.g. paid for 3 months)").pack()
    note_entry = tk.Entry(left_frame, width=30)
    note_entry.pack()

    def highlight_member(member_name):
        listbox.selection_clear(0, tk.END)


    # Payments List
    listbox = tk.Listbox(left_frame,height=10, width=40)
    listbox.pack(pady=10)

    def refresh_list():
        global payments, payment_ids, listbox_index_to_id,listbox_index_to_member
        listbox_index_to_id = {}  # Mapping per every refresh & maps Listbox index to payment ID, prevents the wrong item in listbox from being selected, edited or deleted.
        listbox_index_to_member = {} #  maps Listbox index to member name
        current_index = 0 # Initialized to track current index in listbox
        listbox.delete(0, tk.END) # clear listbox
        payments = get_all_payments_with_id()
        payment_ids = [p[0] for p in payments] # extract IDs for deletion/editing

        # member_totals = {}  # track total per member    ------------"this was removed on 15.01.2026"
        # for p in payments:
        #     member_name , amount , month , note = p[1], p[2], p[3], p[4]
        #     listbox.insert(tk.END, f"{p[1]} | €{p[2]} | {p[3]} | {p[4]}")
        #     if p[1] in member_totals:
        #         member_totals[p[1]] += p[2]
        #     else:
        #         member_totals[member_name] = amount

    # Group payments by member
        members = {}
        for p in payments:
            id_, member, amount, month, note = p
            members.setdefault(member, []).append((id_, month, amount, note)) # group by member function

        # Display grouped view
        for member, entries in members.items():
            listbox.insert(tk.END, member)  # member name line
            listbox_index_to_member[current_index] = member  # ⭐ NEW on 19.01.2026: maps this line to the member name
            current_index += 1

            total = 0
            # Sort entries by month
            # for entry in sorted(entries, key=lambda x: x[1]): ------------" removed and reworked below on 15.01.2026 to show in order of months"
            #     id_, month, amount, note = entry
            for id_, month, amount, note in sorted(entries, key=lambda x: x[1]):
                if amount is None:
                    amount = 0
                listbox.insert(tk.END, f"   {month} - €{amount}  ({note})")
                listbox_index_to_id[current_index] = id_  # maps this line to the payment ID correctly
                listbox_index_to_member[current_index] = member  # ⭐ NEW on 19.01.2026: maps this line to the member name
                current_index+=1
                total += amount
            # Tracks total paid per member
            listbox.insert(tk.END, f"   TOTAL PAID: €{total}")
            current_index += 1

        # Display totals per member -------" removed and reworked below on 14.01.2026 to show in order of months"
        # listbox.insert(tk.END, "-----------------------------")
        # for member, total in member_totals.items():
        # listbox.insert(tk.END, f"Total paid by {member}: €{total}")

        # Just a separator (not a payment)
        listbox.insert(tk.END, "-" * 50) #thisis to separate entries at the very end
        current_index+=1


    # New member added + Payment added wizard UI on 19.01.2026"
    def new_payment():
        wizard = tk.Toplevel(root)
        wizard.title("New Payment")
        wizard.geometry("250x210")
        wizard.grab_set()  # modal window

        data = {
            "name": "",
            "amount": 0,
            "start_month": "",
            "end_month": "",
            "note": ""
        }

        frame = tk.Frame(wizard)
        frame.pack(expand=True, fill="both", padx=10, pady=8)

        def clear():
            for w in frame.winfo_children():
                w.destroy()

        # step 1: name
        def step_name():
                clear()
                tk.Label(frame, text="Enter member name").pack(pady=5)
                entry = tk.Entry(frame)
                entry.pack()

                def next_step():
                    if not entry.get().strip():
                        messagebox.showerror("Error", "Name required")
                        return
                    data["name"] = entry.get().strip()
                    step_amount()

                tk.Button(frame, text="Next", command=next_step).pack(pady=10)

        #step 2: amount
        def step_amount():
                clear()
                tk.Label(frame, text="Enter total amount paid (€)").pack(pady=5)
                entry = tk.Entry(frame)
                entry.pack()

                def next_step():
                    try:
                        amount = float(entry.get().strip())
                        if amount <= 0:
                            raise ValueError
                        data["amount"] = amount
                        step_months()
                    except ValueError:
                        messagebox.showerror("Error", "Valid amount required")
                tk.Button(frame, text="Back", command=step_name).pack(side="left", padx=5, pady=10)
                tk.Button(frame, text="Next", command=next_step).pack(side="right", padx=5, pady=10)
                
                #step 3: months
        def step_months():
                clear()
                tk.Label(frame, text="Enter start month (MM-YYYY)").pack(pady=5)
                start_entry = tk.Entry(frame)
                start_entry.pack()

                tk.Label(frame, text="Enter end month (MM-YYYY)").pack(pady=5)
                end_entry = tk.Entry(frame)
                end_entry.pack()

                tk.Label(frame, text="Enter note (optional)").pack(pady=5)
                note_entry = tk.Entry(frame)
                note_entry.pack()

                def finish():
                    start_month = start_entry.get().strip()
                    end_month = end_entry.get().strip()
                    note = note_entry.get().strip()
                    # Basic validation for month format
                    try:
                        datetime.strptime(start_month, "%m-%Y")
                        datetime.strptime(end_month, "%m-%Y")
                        data["start_month"] = start_month
                        data["end_month"] = end_month
                        data["note"] = note

                        # Use database allocation function to save payment
                        from logic.database import allocate_and_save #import add_payment_auto 
                        #add_payment_auto(data["name"], data["amount"], start_month=data["start_month"], monthly_due=5, note=data["note"])
                        allocate_and_save(
                                name= data["name"],
                                amount= data["amount"],
                                start_month= start_month,
                                end_month= end_month,
                                note= note,
                                monthly_due= 5
                                )
                        messagebox.showinfo("Success", f"Payment for {data['name']} saved and allocated")
                        wizard.destroy()
                        refresh_list()
                    except ValueError:
                        messagebox.showerror("Error", "Start month must be in MM-YYYY format")
                tk.Button(frame, text="Back", command=step_amount).pack(side="left", padx=5, pady=10)
                tk.Button(frame, text="Finish", command=finish).pack(side="right", padx=5, pady=10)
        step_name()



    # Save Payment
    def save_payment():
        name = name_entry.get()
        month = month_entry.get()
        amount = amount_entry.get()
        note = note_entry.get()

        if not name or not month or not amount:
            messagebox.showerror("Error", "Please fill all required fields")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return
        
        from logic.database import add_payment_auto
        add_payment_auto(name, amount, start_month=month,monthly_due=5, note=note)
        messagebox.showinfo("Success", f"Payment saved and allocated")

        name_entry.delete(0, tk.END)
        month_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
        note_entry.delete(0, tk.END)
        refresh_list()
        # update_dashboard()  # <-- keeps dashboard in sync with payments


    # additional buttons UI functions
    def delete_selected(): #delete selected payment/single entry
        try:
            index = listbox.curselection()[0]
            if index not in listbox_index_to_id:
                messagebox.showerror("Error", "Select a payment entry, not a total or member name")
                return
            payment_id = listbox_index_to_id[index]
            from logic.database import delete_payment, get_all_payments_with_id
            delete_payment(payment_id)
            refresh_list()
        except IndexError:
            messagebox.showerror("Error", "Select a payment first")

    def edit_selected():
        try:
            index = listbox.curselection()[0]
            if index not in listbox_index_to_id:
                messagebox.showerror("Error", "Select a valid payment line")
                return
            # payment = payments[index]
            # payment_id = payment[0]-- get payment id from mapping modified below on 19.01.2026

            payment_id = listbox_index_to_id[index]
            payment = [p for p in payments if p[0] == payment_id][0]

            name, month, amount, note = payment[1], payment[3], payment[2], payment[4]  # extract details added on 19.01.2026 to counter obsolete code below

            # Prefill entries
            name_entry.delete(0, tk.END)
            name_entry.insert(0, payment[1])
            month_entry.delete(0, tk.END)
            month_entry.insert(0, payment[3])
            amount_entry.delete(0, tk.END)
            amount_entry.insert(0, payment[2])
            note_entry.delete(0, tk.END)
            note_entry.insert(0, payment[4])

        # # Save button override  -- removed on 19.01.2026 due to obsolescence because of implementation of wizard, see above
        #     # from logic.database import edit_payment, get_all_payments_with_id
        #         edit_payment(payment_id, name_entry.get(), float(amount_entry.get()), month_entry.get(), note_entry.get())
        #         messagebox.showinfo("Success", "Payment updated")
        #         refresh_list()
        #         # Restore original save_payment button
        #         save_btn.config(command=save_payment)

        #     save_btn.config(command=save_edit)

        # Immediate save (no override) added on 19.01.2026
            edit_payment(payment_id, name, amount, month, note)
            refresh_list()

        except IndexError:
            messagebox.showerror("Error", "Select a payment first")

    def delete_allmember(): # Delete ALL selected payments for a specific member
        try:
            index = listbox.curselection()[0]

            # Must be a payment line
            if index not in listbox_index_to_id:
                messagebox.showerror(
                    "Error",
                    "Select one of the member's payment lines"
                )
                return

            payment_id = listbox_index_to_id[index]
            member_name = listbox_index_to_member[index]

            # Find the payment in memory
            payment = next(p for p in payments if p[0] == payment_id)
            member_name = payment[1]

            # Confirm
            confirm = messagebox.askyesno(
                "⚠️ Confirm Delete",
                f"Delete ALL payments for {member_name}\n\n  This cannot be undone.\n\n  Proceed??"
            )
            if not confirm:
                return

            from logic.database import delete_member
            delete_member(member_name)

            refresh_list()

        except IndexError:
            messagebox.showerror("Error", "Select a payment first")


    def export_monthly():
        from logic.export_excel import export_monthly
        month = month_entry.get()
        if not month:
            messagebox.showerror("Error", "Enter month to export")
            return
        export_monthly(get_all_payments_with_id(), month)
        messagebox.showinfo("Exported", f"Excel for {month} exported")

    def export_member():
        from logic.export_excel import export_member
        member = name_entry.get()
        if not member:
            messagebox.showerror("Error", "Enter member name to export")
            return
        export_member(get_all_payments_with_id(), member)
        messagebox.showinfo("Exported", f"Excel for {member} exported")

    # Buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=8)

    # new_btn = ttk.Button(button_frame,  text="New Payment", command=new_payment)
    # new_btn.pack(side=tk.LEFT, pady=2,padx=5)
  
    # editselect_btn=ttk.Button(button_frame, text="Edit Selected", command=edit_selected)
    # editselect_btn.pack(side=tk.LEFT, pady=2,padx=5)
      
    # save_btn = ttk.Button(button_frame,  text="Save Payment", command=save_payment)
    # save_btn.pack(side=tk.LEFT, pady=2,padx=5)

    # delete_btn =ttk.Button(button_frame, text="Delete Selected", command=delete_selected)
    # delete_btn.pack(side=tk.LEFT, pady=2,padx=5)

    # export_member_btn=ttk.Button(button_frame, text="Export Member", command=export_member)
    # export_member_btn.pack(side=tk.LEFT, pady=2,padx=5)

    # export_month_btn=ttk.Button(button_frame, text="Export Month", command=export_monthly)
    # export_month_btn.pack(side=tk.LEFT, pady=2,padx=5)

    # deleteallmember_btn=ttk.Button(button_frame, text="Delete Member & Payments", command=delete_allmember)
    # deleteallmember_btn.pack(side=tk.LEFT, pady=2,padx=5)


    ttk.Button(
            button_frame,
            text="New Payment",
            width=20,
            command=new_payment
        ).grid(row=0, column=0, padx=5, pady=5)
    
    ttk.Button(
        button_frame,
        text="Save Payment",
        width=20,
        command=save_payment
    ).grid(row=0, column=2, padx=5, pady=5)

    ttk.Button(
        button_frame,
        text="Edit Selected",
        width=20,
        command=edit_selected
    ).grid(row=0, column=1, padx=5, pady=5)

    ttk.Button(
        button_frame,
        text="Delete Selected",
        width=20,
        command=delete_selected
    ).grid(row=0, column=4, padx=5, pady=5)

    ttk.Button(
            button_frame,
            text="Export Member",
            width=20,
            command=export_member
        ).grid(row=1, column=0, padx=5, pady=15)
    ttk.Button(
            button_frame,
            text="Export Month",
            width=20,
            command=export_monthly
        ).grid(row=1, column=1, padx=5, pady=15)

    tk.Button(
        button_frame,
        text="⚠️ Delete Member",
        width=20,
        command=delete_allmember,
        bg="#d9534f",
        fg="white",
        activebackground="#c9302c",
        activeforeground="white"
    ).grid(row=1, column=2, padx=5, pady=15)

    refresh_list()
    root.mainloop()