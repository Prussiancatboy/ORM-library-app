from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Author(db.Model):
    """This controls the author table"""
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"Author(id={self.id}, name='{self.name}', " \
               f"birth_date={self.birth_date}, " \
               f"date_of_death={self.date_of_death})"

    def __str__(self):
        return f"{self.name}"


# Define the Book model
class Book(db.Model):
    """This creates the book table"""
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'),
                          nullable=False)

    def __repr__(self):
        return f"Book(id={self.id}, isbn='{self.isbn}', " \
               f"title='{self.title}', " \
               f"publication_year={self.publication_year}, " \
               f"author_id={self.author_id})"

    def __str__(self):
        return f"{self.title}"
