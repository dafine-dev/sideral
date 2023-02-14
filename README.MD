

<h1>Introduction</h1>
<p>Sideral is an ORM (Object Relational Mapper) framework for Python applications which use a MySQL database. It is designed to easily generate repositories able to retrieve row-based information and map it to objects, as well as, translate objects to rows and persist them. To achieve it, besides the needing to understand the correlation between an application’s model classes and their database tables, the framework must provide ways to manage connections and coordinate transactions occurring within them. Sideral succeeds in doing it by just adding minor changes to the code, thus, keeping it as clean as possible.</p>

<h1>Setting up</h1>

<p>To begin, firstly, Sideral must be installed. To do it, use this command:</p>

<div class = "code">
<pre style = "text-aling: center;">pip install sideral</pre>
</div>

<p>Sideral was thought to be used in MVC (Model View Control) systems, so it's recommended that the application structure looks like this:</p>

<div class = "code">
<pre>
src:
    |
    |-- models.py
    |-- repository.py
    |-- database.conf
    |-- main.py
</pre>
</div>

<p>Or like this:</p>

<div class = "code">
<pre>
src:
    |
    |-- models
    |    | -- __init__.py
    |-- repository
    |    | -- __init__.py
    |-- database.conf
    |-- main.py
</pre>
</div>

<p>The <i>database.conf</i> file sets the needed information to create a connection with the desired database. This file has to be in the same directory of the one responsible for running the application. In its inner code, the data must be passed after the <i>[connection]</i> line and be written this way:<p>

<div class = "code">
<pre>
[connection]
host = host_name
database = database_name
user = user_name
password = password
</pre>
</div>

<p>It isn't mandatory to have this file structure. But it's important to make sure all model classes are loaded before using any of them to Sideral work correctly.</p>

<h1>
How to use
</h1>
<p>
Sideral works around its annotations, which are Python decorators intended to be used, generally, on/inside a class. When imported to a project, they modify some Sideral’s inner procedures aspects, if correctly employed. Due to the framework’s architecture, the object-relational mapping is the key process; hence, the annotations – in majority – were thought to be implemented jointly with a model class. However, it’s also noteworthy that to take advantage of this mapping, it’s necessary to build access points. Therefore, Sideral offers annotations able to generate repository classes with custom CRUD operations, besides ones responsible for managing these transactions.
</p>

<p>
The following sections will detail all available annotations, their functionalities, where and how to implement them properly; by responsibility.
</p>
<br>

<h2>
Mapping
</h2>

<p>
Whereas Python applications organize information in classes, objects and attributes; a database storing uses tables, rows and columns. These data structures are not always homogenously and directly represented on the opposite context, hence, these gaps must be tracked and solved.
</p>
<p>
The mapping annotations, by decorating a model class, sets the information needed to Sideral settle these divergences and, thus, be able to convert freely through both structure patterns.
</p>

<br>
<h3 style = "font-weight: bold">
1. Entity</i>
</h3>

<p>
Entity is a model class that has a direct representation in the database as a table and its attributes are mapped as columns. Mapping a class as a database entity is possible by using the <i>@entity</i> annotation on a class:
</p>

<div>
<pre>
from sideral import entity
</br>@entity
class Client:
    ...
</pre>
</div>

<p>
By default, Sideral will assume the class name is also the correspondent table's. In this case: "Client" is both class and table names; but, by adding the <i>name</i> parameter, this default assumption is avoided and a new table name is set.
</p>


<div>
<pre>
from sideral import entity
</br>@entity(name = 'Clients')
class Client:
    ...
</pre>
</div>

<p>
A table has its columns, some of them are mapped as attributes while others may not. Thus, Sideral has a <i>@column</i> annotation to manage this mapping, but it has a small catch. The <i>@column</i> works similarly to Python built-in decorator <i>@property</i>, so all to-column-mapped attributes must be private and define getter and setter functions. Consequently, an entity class should be written like this:
</p>

<div class = "code">
<pre>
from sideral import entity, column<br>
@entity
class Client:<br>
    @column
    def name(self) -> str:
        return self._name<br>
    @name.setter
    def name(self, name: str) -> None:
        self._name = name
</pre>
</div>

<p>
The <i>@column</i> annotation infer the column name to be the same as the annotated attribute's. But, this denomination can be changed by passing a <i>name</i> argument through the decorator parameters:
</p>

<div clas = "code">
<pre>
@column(name = "client_name")
def name(self) -> str:
    return self._name
</pre>
</div>

<p>
In Sideral, there is a special type of column, thought to define which column is the primary key representation. The <i>@id</i> annotation works exactly as <i>@column</i>, but Sideral accepts only one primary key per table.

<div class = "code">
<pre>
from sideral import entity, id<br>
@entity
class Client:<br>
    @id
    def id(self) -> int:
        return self._id
</pre>
</div>
</p>
<br>
<h3>2. Relationship</h3>

<p>
Model classes are associated among themselves and it's important to store and retrieve these relationships from the database. Sideral offers some annotations accountable for mapping these links and, like the previously mentioned <i>@column</i> annotation, they only work on private attributes with implemented getter and setter methods. Moreover, since Sideral saves associations through queries apart, it doesn't support mandatory relationships; also, a relationship annotation knows which class it refers to by accessing the getter function's return type hint, so it's crucial to fill it.
</p>

<div class = "code">
<pre>
from __future__ import annotations
from sideral import entity, many_to_one<br>
@entity
class Order:<br>
    @many_to_one
    def client(self) -> Client:
        return self._client<br>
    @client.setter
    def client(self, client: Client) -> None:
        self._client = client
</pre>
</div>

<p>
In order to connect both sides of a given association, a <i>mapping</i> parameter can be passed through decorator. The mapping values need to be a string and contain the attribute name which represents the relationship opposite side. By filling this field, class instances, retrieved from the database, will have an "loop association" with its related objects.

<div class = "code">
<pre>
from __future__ import annotations
from sideral import one_to_many, many_to_one, entity<br>
@entity
class Client:<br>
    @one_to_many(mapping = 'client')
    def orders(self) -> list[Order]:
        return self._orders
<br>
@entity
class Order:<br>
    @many_to_one(mapping = 'orders')
    def client(self) -> Client:
        return self._client
</pre>
</div>
</p>


<p>
Differently from an object-oriented enviroment, in which an association link stores the whole associated information in object form (or in a list containing many of this), a database context persists these links using foreign keys. In this manner, these keys are columns inside a table, hence, they have a name. And as the <i>@entity</i> or <i>@column</i>, the relationship annotations surmise its foreign key name is equal: to the name whose table the key refers to, preffixed with "id_" characters. However, it's possible to set a non default denomination by using the <i>@join</i> decorator above any side of the relationship.
</p>

<div class = "code">
<pre>
@join(column_name = 'client_id') # previous name: 'id_client'
@many_to_one
def client(self) -> Client:
    return self._client
</pre>
</div>

<p>
or
</p>

<div class = "code">
<pre>
@join(column_name = 'client_id')
@one_to_many
def orders(self) -> list[Order]:
    return self._orders
</pre>
</div>

<br>
<h3 class= "sub-section">2.1. One to many / many to one</h3>

<p>
One to many is one of the relationship types between two tables. As precociously seen above, Sideral uses two annotations to map this association. While <i>@many_to_one</i> must be inside the class which has a single reference to the other side, the <i>@one_to_many</i> decorator has to be used in the class that has a list of objects. It's also noteworthy that its getter return hint should be an <i>List</i>/<i>list</i> embracing the associated class type variable. At last, the table, whose equivalent class has an <i>@many_to_one</i> decorator, must own the foreign key that describes the relationship.
</p>

<div class = "code">
<pre>
from __future__ import annotations
from sideral import one_to_many, many_to_one, entity<br>
@entity
class Client:<br>
    @one_to_many(mapping = 'client')
    def orders(self) -> list[Order]:
        return self._orders
<br>
@entity
class Order:<br>
    @many_to_one(mapping = 'orders')
    def client(self) -> Client:
        return self._client
</pre>
</div>

<br>
<h3 class = "sub-section">2.2. One to one</h3>

<p>
When both sides of a relationship carry a single reference to each other, it's a use case for Sideral <i>@one_to_one</i> annotation. This decorator can be implemented in any side, thus, marking a one to one relationship type between two classes. But, differently from one to many, any table involved in the association can own the foreign key. So, the <i>owner</i> parameter (when <i>True</i>), signs which table must have the join column. At last, if none of the annotations set this parameter, Sideral will assume the firstly loaded one to be the owner. 
</p>

<div class = "code">
<pre>
from __future__ import annotations
from sideral import entity, one_to_one<br>
@entity
class Student:<br>
    @one_to_one(mapping = "student")
    def scholarship(self) -> Scholarship:
        return self._scholarship<br>
@entity
class Scholarship:<br>
    @one_to_one(mapping = "scholarship", owner = True)
    def student(self) -> Student:
        return self._student
</pre>
</div>

<br>
<h3 class = "sub-section">2.3. Many to many</h3>

<p>
Sideral has a <i>@many_to_many</i> decorator, which, just like the <i>@one_to_one</i>, can be used in any class involved in the association. But, unlike its "relative", both sides carry a list of instances to the other and its type hints must have, following this logic, a <i>list/List</i> in it.
</p>
<p>
In order to map this case to a database, a third table - known as join table - is necessary to completely describe the relationship between two entities. Therefore, Sideral will presume the join table name consists of the two related tables', sorted alphabetically, joined by an "_" character. However, it is possible to import the <i>@join_table</i> annotation and use it above the <i>@many_to_many</i> decorator to define a new name.
</p>

<p>
A join table owns both foreign keys derived from two entities in association. And although it's already been presented how Sideral presumes join column names, a many to many relation has some minor differences when renaming these keys. While the <i>@join</i> renames the foreign key referecing the table whose class the annotation is implemented in, the <i>@counter_join</i> is used to rename the opposite side's key of the relationship.
</p>

<div class = "code">
<pre>
from __future__ import annotations
from sideral import entity, many_to_many, join, counter_join, join_table<br>
@entity
class Book:<br>
    @counter_join(column_name = 'author_id') # previous name: 'id_author'
    @join(column_name = 'book_id') # previous name: 'id_book'
    @join_table(name = 'book_authors_join') # previous name: 'Author_Book'
    @many_to_many(mapping = 'books')
    def authors(self) -> list[Author]:
        return self._authors<br>
@entity
class Author:<br>
    @many_to_many(mapping = 'authors')
    def books(self) -> list[Book]:
        return self._books
</pre>
</div>

<p>Each side of the relationship can also set its own join column name.</p>

<div class = "code">
<pre>
from __future__ import annotations
from sideral import entity, many_to_many, join, join_table<br>
@entity
class Book:<br>
    @join(column_name = 'book_id') # previous name: 'id_book'
    @join_table(name = 'book_authors_join') # previous name: 'Author_Book'
    @many_to_many(mapping = 'books')
    def authors(self) -> list[Author]:
        return self._authors<br>
@entity
class Author:<br>
    @join(column_name = 'author_id') # previous name: 'id_author'
    @many_to_many(mapping = 'authors')
    def books(self) -> list[Book]:
        return self._books
</pre>
</div>

<p>Or even the counter join.</p>

<div class = "code">
<pre>
from __future__ import annotations
from sideral import entity, many_to_many, counter_join, join_table<br>
@entity
class Book:<br>
    @counter_join(column_name = 'author_id') # previous name: 'id_author'
    @join_table(name = 'book_authors_join') # previous name: 'Author_Book'
    @many_to_many(mapping = 'books')
    def authors(self) -> list[Author]:
        return self._authors<br>
@entity
class Author:<br>
    @counter_join(column_name = 'book_id') # previous name: 'id_book'
    @many_to_many(mapping = 'authors')
    def books(self) -> list[Book]:
        return self._books
</pre>
</div>

<br>

<h3>3. Inheritance</h3>

<p>
Although native ways to structure inheritance in a database don't exist, there are globally accepted strategies to simulate it. Sideral currently supports two of these methods, one recommended to map long vertical class hierarchies and the other  for single-layered inheritance with many sub-types. 
</p>

<p>
With the objective to set which inheritance representation is being used to a group of classes in the persistent context, thus, making possible a correct object-relational translation; it's needed to import the <i>@inheritance</i> annotation and the <i>strategy</i> enum object. After, the first must be used on the super class, annotated with <i>@entity</i>, and the second has to be passed as parameter to choose the proper strategy. Nevertheless, it's substantial to annotate the sub/child classes too, which will vary according to the case.
</p>

<p>
Lastly, despite Python's tolerance towards multiple inheritance, there aren't enough cases, if any, in which it's worth to map it to a database. In other words, there are more efficient manners to structure this kind of situations and they should be used. Consequently, Sideral considers the first class, passed through Python inheritance field, the unique parent or base class of a child.
</p>

<br>

<h3 class = "sub-section">3.1. Joined table</h3>

<p>
The joined table strategy consists of having one table for each class involved in an inheritance relation. So, the tables in the database only owns columns which refer to exclusive attributes from their correspondent class plus a primary - and foreign - key derived from the class right above on the hierarchy.
</p>

<p>
To set this strategy to a class, the <i>strategy</i>.JOINED_TABLE item must be passed through the <i>@inheritance</i> decorator, which, in turn, goes on top of the super class. Furthermore, the sub classes has to be decorated with the <i>@entity</i> as they have their own table in the database; following the <i>@derived_key</i> annotation, which adds the formely cited inheritance key to the mapping between base and sub class and firms it.
</p>

<div class = "code">
<pre>
from __future__ import annotations
from sideral import entity, inheritance, strategy<br>
@entity
@inheritance(type = strategy.JOINED_TABLE)
class Functionary:
    ...<br>
@derived_key
@entity
class Supervisor(Functionary):
    ...

</pre>
</div>

<p>
Similarly to the <i>@join</i> annotation, the <i>@derived_key</i> supposes the column name; but, in this case, the default denomination is equal to "id_" plus the the table name which owns it. Still similarly, the annotation also accepts a <i>name</i> parameter responsible for dodging this default behavior.
</p>

<div class = "code">
<pre>
@derived_key(name = 'id') # previous name: 'id_supervisor'
@entity
class Supervisor(Functionary):
    ...
</pre>
</div>

<p>
Since sub classes possess a representation in the database as tables, they can also be a parent class and have their own inheritance type towards its children, which does not have to be the JOINED_TABLE strategy. 
</p>

<div class = "code">
<pre>
from __future__ import annotations
from sideral import entity, inheritance, strategy<br>
@entity
@inheritance(type = strategy.JOINED_TABLE)
class Functionary:
    ...<br>
@derived_key
@entity
@inheritance(type = strategy.JOINED_TABLE)
class Supervisor(Functionary):
    ...<br>
@derived_key
@entity
class Manager(Supervisor):
    ...
</pre>
</div>

<p>
Or
</p>

<div class = "code">
<pre>
from __future__ import annotations
from sideral import entity, inheritance, strategy, subclass, discriminator<br>
@entity
@inheritance(type = strategy.JOINED_TABLE)
class Functionary:
    ...<br>
@discriminator(name = 'supervisor_type', value = 1)
@derived_key
@entity
@inheritance(type = strategy.SINGLE_TABLE)
class Supervisor(Functionary):
    ...<br>
@discriminator(value = 2)
@subclass
class Manager(Supervisor):
    ...
</pre>
</div>

<br>

<h3 class = "sub-section">3.2. Single table</h3>

<p>
The single table strategy is ideal for cases in which there aren't many variations between the mapped attributes from a super class to its sub classes'. Thereby, all attributes from every class participating in the inheritance is mapped to columns in the same table. Also, to distinct the class each row belongs to, it's required a discriminator column responsible for indicating this based on the value contained in it.  
</p>

<p>
So as use this inheritance mapping, the <i>@inheritance</i> annotation, with the SINGLE_TABLE <i>strategy</i>'s item as <i>type</i> parameter, has to decorate the parent class. Besides that, the <i>@discriminator</i> decorator shall be implemented on the former's top to define the discriminator column data; the <i>name</i> argument for setting the column name and the <i>value</i> one for the class representing code.
</p>

<p>
With the super class annotated, its sub classes should also be, but by the <i>@subclass</i> decorator instead. In addition, the <i>@discriminator</i> must be used, though just to declare, by setting the <i>value</i> parameter, the child's corresponding value, since the <i>name</i> argument is reserved for the parent class.
</p>

<p>
To conclude, in contrast to the joined table strategy, the sub classes participating in this mapping case must be the end of its hierarchy ramification, to put it another way, all <i>@subclass</i> annotated models don't accept the <i>@inheritance</i> decorator; hence, a class inheriting from them can't be part of the object-relational mapping.
</p>

<div class = "code">
<pre>
from sideral import entity, subclass, discriminator, inheritance, strategy<br>
@discriminator(name = 'type', value = 1)
@entity
@inheritance(type = strategy.SINGLE_TABLE)
class Functionary:
    ...<br>
@discriminator(value = 2)
@subclass
class Supervisor(Functionary):
    ...
</pre>
</div>

<br>

<h3 class = "sub-section">3.3. Overriding getters and setters</h3>

<p>
Due to Sideral's custom descriptors usage for implementing private attributes, some questions may rise when it comes to overriding them. As formerly said, these descriptors has a functioning analagous to Python's <i>@property</i>, therefore, their overriding technique should remains unchanged, which would consists of rewriting them at the overrider sub class.
</p>

<p>
However, considering Sideral's annotations "add a object-relational mapping layer" to a Python descriptor object, the rewriting mentioned above would cause a duplicated mapping for the same column or relationship. In joined table, for example, both parent and child classes would own columns with the same characteristics. 
</p>

<p>
So, for an adequate overriding, the mapping layer should be detached, which would result in a <i>@property</i> decorator equal's; this way, the built-in one must be used. Moreover, when recycling a setter function from a super class, it has to be called by "set", instead of the "fset" usual name from Python properties. 
</p>

<div class = "code">
<pre>
from sideral import entity, inheritance, strategy, column, derived_key<br>
@entity
@inheritance(type = strategy.JOINED_TABLE)
class Functionary:<br>
    @column
    def name(self) -> str:
        return self._name<br>
    @name.setter
    def name(self, name: str) -> None:
        self._name = name<br>
@derived_key
@entity
class Supervisor(Functionary):<br>
    @property
    def name(self) -> str:
        return super().name<br>
    @name.setter
    def name(self, name: str) -> None:
        return Functionary.name.set(self, name) # recycled setter function
</pre>
</div>


<br>

<h3>4. Loading objects</h3>
<p>
Retrieve data from the database can trigger, for a single object, multiple select queries. So, aiming to oversee the performance and memory usage, attribute mapping annotations accept a <i>load</i> parameter that dictates when these queries are executed.
</p>


<p>
By requesting an object, its attributes are loaded in, basically, two occasions. The first, called eager load, happens when the request is made and it's generally used to access core data. And the latter runs when an attribute is specifically accessed, it's called lazy load and is generally used to load heavy situational informations. With this difference, objects can be loaded in quantity without executing unneeded selects or flooding the computer memory with countless instances or byte variables.
</p>

<p>
Sideral, by default, assumes <i>@column</i> annotated attributes to be core information, thereby are eagerly loaded, whereas relationships are lazily requested. But by importing the <i>load</i> enum object and passing it through the parameter of identical name, the annotations can use any loading strategy - EAGER for eager, LAZY for lazy.
</p>

<p>
Besides the strategies presented, the <i>load</i> enum has another in its items: the NO. It consists of never loading an information from the database, which can be useful for confidential columns like passwords or dispensable relationships.
</p>

<div class = "code">
<pre>
from sideral import entity, column, load, one_to_many<br>
@entity
class Account:<br>
    @column(load = load.LAZY) # previous loading: EAGER
    def username(self) -> str:
        return self._username<br>
    @column(load = load.NO) # previous loading: EAGER
    def password(self) -> str:
        return self._password<br>
    @one_to_many(load = load.EAGER) # previous loading: LAZY
    def posts(self) -> list[Post]:
        return self._posts

</pre>
</div>

<br>

<h3>5. Persisting objects</h3>

<p>
When pushing an object to the database, all its to-column-mapped attributes are going to be saved. So, to avoid access errors, they must be defined. Additionally, Sideral will update <i>None</i> and <i>Ellipsis</i> (or ...) as null values. However, not only columns compose an object's data, so their relationships must be persisted too.
</p>

<p>
If Sideral saves all relationships within an object's persist transaction, it would cause multiple queries being executed in sequence, some of them unnedeed. Aiming to control this behavior, relationship annotations accept a <i>master</i> parameter. When <i>True</i>, initiating a persist operation for an class instance causes the association to be saved in cascade, in other words, queries for updating the correspondent foreign key would be executed right after the default ones. Consequently, since only actual relationship information is saved, the objects related must already exist in the database.
</p>

<div class = "code">
<pre>
from sideral import entity, many_to_one<br>
@entity
class Post:<br>
    #now saving a post would save the Account - Post relationship too.
    @many_to_one(master = True)
    def account(self) -> Account:
        return self._account
</pre>
</div>

<br>

<h2>Repository</h2>

<p>
Repositories are classes, modified by Sideral, which act as access points to the database for a model participating in the object-relational mapping. They can return instances of its model originated from the persistent context, as well as, save them. To create a Sideral repository, it's necessary to import the <i>@repository</i> annotation and use it on a class, that can even be blank, with the mapped class as argument. By decorating the class, Sideral will automatically add the CRUD methods specific to the class parameterized.
</p>

<div class = "code">
<pre>
from . import models
from sideral import repository<br>
@repository(models.Account) 
class AccountRepository:
    ...<br>
@repository(models.Post)
class PostRepository:
    ...
</pre>
</div>

<p>
The custom methods, their required parameters and returns are detailed below:
</p>

<ul>
<li> <i>select_all</i>: receives no arguments and returns all model objects existing in the database in a list;</li>
<li> <i>select_by_id</i>: receives an id value and return a single model instance which has primary key equals to the value passed;
<li> <i>save</i>: receives a single model instance, save it to the database and returns its persisted version;</li>
<li> <i>save_all</i>: receives an list containing many model instances, save each at a time and returns their persisted versions in a list as well;
<li> <i>delete</i>: receives an id value and delete instance information related to that specific id, this method returns nothing;
</ul>

<p>
It's also noteworthy that repositories, whose models are decorated with the <i>@inheritance</i> annotation, can return instances of their model's sub types through their select methods, but they can't save or delete them. So, it's recommended that all mapped classes have their correspondent repository.
</p>

<br>

<h2>Transaction</h2>


<p>When perfoming any repository operation, a new connection is created, then a new transaction begins, queries are executed, changes commited and, finally, the connection is closed. Thus, if any error occurs during the transaction, the changes are rollbacked. This behavior pattern is called unit of work and all repository methods' implementation follows it.</p>

<p>
Although it works well for single operations, there are occasions that many methods from many repositories should be in the same transaction. So, in order to support this kind of situations, Sideral has a <i>@transaction</i> annotation that controls transaction creation and usage.
</p>

<p>
Differently from other Sideral's annotations, which have strict places to be used, this one can be implemented in any part of a project. Though, it's recommended to be decorating the service layer. The <i>@transaction</i> must be used on Python functions (belonging to a class or not). When done, all repository methods used inside the function will be part of the same transaction.
</p>

<div class = "code">
<pre>
from sideral import transaction
from .models import Order
from .repository import OrderRepository, ProductRepository<br>
class OrderService:<br>
    @transaction
    def save_order(self, order: Order) -> Order:
        product = order.product
        product.quantity -= 1
        ProductRepository.save(product)
        return OrderRepository.save(order)
</pre>
</div>

<p>
Additionally, a <i>@transaction</i> decorated function, by default, merge with the already initiated transaction if it's implemented inside another one. However, this behavior can be changed by setting the isolated parameter to <i>True</i>.
</p>

<div class = "code">
<pre>
from sideral import transaction
from .models import Order
from .repository import OrderRepository, ProductRepository<br>
class OrderService:<br>
    @transaction(isolated = True)
    def save_order(self, order: Order) -> Order:
        product = order.product
        product.quantity -= 1
        ProductRepository.save(product)
        return OrderRepository.save(order)
</pre>
</div>
