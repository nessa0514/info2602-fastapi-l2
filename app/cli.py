import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select, or_
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command() # exercise 3: Modify all the existing cli commands and add help statements for all arguments and documentation for all the functions
def get_user(username: str):
    """
    Retrieve a single user by their username.
    """

    with get_session() as db:

        user = db.exec(
            select(User).where(User.username == username)
        ).first()

        if not user:
            print(f"{username} not found!")
            return

        print(user)

@cli.command() # exercise 3: Modify all the existing cli commands and add help statements for all arguments and documentation for all the functions
def get_all_users():
    """
    Retrieve and display all users in the database.
    """

    with get_session() as db:

        users = db.exec(select(User)).all()

        if not users:
            print("No users found")
            return

        for user in users:
            print(user)

@cli.command()
def change_email(username: str, new_email:str):
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command()
def create_user(username: str, email:str, password: str):
    with get_session() as db: # Get a connection to the database
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback() #let the database undo any previous steps of a transaction
            #print(e.orig) #optionally print the error raised by the database
            print("Username or email already taken!") #give the user a useful message
        else:
            print(newuser) # print the newly created user

@cli.command()
def delete_user(username: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')

# exercise 1: Create a cli command that allows you to find a user using a partial match of their email OR username.
@cli.command()
def search_user(query: str):
    """
    Search for users by partial username OR email match.
    """

    with get_session() as db:

        results = db.exec(
            select(User).where(
                or_(
                    User.username.contains(query),
                    User.email.contains(query)
                )
            )
        ).all()

        if not results:
            print(f"No users found matching '{query}'")
            return

        for user in results:
            print(user)

# exercise 2: Create cli command that allows you to list the first N users of the database to be used by a paginated table. The command should accept 2 arguments limit and offset and return the appropriate result. limit should be defaulted to 10 and offset should be defaulted to 0
@cli.command()
def list_users(
    limit: int = typer.Argument(10, help="Number of users to return"),
    offset: int = typer.Argument(0, help="Number of users to skip")
):
    """
    List users with pagination support.
    """
    with get_session() as db:
        users = db.exec(
            select(User)
            .offset(offset)
            .limit(limit)
        ).all()

        if not users:
            print("No users found")
            return

        for user in users:
            print(user)

if __name__ == "__main__":
    cli()