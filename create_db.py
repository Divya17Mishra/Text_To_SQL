from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    bio = Column(String(255))
    books = relationship('BookAuthor', back_populates='author')

class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    description = Column(String(255))
    books = relationship('Book', back_populates='genre')

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    description = Column(String(255))
    ISBN = Column(CHAR(13))
    genre_id = Column(Integer, ForeignKey('genres.id'))
    genre = relationship('Genre', back_populates='books')
    authors = relationship('BookAuthor', back_populates='book')

class BookAuthor(Base):
    __tablename__ = 'books_authors'
    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'), primary_key=True)
    is_main_author = Column(Boolean)
    book = relationship('Book', back_populates='authors')
    author = relationship('Author', back_populates='books')

# Create the SQLite database
engine = create_engine('sqlite:///books.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Sample data
if not session.query(Author).first():
    genre1 = Genre(name='Fantasy', description='Fantasy books')
    genre2 = Genre(name='Science Fiction', description='Sci-Fi books')
    session.add_all([genre1, genre2])
    session.commit()

    author1 = Author(name='J.K. Rowling', bio='Author of Harry Potter')
    author2 = Author(name='Isaac Asimov', bio='Science fiction writer')
    session.add_all([author1, author2])
    session.commit()

    book1 = Book(title='Harry Potter and the Philosopher\'s Stone', description='First Harry Potter book', ISBN='9780747532699', genre=genre1)
    book2 = Book(title='Foundation', description='First Foundation book', ISBN='9780553293357', genre=genre2)
    session.add_all([book1, book2])
    session.commit()

    ba1 = BookAuthor(book=book1, author=author1, is_main_author=True)
    ba2 = BookAuthor(book=book2, author=author2, is_main_author=True)
    session.add_all([ba1, ba2])
    session.commit()

    print('Sample data inserted!')
else:
    print('Database already has data.') 