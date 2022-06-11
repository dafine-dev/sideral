from sideral.schema import Table
from sideral.schema import Column
from sideral.schema import PrimaryKey
from sideral.schema import ForeignKey
from sideral.query import builder
from sideral.query import Join


account_table = Table(name = 'Account')

account_pk = Column(name = 'id')
password = Column(name = 'password')
username = Column(name = 'username')
status = Column(name = 'status')

account_table.primary_key = PrimaryKey(account_pk)

account_table.add_column(account_pk)
account_table.add_column(username)
account_table.add_column(password)
account_table.add_column(status)

post_table = Table(name = 'Post')

post_pk = Column(name = 'id_post')
content = Column(name = 'content')
likes = Column(name = 'likes')
post_table.primary_key = PrimaryKey(post_pk)

post_table.add_column(post_pk)
post_table.add_column(content)
post_table.add_column(likes)

fk_column = Column(name = 'id_account')
fk = ForeignKey(fk_column, account_pk)
post_table.add_column(fk_column)
post_table.add_foreign_key(fk)



def test_simple_select():
    sql = builder.Select() \
            .columns(account_table.columns) \
            .from_(account_table) \
    
    expected_sql = \
        "select " + \
            "Account_1.id as Account_id, " + \
            "Account_1.username as Account_username, " + \
            "Account_1.password as Account_password, " + \
            "Account_1.status as Account_status " + \
        "from " \
            "Account as Account_1; "
    
    assert sql.statement == expected_sql


def test_joined_select():
    sql = builder.Select() \
            .columns(account_table.columns) \
            .columns(fk.column) \
            .from_(account_table) \
            .join(post_table, on = fk.column == fk.reference, type = Join.INNER)
        
    expected_sql = \
        "select " + \
            "Account_1.id as Account_id, " + \
            "Account_1.username as Account_username, " + \
            "Account_1.password as Account_password, " + \
            "Account_1.status as Account_status, " + \
            "Post_1.id_account as Post_id_account " + \
        "from " + \
            "Account as Account_1 " + \
        "inner join " + \
            "Post as Post_1 " + \
        "on " + \
            "Post_1.id_account = Account_1.id; "

    assert sql.statement == expected_sql


def test_where_select():
    _id = 'adf35ad7f8ava7'
    sql = builder.Select() \
            .columns(post_table.columns) \
            .from_(post_table) \
            .where(post_pk == _id)
        
    expected_sql = \
        "select " + \
            "Post_1.id_post as Post_id_post, " + \
            "Post_1.content as Post_content, " + \
            "Post_1.likes as Post_likes, " + \
            "Post_1.id_account as Post_id_account " + \
        "from " + \
            "Post as Post_1 " + \
        "where " + \
            f"Post_1.id_post = 0x{_id.encode('utf-8').hex()}; "
    
    assert sql.statement == expected_sql


def test_defer_select():
    sql = builder.Select() \
            .columns(account_table.columns) \
            .defer([password]) \
            .from_(account_table)
    
    expected_sql = \
        "select " + \
            "Account_1.id as Account_id, " + \
            "Account_1.username as Account_username, " + \
            "Account_1.status as Account_status " + \
        "from " + \
            "Account as Account_1; "
    
    assert sql.statement == expected_sql


def test_order_by_select():
    sql = builder.Select() \
            .columns(account_table.columns) \
            .from_(account_table) \
            .order_by(account_pk)
    
    expected_sql = \
        "select " + \
            "Account_1.id as Account_id, " + \
            "Account_1.username as Account_username, " + \
            "Account_1.password as Account_password, " + \
            "Account_1.status as Account_status " + \
        "from " \
            "Account as Account_1 " + \
        "order by " + \
            "Account_1.id; "
    
    assert sql.statement == expected_sql


def test_insert():
    username_value = 'ronalderdman'
    password_value = '10TeMwsevtJPOkU'
    sql = builder.Insert() \
            .into(account_table) \
            .values([
                (account_pk, 1),
                (username, username_value),
                (password, password_value),
                (status, True)
            ])
    
    expected_sql = \
        "insert into " + \
            "Account " + \
            "(Account.id, Account.username, Account.password, Account.status) " + \
        "values " + \
            f"(1, 0x{username_value.encode('utf-8').hex()}, 0x{password_value.encode('utf-8').hex()}, True); "
    
    assert sql.statement == expected_sql


def test_insert_with_null_id():
    username_value = 'ronalderdman'
    password_value = '10TeMwsevtJPOkU'
    sql = builder.Insert() \
            .into(account_table) \
            .values([
                (account_pk, None),
                (username, username_value),
                (password, password_value),
                (status, True)
            ])
    
    expected_sql = \
        "insert into " + \
            "Account " + \
            "(Account.id, Account.username, Account.password, Account.status) " + \
        "values " + \
            f"(default, 0x{username_value.encode('utf-8').hex()}, 0x{password_value.encode('utf-8').hex()}, True); "
    
    assert sql.statement == expected_sql


def test_insert_on_duplicate_key_error():
    sql = builder.Insert() \
            .into(post_table) \
            .values([
                (post_pk, 1),
                (content, ''),
                (likes, 10),
                (fk_column, 1)
            ]).on_duplicate_key()
    
    expected_sql = \
        "insert into " + \
            "Post " + \
            "(Post.id_post, Post.content, Post.likes, Post.id_account) " + \
        "values " + \
            "(1, '', 10, 1) " + \
        "on duplicate key " + \
        "update " + \
            "Post.id_post = 1, Post.content = '', Post.likes = 10, Post.id_account = 1; "
    
    assert sql.statement == expected_sql


def test_update():
    sql = builder.Update() \
            .table(account_table) \
            .set([
              (status, False)  
            ])
    
    expected_sql = 'update Account set Account.status = False; '

    assert sql.statement == expected_sql


def test_where_update():
    user = 'ronald'
    pswrd = 'SOcFLL9pfQ7Mais'
    sql = builder.Update() \
            .table(account_table) \
            .set([
                (username, user),
                (password, pswrd),
                (status, False)  
            ]) \
            .where(account_pk == 1)
    
    expected_sql = \
        "update " + \
            "Account " + \
        "set " + \
            f"Account.username = 0x{user.encode('utf-8').hex()}, " + \
            f"Account.password = 0x{pswrd.encode('utf-8').hex()}, " + \
            f"Account.status = False " + \
        "where " + \
            "Account.id = 1; "

    assert sql.statement == expected_sql


def test_delete():
    sql = builder.Delete().from_(account_table)
    expected_sql = 'delete from Account; '
    assert sql.statement == expected_sql


def test_where_delete():
    sql = builder.Delete().from_(account_table).where(account_pk == 1)
    expected_sql = 'delete from Account where Account.id = 1; '
    assert sql.statement == expected_sql