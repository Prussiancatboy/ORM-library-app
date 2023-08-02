import os
from flask import Flask, render_template, request, redirect, url_for
from data_models import db


class LibraryApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = \
            'sqlite:///' + os.path.join(os.path.abspath(
                os.path.dirname(__file__)), 'data', 'library.sqlite')
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)

        # Register routes
        self.app.route('/add_author', methods=['GET', 'POST']
                       )(self.add_author)

        self.app.route('/add_book', methods=['GET', 'POST']
                       )(self.add_book)

        self.app.route('/', methods=['GET'])(self.home)

        self.app.route('/sort_books', methods=['GET'])(self.sort_books)

        self.app.route('/search_books', methods=['GET'])(self.search_books)

        self.app.route('/book/<int:book_id>/delete', methods=['POST']
                       )(self.delete_book)

    def run(self):
        with self.app.app_context():
            # Create the tables
            db.create_all()
        self.app.run(debug=True)

    def add_author(self):
        """This handles author additions"""
        if request.method == 'POST':
            # Get data from the form
            name = request.form['name']
            birthdate = request.form['birthdate']
            date_of_death = request.form['date_of_death']

            # Convert the birthdate and date_of_death strings to date objects
            from datetime import datetime
            birth_date = datetime.strptime(birthdate, '%Y-%m-%d').date()
            date_of_death = datetime.strptime(
                date_of_death, '%Y-%m-%d').date() if date_of_death else None

            # Create a new author record and add it to the database
            author = Author(name=name, birth_date=birth_date,
                            date_of_death=date_of_death)

            db.session.add(author)
            db.session.commit()

            # Display a success message on the /add_author page
            return redirect(url_for(
                'home', success_message=f'Author {name} added successfully.'))

        return render_template('add_author.html')

    def add_book(self):
        """This handles book additions"""
        if request.method == 'POST':
            # Get data from the form
            title = request.form['title']
            # This will be the selected author's ID from the dropdown
            author_id = request.form['author']
            # Get the publishing year from the form
            publication_year = request.form['publication_year']
            # Get the ISBN code from the form
            isbn = request.form['isbn']

            # Create a new book record and add it to the database
            book = Book(title=title, author_id=author_id,
                        publication_year=publication_year, isbn=isbn)
            db.session.add(book)
            db.session.commit()

            # Redirect to the home page with the success message
            return redirect(url_for(
                'home', success_message=f'Book "{title}" '
                                        f'added successfully.'))

        # Query all authors to populate the dropdown in the form
        authors = Author.query.all()
        return render_template('add_book.html', authors=authors)

    def home(self):
        """This handles the homepage"""
        books = Book.query.all()

        # Fetch the author names for each book using the author_id
        author_names = {author.id: author.name
                        for author in Author.query.all()}

        # Extract relevant data (title, author name,
        # ISBN, and publication year) from books
        book_data = []
        for book in books:
            author_name = author_names.get(book.author_id, "Unknown Author")

            book_info = {
                "title": book.title,
                "author": author_name,
                "isbn": book.isbn,
                "publication_year": book.publication_year,
                "id": book.id
            }
            book_data.append(book_info)

        # Get the success_message from the query string, if present
        success_message = request.args.get('success_message')

        return render_template('home.html',
                               books=book_data,
                               success_message=success_message)

    def sort_books(self):
        """This sorts the books"""

        # Get the sorting criteria from the query string
        sort_by = request.args.get('sort_by')

        if sort_by == 'title':
            # Sort books by title
            books = Book.query.order_by(Book.title).all()
        elif sort_by == 'author':
            # Sort books by author's name
            books = Book.query.order_by(Book.author_id).all()
        else:
            # Default sorting by book's primary key (ID)
            books = Book.query.all()

        # Fetch the author names for each book using the author_id
        author_names = {author.id: author.name
                        for author in Author.query.all()}

        # Extract relevant data (title,
        # author name, ISBN, publication year, and ID) from books
        book_data = []
        for book in books:
            author_name = author_names.get(book.author_id, "Unknown Author")

            book_info = {
                "id": book.id,
                # Add the 'id' attribute to the book_info dictionary
                "title": book.title,
                "author": author_name,
                "isbn": book.isbn,
                "publication_year": book.publication_year
            }
            book_data.append(book_info)

        return render_template('home.html', books=book_data)

    def search_books(self):
        """This searches through the books"""
        search_term = request.args.get('search_term')

        if search_term:
            # Perform the search using the LIKE keyword
            books = Book.query.filter(
                Book.title.like(f"%{search_term}%")).all()

            if books:
                # Fetch the author names for each book using the author_id
                author_names = {
                    author.id: author.name for author in Author.query.all()}

                # Extract relevant data
                # (title, author name, ISBN, and publication year) from books
                book_data = []
                for book in books:
                    author_name = \
                        author_names.get(book.author_id, "Unknown Author")

                    book_info = {
                        "id": book.id,
                        # Add the 'id' attribute to the book_info dictionary
                        "title": book.title,
                        "author": author_name,
                        "isbn": book.isbn,
                        "publication_year": book.publication_year
                    }
                    book_data.append(book_info)

                return render_template('home.html',
                                       books=book_data,
                                       search_term=search_term)
            else:
                # Display a message if no books match the search criteria
                return render_template(
                    'home.html', books=[],
                    search_term=search_term, no_results=True)

        # Redirect to the home route if no search term is provided
        return redirect(url_for('home'))

    def delete_book(self, book_id):
        """This code allows you to delete books"""
        # Get the book by its ID from the database
        book = Book.query.get(book_id)

        if book:
            # Get the author ID before deleting the book
            author_id = book.author_id

            # Delete the book from the database
            db.session.delete(book)
            db.session.commit()

            # Check if the author has any other books in the library
            book_count = Book.query.filter_by(author_id=author_id).count()

            if book_count == 0:
                # If the author doesn't have any other books,
                # delete the author as well
                author = Author.query.get(author_id)
                if author:
                    db.session.delete(author)
                    db.session.commit()

            # Redirect back to the homepage with the success message
            return redirect(url_for(
                'home', success_message='Book deleted successfully.'))
        else:
            # Book not found,
            # redirect back to the homepage with an error message
            return redirect(url_for(
                'home', success_message='Error: Book not found.'))


if __name__ == '__main__':
    from data_models import *
    app = LibraryApp()
    app.run()
