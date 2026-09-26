from extensions import db


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    expenses = db.relationship(
        "Expense",
        backref="user",
        lazy=True
    )


class Category(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    expenses = db.relationship(
        "Expense",
        backref="category",
        lazy=True
    )


class Expense(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    description = db.Column(
        db.String(200)
    )

    date = db.Column(
        db.String(20),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("category.id"),
        nullable=False
    )

    splits = db.relationship(
        "ExpenseSplit",
        backref="expense",
        lazy=True
    )

    group_id = db.Column(
    db.Integer,
    db.ForeignKey("group.id"),
    nullable=True
)


class Group(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    members = db.relationship(
        "GroupMember",
        backref="group",
        lazy=True
    )

    expenses = db.relationship(
    "Expense",
    backref="group",
    lazy=True
)

class GroupMember(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    group_id = db.Column(
        db.Integer,
        db.ForeignKey("group.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref="group_memberships"
    )

class ExpenseSplit(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    expense_id = db.Column(
        db.Integer,
        db.ForeignKey("expense.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    user = db.relationship(
        "User",
        backref="expense_splits"
    )