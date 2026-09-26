from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from langchain_openai import ChatOpenAi
import os

from extensions import db
from models import User, Expense, Category, Group, GroupMember, ExpenseSplit

load_dotenv()

app = Flask(__name__)

llm=ChatOpenAi(
    model="gpt-4o-mini",
    temperature=0
)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

from models import User, Expense, Category, Group, GroupMember


@app.route("/")
def home():

    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not name or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful!")

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id

            flash("Login successful!")

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))
 
    user_id = session["user_id"]
    
    user = User.query.get(user_id)
    
    expenses=Expense.query.filter_by(user_id=user_id).all()

    total=sum(expense.amount for expense in expenses)

    if expenses:
      highest = max(expense.amount for expense in expenses)
    else:
      highest = 0
    expense_count=len(expenses)
    recent_expenses = Expense.query.filter_by(
        user_id=user_id
    ).order_by(
        Expense.date.desc()
    ).limit(5).all()

    return render_template("dashboard.html", user=user,
        total=total,
        expense_count=expense_count,
        recent_expenses=recent_expenses,
        highest=highest)


@app.route("/logout")
def logout():

    session.pop("user_id", None)

    flash("You have been logged out.")

    return redirect(url_for("login"))

@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():

    if "user_id" not in session:
        return redirect(url_for("login"))

    categories = Category.query.all()

    if request.method == "POST":

        amount = request.form.get("amount")
        description = request.form.get("description")
        date = request.form.get("date")
        category_id = request.form.get("category_id")

        if not amount or not description or not date or not category_id:
            flash("All fields are required.")
            return redirect(url_for("add_expense"))

        expense = Expense(
            amount=float(amount),
            description=description,
            date=date,
            user_id=session["user_id"],
            category_id=int(category_id)
        )

        db.session.add(expense)
        db.session.commit()

        flash("Expense added successfully!")

        return redirect(url_for("expenses"))

    return render_template(
        "add_expense.html",
        categories=categories
    )

@app.route("/expenses")
def expenses():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    search = request.args.get("search", "")

    category_id = request.args.get("category_id", "")

    categories = Category.query.all()

    expenses = Expense.query.filter_by(
        user_id=user_id
    ).all()

    if search:
        expenses = [
            expense
            for expense in expenses
            if search.lower() in expense.description.lower()
        ]

    if category_id:
        expenses = [
            expense
            for expense in expenses
            if str(expense.category_id) == category_id
        ]

    total = sum(expense.amount for expense in expenses)

    return render_template(
        "expenses.html",
        expenses=expenses,
        total=total,
        search=search,
        category_id=category_id,
        categories=categories
    )

@app.route("/edit-expense/<int:id>", methods=["GET", "POST"])
def edit_expense(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    expense=Expense.query.get(id)
    if not expense:
        flash("Expense not found.")
        return redirect(url_for("expenses"))

    if expense.user_id != session["user_id"]:
        flash("You are not allowed to edit this expense.")
        return redirect(url_for("expenses"))

    if request.method=="POST":
        expense.amount = request.form.get("amount")
        expense.description = request.form.get("description")
        expense.date = request.form.get("date")
        db.session.commit()
        flash("Expense updated successfully!")

        return redirect(url_for("expenses"))

    return render_template(
        "edit_expense.html",
        expense=expense
    )

@app.route("/delete-expense/<int:id>")
def delete_expense(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    expense=Expense.query.get(id)

    if not expense:
        flash("no expense found")
        return redirect(url_for("expenses"))

    if expense.user_id!=session["user_id"]:
        flash("you cannot edit this expense")
        return redirect(url_for("expenses"))

    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted successfully!")

    return redirect(url_for("expenses"))


@app.route("/create-group", methods=["GET", "POST"])
def create_group():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form.get("name")

        if not name:
            flash("Group name is required.")
            return redirect(url_for("create_group"))

        group = Group(
            name=name,
            created_by=session["user_id"]
        )

        db.session.add(group)
        db.session.commit()

        member = GroupMember(
            group_id=group.id,
            user_id=session["user_id"]
        )

        db.session.add(member)
        db.session.commit()

        flash("Group created successfully!")

        return redirect(url_for("groups"))

    return render_template("create_group.html")


@app.route("/groups")
def groups():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    memberships = GroupMember.query.filter_by(
        user_id=user_id
    ).all()

    groups = [
        membership.group
        for membership in memberships
    ]

    return render_template(
        "groups.html",
        groups=groups
    )


@app.route("/group/<int:group_id>/add-member", methods=["GET", "POST"])
def add_member(group_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    group = Group.query.get_or_404(group_id)

    if request.method == "POST":

        email = request.form.get("email")

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash("User not found.")

            return redirect(
                url_for(
                    "add_member",
                    group_id=group_id
                )
            )

        existing_member = GroupMember.query.filter_by(
            group_id=group_id,
            user_id=user.id
        ).first()

        if existing_member:

            flash("User is already a member.")

            return redirect(
                url_for(
                    "add_member",
                    group_id=group_id
                )
            )

        member = GroupMember(
            group_id=group_id,
            user_id=user.id
        )

        db.session.add(member)
        db.session.commit()

        flash("Member added successfully!")

        return redirect(
            url_for(
                "group_details",
                group_id=group_id
            )
        )

    return render_template(
        "add_member.html",
        group=group
    )


@app.route("/group/<int:group_id>")
def group_details(group_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    group = Group.query.get_or_404(group_id)

    members = GroupMember.query.filter_by(
        group_id=group_id
    ).all()

    expenses = Expense.query.filter_by(
        group_id=group_id
    ).all()

    return render_template(
        "group_details.html",
        group=group,
        members=members,
        expenses=expenses
    )


@app.route(
    "/group/<int:group_id>/add-expense",
    methods=["GET", "POST"]
)
def add_group_expense(group_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    group = Group.query.get_or_404(group_id)

    members = GroupMember.query.filter_by(
        group_id=group_id
    ).all()

    if request.method == "POST":

        amount = request.form.get("amount")
        description = request.form.get("description")
        date = request.form.get("date")

        if not amount or not description or not date:

            flash("All fields are required.")

            return redirect(
                url_for(
                    "add_group_expense",
                    group_id=group_id
                )
            )

        amount = float(amount)

        splits = []

        total_split = 0

        for member in members:

            split_amount = request.form.get(
                f"amount_{member.user_id}"
            )

            if not split_amount:

                flash(
                    f"Enter amount for {member.user.name}."
                )

                return redirect(
                    url_for(
                        "add_group_expense",
                        group_id=group_id
                    )
                )

            split_amount = float(split_amount)

            if split_amount < 0:

                flash("Amount cannot be negative.")

                return redirect(
                    url_for(
                        "add_group_expense",
                        group_id=group_id
                    )
                )

            total_split += split_amount

            splits.append({
                "user_id": member.user_id,
                "amount": split_amount
            })

        if round(total_split, 2) != round(amount, 2):

            flash(
                f"Split amounts must equal ₹{amount}. "
                f"You entered ₹{total_split}."
            )

            return redirect(
                url_for(
                    "add_group_expense",
                    group_id=group_id
                )
            )

        expense = Expense(
            amount=amount,
            description=description,
            date=date,
            user_id=session["user_id"],
            category_id=1,
            group_id=group_id
        )

        db.session.add(expense)
        db.session.commit()

        for split in splits:

            expense_split = ExpenseSplit(
                expense_id=expense.id,
                user_id=split["user_id"],
                amount=split["amount"]
            )

            db.session.add(expense_split)

        db.session.commit()

        flash("Group expense added successfully!")

        return redirect(
            url_for(
                "group_details",
                group_id=group_id
            )
        )

    return render_template(
        "add_group_expense.html",
        group=group,
        members=members
    )


@app.route("/expense/<int:expense_id>/splits")
def expense_splits(expense_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    expense = Expense.query.get_or_404(expense_id)

    splits = ExpenseSplit.query.filter_by(
        expense_id=expense_id
    ).all()

    return render_template(
        "expense_splits.html",
        expense=expense,
        splits=splits
    )

@app.route("/ai-assistant", methods=["GET", "POST"])
def ai_assistant():
    if "user_id" not in session:
        return redirect(url_for("login"))

    answer=""
    question=""

    if request.method=="POST":
        question=request.form.method("question")

    if not question:
            flash("Please enter a question.")
            return redirect(url_for("ai_assistant"))

    expenses=Expense.query.filter_by(user_id=session["user_id"]).all()

    expense_data=[]
    for expense in expenses:
         expense_data.append({
                "amount": expense.amount,
                "description": expense.description,
                "date": expense.date,
                "category": expense.category.name
            })
    prompt = f"""
You are an expense management assistant.

Answer the user's question using ONLY the expense data provided below.

Expense data:
{expense_data}

User question:
{question}

Rules:
- Do not invent expenses or amounts.
- If the information is not available, say that you don't have enough data.
- Give a clear and simple answer.
"""

    res=llm.invoke(prompt)
    answer=res.content()

    return render_template(
        "ai_assistant.html",
        answer=answer,
        question=question
    )

        



if __name__ == "__main__":
    with app.app_context():

        db.create_all()

        if Category.query.count() == 0:
            categories = [
                Category(name="Food"),
                Category(name="Travel"),
                Category(name="Shopping"),
                Category(name="Bills"),
                Category(name="Medical"),
                Category(name="Fees"),
                Category(name="Study"),
                Category(name="Other")
            ]

            db.session.add_all(categories)
            db.session.commit()

    app.run(debug=True)